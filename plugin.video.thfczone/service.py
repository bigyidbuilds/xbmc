# -*- coding: utf-8 -*-
import datetime
import dateutil.parser as dparser
import re
import sqlite3
import time
import threading

from resources.lib.modules import youtubeapi
from resources.lib.modules._addon import *
from resources.lib.modules._common import Log,Notify,DateTimeStrp,FromTimeStamp,ToTimeStamp
from resources.lib.modules import tottenhamhotspur
from resources.lib.modules import podcastrss

class LockableSqliteConnection(object):
	def __init__(self):
		sqlite3.register_adapter(datetime.datetime, ToTimeStamp)
		sqlite3.register_converter("TIMESTAMP", FromTimeStamp)
		sqlite3.register_adapter(bool, int)
		sqlite3.register_converter("BOOLEAN", lambda v: bool(int(v)))
		self.lock = threading.Lock()
		self.conn = sqlite3.connect(CACHEDB, detect_types=sqlite3.PARSE_DECLTYPES,check_same_thread=False)
		self.conn.execute('PRAGMA foreign_keys = ON')
		self.conn.row_factory = sqlite3.Row
		self.conn.text_factory = str

	@staticmethod
	def adapt_datetime(ts):
		return time.mktime(ts.timetuple())

	@staticmethod
	def convert_datetime(ts):
		try:
			return datetime.datetime.fromtimestamp(float(ts))
		except ValueError:
			return None



