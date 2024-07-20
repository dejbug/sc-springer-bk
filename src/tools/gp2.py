import sys, os, re

from lib.File import File
from lib.Names import Name, Synonyms, DEFAULT_SYNONYMS

from lib.History import History
from lib.CsvTablePath import CsvTablePath

from lib import tool

import gp

class MtCsvPath:
	def __init__(self):
		self.path = ''
		self.root = ''
		self.type = ''
		self.year = 0
		self.month = 0
		self.extra = ''

	@classmethod
	def parse(cls, path):
		obj = cls()
		x = re.match('^(.+/)?(blitz|schnell)-(\d+)-(\d+)(?:-(.+))?\.csv$', path)
		if x:
			obj.path = path
			obj.root = x.group(1)
			obj.type = x.group(2)
			obj.year = int(x.group(3))
			obj.month = int(x.group(4))
			obj.extra = x.group(5)
			return obj

	def __repr__(self):
		# return str(self.__dict__)
		# return f'{self.type[0].upper()}-{self.year}-{self.month:02}' + (f'-{self.extra}' if self.extra else '')
		return f'{self.type[0].upper()}-{self.year}-{self.month:02}'

	@classmethod
	def iter(cls, root):
		for t, dd, nn in os.walk('tables'):
			pp = (os.path.join(t, n) for n in nn)
			pp = (MtCsvPath.parse(p) for p in pp)
			pp = (p for p in pp if p)
			pp = sorted(pp, key = lambda p: (p.year, p.month))
			return pp

def augmentPlayerScoresWithMcp(player):
	for s in player.scores:
		s.mcp = MtCsvPath.parse(s.fid.file.path)
	player.scores = sorted(player.scores, key = lambda s: (s.mcp.year, s.mcp.month))

def findPlayerByName(history, name, synonyms = None):
	for p in history.players:
		if p.name == name:
			return p
		if synonyms and synonyms.classify(p.name) == synonyms.classify(name):
			return p

def printHistorySortedByTournamentDate(history, names = [], synonyms = None, debug = False):
	# history.sort_by_ptotals()

	if names:
		# players = [player for player in history.players if player.name in names]
		players = []
		for name in names:
			p = findPlayerByName(history, name)
			if p:
				players.append(p)
	else:
		players = history.players

	for p in players:
		augmentPlayerScoresWithMcp(p)
		print(p.name)
		for s in p.scores:
			print(f'{s.pscore:4}  {s.rscore:4}  ({"#%d" % s.rank:>3} {s.mcp} )')
			if debug:
				for row in s.fid.file._rows:
					p_ = findPlayerByName(history, row[1], synonyms)
					if p_ and p_.name == p.name:
						print(row)
		print()

def get_best_tournament_results(history):
	# history.sort_by_rscores(9)
	history.sort_by_rtotals(9)

	max_name_length = 8

	for player in history.players:
		player._scores = [s.rscore for s in player.scores][:9]
		player._cum = sum(player._scores)
		max_name_length = max(max_name_length, len(player.name))

	results = []

	for i, player in enumerate(sorted(history.players, key = lambda player: player._cum, reverse = True), start = 1):
		result = {}
		result['name'] = player.name
		result['index'] = i
		result['score'] = player._cum
		result['scores'] = player._scores
		result['player'] = player
		result['max_name_length'] = max_name_length
		results.append(result)

	return results

def print_best_tournament_results(history, full = False):

	results = get_best_tournament_results(history)

	for result in results:
		print('%2d' % result['index'], end = ' ')
		print('%5.1f' % result['score'], end = '  ')
		print(f'%-{result["max_name_length"]}s' % result['name'], end = ' ')
		if full:
			player = result['player']
			print('|', end= '')
			for score in player._scores:
				print("%2d" % score if score else "     ", end="|")
			for i in range(8 - len(player._scores)):
				print("  ", end="|")
		print()

#
# file = File('tables/blitz-24-03.csv')
# for row in file.rows: print(row)
# print(file.rscores(contiguous = False))
#
# print()
#
# file = File('tables/schnell-24-04.csv')
# print('  ranks', file.ranks())
# print('rscores', file.rscores())
# for row in file.rows: print(row)
# print(file.rscores(contiguous = False))

# exit()

pp = MtCsvPath.iter('tables')
pp = (p for p in pp if p.year == 24)
pp = list(pp)
# for p in pp: print(p)

names, synonyms = gp.load_names_from_files(p.path for p in pp)
# for name in sorted(names): print(name)
# gp.print_names(names, synonyms)
# gp.print_groups(names, synonyms)

history = History(names, synonyms, contiguous = False)
printHistorySortedByTournamentDate(history, synonyms = synonyms, debug = False)
# gp.print_full_history(history)

# gp.print_best_tournament_results_html(history)
print_best_tournament_results(history, full = True)
# gp.print_cumulative_tournament_results_html(history)

# printHistorySortedByTournamentDate(history, names = ['Sauer', 'Brunner', 'Messer'])
