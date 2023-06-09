import argparse
import csv
import io
import re
import sys
import collections

def parse_args(args=sys.argv[1:]):
	p = argparse.ArgumentParser()
	p.add_argument("--type", action="store_true", help="determine file type")
	p.add_argument("file")
	aa = p.parse_args(args)
	return p, aa

def determine_csv_type(file_or_line):
	"""
	>>> determine_csv_type("Runde,Weiss,Schwarz,Ergebnis")
	'RWSE'
	>>> determine_csv_type("Runde\\tWeiss\\t\\tSchwarz\\tErgebnis")
	't/RWSE'
	>>> determine_csv_type("#,Name,1,2,3,4,5,Punkte")
	'#NP'
	>>> determine_csv_type("#\\tName\\t1\\t2\\t3\\t4\\t5\\tPunkte")
	't/#NP'
	>>> determine_csv_type("#,Name,G,S,R,V,Punkte,Buchh,Soberg")
	'#NGSRVPBS'
	>>> determine_csv_type("#\\tName\\tG\\tS\\tR\\tV\\tPunkte\\tBuchh\\tSoberg")
	't/#NGSRVPBS'
	>>> determine_csv_type("xyz")
	"""
	if isinstance(file_or_line, str):
		header = file_or_line.strip()
	else:
		header = file_or_line.readline().strip()

	if re.match("#,Name(,\d+)+,Punkte", header):
		return "#NP"
	elif re.match("#\t+Name(\t+\d+)+\t+Punkte", header):
		return "t/#NP"
	elif re.match("Runde,Weiss,Schwarz,Ergebnis", header):
		return "RWSE"
	elif re.match("Runde\t+Weiss\t+Schwarz\t+Ergebnis", header):
		return "t/RWSE"
	elif re.match("#,Name,G,S,R,V,Punkte,Buchh,Soberg", header):
		return "#NGSRVPBS"
	elif re.match("#\t+Name\t+G\t+S\t+R\t+V\t+Punkte\t+Buchh\t+Soberg", header):
		return "t/#NGSRVPBS"

def collapse_tabs(text):
	"""
	>>> collapse_tabs("hi\\tho")
	'hi,ho'
	>>> collapse_tabs("hi\\t\\t\\tho")
	'hi,ho'
	"""
	return re.sub(r"\t+", ",", text)

class Score:
	SCORE_FLAG_ASTERISK = 1

	def __init__(self, score, flags, strict=None):
		self.score = score
		self.flags = flags
		self.strict = strict

	def __repr__(self):
		return self.__class__.__name__ + str(self.__dict__)

	@classmethod
	def parse(cls, score, strict=True):
		"""
		>>> Score.parse("1")
		Score{'score': 1, 'flags': 0, 'strict': True}
		>>> Score.parse("1:0")
		Score{'score': 1, 'flags': 0, 'strict': True}
		>>> Score.parse("0")
		Score{'score': 0, 'flags': 0, 'strict': True}
		>>> Score.parse("0:1")
		Score{'score': 0, 'flags': 0, 'strict': True}
		>>> Score.parse("0.5")
		Score{'score': 0.5, 'flags': 0, 'strict': True}
		>>> Score.parse("0.5:0.5")
		Score{'score': 0.5, 'flags': 0, 'strict': True}
		>>> Score.parse("0.5*")
		Score{'score': 0.5, 'flags': 1, 'strict': True}
		>>> Score.parse(".5*")
		Score{'score': 0.5, 'flags': 1, 'strict': True}
		>>> Score.parse("2")
		>>> Score.parse("0:0")
		Traceback (most recent call last):
		ValueError: invalid score "0:0"
		"""
		m = re.match(r"(0?\.5|0|1)(?:[-:](0?\.5|0|1))?(.*)?", score)
		if not m: return None
		w, b, f = m.groups()
		w = int(w) if len(w) == 1 else .5
		if strict and b:
			b = int(b) if len(b) == 1 else .5
			if b != 1 - w:
				raise ValueError("invalid score \"%s\"" % score)

		flags = 0
		if f:
			if "*" in f: flags |= cls.SCORE_FLAG_ASTERISK
			elif strict:
				raise ValueError("invalid flags \"%s\"" % f)
		return cls(w, flags, strict)

