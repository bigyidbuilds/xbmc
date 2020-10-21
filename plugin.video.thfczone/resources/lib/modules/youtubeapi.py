# -*- coding: utf-8 -*-
import xbmc
import xbmcgui

import requests
import youtube_registration
import youtube_resolver


class YouTubeApi():

	baseUrl      = 'https://www.googleapis.com/youtube/v3'
	channels     = '/channels'
	clientId     = '412082269293-mt1jdquscmoe6o8hj88cbmv3hdmq8qfg.apps.googleusercontent.com'
	clientSecret = 'z9xr5F_XyVe_nkeEXpc8sd22'
	search       = '/search'
	key          = 'AIzaSyD99CwfDqlPl2YtdXc_9zFtyw0rxd-7jpM'

	def __init__(self):
		self.session = requests.Session()
		self.session.params.update({'key':self.key})

	def Channelinfo(self,Id):
		data = None
		r = self.session.get(self.baseUrl+self.channels,params={'part':'snippet,brandingSettings','id':Id})
		if r.ok:
			content_type = r.headers.get('Content-Type')
			if 'application/json' in content_type:
				data=r.json()
		return data

	def ChannellatestUpload(self,Id,maxResults):
		data = None
		r = self.session.get(self.baseUrl+self.search,params={'part':'snippet','channelId':Id,'maxResults':maxResults,'order':'date','type':'video'})
		if r.ok:
			content_type = r.headers.get('Content-Type')
			if 'application/json' in content_type:
				data=r.json()
		return data


	def RegistarAPIkey(self):
		youtube_registration.register_api_keys(addon_id='plugin.video.thfczone',api_key=self.key,client_id=self.clientId,client_secret=self.clientSecret)


	def ResolveVideo(self,video_id):
		return youtube_resolver.resolve(video_id, addon_id='plugin.video.thfczone')


class YouTubePlayer():

	def __init__(self):
		self.Player = xbmc.Player()

	def Play(self,video_id):
		stream_info = YouTubeApi().ResolveVideo(video_id)[0]
		meta = stream_info.get('meta')
		liz = xbmcgui.ListItem(meta.get('title'))
		liz.setInfo('video',{'title':meta.get('title')})
		liz.setArt({'thumb':meta.get('images').get('default')})
		self.Player.play(stream_info.get('url',liz))
		while(not xbmc.abortRequested):
			xbmc.sleep(1000)
