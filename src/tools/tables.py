import argparse
import csv
import io
import re
import sys
import collections

# TODO: Use the new lib; in particular lib.File .

def parse_args(args=sys.argv[1:]):
	p = argparse.ArgumentParser()
	p.add_argument("-t", "--type", action="store_true", help="determine file type")
	p.add_argument("file")
	aa = p.parse_args(args)
	return p, aa

def determine_csv_type(file_or_line):
	"""
	>>> determine_csv_type("Runde,Weiss,Schwarz,Ergebnis")
	'RWSE'
	>>> determine_csv_type("Runde,	Weiss,	Schwarz,	Ergebnis")
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
		if file_or_line.endswith(".csv"):
			file_or_line = open(file_or_line, "r", encoding="utf-8")
			header = file_or_line.readline().strip()
		else:
			header = file_or_line.strip()
	else:
		header = file_or_line.readline().strip()

	if re.match("\s*#,\s*Name(,\s*\d+)+,\s*Punkte", header):
		return "#NP"
	elif re.match("#\t+Name(\t+\d+)+\t+Punkte", header):
		return "t/#NP"
	elif re.match("\s*Runde,\s*Weiss,\s*Schwarz,\s*Ergebnis", header):
		return "RWSE"
	elif re.match("Runde\t+Weiss\t+Schwarz\t+Ergebnis", header):
		return "t/RWSE"
	elif re.match("\s*#,\s*Name,\s*G,\s*S,\s*R,\s*V,\s*Punkte,\s*Buchh,\s*Soberg", header):
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
	def __init__(self, score, mark=None):
		self.score = score
		self.other = None
		self.mark = mark

	def __repr__(self):
		return self.__class__.__name__ + str(self.__dict__)

	@staticmethod
	def reduce(x):
		ireduce = lambda i: i if i - int(i) else int(i)
		if isinstance(x, str):
			return ireduce(float(x))
		elif isinstance(x, float):
			return ireduce(x)
		elif isinstance(x, int):
			return x
		raise TypeError

	@classmethod
	def parse(cls, score, strict=True):
		"""
		>>> Score.parse("1")
		Score{'score': 1, 'other': None, 'mark': None}
		>>> Score.parse("1:0")
		Score{'score': 1, 'other': None, 'mark': None}
		>>> Score.parse("0")
		Score{'score': 0, 'other': None, 'mark': None}
		>>> Score.parse("0:1")
		Score{'score': 0, 'other': None, 'mark': None}
		>>> Score.parse("0.5")
		Score{'score': 0.5, 'other': None, 'mark': None}
		>>> Score.parse("0.5:0.5")
		Score{'score': 0.5, 'other': None, 'mark': None}
		>>> Score.parse("0.5*")
		Score{'score': 0.5, 'other': None, 'mark': True}
		>>> Score.parse(".5*")
		Score{'score': 0.5, 'other': None, 'mark': True}
		>>> Score.parse("1w")
		Score{'score': 1, 'other': None, 'mark': False}
		>>> Score.parse("1b")
		Score{'score': 1, 'other': None, 'mark': True}
		>>> Score.parse("1s")
		Score{'score': 1, 'other': None, 'mark': True}
		>>> Score.parse("0/0")
		Score{'score': 0, 'other': Score{'score': 0, 'other': None, 'mark': None}, 'mark': None}
		>>> Score.parse("0/1")
		Score{'score': 0, 'other': Score{'score': 1, 'other': None, 'mark': None}, 'mark': None}
		>>> Score.parse("1*/0")
		Score{'score': 1, 'other': Score{'score': 0, 'other': None, 'mark': None}, 'mark': True}
		>>> Score.parse("1/1*")
		Score{'score': 1, 'other': Score{'score': 1, 'other': None, 'mark': True}, 'mark': None}
		>>> Score.parse("2")
		>>> Score.parse("0:0")
		Traceback (most recent call last):
		ValueError: invalid score "0:0": mismatch
		"""
		m = re.match(r"\s*(0?\.5|0|1)([*wbsWBS]?)(?:([-:/])(0?\.5|0|1)([*wbsWBS]?)(.*))?", score)
		if not m: return None
		#~ print(m.groups())

		a, aflags, sep, b, bflags, rest = m.groups()

		s = cls(cls.reduce(a))
		if aflags:
			if aflags in "*bsBS":
				s.mark = True
			elif aflags in "wW":
				s.mark = False
			elif strict:
				raise ValueError("invalid aflags \"%s\"" % aflags)

		if b:
			b = cls(cls.reduce(b))
			if sep == "/":
				s.other = b
				if bflags:
					if bflags in "*bsBS":
						b.mark = True
					elif bflgs in "wW":
						b.mark = False
					elif strict:
						raise ValueError("invalid bflags \"%s\"" % bflags)
			elif sep == ":":
				if strict and b.score != 1 - s.score:
					raise ValueError("invalid score \"%s\": mismatch" % score)

		return s

class People:
	def __init__(self):
		self.name2id = {}
		self.id2name = {}

	def __len__(self):
		return len(self.name2id)

	def add(self, name):
		name = name.strip()
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
	def __init__(self, pid, oid, score, white=None, rid=0):
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
		if game.oid not in self.games:
			self.games[game.oid] = [game]
		else:
			self.games[game.oid].append(game)
		self.total += game.score

	def has_played(self, oid):
		count = 0
		for gg in self.games.values():
			for g in gg:
				if g.oid == oid:
					count += 1
		return count

	def __str__(self):
		#~ return "Player%s" % { k: self.__dict__[k] for k in ["id", "total", "rank"] }
		s = io.StringIO()
		s.write("Player[%d] : %3.1f  | #%d (%d)" % (
			self.id, self.total, self.place, self.rank))
		if self.name:
			s.write(" \"%s\"" % self.name)
		s.write("\n")
		for gg in self.games.values():
			s.write("    R%s\n" % gg)
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

def iter_table_indices(rowcount, colcount, rowoffset=0, coloffset=0):
	for row in range(rowcount - rowoffset):
		for col in range(colcount - coloffset):
			if col <= row: continue
			yield row + 1, col + 1, row + rowoffset, col + coloffset

def parse(path):
	with open(path, "r", encoding="utf-8") as file:
		t = determine_csv_type(file)
		if not t:
			raise Exception("unknown CSV type")
		elif t.startswith("t/"):
			reader = csv.reader(collapse_tabs(line.strip()) for line in file)
			rows = [line for line in reader]
		else:
			reader = csv.reader(line.strip() for line in file)
			rows = [line for line in reader]

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
			people.add(row[1])
		for rid, cid, i, j in iter_table_indices(len(rows), len(rows[0])-1, 0, 2):
			c = rows[i][j].strip()
			#~ print(rid, cid, "%d:%d" % (i, j), c)
			s = Score.parse(c)
			m = Match(rid, cid, s.score)
			players.add_match(m)
			if s.other:
				m = Match(rid, cid, s.other.score)
				players.add_match(m)
	elif t.endswith("#NGSRVPBS"):
		raise Exception("no crosstable possible")

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

def crosstable(players, show_black=None):
	table = empty_crosstable(len(players))

	for p in players:
		pid = p.rank # p.id of table
		table[pid][-1] = str(Score.reduce(p.total))
		for gg in p.games.values():
			for g in gg:
				oid = players.get(g.oid).rank # g.oid of table
				if not table[pid][oid] or table[pid][oid] == "-":
					table[pid][oid] = str(g.score)
				else:
					table[pid][oid] += "/" + str(g.score)
				if show_black and not g.white: table[pid][oid] += "*"

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
	#~ Namespace = collections.namedtuple("Namespace", "file type")
	#~ aa = Namespace("tables/blitz-22-08.csv", None)
	#~ aa = Namespace("tables/blitz-23-01.csv", None)
	#~ aa = Namespace("tables/schnell-23-04.csv", None)
	#~ aa = Namespace("tables/schnell-23-02.csv", True)
	#~ aa = Namespace("tables/schnell-23-06-games.csv", None)
	#~ aa = Namespace("tables/gp-22-08-12-cumulative.csv", True)

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
