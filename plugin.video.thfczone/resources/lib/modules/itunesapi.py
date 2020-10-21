import requests



class ItunesApi():

	base_url = 'https://itunes.apple.com'
	search_url = '/search'

	def __init__(self):
		self.session = requests.Session()

	def SearchPodcast(self,query):
		data = None 
		query = query.replace(' ','+')
		r = self.session.get(self.base_url+self.search_url,params={'term':query,'media':'podcast','entity':'podcast'})
		if r.ok:
			data=r.json()
		return data


if __name__ == '__main__':
	results = ItunesApi().SearchPodcast('tottenham').get('results')
	for result in results:
		# print(result.get('feedUrl'),result.get('collectionName'))
		print(result)
		print('********************************************************************************')