class People:
	def __init__(self):
		self.name2id = {}
		self.id2name = {}

	def __len__(self):
		return len(self.name2id)

	def add(self, name):
		if name in self.name2id:
			return self.name2id[name]
		id = len(self.name2id) + 1
		self.name2id[name] = id
		self.id2name[id] = name
		return id

	def name(self, id):
		return self.id2name[id]

	def id(self, name):
		return self.name2id[name]

	def print(self):
		for name, pid in self.name2id.items():
			print("%3d" % pid, name)
		print()

	def __str__(self):
		s = io.StringIO()
		for name, pid in self.name2id.items():
			s.write("%3d %s\n" % (pid, name))
		return s.getvalue()

class Game:
	def __init__(self, pid, oid, score, white, rid=0):
		self.pid = pid
		self.oid = oid
		self.score = score
		self.white = white
		self.rid = rid

	def __str__(self):
		#~ r = ["loss", "draw", "win"][int(self.score * 2)]
		r = ["-", "=", "+"][int(self.score * 2)]
		xx = ["0  ", "0.5", "1  "]
		s = "%d" % self.rid
		if self.white:
			x = xx[int(self.score * 2)]
			s += " (%s) : [%d] -  %d  = %s" % (r, self.pid, self.oid, x)
		else:
			x = xx[int((1 - self.score) * 2)]
			s += " (%s) :  %d  - [%d] = %s" % (r, self.oid, self.pid, x)
		return s

class Match:
	def __init__(self, wid, bid, score, rid=0):
		self.wid = wid
		self.bid = bid
		self.score = score
		self.rid = rid

	def white(self):
		return Game(self.wid, self.bid, self.score, True, self.rid)

	def black(self):
		return Game(self.bid, self.wid, 1 - self.score, False, self.rid)

class Player:
	def __init__(self, id):
		self.id = id
		self.name = None
		self.total = 0
		self.rank = 0
		self.place = 0
		self.games = {}

	def resolve(self, people):
		self.name = people.name(self.id)

	def add_game(self, game):
		self.games[game.oid] = game
		self.total += game.score

	def has_played(self, oid):
		for g in self.games.values():
			if g.oid == oid:
				return True
		return False

	def __str__(self):
		#~ return "Player%s" % { k: self.__dict__[k] for k in ["id", "total", "rank"] }
		s = io.StringIO()
		s.write("Player[%d] : %3.1f  | #%d (%d)" % (
			self.id, self.total, self.place, self.rank))
		if self.name:
			s.write(" \"%s\"" % self.name)
		s.write("\n")
		for g in self.games.values():
			s.write("    R%s\n" % g)
		return s.getvalue()

def list_index_of(list, element):
	for i, e in enumerate(list):
		if e == element:
			return i
	return -1

class Players:
	def __init__(self):
		self.players = {}
		self.order = []

	def __len__(self):
		return len(self.players)

	def __iter__(self):
		#~ for p in self.players.values():
			#~ yield p
		for id in self.order:
			yield self.players[id]

	def resolve(self, people):
		for p in self.players.values():
			p.resolve(people)

	def get(self, id):
		if id in self.players:
			return self.players[id]
		self.order.append(id)
		player = Player(id)
		self.players[id] = player
		return player

	def set(self, player):
		self.players[player.id] = player

	def add_match(self, match):
		w = match.white()
		b = match.black()
		self.get(w.pid).add_game(w)
		self.get(b.pid).add_game(b)

	def has_match(self, match):
		w = self.get(match.wid)
		b = self.get(match.bid)
		if not w.has_played(match.bid): return False
		if not b.has_played(match.wid): return False
		return True

	def sort_by_name(self, people=None, reverse=False):
		# (Usually) Assumes self.resolve()  was called.
		if people: self.resolve(people)
		self.order = sorted(self.order,
			key=lambda id: str(self.players[id].name),
			reverse=reverse)

	def sort_by_score(self, reverse=True):
		# (Usually) Assumes self.sort_by_name()  was called.
		self.order = sorted(self.order,
			key=lambda id: self.players[id].total,
			reverse=reverse)

	def placing(self):
		totals = [p.total for p in self]
		ranking = list(range(1, len(self) + 1))
		for i in range(1, len(ranking)):
			if totals[i - 1] == totals[i]:
				ranking[i] = ranking[i - 1]
		return ranking

	def update_placing(self):
		# (Usually) Assumes self.sort_by_score() was called.
		placing = self.placing()
		i = 0
		for i, p in enumerate(self):
			p.rank = i + 1
			p.place = placing[i]
			i += 1

	def update_ranking(self):
		#~ for i, p in enumerate(self):
			#~ p.rank = i + 1
		return self.update_placing()

	def needs_place_column(self):
		# Assumes self.update_placing() was called.
		for p in self:
			if p.rank != p.place:
				return True
		return False

	def print(self):
		for p in self:
			print(p)
		print()

	def __str__(self):
		s = io.StringIO()
		for p in self:
			s.write("%s\n" % p)
		return s.getvalue()

