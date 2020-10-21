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
from resources.lib.modules._common import Log,ToTimeStamp,FromTimeStamp
from resources.lib.modules import tottenhamhotspur


class WindowMatchCenterHighlight(xbmcgui.WindowXML):

	xmlFilename = 'Window_matchcenteritem.xml'
	scriptPath  = addon_path
	defaultSkin = 'Default'
	defaultRes  = '720p'

	MENU_LIST = 2000

	def __new__(cls,listitem,*args,**kwargs):
		return super(WindowMatchCenterHighlight, cls).__new__(cls,WindowMatchCenterHighlight.xmlFilename, WindowMatchCenterHighlight.scriptPath, WindowMatchCenterHighlight.defaultSkin, WindowMatchCenterHighlight.defaultRes)


	def __init__(self,listitem,*args,**kwargs):
		super(WindowMatchCenterHighlight,self).__init__()
		self.InitDB()
		self.listitem = listitem
		self.highlight_list = self.getHighlights(self.listitem)

	def onInit(self):
		self.control_list = self.getControl(self.MENU_LIST)
		if self.control_list.size() == 0:
			for highlight in self.highlight_list:
				fullname = highlight[1]
				if ':' in fullname:
					name = fullname.split(':',1)[0]
				liz = xbmcgui.ListItem(name)
				liz.setProperties({'partnerID':highlight[3],'entryID':highlight[4],'fulltitle':fullname})
				self.control_list.addItem(liz)

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == self.MENU_LIST:
				self.PlayMedia(self.control_list.getListItem(int(self.control_list.getSelectedPosition())))

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
		super(WindowMatchCenterHighlight,self).close()
		'''
		Function: close()
			Closes this window.

		Closes this window by activating the old window.

		Note
			The window is not deleted with this method. 
		'''

	def InitDB(self):
		sqlite3.register_adapter(datetime.datetime, ToTimeStamp)
		sqlite3.register_converter('timestamp', FromTimeStamp)
		sqlite3.register_adapter(bool, int)
		sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
		self.conn = sqlite3.connect(CACHEDB, detect_types=sqlite3.PARSE_DECLTYPES,check_same_thread=False)
		self.conn.execute('PRAGMA foreign_keys = ON')
		self.conn.row_factory = sqlite3.Row
		self.conn.text_factory = str



	def getHighlights(self,listitem):
		matchdate_str = listitem.getProperty('matchdate_str')
		tag = listitem.getProperty('tag')
		tag_query = '%'+tag+'%'
		partmatchdate_str = 'xx.'+matchdate_str.split('.',1)[1]
		Log(partmatchdate_str)
		c = self.conn.cursor()
		c.execute("SELECT * FROM spurs_tv_highlights WHERE matchdate=? ",(matchdate_str,))
		a = c.fetchall()
		c.execute("SELECT * FROM spurs_tv_highlights WHERE matchdate=? AND tags LIKE ?",(partmatchdate_str,tag_query))
		a = a+c.fetchall()
		return a


	def PlayMedia(self,listitem):
		title = listitem.getProperty('fulltitle')
		media = tottenhamhotspur.GetMediaStream(listitem.getProperty('partnerID'),listitem.getProperty('entryID'))
		liz = xbmcgui.ListItem(title)
		liz.setInfo('video',{'Title':title})
		xbmc.Player().play(media, liz)
		while(not xbmc.abortRequested):
			xbmc.sleep(1000)




