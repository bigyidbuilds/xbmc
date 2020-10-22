#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urlparse
import xbmc
import xbmcplugin

from resources.lib.modules._addon import *
from resources.lib.modules import _common

_common.Log(sys.argv[2][1:])

def MainMenu():
	_common.AddDir(name='Test Main Dir',url='',mode=1,iconimage=addon_icon,fanart=addon_fanart,description='',genre='',date='',credits='')

def SubMenu(fanartImage,iconImage,title):
	_common.AddDir(name='Test Sub Dir',url='',mode=2,iconimage=iconImage,fanart=fanartImage,description=title,genre='',date='',credits='')

args   = urlparse.parse_qs(sys.argv[2][1:])
mode   = args.get('mode', None)
if mode:
	mode = int(mode[0])
url    = args.get('url',None)
if url:
	url=(url[0])
name   = args.get('name',None)
if name:
	name=(name[0])
fanart = args.get('fanart',None)
if fanart:
	fanart=(fanart[0])
icon   = args.get('icon',None)
if icon:
	icon=(icon[0])



xbmcplugin.setContent(int(sys.argv[1]), 'movies')

try:
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
except:
    pass
try:
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
except:
    pass
try:
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_DATE)
except:
    pass
try:
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_GENRE)
except:
    pass

if mode==None:
	MainMenu()
elif mode==1:
	SubMenu(fanart,icon,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))	
	
