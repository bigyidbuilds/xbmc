# -*- coding: utf-8 -*-
'''#####-----XBMC Library Modules-----#####'''
import xbmcgui

'''######------External Modules-----#####'''
import datetime
import sqlite3

'''#####-----Internal Modules-----#####'''
from _actions import *
from resources.lib.modules._addon import *
from resources.lib.modules._common import Log,ToTimeStamp,FromTimeStamp
from resources.lib.modules import tottenhamhotspur

class WindowMatchCenterLineup(xbmcgui.WindowXML):

	xmlFilename = 'Window_matchcenterlineup.xml'
	scriptPath  = addon_path
	defaultSkin = 'Default'
	defaultRes  = '720p'

	HOME_PITCH_IMAGE = 4000
	AWAY_PITCH_IMAGE = 4001
	HOME_BADGE       = 4002
	AWAY_BADGE       = 4003

	formations={'343' :[[1],[4,5,6],    [2,7,8,3],  [10,9,11]],
				'3412':[[1],[4,5,6],    [2,7,8,3],  [11],[9,10]],
				'3421':[[1],[4,5,6],    [2,7,8,3],  [11,10],[9]],
				'4231':[[1],[2,5,6,3],  [4,8],      [7,10,11],[9]],
				'433' :[[1],[2,5,6,3],  [7,4,8],    [10,9,11]],
				'4411':[[1],[2,5,6,3],  [7,8,4,11], [10],     [9]],
				'442' :[[1],[2,5,6,3],  [7,8,4,11], [9,10]],
				'532' :[[1],[2,4,5,6,3],[7,8,11],   [9,10]]}

	def __new__(cls,listitem,*args,**kwargs):
		return super(WindowMatchCenterLineup, cls).__new__(cls,WindowMatchCenterLineup.xmlFilename, WindowMatchCenterLineup.scriptPath, WindowMatchCenterLineup.defaultSkin, WindowMatchCenterLineup.defaultRes)


	def __init__(self,listitem,*args,**kwargs):
		super(WindowMatchCenterLineup,self).__init__()
		self.InitDB()
		self.listitem = listitem
		self.isHome = True if self.listitem.getProperty('hometeam')=='Tottenham Hotspur' else False
		self.isAway = True if self.listitem.getProperty('awayteam')=='Tottenham Hotspur' else False
		self.optaid = self.listitem.getProperty('optaId')
		if self.optaid:
			self.lineup = tottenhamhotspur.GetMatchLIneUp(self.optaid)
		else:
			self.lineup = None


	def onInit(self):
		self.setControlImage(self.HOME_BADGE,self.listitem.getArt('homebadge'))
		self.setControlImage(self.AWAY_BADGE,self.listitem.getArt('awaybadge'))
		self.LineUpView(self.HOME_PITCH_IMAGE,'HomeTeamDetails',self.isHome)
		self.LineUpView(self.AWAY_PITCH_IMAGE,'AwayTeamDetails',self.isAway)

	def onAction(self,action):
		Log('onAction: {}'.format(action.getId()))
		if action.getId() in [ACTION_NAV_BACK,ACTION_PREVIOUS_MENU]:
			self.Close()

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
		super(WindowMatchCenterLineup,self).close()

	def setControlImage(self, controlId,label):
		if not controlId:
			Log('controlId {} not recognized'.format(controlId))
			return
		control = self.getControl(controlId)
		if control:
			control.setImage(label)

	def setControlVisible(self, controlId, visible):
		if not controlId:
			Log('controlId {} not recognized'.format(controlId))
			return
		control = self.getControl(controlId)
		if control:
			control.setVisible(visible)

	def InitDB(self):
		sqlite3.register_adapter(datetime.datetime, ToTimeStamp)
		sqlite3.register_converter('timestamp', FromTimeStamp)
		sqlite3.register_adapter(bool, int)
		sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
		self.conn = sqlite3.connect(CACHEDB, detect_types=sqlite3.PARSE_DECLTYPES,check_same_thread=False)
		self.conn.execute('PRAGMA foreign_keys = ON')
		self.conn.row_factory = sqlite3.Row
		self.conn.text_factory = str


	def LineUpView(self,controlId,lineupKey,isSpurs):
		player_label_bg = os.path.join(addon_path,'resources','skins','Default','media','rc-button-focus.png')
		c = self.conn.cursor()
		pitch = self.getControl(controlId)
		pitch_h = pitch.getHeight()
		pitch_w = pitch.getWidth()
		pitch_x = pitch.getX()
		pitch_y = pitch.getY()
		img_w   = 100
		img_h   = 100
		teamlineup = self.lineup.get(lineupKey)
		formation = teamlineup.get('Formation')
		Log(formation)
		startlineup = teamlineup.get('StartingLineUp')
		subs = teamlineup.get('Substitutes')
		layout = self.formations.get(formation)
		space_h = (pitch_h-(len(layout)*img_h))/len(layout)
		for index,row in enumerate(layout):
			y_pos = (img_h*index)+(space_h*index)
			space_w = (pitch_w - (len(row)*img_w))/len(row)
			start_pos_x = space_w/2
			for i,item in enumerate(row):
				x_pos = start_pos_x+(img_w*i)+(space_w*i)+pitch_x
				player = list(filter(lambda d: d.get('FormationPlace') == item, startlineup))
				if isSpurs:
					c.execute("SELECT image FROM players_info WHERE shirt_no =?",(int(player[0].get('Number')),))
					self.addControl(xbmcgui.ControlImage(x_pos, y_pos,img_w,img_h,c.fetchone()[0],2))
				self.addControl(xbmcgui.ControlImage(x_pos,y_pos+img_h,img_w,20,player_label_bg))
				self.addControl(xbmcgui.ControlLabel(x_pos, y_pos+img_h,img_w,20,player[0].get('Name').split(' ',1)[-1], font='font10', textColor='0xFF000033', alignment=0x00000002|0x00000004))
		for s,sub in enumerate(subs):
			if isSpurs:
				c.execute("SELECT image FROM players_info WHERE shirt_no =?",(int(sub.get('Number')),))
				sub_img_w = 50
				sub_img_h = 50
				if self.isHome:
					startsubpos_x = pitch_x+pitch_w+5
					y_pos = (s*sub_img_h)+pitch_y
					self.addControl(xbmcgui.ControlImage(startsubpos_x, y_pos,sub_img_w,sub_img_h,c.fetchone()[0],2))
					self.addControl(xbmcgui.ControlImage(startsubpos_x+sub_img_w,y_pos+sub_img_h/2,100,20,player_label_bg))
					self.addControl(xbmcgui.ControlLabel(startsubpos_x+sub_img_w, y_pos+sub_img_h/2,100,20,sub.get('Name').split(' ',1)[-1], font='font10', textColor='0xFF000033', alignment=0x00000002|0x00000004))
				elif self.isAway:
					startsubpos_x = pitch_x-155
					y_pos = (pitch_y+pitch_h)-((s+1)*sub_img_h)
					self.addControl(xbmcgui.ControlImage(startsubpos_x, y_pos,sub_img_w,sub_img_h,c.fetchone()[0],2))
					self.addControl(xbmcgui.ControlImage(startsubpos_x+sub_img_w,y_pos+sub_img_h/2,100,20,player_label_bg))
					self.addControl(xbmcgui.ControlLabel(startsubpos_x+sub_img_w, y_pos+sub_img_h/2,100,20,sub.get('Name').split(' ',1)[-1], font='font10', textColor='0xFF000033', alignment=0x00000002|0x00000004))

			else:
				if not self.isAway:
					startsubpos_x = pitch_x-105
					y_pos = (pitch_y+pitch_h)-((s+1)*20)
					self.addControl(xbmcgui.ControlImage(startsubpos_x,y_pos,100,20,player_label_bg))
					self.addControl(xbmcgui.ControlLabel(startsubpos_x, y_pos,100,20,sub.get('Name').split(' ',1)[-1], font='font10', textColor='0xFF000033', alignment=0x00000002|0x00000004))
				elif not self.isHome:
					startsubpos_x = pitch_x+pitch_w+5
					y_pos = (s*20)+pitch_y
					self.addControl(xbmcgui.ControlImage(startsubpos_x,y_pos,100,20,player_label_bg))
					self.addControl(xbmcgui.ControlLabel(startsubpos_x, y_pos,100,20,sub.get('Name').split(' ',1)[-1], font='font10', textColor='0xFF000033', alignment=0x00000002|0x00000004))




					











