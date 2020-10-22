#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import xbmc
import xbmcaddon

addon           = xbmcaddon.Addon()
addoninfo       = addon.getAddonInfo
setting         = addon.getSetting
setting_true    = lambda x: bool(True if setting(str(x)) == "true" else False)
setting_set     = addon.setSetting
local_str       = addon.getLocalizedString
has_addon       = lambda x: xbmc.getCondVisibility("System.HasAddon({addon})".format(addon=str(x)))



addon_version   = addoninfo('version')
addon_name      = addoninfo('name')
addon_id        = addoninfo('id')
addon_icon      = addoninfo("icon")
addon_fanart    = addoninfo("fanart")
addon_path      = xbmc.translatePath(addoninfo('path').decode('utf-8'))
addon_profile   = xbmc.translatePath(addoninfo('profile').decode('utf-8'))