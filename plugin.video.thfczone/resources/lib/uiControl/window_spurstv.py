# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmc
import xbmcgui

'''######------External Modules-----#####'''
from collections import Counter

'''#####-----Internal Modules-----#####'''
from _actions import *
from resources.lib.modules._addon import *
from resources.lib.modules._common import Log,DateTimeStrf
from resources.lib.modules import tottenhamhotspur

class WindowSpursTv(xbmcgui.WindowXML):

	xmlFilename = 'Window_spurstv.xml'
	scriptPath  = addon_path
	defaultSkin = 'Default'
	defaultRes  = '720p'

	FILTER_GROUP  = 1000
	FILTER_MENU   = 1001
	SEARCH_BUTTON = 1003
	MAIN_MENU     = 2000

	def __new__(cls,listitems,*args,**kwargs):
		return super(WindowSpursTv, cls).__new__(cls,WindowSpursTv.xmlFilename, WindowSpursTv.scriptPath, WindowSpursTv.defaultSkin, WindowSpursTv.defaultRes)


	def __init__(self,listitems,*args,**kwargs):
		super(WindowSpursTv,self).__init__()
		self.listitems = listitems
		self.taglist = kwargs.get('taglist')
		self.tags = self.GetFilterTags()

	def onInit(self):
		self.control_main_menu = self.getControl(self.MAIN_MENU)
		if self.control_main_menu.size() == 0:
			for i in self.listitems:
				date = DateTimeStrf(i[7],'%Y-%m-%d')
				Liz = xbmcgui.ListItem(date,i[1])
				Liz.setInfo('video', {'aired':date})
				Liz.setArt({'poster':i[2]})
				Liz.setProperties({'partnerId':i[3],'entryId':i[4]})
				self.control_main_menu.addItem(Liz)
		self.setFocus(self.control_main_menu)
		self.control_filter_list = self.getControl(self.FILTER_MENU)
		if self.control_filter_list.size() == 0:
			for t in self.tags:
				Liz = xbmcgui.ListItem(t[0]+'('+str(t[1])+')')
				self.control_filter_list.addItem(Liz)
		self.control_filter_list.setHeight(len(self.tags)*30)

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == self.FILTER_MENU:
				self.FilterBy(self.control_filter_list.getListItem(int(self.control_filter_list.getSelectedPosition())))
			elif self.getFocusId() == self.MAIN_MENU:
				self.PlayMedia(self.control_main_menu.getListItem(int(self.control_main_menu.getSelectedPosition())))

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
		super(WindowSpursTv,self).close()

	def GetFilterTags(self):
		tagslist = []
		tag = []
		for item in self.listitems:
			tagslist += eval(item[5])
		C = Counter(tagslist)
		if self.taglist:
			for c in C.items():
				if c[0] in self.taglist:
					tag.append(c)
		else:
			tag = C.items()
		tags = sorted(tag, key=lambda tup: tup[1],reverse=True)
		return tags


	def FilterBy(self,listitem):
		filtertag = listitem.getLabel().split('(')[0].strip()
		self.control_main_menu.reset()
		for i in self.listitems:
			if filtertag in eval(i[5]):
				date = DateTimeStrf(i[7],'%Y-%m-%d')
				Liz = xbmcgui.ListItem(date,i[1])
				Liz.setInfo('video', {'aired':date})
				Liz.setArt({'poster':i[2]})
				Liz.setProperties({'partnerId':i[3],'entryId':i[4]})
				self.control_main_menu.addItem(Liz)
		self.setFocus(self.control_main_menu)


	def PlayMedia(self,listitem):
		title = listitem.getLabel2()
		media = tottenhamhotspur.GetMediaStream(listitem.getProperty('partnerID'),listitem.getProperty('entryID'))
		liz = xbmcgui.ListItem(title)
		liz.setInfo('video',{'Title':title})
		xbmc.Player().play(media, liz)
		while(not xbmc.abortRequested):
			xbmc.sleep(1000)
