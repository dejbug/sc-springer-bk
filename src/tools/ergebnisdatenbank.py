import sys, os, re, urllib.parse, json, pprint, datetime
import argparse

from dejlib import stringify, fetch
from dejlib import RequestCache

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

def ApiCall(endpoint, cache = None, force = False, offline = False, **kk):
	url = ApiUrl(endpoint, **kk)
	text = fetch(url, cache = cache, force = force, offline = offline)
	return json.loads(text)


def ApiGetTurniereUrl():
	'''
	>>> ApiGetTurniereUrl()
	'https://www.schach-in-starkenburg.de/webservice/api/Turniere/GetTurniere'
	'''
	return API_ROOT + E_GET_TURNIERE

def ApiGetTurniere(cache = None, force = False, offline = False):
	return ApiCall(E_GET_TURNIERE, cache, force, offline)


def ApiGetSpielklassenUrl():
	'''
	>>> ApiGetSpielklassenUrl()
	'https://www.schach-in-starkenburg.de/webservice/api/Vereine/GetSpielklassen'
	'''
	return API_ROOT + E_GET_SPIELKLASSEN

def ApiGetSpielklassen(cache = None, force = False, offline = False):
	return ApiCall(E_GET_SPIELKLASSEN, cache, force, offline)


def ApiGetSpieltageByTurnierSpielklasseUrl(turnierId, klassenId):
	'''
	>>> ApiGetSpieltageByTurnierSpielklasseUrl(T_2023, K_STARKENBURG)
	'https://www.schach-in-starkenburg.de/webservice/api/Spieltage/GetSpieltageByTurnierSpielklasse?turnierid=16&spielklassenid=5'
	'''
	return ApiUrl(E_GET_SPIELTAGE_BY_TURNIER_SPIELKLASSE,
		turnierid=turnierId, spielklassenid=klassenId)

def ApiGetSpieltageByTurnierSpielklasse(turnierId, klassenId,
		cache = None, force = False, offline = False):
	return ApiCall(E_GET_SPIELTAGE_BY_TURNIER_SPIELKLASSE, cache, force, offline,
		turnierid=turnierId, spielklassenid=klassenId)


def ApiGetMKTabellenUrl(turnierId, klassenId, runde):
	'''
	>>> ApiGetMKTabellenUrl(T_2023, K_B, 2)
	'https://www.schach-in-starkenburg.de/webservice/api/MKTabellen/GetMKTabellen?turnierid=16&spielklassenid=8&runde=2'
	'''
	return ApiUrl(E_GET_MK_TABELLEN,
		turnierid=turnierId, spielklassenid=klassenId, runde=runde)

def ApiGetMKTabellen(turnierId, klassenId, runde,
		cache = None, force = False, offline = False):
	return ApiCall(E_GET_MK_TABELLEN, cache, force, offline,
		turnierid=turnierId, spielklassenid=klassenId, runde=runde)


def ApiGetMKResultateUrl(turnierId, klassenId, runde):
	'''
	>>> ApiGetMKResultateUrl(T_2023, K_C, 2)
	'https://www.schach-in-starkenburg.de/webservice/api/MKResultate/GetMKResultate?turnierid=16&spielklassenid=9&runde=2'
	'''
	return ApiUrl(E_GET_MK_RESULTATE,
		turnierid=turnierId, spielklassenid=klassenId, runde=runde)

def ApiGetMKResultate(turnierId, klassenId, runde,
		cache = None, force = False, offline = False):
	return ApiCall(E_GET_MK_RESULTATE, cache, force, offline,
		turnierid=turnierId, spielklassenid=klassenId, runde=runde)

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


# class Group:

# 	def __init__(self, kk, cache = None):
# 		self.kk = list(kk)
# 		self.dd = {}
# 		self.cache = cache

# 	def getDays(self, turnierId = T_2023):
# 		if not self.dd:
# 			for k in self.kk:
# 				dd = ApiGetSpieltageByTurnierSpielklasse(turnierId, k, self.cache)
# 				dd = (Spieltag.fromApiResponse(d) for d in dd)
# 				self.dd[k] = sorted(dd)
# 		return self.dd

def doUsage(parser, aa):
	parser.print_usage()

def doKlassen(parser, aa):
	cache = RequestCache(root = aa.cache)
	for x in ApiGetSpielklassen(cache = cache,
			force = aa.force, offline = aa.offline):
		print('%2d' % x['id'], x['klassenname'])