class cacheData():

	pastseasons  = ['2019-2020','2018-2019','2017-2018','2016-2017']
	cleartables  = ['season_2019_2020','presant_season','next_fixture','league_table']
	podcastfeeds = [('https://rss.acast.com/thefightingcock','Fighting Cock PodCast'),
					('https://rss.acast.com/theextrainch','The Extra Inch'),
					# ('http://broadandhotspur.buzzsprout.com/78880.rss','Broad and Hotspur PodCast'),
					('http://feeds.soundcloud.com/users/soundcloud:users:142515494/sounds.rss','Echoes Of Glory PodCast'),
					# ('http://cospurs.com/wp/feed/podcast/','Colorado Spurs Podcast'),
					# ('https://rss.acast.com/espurs','E-Spurs PodCast'),
					# ('http://audioboom.com/channels/4902566.rss','Oh When The Spurs PodCast'),
					('http://www.spreaker.com/user/7564778/episodes/feed','Hotspur America PodCast'),
					('https://rss.acast.com/ruletheroost','Rule The Roost PodCast'),
					('http://podcast.playbackmedia.co.uk/spurs.xml','The Spurs Show PodCast'),
					('http://feeds.soundcloud.com/users/soundcloud:users:124425344/sounds.rss','Tottenham Hotspur Family PodCast'),
					('https://audioboom.com/channels/4871099.rss','The Tottenham Way PodCast'),
					('https://cartilagefree.podbean.com/feed.xml','Wheeler Dealer Radio - A Ridiculous Tottenham Hotspur PodCast'),
					('https://audioboom.com/channels/4926959.rss','Last Word on Spurs'),
					('http://feeds.soundcloud.com/users/soundcloud:users:452500566/sounds.rss','Spurs News Podcast')]
	youtubeids   = [('UCEg25rdRZXg32iwai6N6l0w','spurs offical'),
					('UCCrdSzn0ZQDeH_9RGYe01tA','spurs ladies')]

	def __init__(self):
		self.lsc = LockableSqliteConnection()
		self.threadevents = [self.CreateDBTables,self.cachePod,self.cacheLeagueTable,self.CachePastSeasons,self.cachePresentSeason,self.cacheYoutube,self.cacheSpursTvHighlights,self.cacheFirstTeamSquad]
		threads = [threading.Thread(target=threadevent) for threadevent in self.threadevents]
		for thread in threads:
			thread.start()
		for thread in threads:
			thread.join()


	def CreateDBTables(self):
		with self.lsc.lock:
			with self.lsc.conn:
				c = self.lsc.conn.cursor()
				try:
					c.execute('SELECT major, minor, patch FROM db_version')
					(major, minor, patch) = c.fetchone()
					version = [major, minor, patch]
				except sqlite3.OperationalError:
					version = [0, 0, 0]

				if version < [0,0,1]:
					c.execute("CREATE TABLE IF NOT EXISTS podcast_list (podcast_id TEXT,podcast_title TEXT,podcast_rss TEXT,enabled BOOLEAN,user_added BOOLEAN ,PRIMARY KEY(podcast_id))")
					for p in self.podcastfeeds:
						c.execute("INSERT INTO podcast_list VALUES(?,?,?,?,?)",(''.join(p[1].split()).lower(),p[1],p[0],True,False))
					c.execute("CREATE TABLE IF NOT EXISTS youtube_list (youtube_id TEXT,youtube_name TEXT,enabled BOOLEAN,user_added BOOLEAN,PRIMARY KEY(youtube_id))")
					for y in self.youtubeids:
						c.execute("INSERT INTO youtube_list VALUES(?,?,?,?)",(y[0],y[1],True,False))
					c.execute("CREATE TABLE IF NOT EXISTS podcast_channels (podcast_id TEXT,podcast_title TEXT,podcast_description TEXT,podcast_image TEXT,podcast_rss TEXT,last_publish TIMESTAMP,PRIMARY KEY(podcast_id))")
					c.execute("CREATE TABLE IF NOT EXISTS podcast_episodes(podcast_id TEXT,episode_title TEXT,episode_description TEXT,episode_pubdate TIMESTAMP,episode_image TEXT,episode_stream TEXT,FOREIGN KEY(podcast_id) REFERENCES podcast_channels(podcast_id) ON DELETE CASCADE)")
					c.execute("CREATE TABLE IF NOT EXISTS league_table (pos INTEGER,team TEXT,pld INTEGER,w INTEGER,d INTEGER,l INTEGER,f INTEGER,a INTEGER,gd INTEGER,pts INTEGER, PRIMARY KEY(pos,team))")
					c.execute("CREATE TABLE IF NOT EXISTS season_results (matchdate TIMESTAMP,comp TEXT,hometeam TEXT,awayteam TEXT,score TEXT,venue TEXT,home_team_image TEXT,away_team_image TEXT,optaid INTEGER,fixtureid INTEGER,comp_image TEXT,matchdate_str TEXT,matchreport_url TEXT,tag TEXT,tag_id INTEGER,season TEXT,PRIMARY KEY(fixtureid))")
					c.execute("CREATE TABLE IF NOT EXISTS present_season (matchdate TIMESTAMP,comp TEXT,hometeam TEXT,awayteam TEXT,score TEXT,venue TEXT,home_team_image TEXT,away_team_image TEXT,optaid INTEGER,fixtureid INTEGER,comp_image TEXT,matchdate_str TEXT,matchreport_url TEXT,tag TEXT,tag_id INTEGER,isNextFixture BOOLEAN,PRIMARY KEY(fixtureid))")
					c.execute("CREATE TABLE IF NOT EXISTS youtube_channels (thumbnail TEXT,title TEXT,description TEXT,channel_id TEXT,banner TEXT,PRIMARY KEY(channel_id))")
					c.execute("CREATE TABLE IF NOT EXISTS youtube_latest (thumbnail TEXT,title TEXT,description TEXT,video_id TEXT,channel_id TEXT,publishtime TIMESTAMP ,PRIMARY KEY(video_id),FOREIGN KEY(channel_id) REFERENCES youtube_channels(channel_id) ON DELETE CASCADE)")
					c.execute("CREATE TABLE IF NOT EXISTS spurs_tv_highlights(matchdate TEXT,title TEXT,image_url TEXT,partnerId INTEGER,entryId TEXT NOT NULL,tags BLOB,article_id INTEGER,releasedate TIMESTAMP,PRIMARY KEY(entryId))")
					c.execute("CREATE TABLE IF NOT EXISTS spurs_tv_all(matchdate TEXT,title TEXT,image_url TEXT,partnerId INTEGER,entryId TEXT NOT NULL,tags BLOB,article_id INTEGER,releasedate TIMESTAMP,PRIMARY KEY(entryId))")
					c.execute("CREATE TABLE IF NOT EXISTS players_info(shirt_no INTEGER ,name TEXT,image TEXT,url TEXT,player_id_opta INTEGER,player_hashtag_id INTEGER,player_hashtag_name TEXT,PRIMARY KEY(shirt_no))")
					c.execute("CREATE TABLE IF NOT EXISTS db_version(major INTEGER, minor INTEGER, patch INTEGER)")
					c.execute('INSERT INTO db_version(major, minor, patch) VALUES(0, 0, 1)')
					c.execute("CREATE TABLE IF NOT EXISTS cache_dt(podcast_list TIMESTAMP,youtube_list TIMESTAMP,podcast_channels TIMESTAMP,podcast_episodes TIMESTAMP,league_table TIMESTAMP,season_results TIMESTAMP,present_season TIMESTAMP,youtube_channels TIMESTAMP,youtube_latest TIMESTAMP,spurs_tv_highlights TIMESTAMP,spurs_tv_all TIMESTAMP,players_info TIMESTAMP)")
					c.execute("INSERT INTO cache_dt VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(0,0,0,0,0,0,0,0,0,0,0,0))
				self.lsc.conn.commit()
				c.close()


	def cacheFirstTeamSquad(self):
		with self.lsc.lock:
			with self.lsc.conn:
				c = self.lsc.conn.cursor()
				c.execute("DELETE FROM players_info")
				players = tottenhamhotspur.Getplayers()
				for player in players:
					shirt_no = player.get('number')
					if shirt_no:
						c.execute("INSERT OR IGNORE INTO players_info VALUES(?,?,?,?,?,?,?)",(shirt_no,player.get('name'),player.get('img_url'),player.get('url'),player.get('optaId'),player.get('tagId'),player.get('tagName')))
				self.lsc.conn.commit()
				c.close()


	def cacheSpursTvHighlights(self):
		with self.lsc.lock:
			with self.lsc.conn:
				c = self.lsc.conn.cursor()
				tottenhamhotspur.TrendingGrid(0,1,45833,100,'')
				for hl in tottenhamhotspur.TRENDING_GRID:
					date = False
					thumbnail=''
					partnerId=''
					entryId=None
					tags=[]
					data = hl.get('data')
					article = data.get('article')
					articleId = data.get('articleId')
					title = article.get('title')
					media = article.get('media')
					tags = [n.get('name') for n in article.get('tags')]
					releasedate = DateTimeStrp(article.get('date'),"%Y-%m-%dT%H:%M:%SZ")
					if media:
						thumbnail = media.get('thumbnail').get('url')
						partnerId = media.get('partnerId')
						entryId = media.get('entryId')
						date = re.search(r'(\d\d\.\d\d.\d\d)',media.get('caption',''))
						if date:
							date = date.group(0)
					if not date and title.startswith('The Archive'):
						date = re.search(r'(\d\d\.\d\d.\d\d)',title)
						if date:
							date = date.group(0)
					if not date:
						url = article.get('url')
						urlsplit = url.split('/')
						year = urlsplit[2]
						month = urlsplit[3]
						try:
							month = time.strptime(month,'%B')
							month = time.strftime('%m',month)
						except:
							pass
						try:
							year = time.strptime(year,'%Y')
							year = time.strftime('%y',year)
						except:
							pass
						date =  'xx.'+month+'.'+year
					c.execute("INSERT OR IGNORE INTO spurs_tv_highlights VALUES(?,?,?,?,?,?,?,?)",(date,title,thumbnail,partnerId,entryId,str(tags),articleId,ToTimeStamp(releasedate)))
				self.lsc.conn.commit()
				c.close()
				del tottenhamhotspur.TRENDING_GRID[:]		





	def cacheYoutube(self):
		self.utdata = []
		self.utlate = []
		self.utapi = youtubeapi.YouTubeApi()
		with self.lsc.lock:
			with self.lsc.conn:
				c = self.lsc.conn.cursor()
				c.execute("DELETE FROM youtube_channels")
				c.execute("SELECT youtube_id FROM youtube_list WHERE enabled = 1")
				youtubeids = c.fetchall() 
				threads = [threading.Thread(target=self._cacheyoutube, args=(channel_id[0],)) for channel_id in youtubeids]
				threads.extend([threading.Thread(target=self._cacheyoutubelate, args=(channel_id[0],)) for channel_id in youtubeids])
				for thread in threads:
					thread.start()
				for thread in threads:
					thread.join()
				for data in self.utdata:
					details = data.get('items')[0].get('snippet')
					Id = data.get('items')[0].get('id')
					banner = data.get('items')[0].get('brandingSettings').get('image').get('bannerImageUrl')
					c.execute("INSERT INTO youtube_channels VALUES(?,?,?,?,?)",(details.get('thumbnails').get('high').get('url'),details.get('title'),details.get('description'),Id,banner))
				for d in self.utlate:
					items=d.get('items')
					for item in items:
						snippet = item.get('snippet')
						c.execute("INSERT INTO youtube_latest VALUES(?,?,?,?,?,?)",(snippet.get('thumbnails').get('default').get('url'),snippet.get('title'),snippet.get('description'),item.get('id').get('videoId'),snippet.get('channelId'),ToTimeStamp(dparser.parse(snippet.get('publishTime')))))
				self.lsc.conn.commit()
				c.close()



	def _cacheyoutube(self,Id):
		self.utdata.append((self.utapi.Channelinfo(Id)))

	def _cacheyoutubelate(self,Id):
		self.utlate.append(self.utapi.ChannellatestUpload(Id,3))


	def cachePod(self):
		with self.lsc.lock:
			with self.lsc.conn:
				c = self.lsc.conn.cursor()
				c.execute("SELECT podcast_rss FROM podcast_list WHERE enabled = 1")
				podfeed = c.fetchall()
				c.execute("DELETE FROM podcast_channels")
				threads = [threading.Thread(target=self._cachepod, args=(url[0],)) for url in podfeed]
				for thread in threads:
					thread.start()
				for thread in threads:
					thread.join()
				podcast_id = None
				for a in podcastrss.PodcastRss().CHANNEL:
					podcast_id = ''.join(a.get('title').lower().split())
					c.execute("INSERT INTO podcast_channels VALUES(?,?,?,?,?,?)",(podcast_id,a.get('title'),a.get('description').decode('utf-8','ignore'),a.get('image'),a.get('rss_url'),None))
				for b in podcastrss.PodcastRss().ITEM:
					c.execute("INSERT INTO podcast_episodes VALUES(?,?,?,?,?,?)",(b.get('podid'),b.get('title'),b.get('description'),ToTimeStamp(dparser.parse(b.get('date'))),b.get('image'),b.get('playlink')))
				self.lsc.conn.commit()
				c.close()
		
		del podcastrss.PodcastRss().CHANNEL[:]
		del podcastrss.PodcastRss().ITEM[:]



	def _cachepod(self,url):
		podcastrss.PodcastRss().Channel(url)
		podcastrss.PodcastRss().Items(url)
		

	def CachePastSeasons(self):
		missingseason=[]
		with self.lsc.lock:
			with self.lsc.conn:
				c = self.lsc.conn.cursor()
				for season in self.pastseasons:
					c.execute("SELECT season FROM season_results WHERE season=?",(season,))
					data = c.fetchone()
					if not data:
						missingseason.append(season)
					else:
						pass
				threads = [threading.Thread(target=tottenhamhotspur.GetFixturesForSeason, args=(url,)) for url in missingseason]
				for thread in threads:
					thread.start()
				for thread in threads:
					thread.join()
				for res in tottenhamhotspur.RESULTS:
					c.execute("INSERT INTO season_results VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(ToTimeStamp(res.get('fulldate')),res.get('comp'),res.get('home_team'),res.get('away_team'),res.get('result'),res.get('venue'),res.get('home_team_image_dark'),res.get('away_team_image_dark'),res.get('optaId'),res.get('fixtureId'),res.get('comp_image'),res.get('fulldate').strftime('%d.%m.%y'),res.get('buttonlink'),res.get('tag'),res.get('tag_id'),res.get('season')))
				self.lsc.conn.commit()
				c.close()
				del tottenhamhotspur.RESULTS[:]

	def cachePresentSeason(self):
		with self.lsc.lock:
			with self.lsc.conn:
				c = self.lsc.conn.cursor()
				c.execute("DELETE FROM present_season")
				tottenhamhotspur.GetFixturesForSeason('')
				for res in tottenhamhotspur.FIXTURE_RESULTS:
					c.execute("INSERT INTO present_season VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(ToTimeStamp(res.get('fulldate')),res.get('comp'),res.get('home_team'),res.get('away_team'),res.get('result'),res.get('venue'),res.get('home_team_image_dark'),res.get('away_team_image_dark'),res.get('optaId'),res.get('fixtureId'),res.get('comp_image'),res.get('fulldate').strftime('%d.%m.%y'),res.get('buttonlink'),res.get('tag'),res.get('tag_id'),res.get('isNextFixture')))
				self.lsc.conn.commit()
				c.close()

	def cacheNextFixture(self):
		with self.lsc.lock:
			with self.lsc.conn:
				c = self.lsc.conn.cursor()
				c.execute("DELETE FROM next_fixture")
				fulldate,comp,comp_image,home_team,home_team_image,away_team,away_team_image,venue,venue_image = tottenhamhotspur.NextGame()
				c.execute("INSERT INTO next_fixture VALUES (?,?,?,?,?,?,?,?,?)",(ToTimeStamp(fulldate),comp,comp_image,home_team,home_team_image,away_team,away_team_image,venue,venue_image))



	def cacheLeagueTable(self):
		tottenhamhotspur.league_table('premierleague')
		with self.lsc.lock:
			with self.lsc.conn:
				c = self.lsc.conn.cursor()
				c.execute("DELETE FROM league_table")
				for s in tottenhamhotspur.LEAGUE_TABLE:
					c.execute("INSERT INTO league_table VALUES(?,?,?,?,?,?,?,?,?,?)",(s.get('Pos'),s.get('Team'),s.get('Pld'),s.get('W'),s.get('D'),s.get('L'),s.get('F'),s.get('A'),s.get('GD'),s.get('Pts')))
				self.lsc.conn.commit()
				c.close()



if __name__ == '__main__':
	cacheData()
	Notify(message='Cache Updated')		