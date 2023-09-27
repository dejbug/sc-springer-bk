import re, urllib.parse, json, pprint

from dejlib import stringify, fetch

API_ROOT = 'https://www.schach-in-starkenburg.de/webservice/api/'

K_HESSEN = 2
K_VERBAND = 3
K_LAND = 4
K_STARKENBURG = 5
K_BEZIRK = 6
K_A = 7
K_B = 8
K_C = 9

T_2008 = 1
T_2009 = 2
T_2010 = 3
T_2011 = 4
T_2012 = 5
T_2013 = 6
T_2014 = 7
T_2015 = 8
T_2016 = 9
T_2017 = 10
T_2018 = 11
T_2019 = 12
T_2020 = 13
T_2021 = 14
T_2022 = 15
T_2023 = 16

E_GET_TURNIERE = 'Turniere/GetTurniere'
E_GET_SPIELKLASSEN = 'Vereine/GetSpielklassen'
E_GET_SPIELTAGE_BY_TURNIER_SPIELKLASSE = 'Spieltage/GetSpieltageByTurnierSpielklasse'
E_GET_MK_TABELLEN = 'MKTabellen/GetMKTabellen'
E_GET_MK_RESULTATE = 'MKResultate/GetMKResultate'


def ApiUrl(endpoint, **kk):
	return API_ROOT + endpoint + '?' + urllib.parse.urlencode(kk)

def ApiCall(endpoint, cache = None, **kk):
	url = ApiUrl(endpoint, **kk)
	text = fetch(url, cache = cache)
	return json.loads(text)


def ApiGetTurniereUrl():
	return API_ROOT + E_GET_TURNIERE

def ApiGetTurniere(cache = None):
	return ApiCall(E_GET_TURNIERE, cache)


def ApiGetSpielklassenUrl():
	return API_ROOT + E_GET_SPIELKLASSEN

def ApiGetSpielklassen(cache = None):
	return ApiCall(E_GET_SPIELKLASSEN, cache)


def ApiGetSpieltageByTurnierSpielklasseUrl(turnierId, klassenId):
	return ApiUrl(E_GET_SPIELTAGE_BY_TURNIER_SPIELKLASSE,
		turnierid=turnierId, spielklassenid=klassenId)

def ApiGetSpieltageByTurnierSpielklasse(turnierId, klassenId, cache = None):
	return ApiCall(E_GET_SPIELTAGE_BY_TURNIER_SPIELKLASSE, cache,
		turnierid=turnierId, spielklassenid=klassenId)


def ApiGetMKTabellenUrl(turnierId, klassenId, runde):
	return ApiUrl(E_GET_MK_TABELLEN,
		turnierid=turnierId, spielklassenid=klassenId, runde=runde)

def ApiGetMKTabellen(turnierId, klassenId, runde, cache = None):
	return ApiCall(E_GET_MK_TABELLEN, cache,
		turnierid=turnierId, spielklassenid=klassenId, runde=runde)


def ApiGetMKResultateUrl(turnierId, klassenId, runde):
	return ApiUrl(E_GET_MK_RESULTATE,
		turnierid=turnierId, spielklassenid=klassenId, runde=runde)

def ApiGetMKResultate(turnierId, klassenId, runde, cache = None):
	return ApiCall(E_GET_MK_RESULTATE, cache,
		turnierid=turnierId, spielklassenid=klassenId, runde=runde)


def tests_1():
	'''
	>>> ApiGetSpieltageByTurnierSpielklasseUrl(T_2023, K_STARKENBURG)
	'https://www.schach-in-starkenburg.de/webservice/api/Spieltage/GetSpieltageByTurnierSpielklasse?turnierid=16&spielklassenid=5'
	>>> ApiGetMKTabellenUrl(T_2023, K_B, 2)
	'https://www.schach-in-starkenburg.de/webservice/api/MKTabellen/GetMKTabellen?turnierid=16&spielklassenid=8&runde=2'
	>>> ApiGetMKResultateUrl(T_2023, K_C, 2)
	'https://www.schach-in-starkenburg.de/webservice/api/MKResultate/GetMKResultate?turnierid=16&spielklassenid=9&runde=2'
	>>> ApiGetTurniereUrl()
	'https://www.schach-in-starkenburg.de/webservice/api/Turniere/GetTurniere'
	>>> ApiGetSpielklassenUrl()
	'https://www.schach-in-starkenburg.de/webservice/api/Vereine/GetSpielklassen'
	'''
	pass

def tests_2():
	from dejlib import RequestCache
	cache = RequestCache('../.local/cache')

	text = cache.fetch(ApiGetSpielklassenUrl())
	pprint.pprint(json.loads(text))
	text = cache.fetch(ApiGetTurniereUrl())
	pprint.pprint(json.loads(text))

	text = cache.fetch(ApiGetSpieltageByTurnierSpielklasseUrl(T_2023, K_STARKENBURG))
	pprint.pprint(json.loads(text))
	text = cache.fetch(ApiGetSpieltageByTurnierSpielklasseUrl(T_2023, K_B))
	pprint.pprint(json.loads(text))

	text = cache.fetch(ApiGetMKTabellenUrl(T_2023, K_STARKENBURG, 1))
	pprint.pprint(json.loads(text))

	text = cache.fetch(ApiGetMKResultateUrl(T_2023, K_C, 2))
	pprint.pprint(json.loads(text))


@stringify
class Spieltag:
	def __init__(self, id = 0, day = 0, month = 0, year = 0):
		self.id = int(id)
		self.day = int(day)
		self.month = int(month)
		self.year = int(year)

	def __int__(self):
		return self.year * 10000 + self.month * 100 + self.day

	def __lt__(self, other):
		if self.id == other.id:
			return int(self) < int(other)
		return self.id < other.id

	@classmethod
	def parse(cls, text):
		m = re.match(r'(\d+)\.(\d+)\.(\d+)', text)
		return cls(0, *m.groups())

	@classmethod
	def fromApiResponse(cls, json):
		obj = cls.parse(json['spieltag'])
		obj.id = int(json['id'])
		return obj


class Group:

	def __init__(self, kk, cache = None):
		self.kk = list(kk)
		self.dd = {}
		self.cache = cache

	def getDays(self, turnierId = T_2023):
		if not self.dd:
			for k in self.kk:
				dd = ApiGetSpieltageByTurnierSpielklasse(turnierId, k, self.cache)
				dd = (Spieltag.fromApiResponse(d) for d in dd)
				self.dd[k] = sorted(dd)
		return self.dd

if __name__ == '__main__':
	from dejlib import RequestCache
	cache = RequestCache('../.local/cache')
	group = Group([K_STARKENBURG, K_B, K_C], cache)
	dd = group.getDays()
	for d in dd.items():
		print(d)
