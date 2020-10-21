# -*- coding: UTF-8 -*-
'''
	Copyright (C) 2018 THFC Zone,BigYidBuilds

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''
from bs4 import BeautifulSoup
import datetime
import dateutil.parser as dparser
import json
import livestreamer
import re
import requests
import urllib2
import urlparse
from dateutil import tz

from resources.lib.modules._common import *

http                 = 'http'
https                = 'https'
site                 = 'www.tottenhamhotspur.com'
GetFixturesForSeason = '/umbraco/Surface/FixtureGrid/GetFixturesForSeason'
scrapename           = 'tottenhamhotspur'
matchesurl           = '/matches/'
first_teamurl        = '/teams/first-team/players/'
matchdayapp          = 'tot-matchdayapp-prd.azureedge.net'
mediasite            = 'open.http.mp.streamamg.com'

baseurl = urlparse.urlunparse((https,site,'',None,None,None))
#season results api
season_2020_2021 = urlparse.urlunparse((https,site,GetFixturesForSeason,None,'seasonId=336987',None))
season_2019_2020 = urlparse.urlunparse((https,site,GetFixturesForSeason,None,'seasonId=193556',None))
season_2018_2019 = urlparse.urlunparse((https,site,GetFixturesForSeason,None,'seasonId=49596',None))
season_2017_2018 = urlparse.urlunparse((https,site,GetFixturesForSeason,None,'seasonId=1326',None))
season_2016_2017 = urlparse.urlunparse((https,site,GetFixturesForSeason,None,'seasonId=44043',None))
season_2015_2016 = urlparse.urlunparse((https,site,GetFixturesForSeason,None,'seasonId=44427 ',None))
season_2014_2015 = urlparse.urlunparse((https,site,GetFixturesForSeason,None,'seasonId=44700',None))
season_2013_2014 = urlparse.urlunparse((https,site,GetFixturesForSeason,None,'seasonId=44808',None))
#League Tables
prem_league = 'https://matchday.tottenhamhotspur.com/FootballAroundTheGrounds/LeagueTableByCompetition/c8'

#matchday app
matchdayapp_baseurl = urlparse.urlunparse((https,matchdayapp,'',None,None,None))
lineup = '/Mdc/Lineup/{optaID}'
matchdetails = '/FootballMatchDetails/Index/{optaId}'

stats= 'https://tot-matchdayapp-prd.azureedge.net/FootballStats/Index/f1060030'
commarty = 'https://tot-matchdayapp-prd.azureedge.net/Commentary/CommentaryAndHighlights/f1060030'

matchtabs = urlparse.urlunparse((https,site,'umbraco/Surface/MatchTabs/GetTabsModule',None,None,None))#params ='fixtureId=193575'

#stream service spurstv
media_url = urlparse.urlunparse((http,mediasite,'p/{partnerId}/playManifest/entryId/{entryId}/format/applehttp',None,None,None))

VENUE = ['Wembley','White Hart Lane']
wdl = ['W','D','L']
RESULTS = []
FIXTURE_RESULTS = []
LEAGUE_TABLE = []
TRENDING_GRID = []

headers  = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:19.0) Gecko/20100101 Firefox/19.0'}

comp_tags = {'Premier League':'PremierLeague','International Champions Cup':'InternationalChampionsCup','Audi Cup':'AudiCup','UEFA Champions League':'ChampionsLeague','Carabao Cup':'CarabaoCup','FA Cup':'FACup'}

def league_table(league):
	if league == 'premierleague':
		league = prem_league
	html = requests.get(league,headers=headers)
	data = html.json()
	LeagueTable =  data.get("LeagueTable").get("Tables")
	Table = LeagueTable[0].get("Table")
	for teams in Table:
		LEAGUE_TABLE.append({'Pos':teams.get('Position'),'Team':teams.get('TeamName'),'Pld':teams.get('Played'),'W':teams.get('Won'),'D':teams.get('Drawn'),'L':teams.get('Lost'),'F':teams.get('GoalsFor'),'A':teams.get('GoalsAgainst'),'GD':teams.get('GoalDifference'),'Pts':teams.get('Points')})


def GetFixturesForSeason(season):
	try:
		season = season.replace('-','_')
		apiurl = eval('season_{}'.format(season))
	except NameError:
		apiurl = season_2020_2021
	html = requests.get(apiurl,headers=headers)
	data = html.json()
	for dat in data:
		items = dat.get("items")
		for item in items:
			fixtures = item.get("fixture")
			opta_id  = fixtures.get("optaId")
			fixture_id = fixtures.get('id')
			isNextFixture = item.get("isNextFixture")
			try:
				fulldate = dparser.parse(fixtures.get("kickOffOverrideText"),ignoretz=True)
			except dparser._parser.ParserError:
				fulldate = dparser.parse(fixtures.get("kickOff"),ignoretz=True)
			comp = fixtures.get("competition").get("name")
			home_team = fixtures.get("homeTeam").get("name").replace('Spurs','Tottenham Hotspur')
			away_team = fixtures.get("awayTeam").get("name").replace('Spurs','Tottenham Hotspur')
			home_score = fixtures.get("homeScore")
			away_score = fixtures.get("awayScore")
			if home_score == None or away_score == None:
				result = 'v'
			else:
				result = '{}-{}'.format(home_score,away_score)
			venue = fixtures.get("stadium").get("name")
			home_team_image_dark = fixtures.get('homeTeam').get("darkCrest").get("url").split('?',1)[0]
			home_team_image_light = fixtures.get('homeTeam').get("lightCrest").get("url").split('?',1)[0]
			away_team_image_dark = fixtures.get('awayTeam').get("darkCrest").get("url").split('?',1)[0]
			away_team_image_light = fixtures.get('awayTeam').get("lightCrest").get("url").split('?',1)[0]
			try:
				comp_image = fixtures.get("competition").get("darkCrest").get("url").split('?',1)[0]
			except AttributeError:
				comp_image = ''
			buttonlink = fixtures.get("buttonLink").get('url')
			if not buttonlink.startswith(baseurl):
				buttonlink = baseurl+buttonlink
			tag = fixtures.get('tag').get('name')
			tagId = fixtures.get('tag').get('id')
			if season == '':
				FIXTURE_RESULTS.append({'fulldate':fulldate,'comp':comp,'home_team':home_team,'away_team':away_team,'result':result,'venue':venue,'home_team_image_dark':home_team_image_dark,'home_team_image_light':home_team_image_light,'away_team_image_dark':away_team_image_dark,'away_team_image_light':away_team_image_light,'optaId':opta_id,'fixtureId':fixture_id,'comp_image':comp_image,'buttonlink':buttonlink,'tag':tag,'tag_id':tagId,'isNextFixture':isNextFixture})
			else:
				if DateTimeNow().date() >= fulldate.date():				
					RESULTS.append({'season':season.replace('_','-'),'fulldate':fulldate.date(),'comp':comp,'home_team':home_team,'away_team':away_team,'result':result,'venue':venue,'season_name':season,'home_team_image_dark':home_team_image_dark,'home_team_image_light':home_team_image_light,'away_team_image_dark':away_team_image_dark,'away_team_image_light':away_team_image_light,'optaId':opta_id,'fixtureId':fixture_id,'comp_image':comp_image,'buttonlink':buttonlink,'tag':tag,'tag_id':tagId})
 
def NextGame():
	fulldate='';comp='';comp_image='';home_team='';home_team_image='';away_team='';away_team_image='';venue='';venue_image=''
	from_zone = tz.gettz('UTC')
	to_zone = tz.tzlocal()
	url = season_2019_2020
	html = requests.get(url,headers=headers)
	data = html.json()
	for dat in data:
		items = dat.get("items")
		for item in items:
			if item.get("isNextFixture"):
				fixtures = item.get("fixture")
				try:
					fulldate = dparser.parse(fixtures.get("kickOffOverrideText"),ignoretz=True)
				except dparser._parser.ParserError:
					fulldate = dparser.parse(fixtures.get("kickOff"),ignoretz=True)
				fulldate = fulldate.replace(tzinfo=from_zone)
				fulldate = fulldate.astimezone(to_zone)
				fulldate = fulldate.replace(tzinfo=None)
				comp = fixtures.get("competition").get("name")
				comp_image = fixtures.get("competition").get("darkCrest").get("url").split('?',1)[0]
				home_team = fixtures.get("homeTeam").get("name").replace('Spurs','Tottenham Hotspur')
				home_team_image = fixtures.get('homeTeam').get("darkCrest").get("url").split('?',1)[0]
				away_team = fixtures.get("awayTeam").get("name").replace('Spurs','Tottenham Hotspur')
				away_team_image = fixtures.get('awayTeam').get("darkCrest").get("url").split('?',1)[0]
				venue = fixtures.get("stadium").get("name")
				venue_image = fixtures.get("stadium").get("image").get("url").split('?',1)[0]
				break
	return fulldate,comp,comp_image,home_team,home_team_image,away_team,away_team_image,venue,venue_image



def TrendingGrid(fromPage,toPage,tagIds,itemsPerGrid,excludeArticleIds,getall=True):
	r=requests.get(baseurl+'/TrendingGrid/LoadMore',headers=headers, params={'fromPage':fromPage,'toPage':toPage,'tagIds':tagIds,'itemsPerGrid':itemsPerGrid,'excludeArticleIds':excludeArticleIds})
	data = json.loads(re.search(r'ReactDOM\.hydrate\(React\.createElement\(Components\.TrendingGridModule,(.+?)\), document.getElementById',r.content,re.DOTALL).group(1)).get('data')
	modules=data.get('modules')
	TRENDING_GRID.extend(modules)
	loadmore = data.get('loadMoreLink')
	if loadmore and getall:
		url = loadmore.get('url')
		if url:
			_params=urlparse.parse_qs( urlparse.urlparse(url).query )
			TrendingGrid(_params.get('fromPage')[0],_params.get('toPage')[0],_params.get('tagIds')[0],_params.get('itemsPerGrid')[0],_params.get('excludeArticleIds',[''])[0])

	

def Getplayers(team=first_teamurl):
	PLAYERS=[]
	s = requests.Session()
	s.headers.update(headers)
	r = s.get(baseurl+team)
	soup = BeautifulSoup(r.content, 'html.parser')
	players = [x.get('href') for x in soup.find_all('a',"PlayersPlayer")]
	for player in players:
		r = s.get(baseurl+player)
		data = json.loads(re.search(r'ReactDOM\.hydrate\(React\.createElement\(Components\.PlayerHeroModule,(.+?)\), document.getElementById',r.content,re.DOTALL).group(1)).get('data').get('player')
		PLAYERS.append({'url':player,'optaId':data.get('optaId'),'tagId':data.get('tags')[0].get('id'),'tagName':data.get('tags')[0].get('name'),'img_url':data.get('playerImage').get('url'),'number':data.get('playerNumber'),'name':data.get('fullName')})
	return PLAYERS


def GetMatchLIneUp(optaId):
	r=requests.get(matchdayapp_baseurl+lineup.format(optaID=optaId),headers=headers)
	if r.ok:
		application = r.headers.get('Content-Type')
		if 'application/json' in application:
			return r.json()
		else:
			return None
	else:
		return None

def GetMatchReportImages(url):
	r=requests.get(url,headers=headers)
	data = json.loads(re.search(r'ReactDOM\.hydrate\(React\.createElement\(Components\.GalleryModule,(.+?)\), document.getElementById',r.content,re.DOTALL).group(1))
	slides = data.get('data').get('slides')
	if slides:
		return slides
	else:
		return None


def GetMediaStream(partner_id,entry_id):
	livestreamer_url = 'hlsvariant://' + media_url.format(partnerId=partner_id,entryId=entry_id)
	streams = livestreamer.streams(livestreamer_url)
	mediaUrl = streams['best'].url
	Log(mediaUrl)
	return mediaUrl


def GetMAtchDetails(optaId):
	r=requests.get(matchdayapp_baseurl+matchdetails.format(optaId=optaId),headers=headers)
	if r.ok:
		application = r.headers.get('Content-Type')
		if 'application/json' in application:
			return r.json()
		else:
			return None
	else:
		return None


def PlayerHeroModule(playerUrl):
	r=requests.get(playerUrl,headers=headers)
	if r.ok:
		data = json.loads(re.search(r'ReactDOM\.hydrate\(React\.createElement\(Components\.PlayerHeroModule,(.+?)\), document.getElementById',r.content,re.DOTALL).group(1)).get('data').get('player')
		if data:
			return data
		else:
			return None
	else: return None

tags = [
		{
		"name": "FirstTeam",
		"hashtag": "#FirstTeam",
		"description": "",
		"url": "/tags/firstteam/",
		"id": 4850
		},
		{
		"name": "PremierLeague",
		"hashtag": "#PremierLeague",
		"description": "Latest news on the Premier League",
		"url": "/tags/premierleague/",
		"id": 43172
		},
		{
		"name": "MatchHighlights",
		"hashtag": "#MatchHighlights",
		"description": "",
		"url": "/tags/matchhighlights/",
		"id": 45833
		},
		{
		"name": "CrystalPalace",
		"hashtag": "#CrystalPalace",
		"description": "",
		"url": "/tags/crystalpalace/",
		"id": 44032
		},
		{
		"name": "SpursTV",
		"hashtag": "#SpursTV",
		"description": "",
		"url": "/tags/spurstv/",
		"id": 56552
		}
		]