def doTurniere(parser, aa):
	cache = RequestCache(root = aa.cache)
	for x in ApiGetTurniere(cache = cache,
			force = aa.force, offline = aa.offline):
		start = parseDate(x['startdatum'])
		tid = getTidFromStartYear(start.year)
		print('%3d' % tid, end = '  ')
		print(start.strftime('%x'), end = ' - ')
		print(parseDate(x['enddatum']).strftime('%x'), end = '   ')
		print(parseKurzBez(x['kurzbezeichnung']), f' ({x["turniername"]})')

def doSpieltage(parser, aa):
	cache = RequestCache(root = aa.cache)
	# group = Group([K_STARKENBURG, K_B, K_C], cache)
	# ddd = group.getDays()
	# for k, dd in ddd.items():
	# 	print('Klasse', k)
	# 	for d in dd:
	# 		date = datetime.datetime(year = d.year, month = d.month, day = d.day)
	# 		print('Runde', d.id, date.strftime('%x'))
	# 	print()
	ss = ApiGetSpieltageByTurnierSpielklasse(aa.turnier, aa.klasse, cache,
			force = aa.force, offline = aa.offline)
	ss = (Spieltag.fromApiResponse(s) for s in ss)
	ss = sorted(ss)
	print('Klasse', aa.klasse)
	for s in ss:
		date = datetime.datetime(year = s.year, month = s.month, day = s.day)
		print('Runde', s.id, date.strftime('%x'))
	print()

def doResultate(parser, aa):
	cache = RequestCache(root = aa.cache)
	for x in ApiGetMKResultate(aa.turnier, aa.klasse, aa.runde,
			cache = cache, force = aa.force, offline = aa.offline):
		print(x)

def doTabellen(parser, aa):
	cache = RequestCache(root = aa.cache)
	for x in ApiGetMKTabellen(aa.turnier, aa.klasse, aa.runde,
			cache = cache, force = aa.force, offline = aa.offline):
		print(x)

def parseArgs(args = sys.argv[1:]):
	parser = argparse.ArgumentParser()
	parser.set_defaults(cmd = doUsage)
	parser.add_argument('-o', '--offline', action = 'store_true')
	parser.add_argument('-f', '--force', action = 'store_true')
	parser.add_argument('-c', '--cache', default='../.local/cache', help = 'alternate cache path')
	s = parser.add_subparsers()

	# p = s.add_parser('klassen')
	p = s.add_parser('kk')
	p.set_defaults(cmd = doKlassen)

	# p = s.add_parser('turniere')
	p = s.add_parser('tt')
	p.set_defaults(cmd = doTurniere)

	# p = s.add_parser('spieltage')
	p = s.add_parser('ss')
	p.set_defaults(cmd = doSpieltage)
	p.add_argument('turnier', type = int)
	p.add_argument('klasse', type = int)

	# p = s.add_parser('resultate')
	p = s.add_parser('r')
	p.set_defaults(cmd = doResultate)
	p.add_argument('turnier', type = int)
	p.add_argument('klasse', type = int)
	p.add_argument('runde', type = int)

	# p = s.add_parser('tabellen')
	p = s.add_parser('t')
	p.set_defaults(cmd = doTabellen)
	p.add_argument('turnier', type = int)
	p.add_argument('klasse', type = int)
	p.add_argument('runde', type = int)

	return parser, parser.parse_args(args)

def parseDate(text):
	'''
	>>> parseDate('2023-10-01T03:39:47')
	datetime.datetime(2023, 10, 1, 3, 39, 47)
	'''
	return datetime.datetime.strptime(text, '%Y-%m-%dT%H:%M:%S')

def parseKurzBez(text, form = '%-3s %s'):
	'''
	>>> parseKurzBez('MM 2013/2014')
	'MM  2013'
	>>> parseKurzBez('HSV 2014/15')
	'HSV 2014'
	'''
	m = re.match(r'(.+?) +(\d+)/(\d+)', text)
	s, b, e = m.groups()
	if len(b) < 4: b = '20' + b
	# if len(e) < 4: e = str(int(b) + 1)
	# return f'{s:>3} {b}/{e}'
	return form % (s, b)

def getTidFromStartYear(year):
	return year - 2007

if __name__ == '__main__':
	parser, aa = parseArgs()
	# print(aa)
	if aa.cmd:
		aa.cmd(parser, aa)
