# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
'''___info__ add other xbmc library modules xbmcgui will be needed'''
import xbmcgui


'''######------External Modules-----#####'''
import datetime
import sqlite3


'''#####-----Internal Modules-----#####'''
from _actions import *
from resources.lib.modules._addon import *
from resources.lib.modules._common import DateTimeStrf,FromTimeStamp,Log,ToTimeStamp,KeyBoard
from resources.lib.modules import youtubeapi


class WindowYoutubeChannel(xbmcgui.WindowXML):

	xmlFilename = 'Window_youtubechannel.xml'
	scriptPath  = addon_path
	defaultSkin = 'Default'
	defaultRes  = '720p'


	MAIN_ITEMLIST    = 2000
	SUB_ITEMLIST     = 3000

	def __new__(cls,*args,**kwargs):
		return super(WindowYoutubeChannel, cls).__new__(cls,WindowYoutubeChannel.xmlFilename, WindowYoutubeChannel.scriptPath, WindowYoutubeChannel.defaultSkin, WindowYoutubeChannel.defaultRes)


	def __init__(self,*args,**kwargs):
		super(WindowYoutubeChannel,self).__init__()
		self.conn = None
		self.dbConnection()
		self.mainmenuitems = self.GetMainMenuItems()
		youtubeapi.YouTubeApi().RegistarAPIkey()

	def onInit(self):
		self.main_control_list = self.getControl(self.MAIN_ITEMLIST)
		if self.main_control_list.size() == 0:
			for i in self.mainmenuitems:
				Liz = xbmcgui.ListItem(i[1])
				Liz.setArt({'thumb':i[0],'banner':i[4]})
				Liz.setProperty('youtube_id',i[3])
				Liz.setInfo('video',{'plot':i[2]})
				self.main_control_list.addItem(Liz)
		self.setFocus(self.main_control_list)
		self.LoadSubMenu(self.main_control_list.getListItem(int(self.main_control_list.getSelectedPosition())))


	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_UP,ACTION_DOWN,ACTION_PAGE_UP,ACTION_PAGE_DOWN] and self.getFocusId() == self.MAIN_ITEMLIST: 
			self.LoadSubMenu(self.main_control_list.getListItem(int(self.main_control_list.getSelectedPosition())))
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == self.SUB_ITEMLIST:
				self.SubMenuAction(self.sub_control_list.getListItem(int(self.sub_control_list.getSelectedPosition())))

	def onClick(self,controlId):
		'''
		onClick method.

					This method will receive all click events that the main program will send to this window.

		Parameters
					self	Own base class pointer
		controlId	The one time clicked GUI control identifier
		Example:
				# Define own function where becomes called from Kodi
				def onClick(self,controlId):
					if controlId == 10:
						print("The control with Id 10 is clicked")
		'''

	def onControl(self,control):
		'''
		Function: onControl(self, Control)
				onControl method.

		This method will receive all click events on owned and selected controls when the control itself doesn't handle the message.

		Parameters
			self	Own base class pointer
			control	The Control class
		Example:
			# Define own function where becomes called from Kodi
			def onControl(self, control):
				print("Window.onControl(control=[%s])"%control)
		'''

	def onDoubleClick(self,controlId):
		'''
		Function: onDoubleClick(self, int controlId)
				onDoubleClick method.

		This method will receive all double click events that the main program will send to this window.

		Parameters
				self	Own base class pointer
				controlId	The double clicked GUI control identifier
		Example:
				# Define own function where becomes called from Kodi
				def onDoubleClick(self,controlId):
				  if controlId == 10:
					print("The control with Id 10 is double clicked")
		'''

	def onFocus(self,controlId):
		'''
		Function: onFocus(self, int controlId)
				onFocus method.

		This method will receive all focus events that the main program will send to this window.

		Parameters
			self	Own base class pointer
			controlId	The focused GUI control identifier
		Example:
		# Define own function where becomes called from Kodi
		def onDoubleClick(self,controlId):
		   if controlId == 10:
		   print("The control with Id 10 is focused")
		'''

	def Close(self):
		super(WindowYoutubeChannel,self).close()
		
	def GetMainMenuItems(self):
		c=self.conn.cursor()
		c.execute("SELECT * FROM youtube_channels")
		return c.fetchall()

	def LoadSubMenu(self,listitem):
		youtube_id = listitem.getProperty('youtube_id')
		banner = listitem.getArt('banner')
		self.sub_control_list = self.getControl(self.SUB_ITEMLIST)
		self.sub_control_list.reset()
		for i in [{'title':'Play Lists','func':'playlists'},{'title':'Latest Videos','func':'latestvideos'},{'title':'Popular Videos','func':'popularvideos'},{'title':'Rated Videos','func':'ratedvideos'},{'title':'Search Channel','func':'searchchannel'}]:
			liz = xbmcgui.ListItem(i.get('title'))
			i.update({'youtube_id':youtube_id})
			liz.setProperties(i)
			liz.setArt({'banner':banner})
			self.sub_control_list.addItem(liz)

	def SubMenuAction(self,listitem):
		import window_youtubecontent
		func = listitem.getProperty('func')
		if func == 'playlists':
			d=window_youtubecontent.WindowYoutubePlayList(listitem)
			d.doModal()
			del d
		elif func == 'latestvideos':
			d=window_youtubecontent.WindowYoutubeList(listitem,'date')
			d.doModal()
			del d
		elif func == 'popularvideos':
			d=window_youtubecontent.WindowYoutubeList(listitem,'viewCount')
			d.doModal()
			del d
		elif func == 'ratedvideos':
			d=window_youtubecontent.WindowYoutubeList(listitem,'rating')
			d.doModal()
			del d
		elif func == 'searchchannel':
			searchquery = KeyBoard('Enter search phrase or keywords')
			d=window_youtubecontent.WindowYoutubeList(listitem,'relevance',searchQuery=searchquery)
			d.doModal()
			del d



	def dbConnection(self):
		sqlite3.register_adapter(datetime.datetime, ToTimeStamp)
		sqlite3.register_converter('timestamp', FromTimeStamp)
		# self.lock = threading.Lock()
		self.conn = sqlite3.connect(CACHEDB, detect_types=sqlite3.PARSE_DECLTYPES,check_same_thread=False)
		self.conn.execute('PRAGMA foreign_keys = ON')
		self.conn.row_factory = sqlite3.Row
		self.conn.text_factory = str
