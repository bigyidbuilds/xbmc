# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
'''___info__ add other xbmc library modules xbmcgui will be needed'''
import xbmc
import xbmcgui
import xbmcplugin


'''######------External Modules-----#####'''
import datetime
import requests
import sqlite3
import sys
import time
import xml.etree.ElementTree as ET


'''#####-----Internal Modules-----#####'''
from resources.lib.modules._addon import *
from resources.lib.modules._common import Log
from resources.lib.modules import youtubeapi
from resources.lib.modules import tottenhamhotspur
from _actions import *



class WindowHome(xbmcgui.WindowXML):

	xmlFilename = 'Window_home.xml'
	scriptPath  = addon_path
	defaultSkin = 'Default'
	defaultRes  = '720p'

	listitem = [
				('MatchCenter',1),
				('PodCasts',2),
				('THFC YouTube Channels',3),
				('Spurs TV',4),
				('Tools & Settings',5),
				('Close',100)
				]

	RSS_FEED             = 1000
	ITEMLIST             = 2000
	NEXTMATCH_GROUP      = 3000
	NM_LEAGUE_LOGO       = 3001
	NM_HOMEBADGE         = 3002
	NM_AWAYBADGE         = 3003
	NM_DATETIME          = 3004
	NM_STADNAME          = 3005
	NM_STADIMAGE         = 3006
	NM_LEAGUE_NAME       = 3007
	NM_HOMENAME          = 3008
	NM_AWAYNAME          = 3009
	NM_BUTTON            = 3010
	LATESTPOD_GROUP      = 4000
	LATESTPOD_BUTTON     = 4001
	LATESTPOD_LIST       = 4002
	LATESTUTUBE_GROUP    = 5000
	LATESTUTUBE_BUTTON   = 5001
	LATESTUTUBE_LIST     = 5002
	PODPLAYER_GROUP      = 6000
	PODPLAYER_ICON       = 6001
	PODPLAYER_STOP       = 6003
	PODPLAYER_PLAY       = 6004
	PODPLAYER_LABEL      = 6005
	PODPLAYER_DESC       = 6007
	DIALOG_BOX           = 7000
	DIALOG_TEXT          = 7001
	DIALOG_BUTTON_A      = 7002
	DIALOG_BUTTON_B      = 7003
	DIALOG_BUTTON_C      = 7004
	LATESTSPURSTV_GROUP  = 8000
	LATESTSPURSTV_BUTTON = 8001
	LATESTSPURSTV_LIST   = 8002

	def __new__(cls,*args,**kwargs):
		return super(WindowHome, cls).__new__(cls,WindowHome.xmlFilename, WindowHome.scriptPath, WindowHome.defaultSkin, WindowHome.defaultRes)


	def __init__(self,*args,**kwargs):
		super(WindowHome,self).__init__()
		youtubeapi.YouTubeApi().RegistarAPIkey()
		self.InitDB()

	def onInit(self):
		self.setControlVisible(self.DIALOG_BOX,False)
		self.control_list = self.getControl(self.ITEMLIST)
		if self.control_list.size() == 0:
			for i in self.listitem:
				Liz = xbmcgui.ListItem(i[0])
				Liz.setProperty('mode',str(i[1]))
				self.control_list.addItem(Liz)
		self.setFocus(self.control_list)
		self.setNextMatch()
		self.RssFeed()
		self.setLatestPods()
		self.setLatestUtube()
		self.setLatestSpursTv()
		

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == self.ITEMLIST:
				self.MainMenuControl(self.control_list.getListItem(int(self.control_list.getSelectedPosition())))
			elif self.getFocusId() == self.LATESTPOD_LIST:
				self.PlayPod(self.control_list_pod.getListItem(int(self.control_list_pod.getSelectedPosition())))
			elif self.getFocusId() == self.LATESTUTUBE_LIST:
				self.PlayUtube(self.control_list_utube.getListItem(int(self.control_list_utube.getSelectedPosition())))
			elif self.getFocusId() == self.LATESTSPURSTV_LIST:
				self.PlaySpursTv(self.control_list_spurstv.getListItem(int(self.control_list_spurstv.getSelectedPosition())))


	def onClick(self,controlId):
		Log('onClick: {}'.format(controlId))
		if controlId == self.DIALOG_BUTTON_A:
			self.DialogButtonA()
		elif controlId == self.DIALOG_BUTTON_B:
			self.DialogButtonB()
		elif controlId == self.DIALOG_BUTTON_C:
			self.DialogButtonC()
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
		if xbmc.getCondVisibility('Player.HasMedia'):
			self.setControlText(self.DIALOG_TEXT,'Media is still playing')
			self.setControlLabel(self.DIALOG_BUTTON_A,'Stop & Close')
			self.setControlLabel(self.DIALOG_BUTTON_B,'Close')
			self.setControlLabel(self.DIALOG_BUTTON_C,'Cancel')
			self.buttonA = self.PlayerStopClose
			self.buttonB = self.ActivateWindowHome
			self.buttonC = self.CancelDialog
			self.setControlVisible(self.DIALOG_BOX,True)
			self.setFocusId(self.DIALOG_BUTTON_A)
		else:
			self.ActivateWindowHome()

	def setControlFadeLabel(self, controlId,label):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.addLabel(label)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return

	def setControlProgress(self,controlId,percent):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setPercent(percent)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return


	def setControlImage(self, controlId,label):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setImage(label)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return

	def setControlVisible(self, controlId, visible):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setVisible(visible)
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

	def setControlText(self, controlId,text):
		if not controlId:
			return
		control = self.getControl(controlId)
		if control:
			control.setText(text)
		else:
			Log('controlId {} not recognized'.format(controlId))
			return

	def DialogButtonA(self):
		self.buttonA()

	def DialogButtonB(self):
		self.buttonB()

	def DialogButtonC(self):
		self.buttonC()

	def ActivateWindowHome(self):
		xbmc.executebuiltin('XBMC.ActivateWindow(Home)')

	def PlayerStopClose(self):
		xbmc.Player().stop()
		self.ActivateWindowHome()

	def CancelDialog(self):
		self.setControlVisible(self.DIALOG_BOX,False)


	def PlayPod(self,listitem):
		self.setControlImage(self.PODPLAYER_ICON,listitem.getArt('thumb'))
		self.setControlLabel(self.PODPLAYER_LABEL,listitem.getLabel())
		self.setControlLabel(self.PODPLAYER_DESC,listitem.getProperty('description'))
		xbmc.Player().play(listitem.getPath(), listitem, windowed=True)


	def PlayUtube(self,listitem):
		youtubeapi.YouTubePlayer().Play(listitem.getProperty('video_id'))

	def PlaySpursTv(self,listitem):
		title = listitem.getLabel()
		media = tottenhamhotspur.GetMediaStream(listitem.getProperty('partnerID'),listitem.getProperty('entryID'))
		liz = xbmcgui.ListItem(title)
		liz.setInfo('video',{'Title':title})
		xbmc.Player().play(media, liz)
		while(not xbmc.abortRequested):
			xbmc.sleep(1000)

	def MainMenuControl(self,items):
		mode = int(items.getProperty('mode'))
		if mode == 1:
			import window_matchcenter
			d=window_matchcenter.WindowMatchCenter()
			d.doModal()
			del d
		elif mode == 2:
			import window_podcast
			d=window_podcast.WindowPodcast()
			d.doModal()
			del d
		elif mode == 3:
			import window_youtubechannel
			d=window_youtubechannel.WindowYoutubeChannel()
			d.doModal()
			del d
		elif mode == 4:
			import window_spurstvhome
			d=window_spurstvhome.WindowSpursTvHome()
			d.doModal()
			del d
		elif mode == 5:
			import window_tools
			d=window_tools.WindowTools()
			d.doModal()
			del d 
		elif mode == 6:
			pass
		else:
			self.Close()

	def setNextMatch(self):
		c = self.conn.cursor()
		c.execute("SELECT * FROM present_season WHERE isNextFixture=?",(True,))
		nextmatch = c.fetchall()
		if nextmatch:
			self.setControlImage(self.NM_LEAGUE_LOGO,nextmatch[0][10])
			self.setControlImage(self.NM_HOMEBADGE,nextmatch[0][6])
			self.setControlImage(self.NM_AWAYBADGE,nextmatch[0][7])
			self.setControlLabel(self.NM_DATETIME,nextmatch[0][0].strftime('%A, %d %B %H:%M'))
			self.setControlLabel(self.NM_STADNAME,nextmatch[0][5])
			self.setControlLabel(self.NM_LEAGUE_NAME,nextmatch[0][1])
			self.setControlLabel(self.NM_HOMENAME,nextmatch[0][2])
			self.setControlLabel(self.NM_AWAYNAME,nextmatch[0][3])
		c.close()

	def InitDB(self):
		sqlite3.register_adapter(datetime, self.adapt_datetime)
		sqlite3.register_converter('timestamp', self.convert_datetime)
		sqlite3.register_adapter(bool, int)
		sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
		self.conn = sqlite3.connect(CACHEDB, detect_types=sqlite3.PARSE_DECLTYPES,check_same_thread=False)
		self.conn.execute('PRAGMA foreign_keys = ON')
		self.conn.row_factory = sqlite3.Row
		self.conn.text_factory = str


	def RssFeed(self):
		root = ET.fromstring(requests.get('https://www.football.london/tottenham-hotspur-fc/?service=rss').content)
		channel = root.find('channel')
		supplier = channel.find('title').text
		for item in channel.findall('item'):
			self.setControlFadeLabel(self.RSS_FEED,'[B][I]'+supplier+'[/I], '+item.find('title').text+'[/B]: '+item.find('description').text)


	def setLatestPods(self):
		self.control_list_pod = self.getControl(self.LATESTPOD_LIST)
		c = self.conn.cursor()
		c.execute("SELECT * FROM podcast_episodes ORDER BY episode_pubdate DESC")
		pods = c.fetchmany(3)
		for pod in pods:
			liz = xbmcgui.ListItem(pod[1])
			liz.setPath(pod[5])
			liz.setInfo('video', {'plot':pod[2]})
			liz.setProperty('description',pod[2])
			liz.setArt({'thumb':pod[4]})
			self.control_list_pod.addItem(liz)

	def setLatestUtube(self):
		self.control_list_utube = self.getControl(self.LATESTUTUBE_LIST)
		c = self.conn.cursor()
		c.execute("SELECT * FROM youtube_latest ORDER BY publishtime DESC")
		uvids = c.fetchmany(3)
		for uvid in uvids:
			liz = xbmcgui.ListItem(uvid[1])
			liz.setProperty('video_id',uvid[3])
			liz.setArt({'thumb':uvid[0]})
			self.control_list_utube.addItem(liz)

	def setLatestSpursTv(self):
		self.control_list_spurstv = self.getControl(self.LATESTSPURSTV_LIST)
		tottenhamhotspur.TrendingGrid(0,1,56552,3,'',getall=False)
		for data in tottenhamhotspur.TRENDING_GRID:
			item = data.get('data').get('article')
			media = item.get('media')
			liz = xbmcgui.ListItem(item.get('title'))
			liz.setArt({'thumb':media.get('thumbnail').get('url')})
			liz.setProperties({'partnerId':media.get('partnerId'),'entryId':media.get('entryId')})
			self.control_list_spurstv.addItem(liz)


	@staticmethod
	def adapt_datetime(ts):
		return time.mktime(ts.timetuple())

	@staticmethod
	def convert_datetime(ts):
		try:
			return datetime.datetime.fromtimestamp(float(ts))
		except ValueError:
			return None



