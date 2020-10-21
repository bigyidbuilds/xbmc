import base64
import cgi
import fnmatch
import gzip
import math
import os
import re
import shutil
import sqlite3
import sys
import time
import requests
import urllib
import zipfile
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import xml.etree.ElementTree as ET
from datetime import date,datetime,timedelta
from dateutil import parser as dparser
from resources.lib.modules._addon import *


GetDigit = lambda x: int(filter(str.isdigit, x) or 0)

def AddonInfo(addonID,info):
	ADDON = xbmcaddon.Addon(addonID)
	INFO = ADDON.getAddonInfo(info)
	return INFO

def InstallAddon(addonID):
	if not HasAddon(addonID):
		xbmc.executebuiltin('InstallAddon({})'.format(addonID))
	else:
		Log('Addon already installed {}'.format(addonID))

def AddonSetSetting(addonID,setting,value):
	ADDON = xbmcaddon.Addon(addonID)
	ADDON.setSetting(setting, value)
	Sleep(1)
	if ADDON.getSetting(setting) == value:
		Log('{} setting {} modified to {}'.format(addonID,setting,value))
	else:
		Log('{} Unable to modify setting {} to {}'.format(addonID,setting,value))

def AddonSetting(addonID,setting):
	#Use for getting settings of other addons
	setting_str = xbmcaddon.Addon(addonID).getSetting(setting)
	if setting_str == 'true':
		return True
	elif setting_str == 'false':
		return False
	else:
		return setting_str
		
def CreateDir(folder_path):
	if not xbmcvfs.exists(folder_path):
			created = xbmcvfs.mkdir(folder_path)
			if created:
				Log('Directory Created {}'.format(folder_path))
			else:
				Log('Unable to create {}'.format(folder_path))
	else:
		Log('Directory {} already exists'.format(folder_path))

def CreateFile(file_path):
	if not xbmcvfs.exists(file_path):
		file=open(file_path,'a')
		file.close()
		XbmcSleep(5)
		if xbmcvfs.exists(file_path):
			Log('{} created '.format(file_path))
		else:
			Log('{} not created '.format(file_path))
	else:
		Log('{} already excist'.format(file_path))

def CopyFile(src,dst):
	if os.path.exists(src):
		try:
			shutil.copy2(src, dst)
			Sleep(3)
			if PathExists(dst):
				Log('File {} copied to {}'.format(src,dst))
		except:
			xbmcvfs.copy(src, dst)
			Sleep(3)
			if PathExists(dst):
				Log('File {} copied to {}'.format(src,dst))
	else:
		Log('{} does not excist'.format(src))

def bsixfour(s):
	try:
		bs = base64.b64decode(s)
		return bs
	except TypeError:
		Log('s = {} TypeError = {}'.format(s,TypeError))
		return s
	except:
		Log('s = {} Unknown Error'.format(s))
		return s

def ConvertTimeDelta(td):
	#convert timedelta seconds to days h m s 
	days = td.days
	hours, remainder = divmod(td.seconds, 3600)
	minutes, seconds = divmod(remainder, 60)
	return days,hours,minutes,seconds

def CreateModule(url='',mode='',name='',description='',icon=''):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+urllib.quote_plus(description)+"&iconimage="+urllib.quote_plus(icon)
	return u

def DateTimeDelta(date,h=0,d=0):
	newDT = date+timedelta(hours=h,days=d)
	return newDT

def DateTimeObject(date_str,df=False):
	DTO = dparser.parse(date_str,dayfirst=df)
	return DTO

def DateTimeNow():
	DTN = datetime.now()
	return DTN

def DateTimeStrf(dateString,fmt):
	DTS = dateString.strftime(fmt)
	return DTS

def DateTimeStrp(dateString,fmt):
	try:
		DTS = datetime.strptime(dateString, fmt)
	except TypeError:
		DTS = datetime.fromtimestamp(time.mktime(time.strptime(dateString,fmt)))
	return DTS

def DateTimeToday():
	DTT = datetime.today()
	return DTT

def dbCreateTableHeaders(file,table,headers):
	cursor = dbConnect(file)
	cursor.execute('CREATE TABLE IF NOT EXISTS {}({})'.format(table,headers))
	conn = cursor.connection 
	conn.close()

def dbConnect(file):
	conn = sqlite3.connect(file)
	cursor = conn.cursor()
	return cursor

def dbCountRows(file,table):
	cursor =  dbConnect(file)
	result = cursor.execute("SELECT count(*) FROM {}".format(table)) 
	num_of_rows = result.fetchone()[0]
	return num_of_rows

def dbDeleteTableContent(file,table):
	#Delete contents of database file table
	cursor = dbConnect(file)
	sql = "DELETE FROM {}".format(table)
	cursor.execute(sql)
	conn = cursor.connection
	conn.commit()
	conn.close()

def dbDeleteFrom(file,table,col,match):
	cursor = dbConnect(file)
	sql = 'DELETE FROM {} WHERE {}=?'.format(table,col)
	cursor.execute(sql, (match,))
	conn = cursor.connection
	conn.commit()
	conn.close()