class Table:
	def __init__(self, filler=None):
		self.filler = filler
		self.rows = []

	def set(self, row, col, data):
		self.ensure_row_exits(row)
		self.ensure_col_exists(col)
		self.rows[row][col] = data

	def ensure_row_exits(self, row):
		colcount = self.colcount
		need = row + 1 - len(self.rows)
		if need > 0:
			for _ in range(need):
				self.rows.append([self.filler] * colcount)

	def ensure_col_exists(self, col):
		colcount = len(self.rows[0]) if self.rows else 0
		need = col + 1 - colcount
		if need > 0:
			for row in self.rows:
				row.extend([self.filler] * need)

	@property
	def rowcount(self):
		return len(self.rows)

	@property
	def colcount(self):
		return len(self.rows[0]) if self.rows else 0

	def __str__(self):
		s = io.StringIO()
		s.write("Table %d %d\n" % (self.rowcount, self.colcount))
		for i, row in enumerate(self.rows):
			s.write("%d:" % i)
			for cell in row:
				s.write(" %s" % cell)
			s.write("\n")
		return s.getvalue()

def parse(path):
	with open(path, "r", encoding="utf-8") as file:
		t = determine_csv_type(file)
		if t.startswith("t/"):
			reader = csv.reader(map(collapse_tabs, file))
			rows = [line for line in reader]
		else:
			reader = csv.reader(file)
			rows = [line for line in reader]
		#~ else:
			#~ raise Exception("unknown CSV type: %s" % t)

	people = People()
	players = Players()

	if t.endswith("RWSE"):
		for r, w, b, s in rows:
			w = people.add(w)
			b = people.add(b)
			s = Score.parse(s)
			players.add_match(Match(w, b, s.score, int(r)))
	elif t.endswith("#NP"):
		for row in rows:
			i = people.add(row[1])
		for i, row in enumerate(rows):
			for j, c in enumerate(row[2:-1]):
				if i == j: continue
				s = Score.parse(c)
				m = Match(i + 1, j + 1, s.score)
				if not players.has_match(m):
					players.add_match(m)

	return people, players

def empty_crosstable(pc):
	header = ["#"]
	for i in range(pc):
		header.append(str(i+1))
	header.append("Punkte")

	table = [header]

	for i in range(pc):
		row = []
		row.append(str(i+1))
		for j in range(pc):
			if i == j: row.append("=")
			else: row.append("-")
		row.append("0")
		table.append(row)

	return table

def crosstable(players, show_white=None):
	table = empty_crosstable(len(players))

	for p in players:
		pid = p.rank # p.id of table
		table[pid][-1] = str(p.total)
		for g in p.games.values():
			oid = players.get(g.oid).rank # g.oid of table
			table[pid][oid] = str(g.score)
			if show_white == g.white: table[pid][oid] += "*"

	if players.needs_place_column():
		table[0].append("Platz")
		for p in players:
			table[p.rank].append(str(p.place))

	table[0][1:1] = ["Name"]
	for p in players:
		table[p.rank][1:1] = [p.name]

	return table

def render(inpath):
	people, players = parse(inpath)
	players.sort_by_name(people)
	players.sort_by_score()
	players.update_placing()
	return people, players, crosstable(players)

if __name__ == "__main__":
	p, aa = parse_args()
	#~ print(aa)
	if aa.type:
		with open(aa.file, "r", encoding="utf-8") as file:
			print(determine_csv_type(file))
		exit()

	people, players = parse(aa.file)
	#~ print(people)

	players.sort_by_name(people)
	players.sort_by_score()
	players.update_placing()
	#~ players.print()

	table = crosstable(players)
	for row in table:
		print(",".join(row))
