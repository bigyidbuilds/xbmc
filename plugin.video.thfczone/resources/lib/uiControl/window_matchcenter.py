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
from resources.lib.modules._common import Log,ToTimeStamp,FromTimeStamp,KeyBoard
from resources.lib.modules import tottenhamhotspur

class WindowMatchCenter(xbmcgui.WindowXML):

	xmlFilename = 'Window_matchcenter.xml'
	scriptPath  = addon_path
	defaultSkin = 'Default'
	defaultRes  = '720p'

	FILTER_SEASON_LIST = ['2020-2021','2019-2020','2018-2019','2017-2018','2016-2017']

	FILTER_GROUP  = 1000
	FILTER_SEASON = 1001
	FILTER_COMP   = 1002
	FILTER_SEARCH = 1003
	GAMES_LIST    = 2000

	def __new__(cls,*args,**kwargs):
		return super(WindowMatchCenter, cls).__new__(cls,WindowMatchCenter.xmlFilename, WindowMatchCenter.scriptPath, WindowMatchCenter.defaultSkin, WindowMatchCenter.defaultRes)

	def __init__(self,*args,**kwargs):
		super(WindowMatchCenter,self).__init__()
		self.InitDB()
		self.comps = self.GetCompsList('present_season')
		self.gameslist = self.GetSeasonGames('present_season')
		self.seasonfilter = self.FILTER_SEASON_LIST[0]
		self.compfilter = 'all'
		

	def onInit(self):
		self.filter_season_list = self.getControl(self.FILTER_SEASON)
		if self.filter_season_list.size() == 0:
			for season in self.FILTER_SEASON_LIST:
				liz = xbmcgui.ListItem(season)
				liz.setProperty('season',season)
				self.filter_season_list.addItem(liz)
		self.filter_season_list.setHeight(len(self.FILTER_SEASON_LIST)*30)
		self.filter_comp_list = self.getControl(self.FILTER_COMP)
		if self.filter_comp_list.size() ==0:
			for c in self.comps:
				liz = xbmcgui.ListItem(c)
				self.filter_comp_list.addItem(liz)
		self.filter_comp_list.setHeight(len(self.comps)*30)
		self.games_list = self.getControl(self.GAMES_LIST)
		if self.games_list.size() == 0:
			self.SetGamesList(self.gameslist)
		self.setFocus(self.games_list)

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()
		elif action.getId() in [ACTION_SELECT_ITEM,ACTION_MOUSE_LEFT_CLICK]:
			if self.getFocusId() == self.FILTER_SEASON:
				self.FilterSeason(self.filter_season_list.getListItem(int(self.filter_season_list.getSelectedPosition())))
			elif self.getFocusId() == self.FILTER_COMP:
				self.FilterComp(self.filter_comp_list.getListItem(int(self.filter_comp_list.getSelectedPosition())),self.filter_season_list.getListItem(int(self.filter_season_list.getSelectedPosition())))
			elif self.getFocusId() == self.GAMES_LIST:
				import window_matchcenteritem
				d=window_matchcenteritem.WindowMatchCenterItems(self.games_list.getListItem(int(self.games_list.getSelectedPosition())))
				d.doModal()
				del d
				

	def onClick(self,controlId):
		Log('onClick: {}'.format(controlId))
		if controlId ==  self.FILTER_SEARCH:
			self.SearchGames()

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
		super(WindowMatchCenter,self).close()
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


	def GetCompsList(self,season):
		c = self.conn.cursor()
		if season == 'present_season':
			c.execute("SELECT DISTINCT comp FROM present_season")
		else:
			c.execute("SELECT DISTINCT comp FROM season_results WHERE season=?",(season,))
		comps = [comp[0] for comp in c.fetchall()]
		comps.insert(0,'All')
		return comps

	def GetSeasonGames(self,season):
		c = self.conn.cursor()
		if season == 'present_season':
			c.execute("SELECT * FROM present_season ORDER BY matchdate DESC")
		else:
			c.execute("SELECT * FROM season_results WHERE season=? ORDER BY matchdate DESC",(season,))
		return c.fetchall()


	def GetSeasonCompGames(self,season,comp):
		c = self.conn.cursor()
		if season == 'present_season':
			c.execute("SELECT * FROM present_season WHERE comp=? ORDER BY matchdate DESC",(comp,))
		else:
			c.execute("SELECT * FROM season_results WHERE season=? AND comp=? ORDER BY matchdate DESC",(season,comp))
		return c.fetchall()


	def FilterSeason(self,listitem):
		season = listitem.getLabel()
		if season == self.FILTER_SEASON_LIST[0]:
			season = 'present_season'
		games = self.GetSeasonGames(season)
		comps = self.GetCompsList(season)
		self.games_list.reset()
		self.filter_comp_list.reset()
		self.SetGamesList(games)
		for c in comps:
			liz = xbmcgui.ListItem(c)
			self.filter_comp_list.addItem(liz)
		self.filter_comp_list.setHeight(len(comps)*30)
		self.setFocus(self.games_list)


	def FilterComp(self,complistitem,seasonlistitem):
		comp = complistitem.getLabel()
		season = seasonlistitem.getLabel()
		c = self.conn.cursor()
		if season == self.FILTER_SEASON_LIST[0]:
			season = 'present_season'
		self.games_list.reset()
		if comp == 'All':
			games = self.GetSeasonGames(season)
		else:
			games = self.GetSeasonCompGames(season,comp)
		self.SetGamesList(games)
		self.setFocus(self.games_list)


	def SetGamesList(self,games):
		for game in games:
			optaId = game[8]
			score =  game[4]
			ht_scores = ''
			at_scores = ''
			referee = ''
			stadium = ''
			if optaId:
				matchdetail = tottenhamhotspur.GetMAtchDetails(optaId)
				ht_matchdetail = matchdetail.get('Home')
				at_matchdetail = matchdetail.get('Away')
				referee = matchdetail.get('Referee')
				stadium = matchdetail.get('Stadium')
				for a in ht_matchdetail.get('Scorers'):
					ht_scores += a.get('Surname')+' '+a.get('GoalTimes')+'\n'
				for b in at_matchdetail.get('Scorers'):
					at_scores += b.get('Surname')+' '+b.get('GoalTimes')+'\n'
				if matchdetail.get('ShowAggregateScore'):
					score = '('+str(ht_matchdetail.get('AggregateScore'))+') '+score+' ('+str(at_matchdetail.get('AggregateScore'))+')'
			liz = xbmcgui.ListItem(game[0].strftime('%d %b %y'))
			matchreportUrl = game[12]
			liz.setProperties({'hometeam':game[2],'awayteam':game[3],'compname':game[1],'score':score,'optaId':optaId,'matchId':game[9],'matchreportUrl':game[12],'matchdate_str':game[11],'tag':game[13],'tag_id':game[14],'matchdatetime':str(ToTimeStamp(game[0])),'ht_scores':ht_scores,'at_scores':at_scores,'stadium':stadium,'referee':referee})
			liz.setArt({'complogo':game[10],'homebadge':game[6],'awaybadge':game[7]})
			self.games_list.addItem(liz)

	def SearchGames(self):
		query = KeyBoard('Enter Search Term')
		query = '%'+query+'%'
		c = self.conn.cursor()
		c.execute("SELECT * FROM present_season WHERE hometeam LIKE ? OR awayteam LIKE ? ORDER BY matchdate DESC",(query,query))
		a = c.fetchall()
		c.execute("SELECT * FROM season_results WHERE hometeam LIKE ? OR awayteam LIKE ? ORDER BY matchdate DESC",(query,query))
		games = a + c.fetchall()
		self.games_list.reset()
		self.SetGamesList(games)
		self.setFocus(self.games_list)









