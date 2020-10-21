# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmcgui
import xbmcvfs

'''######------External Modules-----#####'''
import datetime
import os
import sqlite3
import threading
'''#####-----Internal Modules-----#####'''
from _actions import *
from resources.lib.modules._addon import *
from resources.lib.modules._common import Log,DownloadFile,DelAllContents
from resources.lib.modules import tottenhamhotspur



class WindowMatchCenterItems(xbmcgui.WindowXML):

	xmlFilename = 'Window_matchcenteritem.xml'
	scriptPath  = addon_path
	defaultSkin = 'Default'
	defaultRes  = '720p'

	MENU_ITEMS = [{'name':'Replays & Highlights','func':'self.loadReplays'},{'name':'Team Line ups','func':'self.loadLineUp'},{'name':'Videos & Interviews','func':'self.loadVideos'},{'name':'Back','func':'self.Close'}]

	MENU_LIST = 2000

	def __new__(cls,listitem,*args,**kwargs):
		return super(WindowMatchCenterItems, cls).__new__(cls,WindowMatchCenterItems.xmlFilename, WindowMatchCenterItems.scriptPath, WindowMatchCenterItems.defaultSkin, WindowMatchCenterItems.defaultRes)


	def __init__(self,listitem,*args,**kwargs):
		super(WindowMatchCenterItems,self).__init__()
		self.listitem = listitem
		self.slide_temp_path = os.path.join(addon_profile,'temp','matchcenter_slides')
		try:
			self.MatchSlides(self.listitem.getProperty('matchreportUrl'))
		except:
			pass


	def onInit(self):
		self.control_list = self.getControl(self.MENU_LIST)
		if self.control_list.size() == 0:
			for i in self.MENU_ITEMS:
				Liz = xbmcgui.ListItem(i.get('name'))
				Liz.setProperty('func',i.get('func'))
				self.control_list.addItem(Liz)
		self.setFocus(self.control_list)

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == self.MENU_LIST:
				self.RunFunc(self.control_list.getListItem(int(self.control_list.getSelectedPosition())))


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
		DelAllContents(self.slide_temp_path)
		super(WindowMatchCenterItems,self).close()
		'''
		Function: close()
			Closes this window.

		Closes this window by activating the old window.

		Note
			The window is not deleted with this method. 
		'''
	def setControlVisible(self, controlId, visible):
		if not controlId:
			Log('controlId {} not recognized'.format(controlId))
			return
		control = self.getControl(controlId)
		if control:
			control.setVisible(visible)

	def RunFunc(self,lI):
		eval(lI.getProperty('func'))()

	def MatchSlides(self,url):
		threads = []
		if not xbmcvfs.exists(self.slide_temp_path):
			xbmcvfs.mkdirs(self.slide_temp_path)
		slides = tottenhamhotspur.GetMatchReportImages(url)
		for slide in slides:
			slide = slide
			threads.append(threading.Thread(target=DownloadFile, args=(slide.get('image') .get('url'),os.path.join(self.slide_temp_path,slide.get('image') .get('name')))))
		for thread in threads:
			thread.start()
		for thread in threads:
			thread.join()

	def loadLineUp(self):
		import window_matchcenterlineup
		d=window_matchcenterlineup.WindowMatchCenterLineup(self.listitem)
		d.doModal()
		del d

	def loadReplays(self):
		import window_matchcenterhighlight
		d=window_matchcenterhighlight.WindowMatchCenterHighlight(self.listitem)
		d.doModal()
		del d

	def loadVideos(self):
		import window_matchcentervideo
		d=window_matchcentervideo.WindowMatchCenterVideo(self.listitem)
		d.doModal()
		del d