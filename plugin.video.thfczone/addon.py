#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urlparse
import xbmc



args = urlparse.parse_qs(sys.argv[2][1:])
mode = args.get('mode', None)



if mode==None:
	if float(xbmc.getInfoLabel("System.BuildVersion")[:4]) >= 18:
		xbmc.executebuiltin('Dialog.Close(busydialog)')
	from resources.lib.uiControl import window_home
	d=window_home.WindowHome()
	d.doModal()
	del d
