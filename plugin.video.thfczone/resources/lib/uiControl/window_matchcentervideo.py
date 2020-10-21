# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
'''___info__ add other xbmc library modules xbmcgui will be needed'''
import xbmcgui


'''######------External Modules-----#####'''
import datetime
import sqlite3

'''#####-----Internal Modules-----#####'''
from  _actions import *
from resources.lib.modules._addon import *
from resources.lib.modules._common import Log,DateTimeDelta,DateTimeStrp,FromTimeStamp,ToTimeStamp
from resources.lib.modules import tottenhamhotspur


class WindowMatchCenterVideo(xbmcgui.WindowXML):

	xmlFilename = 'Window_matchcentervideo.xml'
	scriptPath  = addon_path
	defaultSkin = 'Default'
	defaultRes  = '720p'

	MENU_LIST   = 2000

	def __new__(cls,listitem,*args,**kwargs):
		return super(WindowMatchCenterVideo, cls).__new__(cls,WindowMatchCenterVideo.xmlFilename, WindowMatchCenterVideo.scriptPath, WindowMatchCenterVideo.defaultSkin, WindowMatchCenterVideo.defaultRes)


	def __init__(self,listitem,*args,**kwargs):
		super(WindowMatchCenterVideo,self).__init__()
		self.listitem = listitem
		self.videoitems = self.GetVideos(self.listitem)

	def onInit(self):
		self.control_list = self.getControl(self.MENU_LIST)
		if self.control_list.size() == 0:
			for item in self.videoitems:
				media = item.get('media')
				liz = xbmcgui.ListItem(item.get('title'))
				liz.setArt({'poster':media.get('thumbnail').get('url')})
				liz.setProperties({'partnerId':media.get('partnerId'),'entryId':media.get('entryId')})
				self.control_list.addItem(liz)
		self.setFocus(self.control_list)


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
		super(WindowMatchCenterVideo,self).close()

	def setControlVisible(self, controlId, visible):
		if not controlId:
			Log('controlId {} not recognized'.format(controlId))
			return
		control = self.getControl(controlId)
		if control:
			control.setVisible(visible)


	def GetVideos(self,listitem):
		videolist = []
		tottenhamhotspur.TrendingGrid(0,1,listitem.getProperty('tag_id'),100,'')
		matchdt = FromTimeStamp(listitem.getProperty('matchdatetime'))
		for items in tottenhamhotspur.TRENDING_GRID:
			article = items.get('data').get('article')
			# Log(article.get('isVideoPage'))
			article_dt = DateTimeStrp(article.get('date'),"%Y-%m-%dT%H:%M:%SZ")
			article_dt_min = DateTimeDelta(article_dt,d=-7)
			article_dt_max = DateTimeDelta(article_dt,d=7)
			if article.get('isVideoPage')== True:
				if matchdt > article_dt_min and matchdt < article_dt_max:
					tag_list = article.get('tags')
					if not any(d.get('id') == 45833 for d in tag_list):
						videolist.append(article)
		return videolist


	def PlayMedia(self,listitem):
		title = listitem.getProperty('fulltitle')
		media = tottenhamhotspur.GetMediaStream(listitem.getProperty('partnerID'),listitem.getProperty('entryID'))
		liz = xbmcgui.ListItem(title)
		liz.setInfo('video',{'Title':title})
		xbmc.Player().play(media, liz)
		while(not xbmc.abortRequested):
			xbmc.sleep(1000)






