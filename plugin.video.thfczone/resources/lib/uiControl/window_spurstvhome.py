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
from resources.lib.modules._common import Log,ToTimeStamp,FromTimeStamp,DateTimeStrp,DateTimeNow,DateTimeDelta
from resources.lib.modules import tottenhamhotspur


class WindowSpursTvHome(xbmcgui.WindowXML):

	xmlFilename = 'Window_spurstvhome.xml'
	scriptPath  = addon_path
	defaultSkin = 'Default'
	defaultRes  = '720p'

	listitems = [
				('All',1),
				('Highlight Archive',2),
				('Managers',7),
				('Players',3),
				('Spurs Ladies',4),
				('New Stadium',5),
				('Legends',6),
				('Youth Teams',8),
				('Back',9)]

	ManagersTags  = ['JoseMourinho','MauricioPochettino']
	YouthTeamTags = ['U18','PL2','U23']

	ITEMLIST             = 2000

	def __new__(cls,*args,**kwargs):
		return super(WindowSpursTvHome, cls).__new__(cls,WindowSpursTvHome.xmlFilename, WindowSpursTvHome.scriptPath, WindowSpursTvHome.defaultSkin, WindowSpursTvHome.defaultRes)


	def __init__(self,*args,**kwargs):
		super(WindowSpursTvHome,self).__init__()
		self.InitDB()
		self.exculdeList = self.GetexcludeArticleIds()
		self.CacheVideoItems()

	def onInit(self):
		self.control_list = self.getControl(self.ITEMLIST)
		if self.control_list.size() == 0:
			for i in self.listitems:
				Liz = xbmcgui.ListItem(i[0])
				Liz.setProperty('mode',str(i[1]))
				self.control_list.addItem(Liz)
		self.setFocus(self.control_list)

	def onAction(self,action):
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == self.ITEMLIST:
				self.MainMenuControl(self.control_list.getListItem(int(self.control_list.getSelectedPosition())))

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
		super(WindowSpursTvHome,self).close()


	def MainMenuControl(self,item):
		import window_spurstv
		mode = int(item.getProperty('mode'))
		c = self.conn.cursor()
		if mode == 1:
			c.execute("SELECT * FROM spurs_tv_highlights")
			i = c.fetchall()
			c.execute("SELECT * FROM spurs_tv_all")
			i += c.fetchall()
			itemlist = sorted(i, key=lambda x: x[7],reverse = True)
			d=window_spurstv.WindowSpursTv(itemlist)
			d.doModal()
			del d
		elif mode == 2:
			c.execute("SELECT min(matchdate) FROM season_results")
			mindate = c.fetchone()
			tag = r'%FirstTeam%'
			releasedate = mindate[0]
			c.execute("SELECT * FROM spurs_tv_highlights WHERE releasedate < ? AND tags LIKE ?",(releasedate,tag))
			itemlist = c.fetchall()
			d=window_spurstv.WindowSpursTv(itemlist)
			d.doModal()
			del d 
		elif mode == 3:
			il=[]
			c.execute("SELECT player_hashtag_name FROM players_info")
			playertaglist = [i[0] for i in c.fetchall()]
			for player in playertaglist:
				tag = '%'+player+'%'
				c.execute("SELECT * FROM spurs_tv_all WHERE tags LIKE ?",(tag,))
				il += c.fetchall()
			itemlist = sorted(list(set(il)), key=lambda x: x[7],reverse = True)
			d=window_spurstv.WindowSpursTv(itemlist,taglist=playertaglist)
			d.doModal()
			del d 
		elif mode == 4:
			tag = r'%TottenhamHotspurWomen%'
			c.execute("SELECT * FROM spurs_tv_highlights WHERE tags LIKE ?",(tag,))
			i = c.fetchall()
			c.execute("SELECT * FROM spurs_tv_all WHERE tags LIKE ?",(tag,))
			i += c.fetchall()
			itemlist = sorted(i, key=lambda x: x[7],reverse = True)
			d=window_spurstv.WindowSpursTv(itemlist)
			d.doModal()
			del d 
		elif mode == 5:
			tag = r'%NewStadium%'
			c.execute("SELECT * FROM spurs_tv_highlights WHERE tags LIKE ?",(tag,))
			i = c.fetchall()
			c.execute("SELECT * FROM spurs_tv_all WHERE tags LIKE ?",(tag,))
			i += c.fetchall()
			itemlist = sorted(i, key=lambda x: x[7],reverse = True)
			d=window_spurstv.WindowSpursTv(itemlist)
			d.doModal()
		elif mode == 6:
			tag = r'%Legends%'
			c.execute("SELECT * FROM spurs_tv_highlights WHERE tags LIKE ?",(tag,))
			i = c.fetchall()
			c.execute("SELECT * FROM spurs_tv_all WHERE tags LIKE ?",(tag,))
			i += c.fetchall()
			itemlist = sorted(i, key=lambda x: x[7],reverse = True)
			d=window_spurstv.WindowSpursTv(itemlist)
			d.doModal()
		elif mode == 7:
			il = []
			for m in self.ManagersTags:
				tag = '%'+m+'%'
				c.execute("SELECT * FROM spurs_tv_all WHERE tags LIKE ?",(tag,))
				il += c.fetchall()
			itemlist = sorted(list(set(il)), key=lambda x: x[7],reverse = True)
			d=window_spurstv.WindowSpursTv(itemlist,taglist=self.ManagersTags)
			d.doModal()
		elif mode == 8:
			il = []
			for m in self.YouthTeamTags:
				tag = '%'+m+'%'
				c.execute("SELECT * FROM spurs_tv_all WHERE tags LIKE ?",(tag,))
				il += c.fetchall()
				c.execute("SELECT * FROM spurs_tv_highlights WHERE tags LIKE ?",(tag,))
				il += c.fetchall()
			itemlist = sorted(list(set(il)), key=lambda x: x[7],reverse = True)
			d=window_spurstv.WindowSpursTv(itemlist,taglist=self.YouthTeamTags)
			d.doModal()
		elif mode == 9:
			self.Close()


	def GetexcludeArticleIds(self):
		c = self.conn.cursor()
		c.execute("SELECT article_id FROM spurs_tv_highlights")
		return [i[0] for i in c.fetchall()]

	def CacheVideoItems(self):
		c = self.conn.cursor()
		c.execute("SELECT spurs_tv_all FROM cache_dt")
		cache_dt = c.fetchone()[0]
		if DateTimeNow() > cache_dt:
			tottenhamhotspur.TrendingGrid(0,1,56552,100,'')
			for item in tottenhamhotspur.TRENDING_GRID:
				thumbnail=''
				partnerId=''
				entryId=''
				data = item.get('data')
				articleId = data.get('articleId')
				if not articleId in self.exculdeList:
					article = data.get('article')
					title = article.get('title')
					media = article.get('media')
					tags = [n.get('name') for n in article.get('tags')]
					releasedate = DateTimeStrp(article.get('date'),"%Y-%m-%dT%H:%M:%SZ")
					if media:
						try :
							thumbnail = media.get('thumbnail').get('url')
						except:
							pass
						partnerId = media.get('partnerId')
						entryId = media.get('entryId')
					c.execute("INSERT OR IGNORE INTO spurs_tv_all VALUES(?,?,?,?,?,?,?,?)",(None,title,thumbnail,partnerId,entryId,str(tags),articleId,releasedate))
			c.execute("UPDATE cache_dt SET spurs_tv_all = ?",(DateTimeDelta(DateTimeNow(),h=int(setting('cache.refresh'))),))
			self.conn.commit()
		c.close()
		del tottenhamhotspur.TRENDING_GRID[:]

	def InitDB(self):
		sqlite3.register_adapter(datetime.datetime, ToTimeStamp)
		sqlite3.register_converter('timestamp', FromTimeStamp)
		sqlite3.register_adapter(bool, int)
		sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
		self.conn = sqlite3.connect(CACHEDB, detect_types=sqlite3.PARSE_DECLTYPES,check_same_thread=False)
		self.conn.execute('PRAGMA foreign_keys = ON')
		self.conn.row_factory = sqlite3.Row
		self.conn.text_factory = str