def dbDropTable(filename,tablename):
	if PathExists(filename):
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()
		sql = "DROP TABLE IF EXISTS {};".format(tablename)
		cursor.execute(sql)
		conn.commit()
		conn.close()


def dbIsInTable(file,table,row_header,check_item):
	'''Returns True or False if item is in a row'''
	cursor = dbConnect(file)
	cursor.execute("select "+str(row_header)+" from "+str(table)+" where "+str(row_header)+"=?", (check_item,))
	data = cursor.fetchall()
	if not data:
		check = False
	if data:
		check = True 
	conn = cursor.connection 
	conn.close()  
	return check

def dbReadAll(file,table):
	DB_list = list()
	cursor = dbConnect(file)
	for row in cursor.execute('SELECT * FROM '+str(table)):
		DB_list.append(row)
	conn = cursor.connection 
	conn.close()
	return DB_list

def dbReadCol(file,table,column):
	cc = list()
	cursor = dbConnect(file)
	for row in cursor.execute('SELECT {} FROM {}'.format(column,table)):	
		cc.append(row)
	conn = cursor.connection 
	conn.close()
	return cc


def dbReadColMatch(file,table,column_header,return_column,check_item):
	#returns a column match single item,return column is the item for return and column header is the one to be matched  return column and  row_header can be same column or different depending on return required
	cursor = dbConnect(file)
	if dbTableExists(file,table):
		cursor.execute("SELECT {} FROM {} WHERE {}=?".format(return_column,table,column_header), (check_item,))
		match = cursor.fetchone()
		conn = cursor.connection 
		conn.close()
		if match:
			return match[0]
		else:
			return None
	else:
		return None

def dbReadRows(filename,table):
	#Read Rows of db table and return as a list
	DB_list = list()
	if PathExists(filename) and dbTableExists(filename,table):
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()
		for row in cursor.execute('SELECT * FROM {}'.format(table)):
			DB_list.append(row)
	return DB_list

def dbReadMatch(file,table,row_header,check_item):
	#returns a row were row_header value matchs check_item
	cursor = dbConnect(file)
	cursor.execute("SELECT * FROM "+str(table)+" WHERE "+str(row_header)+"=?", (check_item,))
	match = cursor.fetchone()
	conn = cursor.connection 
	conn.close()
	return match

def dbReadMultiCol(file,table,column_headers):
	# column headers is a string of column names  column_headers = 'a_column,b_column'
	cursor = dbConnect(file)
	cursor.execute("SELECT {} FROM {}".format(column_headers,table))
	results = cursor.fetchall()
	conn = cursor.connection 
	conn.close()
	return results

def dbTableExists(filename,tablename):
	check = False
	if PathExists(filename):
		conn = sqlite3.connect(filename)
		cursor = conn.cursor()
		sql = "SELECT name FROM sqlite_master WHERE type='table'"
		cursor.execute(sql)
		tables = cursor.fetchall()
		for table in tables:
			if table[0] == tablename:
				check = True
		conn = cursor.connection 
		conn.close()
	return check

def dbTableNames(file):
	cursor = dbConnect(file)
	sql = "SELECT name FROM sqlite_master WHERE type='table'"
	cursor.execute(sql)
	tables = cursor.fetchall()
	return tables


def dbWrite(file,table,items):
	headers = list()
	for i in range(len(items)):
		headers.append('?')
	headers = ','.join(headers)
	cursor = dbConnect(file)
	cursor.execute("INSERT INTO {} VALUES ({})".format(table,headers),items)
	conn = cursor.connection
	conn.commit()
	conn.close()

def dbUpdate(file,tablename,change_column,new_value):
	cursor = dbConnect(file)
	sql =  'UPDATE {} SET {} = ?'.format(tablename,change_column)
	cursor.execute(sql,(new_value,))
	conn = cursor.connection
	conn.commit()
	conn.close()

def DelAllContents(path,ignore_errors=True):
	if PathExists(path):
		shutil.rmtree(path,ignore_errors=ignore_errors)
		Sleep(3)
		if not PathExists(path):
			Log('{} deleted '.format(path))

def DownloadFile(url,dst):
	from requests.adapters import HTTPAdapter
	from requests.packages.urllib3.util.retry import Retry
	session = requests.Session()
	retry = Retry(connect=3, backoff_factor=0.5)
	adapter = HTTPAdapter(max_retries=retry)
	session.mount('http://', adapter)
	session.mount('https://', adapter)
	file = session.get(url, stream=True,proxies=urllib.getproxies())
	dump = file.raw
	with open(dst, 'wb') as location:
		shutil.copyfileobj(dump, location)
	if os.path.exists(dst):
		Log('File {} downloaded From {}'.format(dst,url))
		return True
	else:
		Log('File {} not downloaded From {}'.format(dst,url))
		return False

def EnscapeStr(s,Quotes=True):
	# escape string to html quotes true will inc " false will not 
	es = cgi.escape(s, quote=Quotes)
	return es


