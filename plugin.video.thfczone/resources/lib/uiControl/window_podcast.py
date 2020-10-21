# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
'''___info__ add other xbmc library modules xbmcgui will be needed'''
import xbmc
import xbmcgui


'''######------External Modules-----#####'''
import datetime
import sqlite3


'''#####-----Internal Modules-----#####'''
from _actions import *
from resources.lib.modules._addon import *
from resources.lib.modules._common import DateTimeStrf,FromTimeStamp,Log,ToTimeStamp


class WindowPodcast(xbmcgui.WindowXML):

	xmlFilename = 'Window_podcast.xml'
	scriptPath  = addon_path
	defaultSkin = 'Default'
	defaultRes  = '720p'

	MAIN_ITEMLIST    = 2000
	EPISODE_ITEMLIST = 3000
	PODPLAYER_GROUP  = 6000
	PODPLAYER_ICON   = 6001
	PODPLAYER_STOP   = 6003
	PODPLAYER_PLAY   = 6004
	PODPLAYER_LABEL  = 6005
	PODPLAYER_DESC   = 6007

	def __new__(cls,*args,**kwargs):
		return super(WindowPodcast, cls).__new__(cls,WindowPodcast.xmlFilename, WindowPodcast.scriptPath, WindowPodcast.defaultSkin, WindowPodcast.defaultRes)
		'''___info___
		xmlFilename	string - the name of the xml file to look for.
		scriptPath	string - path to script. used to fallback to if the xml doesn't exist in the current skin. (eg xbmcaddon.Addon().getAddonInfo('path').decode('utf-8'))
		defaultSkin	[opt] string - name of the folder in the skins path to look in for the xml. (default='Default')
		defaultRes	[opt] string - default skins resolution. (1080i, 720p, ntsc16x9, ntsc, pal16x9 or pal. default='720p')
		'''

	def __init__(self,*args,**kwargs):
		super(WindowPodcast,self).__init__()
		self.conn = None
		self.dbConnection()
		self.mainmenuitems = self.GetMainMenuItems()
		'''
		___info__ addcode items you wish to be run when class is called
		'''

	def onInit(self):
		self.main_control_list = self.getControl(self.MAIN_ITEMLIST)
		if self.main_control_list.size() == 0:
			for i in self.mainmenuitems:
				Liz = xbmcgui.ListItem(i[1])
				Liz.setArt({'thumb':i[3]})
				Liz.setProperty('pod_id',i[0])
				Liz.setInfo('video',{'plot':i[2]})
				self.main_control_list.addItem(Liz)
		self.setFocus(self.main_control_list)
		self.LoadEpisodes(self.main_control_list.getListItem(int(self.main_control_list.getSelectedPosition())))

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_UP,ACTION_DOWN,ACTION_PAGE_UP,ACTION_PAGE_DOWN] and self.getFocusId() == self.MAIN_ITEMLIST: 
			self.LoadEpisodes(self.main_control_list.getListItem(int(self.main_control_list.getSelectedPosition())))
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == self.EPISODE_ITEMLIST:
				self.PlayPod(self.episode_list.getListItem(int(self.episode_list.getSelectedPosition())))


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
		Log('onFocus: {}'.format(controlId))
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
		super(WindowPodcast,self).close()
		'''
		Function: close()
			Closes this window.

		Closes this window by activating the old window.

		Note
			The window is not deleted with this method. 
		'''

	def setControlImage(self, controlId,label):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setImage(label)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return

	def setControlLabel(self, controlId, label):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control and label:
			control.setLabel(label)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return

	def PlayPod(self,listitem):
		xbmc.Player().play(listitem.getPath(), listitem, windowed=True)

	def LoadEpisodes(self,listitems):
		pod_id = listitems.getProperty('pod_id')
		self.episode_list = self.getControl(self.EPISODE_ITEMLIST)
		self.episode_list.reset()
		c=self.conn.cursor()
		c.execute("SELECT * FROM podcast_episodes WHERE podcast_id=? ORDER BY episode_pubdate DESC",(pod_id,))
		items = c.fetchall()
		for i in items:
			liz = xbmcgui.ListItem(i[1])
			liz.setInfo('video',{'plot':" ".join(i[2].split())})
			liz.setArt({'thumb':i[4]})
			liz.setProperty('Date',DateTimeStrf(i[3],'%d %B %Y'))
			liz.setPath(i[5])
			self.episode_list.addItem(liz)
		



	def GetMainMenuItems(self):
		c=self.conn.cursor()
		c.execute("SELECT * FROM podcast_channels")
		return c.fetchall()


	def dbConnection(self):
		sqlite3.register_adapter(datetime.datetime, ToTimeStamp)
		sqlite3.register_converter('timestamp', FromTimeStamp)
		# self.lock = threading.Lock()
		self.conn = sqlite3.connect(CACHEDB, detect_types=sqlite3.PARSE_DECLTYPES,check_same_thread=False)
		self.conn.execute('PRAGMA foreign_keys = ON')
		self.conn.row_factory = sqlite3.Row
		self.conn.text_factory = str

