# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
'''___info__ add other xbmc library modules xbmcgui will be needed'''
import xbmcgui


'''######------External Modules-----#####'''
import dateutil.parser as dparser
import datetime
import sqlite3
import youtube_requests


'''#####-----Internal Modules-----#####'''
from resources.lib.modules._addon import *
from resources.lib.modules._common import FromTimeStamp,KeyBoard,Log,ToTimeStamp
from resources.lib.modules import itunesapi
from resources.lib.modules import podcastrss
from _actions import *


class WindowTools(xbmcgui.WindowXML):

	xmlFilename = 'Window_tools.xml'
	scriptPath  = addon_path
	defaultSkin = 'Default'
	defaultRes  = '720p'

	MAIN_MENU         = 2000
	SUB_MENU          = 3000
	SELECT_MENU_GROUP = 4000
	SELECT_MENU       = 4001
	SELECT_MENU_DONE  = 4002
	SELECT_MENU_LABEL = 4003

	MenuItems =    {'podcastmanager':{'label':'Podcast Manager','items':[{'label':'Add Podcast via RSS feed url','func':'self.AddPodRss'},{'label':'Add Podcast via Search','func':'self.AddPodSearch'},{'label':'Disable Podcast','func':'self.DisablePod'},{'label':'Enable Podcast','func':'self.EnablePod'}]},'youtubemanager':{'label':'YouTube Manager','items':[{'label':'Add YouTube channel via search','func':'self.AddUtubeSearch'},{'label':'Disable YouTube Channel','func':'self.DisableUtube'},{'label':'Enable YouTube Channel','func':'self.EnableUtube'}]}}

	def __new__(cls,*args,**kwargs):
		return super(WindowTools, cls).__new__(cls,WindowTools.xmlFilename, WindowTools.scriptPath, WindowTools.defaultSkin, WindowTools.defaultRes)


	def __init__(self,*args,**kwargs):
		super(WindowTools,self).__init__()
		self.InitDB()


	def onInit(self):
		self.setControlVisible(self.SELECT_MENU_GROUP,False)
		self.main_control_list = self.getControl(self.MAIN_MENU)
		menus = self.MenuItems.keys()
		if self.main_control_list.size() < 1:
			for m in menus:
				liz = xbmcgui.ListItem(self.MenuItems.get(m).get('label'))
				liz.setProperty('menu_id',m)
				self.main_control_list.addItem(liz)
		self.setFocus(self.main_control_list)
		self.SetSubMenu(self.main_control_list.getListItem(int(self.main_control_list.getSelectedPosition())))

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_UP,ACTION_DOWN,ACTION_PAGE_UP,ACTION_PAGE_DOWN] and self.getFocusId() == self.MAIN_MENU: 
			self.SetSubMenu(self.main_control_list.getListItem(int(self.main_control_list.getSelectedPosition())))
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == self.SUB_MENU:
				self.SubMenuFunc(self.sub_menu_control.getListItem(int(self.sub_menu_control.getSelectedPosition())))
			elif self.getFocusId() == self.SELECT_MENU:
				self.SelectMenuFunc(self.sel_menu_control.getListItem(int(self.sel_menu_control.getSelectedPosition())))


	def onClick(self,controlId):
		if controlId == self.SELECT_MENU_DONE:
			self.getControl(self.SELECT_MENU).reset()
			self.setControlVisible(self.SELECT_MENU_GROUP,False)
			self.setFocusId(self.SUB_MENU)


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
		super(WindowTools,self).close()


	def setControlVisible(self, controlId, visible):
		if not controlId:
			return
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



	def SetSubMenu(self,listitem):
		self.sub_menu_control = self.getControl(self.SUB_MENU)
		self.sub_menu_control.reset()
		menu_id = listitem.getProperty('menu_id')
		menuitems = self.MenuItems.get(menu_id).get('items')
		for m in menuitems:
			liz = xbmcgui.ListItem(m.get('label'))
			liz.setProperties(m)
			self.sub_menu_control.addItem(liz)

	def SelectMenuFunc(self,listitem):
		eval(listitem.getProperty('func'))(listitem)


	def SubMenuFunc(self,listitem):
		eval(listitem.getProperty('func'))()

	def EnableUtube(self):
		c = self.conn.cursor()
		c.execute("SELECT * FROM youtube_list WHERE enabled=0")
		enabled = c.fetchall()
		self.sel_menu_control = self.getControl(self.SELECT_MENU)
		for en in enabled:
			liz = xbmcgui.ListItem(en[1])
			liz.setProperties({'func':'self._EnableUtube','channel_id':en[0]})
			self.sel_menu_control.addItem(liz)
		self.setControlLabel(self.SELECT_MENU_LABEL,'Click on channel to Enable')
		self.setControlVisible(self.SELECT_MENU_GROUP,True)
		self.setFocusId(self.SELECT_MENU)

	def _EnableUtube(self,listitem):
		cid = listitem.getProperty('channel_id')
		c = self.conn.cursor()
		c.execute("UPDATE youtube_list SET enabled=? WHERE youtube_id=?",(True,cid))
		channelinfo = youtube_requests.get_channels(cid, addon_id=addon_id)
		banner = channelinfo[0].get('brandingSettings').get('image').get('bannerImageUrl')
		details = channelinfo[0].get('snippet')
		c.execute("INSERT INTO youtube_channels VALUES(?,?,?,?,?)",(details.get('thumbnails').get('high').get('url'),details.get('title'),details.get('description'),cid,banner))
		self.conn.commit()
		c.close()
		self.sel_menu_control.reset()
		self.EnableUtube()


	def DisableUtube(self):
		c = self.conn.cursor()
		c.execute("SELECT * FROM youtube_list WHERE enabled=1")
		enabled = c.fetchall()
		self.sel_menu_control = self.getControl(self.SELECT_MENU)
		for en in enabled:
			liz = xbmcgui.ListItem(en[1])
			liz.setProperties({'func':'self._DisableUtube','channel_id':en[0]})
			self.sel_menu_control.addItem(liz)
		self.setControlLabel(self.SELECT_MENU_LABEL,'Click on channel to Disable')
		self.setControlVisible(self.SELECT_MENU_GROUP,True)
		self.setFocusId(self.SELECT_MENU)

	def _DisableUtube(self,listitem):
		cid = listitem.getProperty('channel_id')
		c = self.conn.cursor()
		Log(cid)
		c.execute("UPDATE youtube_list SET enabled=? WHERE youtube_id=?",(False,cid))
		c.execute("DELETE FROM youtube_channels WHERE channel_id=?",(cid,))
		self.conn.commit()
		c.close()
		self.sel_menu_control.reset()
		self.DisableUtube()



	def AddUtubeSearch(self):
		c = self.conn.cursor()
		searchquery = KeyBoard('Enter Search Query')
		queryresults = youtube_requests.get_search(searchquery, search_type='channel', order='relevance', safe_search='none', addon_id=addon_id)
		c.execute("SELECT channel_id FROM youtube_channels")
		channel_ids = [i[0] for i in c.fetchall()]
		self.sel_menu_control = self.getControl(self.SELECT_MENU)
		for res in queryresults:
			s = res.get('snippet')
			if s:
				cid = s.get('channelId')
				if cid not in channel_ids:
					liz = xbmcgui.ListItem(s.get('title'))
					liz.setProperties({'func':'self.AddUtubeChannel','channel_id':cid})
					liz.setArt({'thumb':s.get('thumbnails').get('default').get('url')})
					self.sel_menu_control.addItem(liz)
		self.setControlLabel(self.SELECT_MENU_LABEL,'Click on channel to Add')
		self.setControlVisible(self.SELECT_MENU_GROUP,True)
		self.setFocusId(self.SELECT_MENU)

	def AddUtubeChannel(self,listitem):
		cid = listitem.getProperty('channel_id')
		c = self.conn.cursor()
		c.execute("SELECT * FROM youtube_list WHERE youtube_id=?",(cid,))
		if c.fetchall():
			c.execute("UPDATE youtube_list SET enabled=? WHERE youtube_id=?",(True,cid))
		else:
			c.execute("INSERT INTO youtube_list VALUES (?,?,?,?)",(cid,listitem.getLabel(),True,True))
		channelinfo = youtube_requests.get_channels(cid, addon_id=addon_id)
		banner = channelinfo[0].get('brandingSettings').get('image').get('bannerImageUrl')
		details = channelinfo[0].get('snippet')
		c.execute("INSERT INTO youtube_channels VALUES(?,?,?,?,?)",(details.get('thumbnails').get('high').get('url'),details.get('title'),details.get('description'),cid,banner))
		self.conn.commit()
		c.close()



	def EnablePod(self):
		c = self.conn.cursor()
		c.execute("SELECT * FROM podcast_list WHERE enabled=?",(False,))
		data = c.fetchall()
		self.sel_menu_control = self.getControl(self.SELECT_MENU)
		for d in data:
			liz = xbmcgui.ListItem(d[1])
			liz.setPath(d[2])
			liz.setProperties({'func':'self._EnablePod'})
			self.sel_menu_control.addItem(liz)
		self.setControlLabel(self.SELECT_MENU_LABEL,'Click on item to Enable')
		self.setControlVisible(self.SELECT_MENU_GROUP,True)
		self.setFocusId(self.SELECT_MENU)

	def _EnablePod(self,listitem):
		c = self.conn.cursor()
		rss = listitem.getPath()
		self.AddPod(rss)
		self.sel_menu_control.reset()
		self.EnablePod()



	def DisablePod(self):
		c = self.conn.cursor()
		c.execute("SELECT * FROM podcast_list WHERE enabled=?",(True,))
		data = c.fetchall()
		self.sel_menu_control = self.getControl(self.SELECT_MENU)
		for d in data:
			liz = xbmcgui.ListItem(d[1])
			liz.setPath(d[2])
			liz.setProperties({'func':'self._DisablePod'})
			self.sel_menu_control.addItem(liz)
		self.setControlLabel(self.SELECT_MENU_LABEL,'Click on item to disable')
		self.setControlVisible(self.SELECT_MENU_GROUP,True)
		self.setFocusId(self.SELECT_MENU)

	def _DisablePod(self,listitem):
		c = self.conn.cursor()
		rss = listitem.getPath()
		c.execute("UPDATE podcast_list SET enabled=? WHERE podcast_rss=?",(False,rss))
		c.execute("DELETE FROM podcast_channels WHERE podcast_rss=?",(rss,))
		self.conn.commit()
		c.close()
		self.sel_menu_control.reset()
		self.DisablePod()



	def AddPodSearch(self):
		searchquery = KeyBoard('Enter Search Name')
		itunes = itunesapi.ItunesApi()
		data = itunes.SearchPodcast(searchquery)
		results = data.get('results')
		self.sel_menu_control = self.getControl(self.SELECT_MENU)
		c = self.conn.cursor()
		c.execute("SELECT podcast_rss FROM podcast_channels")
		channelsrss = [i[0] for i in c.fetchall()]
		for result in results:
			rss = result.get('feedUrl')
			if not rss in channelsrss:
				liz = xbmcgui.ListItem(result.get('collectionName'))
				liz.setArt({'thumb':result.get('artworkUrl600')})
				liz.setPath(rss)
				liz.setProperties({'func':'self.AddPodFromSearch'})
				self.sel_menu_control.addItem(liz)
		self.setControlLabel(self.SELECT_MENU_LABEL,'Click on item to add') 
		self.setControlVisible(self.SELECT_MENU_GROUP,True)
		self.setFocusId(self.SELECT_MENU)

	def AddPodFromSearch(self,listitem):
		self.AddPod(listitem.getPath())

	def AddPodRss(self):
		feedrss = KeyBoard('Enter URL of RSS for Podcast')
		self.AddPod(feedrss)


	def AddPod(self,feedrss):
		c = self.conn.cursor()
		podcastrss.PodcastRss().Channel(feedrss)
		podcastrss.PodcastRss().Items(feedrss)
		for a in podcastrss.PodcastRss().CHANNEL:
			podcast_id = ''.join(a.get('title').lower().split())
			title = a.get('title')
			rss =  a.get('rss_url')
			c.execute("SELECT * FROM podcast_list WHERE podcast_rss=?",(rss,))
			if c.fetchall():
				c.execute("UPDATE podcast_list SET enabled=? WHERE podcast_rss=?",(True,rss))
			else:
				c.execute("INSERT INTO podcast_list VALUES(?,?,?,?,?)",(podcast_id,title,rss,True,True))
			c.execute("INSERT INTO podcast_channels VALUES(?,?,?,?,?,?)",(podcast_id,title,a.get('description').decode('utf-8','ignore'),a.get('image'),rss,None))
		for b in podcastrss.PodcastRss().ITEM:
			c.execute("INSERT INTO podcast_episodes VALUES(?,?,?,?,?,?)",(b.get('podid'),b.get('title'),b.get('description'),ToTimeStamp(dparser.parse(b.get('date'))),b.get('image'),b.get('playlink')))
		self.conn.commit()
		c.close()
		del podcastrss.PodcastRss().CHANNEL[:]
		del podcastrss.PodcastRss().ITEM[:]


	def InitDB(self):
		sqlite3.register_adapter(datetime.datetime, ToTimeStamp)
		sqlite3.register_converter('timestamp', FromTimeStamp)
		sqlite3.register_adapter(bool, int)
		sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
		self.conn = sqlite3.connect(CACHEDB, detect_types=sqlite3.PARSE_DECLTYPES,check_same_thread=False)
		self.conn.execute('PRAGMA foreign_keys = ON')
		self.conn.row_factory = sqlite3.Row
		self.conn.text_factory = str


