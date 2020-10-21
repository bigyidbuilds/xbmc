# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
'''___info__ add other xbmc library modules xbmcgui will be needed'''
import xbmcgui


'''######------External Modules-----#####'''
'''___info__ add External Modules that are required'''
import youtube_requests

'''#####-----Internal Modules-----#####'''
from _actions import *
from resources.lib.modules._addon import *
from resources.lib.modules._common import Log

BANNER    = 1000
MAIN_LIST = 2000

xmlFilename = 'Window_youtubecontent.xml'
scriptPath  = addon_path
defaultSkin = 'Default'
defaultRes  = '720p'

class WindowYoutubePlayList(xbmcgui.WindowXML):



	def __new__(cls,listitem,*args,**kwargs):
		return super(WindowYoutubePlayList, cls).__new__(cls,xmlFilename, scriptPath, defaultSkin, defaultRes)


	def __init__(self,listitem,*args,**kwargs):
		super(WindowYoutubePlayList,self).__init__()
		self.youtube_id = listitem.getProperty('youtube_id')
		self.channelbanner = listitem.getArt('banner')
		self.content = youtube_requests.get_playlists_of_channel(self.youtube_id,  addon_id=addon_id)


	def onInit(self):
		self.setControlImage(BANNER,self.channelbanner)
		self.main_list_control = self.getControl(MAIN_LIST)
		if self.main_list_control.size() == 0:
			for c in self.content:
				s = c.get('snippet')
				if s:
					liz = xbmcgui.ListItem(s.get('title'))
					liz.setArt({'thumb':s.get('thumbnails').get('high').get('url'),'banner':self.channelbanner})
					liz.setProperties({'playlist_id':c.get('id')})
					self.main_list_control.addItem(liz)
		self.setFocus(self.main_list_control)

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == MAIN_LIST:
				d=WindowYoutubePlayListVideos(self.main_list_control.getListItem(int(self.main_list_control.getSelectedPosition())))
				d.doModal()
				del d

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
		super(WindowYoutubePlayList,self).close()
		
	def setControlImage(self, controlId,img):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setImage(img)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return


class WindowYoutubePlayListVideos(xbmcgui.WindowXML):



	def __new__(cls,listitem,*args,**kwargs):
		return super(WindowYoutubePlayListVideos, cls).__new__(cls,xmlFilename, scriptPath, defaultSkin, defaultRes)


	def __init__(self,listitem,*args,**kwargs):
		super(WindowYoutubePlayListVideos,self).__init__()
		self.playlist_id = listitem.getProperty('playlist_id')
		self.channelbanner = listitem.getArt('banner')
		self.content = youtube_requests.get_playlist_items(self.playlist_id,  addon_id=addon_id)


	def onInit(self):
		self.setControlImage(BANNER,self.channelbanner)
		self.main_list_control = self.getControl(MAIN_LIST)
		if self.main_list_control.size() == 0:
			for c in self.content:
				s = c.get('snippet')
				if s:
					liz = xbmcgui.ListItem(s.get('title'))
					liz.setArt({'thumb':s.get('thumbnails').get('high').get('url'),'banner':self.channelbanner})
					liz.setProperties({'video_id':s.get('resourceId').get('videoId')})
					self.main_list_control.addItem(liz)
		self.setFocus(self.main_list_control)

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == MAIN_LIST:
				self.PlayUtube(self.main_list_control.getListItem(int(self.main_list_control.getSelectedPosition())))


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
		super(WindowYoutubePlayListVideos,self).close()
		
	def setControlImage(self, controlId,img):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setImage(img)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return


	def PlayUtube(self,listitem):
		from resources.lib.modules import youtubeapi
		youtubeapi.YouTubePlayer().Play(listitem.getProperty('video_id'))



class WindowYoutubeList(xbmcgui.WindowXML):



	def __new__(cls,listitem,order,*args,**kwargs):
		return super(WindowYoutubeList, cls).__new__(cls,xmlFilename, scriptPath, defaultSkin, defaultRes)


	def __init__(self,listitem,order,*args,**kwargs):
		super(WindowYoutubeList,self).__init__()
		self.channelbanner = listitem.getArt('banner')
		self.query = kwargs.get('searchQuery','')
		self.content = youtube_requests.get_search(self.query, search_type='video', channel_id=listitem.getProperty('youtube_id'), order=order, safe_search='none', addon_id=addon_id)


	def onInit(self):
		self.setControlImage(BANNER,self.channelbanner)
		self.main_list_control = self.getControl(MAIN_LIST)
		if self.main_list_control.size() == 0:
			for c in self.content:
				s = c.get('snippet')
				if s:
					liz = xbmcgui.ListItem(s.get('title'))
					liz.setArt({'thumb':s.get('thumbnails').get('high').get('url'),'banner':self.channelbanner})
					liz.setProperties({'video_id':c.get('id').get('videoId')})
					self.main_list_control.addItem(liz)
		self.setFocus(self.main_list_control)

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == MAIN_LIST:
				self.PlayUtube(self.main_list_control.getListItem(int(self.main_list_control.getSelectedPosition())))


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
		super(WindowYoutubeList,self).close()
		
	def setControlImage(self, controlId,img):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setImage(img)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return


	def PlayUtube(self,listitem):
		from resources.lib.modules import youtubeapi
		youtubeapi.YouTubePlayer().Play(listitem.getProperty('video_id'))