def ExtractZip(file,dst):
	if file.endswith('.zip'):
		z = zipfile.ZipFile(file)
		z.extractall(dst)
	elif file.endswith('.gz'):
		with gzip.open(file, 'r') as f_in, open(dst, 'wb') as f_out:
			shutil.copyfileobj(f_in, f_out)

def FileMod_dt(file):
	#modified datetime of file returns as 0 if file does not excist 
	if PathExists(file):
		modTime = datetime.fromtimestamp(os.path.getmtime(file))
	else:
		modTime = datetime.fromtimestamp(0)
	return modTime

def FromTimeStamp(dt_stamp,fmt=''):
	stamp = datetime.fromtimestamp(float(dt_stamp))
	if fmt == '':
		return stamp
	else:
		strstamp = stamp.strftime(fmt)
		return strstamp

def FnMatch(string,regex):
	match = fnmatch.fnmatch(string,regex)
	return match

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]
	return param


def HasAddon(addonID):
	if xbmc.getCondVisibility('System.HasAddon({})'.format(addonID)):
		return True
	else:
		return False

def KeyBoard(msg,default='',hidden=False):
	text = ''
	kb = xbmc.Keyboard()
	kb.setDefault(default)
	kb.setHeading(msg)
	kb.setHiddenInput(hidden)
	kb.doModal()
	if (kb.isConfirmed()):
		text = kb.getText()
	return text

def Log(msg):
	if setting_true('debug'):
		from inspect import getframeinfo, stack
		fileinfo = getframeinfo(stack()[1][0])
		xbmc.log('*__{}__{}*{} Python file name = {} Line Number = {}'.format(addon_name,addon_version,msg,fileinfo.filename,fileinfo.lineno), level=xbmc.LOGNOTICE)
	else:pass

def Notify(title='',message='',times='',icon=''):
	if title == '':
		title = addon_name
	if times == '':
		times = '10000'
	if icon == '':
		icon = addon_icon
	Notification = 'XBMC.Notification({},{},{},{})'.format(title,message,times,icon)
	xbmc.executebuiltin(str(Notification))


def OpenSettings(addonID=''):
	if addonID:
		xbmcaddon.Addon(addonID).openSettings()
	else:
		addon.openSettings()

def PathExists(path):
	if os.path.exists(path):
		return True
	else:
		return False

def refresh_container():
	xbmc.executebuiltin("XBMC.Container.Refresh")

def ReplaceMulti(string,replace_items):
	#replace_items is a dict with keys {'to replace':'replacement'}
	String = re.compile('|'.join(replace_items.keys()))
	string = String.sub(lambda m:replace_items[m.group(0)],string)
	return string

def RemoveFormatting(label):
	label = re.sub(r"\[/?[BI]\]",'',label)
	label = re.sub(r"\[/?COLOR.*?\]",'',label)
	return label

def RunModule(url='',mode='',name='',description=''):
	u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&description="+urllib.quote_plus(description)
	xbmc.executebuiltin('XBMC.RunPlugin({})'.format(u))

def SettingDefault(settingID):
	tree = ET.parse(SETTINGS_XML)
	settings = tree.getroot()
	for setting in settings.iter('setting'):
		if setting.attrib.get('id')==settingID:
			if SystemBuild() >= 18:
				s=setting.findtext('default')
				break
			else:
				s=(setting.attrib.get('default',''))
				break
		else:
			s=None
	return s 

def Sleep(sec):
	time.sleep(sec)

def XbmcSleep(sec):
	xbmc.sleep(sec)

def SystemBuild():
	sb = float(xbmc.getInfoLabel("System.BuildVersion")[:4])
	return sb

def TimedeltaTotalSeconds(timedelta):
	return (
		timedelta.microseconds + 0.0 +
		(timedelta.seconds + timedelta.days * 24 * 3600) * 10 ** 6) / 10 ** 6

def ToTimeStamp(dt):
	#varible must be datetime object
	ts = time.mktime(dt.timetuple())
	return ts

def TranslatePath(addonID,info):
	addon = xbmcaddon.Addon(addonID)
	addoninfo = addon.getAddonInfo
	tran_path = xbmc.translatePath(addoninfo(info).decode('utf-8'))
	return tran_path

def update_container():
	xbmc.executebuiltin("XBMC.Container.Update")

def UrlStatusCode(url):
	r = requests.get(url)
	return r.status_code

class Point(object):
	def __init__(self):
		self.x = self.y = 0
	def __repr__(self):
		Log('Point(x=%d, y=%d)' % (self.x, self.y))
		return 'Point(x=%d, y=%d)' % (self.x, self.y)

class XbmcPlayer(xbmc.Player):

	def __init__( self, *args, **kwargs ):
		xbmc.Player.__init__(self)
		self.is_active = True
		self.is_stopped = False
		self.urlplayed = False
		self.pdialogue=None
   
		
	def onPlayBackStarted( self ):
		Log("#Playback Started#")
		self.urlplayed = True
		self.is_stopped = False
			
	def onPlayBackEnded( self ):
		Log('PlayBack Ended')
		self.is_active = False
		self.is_stopped = True
		
	def onPlayBackStopped( self ):
		Log('Playback Stopped')
		self.is_active = False
		self.is_stopped = True
	  
