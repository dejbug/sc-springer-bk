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

def translate_score(score):
	"""
	>>> translate_score("1")
	1
	>>> translate_score("1:0")
	1
	>>> translate_score("0")
	0
	>>> translate_score("0:1")
	0
	>>> translate_score("2")
	>>> translate_score("0:0")
	Traceback (most recent call last):
	ValueError: invalid score "0:0"
	>>> translate_score("0.5")
	0.5
	>>> translate_score("0.5:0.5")
	0.5
	"""
	m = re.match(r"(0\.5|0|1)(?:[-:](0\.5|0|1))?", score)
	if not m: return None
	w, b = m.groups()
	w = int(w) if len(w) == 1 else .5
	if b:
		b = int(b) if len(b) == 1 else .5
		if b != 1 - w:
			raise ValueError("invalid score \"%s\"" % score)
	return w

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

#~ def add_player(players, name):
	#~ if not players:
		#~ players["n2i"] = {}
		#~ players["i2n"] = {}
	#~ if name in players["n2i"]: return players["n2i"][name]
	#~ pid = len(players["n2i"]) + 1
	#~ players["n2i"][name] = pid
	#~ players["i2n"][pid] = name
	#~ return pid

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

#~ def add_match(matches, w, b, s, r):
	#~ if w not in matches:
		#~ matches[w] = {"score": s, b : {"score": s, "white": True, "round": r}}
	#~ else:
		#~ matches[w][b] = {"score": s, "white": True, "round": r}
		#~ matches[w]["score"] += s

	#~ if b not in matches:
		#~ matches[b] = {"score": 1 - s, w : {"score": 1 - s, "white": False, "round": r}}
	#~ else:
		#~ matches[b][w] = {"score": 1 - s, "white": False, "round": r}
		#~ matches[b]["score"] += 1 - s

#~ def sorted_ranking(matches, people=None):
	#~ xx = ({"pid": wid, "score": info["score"]} for wid, info in matches.items())
	#~ if people: xx = sorted(xx, key=lambda x: people.name(x["pid"]), reverse=False)
	#~ xx = sorted(xx, key=lambda x: x["score"], reverse=True)

	#~ s = -1
	#~ i = 0
	#~ for x in xx:
		#~ if s != x["score"]:
			#~ s = x["score"]
			#~ i += 1
		#~ x["rank"] = i

	#~ return xx

def parse(path):
	with open(path, "r", encoding="utf-8") as file:
		t = determine_csv_type(file)
		if t == "t/RWSE":
			reader = csv.reader(map(collapse_tabs, file))
			rows = [line for line in reader]
		else:
			raise Exception("unknown CSV type")

	people = People()
	players = Players()

	for r, w, b, s in rows:
		#~ print(r, w, b, s)
		w = people.add(w)
		b = people.add(b)
		s = translate_score(s)
		players.add_match(Match(w, b, s, int(r)))

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

#~ def crosstable(people, matches=None):
	#~ table = empty_crosstable(len(people))

	#~ if not matches:
		#~ return table

	#~ ranking = sorted_ranking(matches, people)
	#~ for rinfo in ranking:
		#~ print(rinfo)
	#~ print()

	#~ r2i = [0] + [x["pid"] for x in ranking]
	#~ i2r = [0] + [None] * len(ranking)
	#~ for rank, x in enumerate(ranking, start=1):
		#~ i2r[x["pid"]] = rank
	#~ print("r2i", r2i)
	#~ print("i2r", i2r)
	#~ print()

	#~ for x in ranking:
		#~ pid = x["pid"]
		#~ prank = i2r[x["pid"]]
		#~ print(pid, prank, end=" : ")
		#~ info = matches[pid]
		#~ for oid in range(1, len(ranking)+1):
			#~ if oid in info:
				#~ orank = i2r[oid]
				#~ print(oid, "(%d)" % orank, end=" ")
				#~ table[pid][oid] = info[oid]["score"]
		#~ table[prank][-1] = info["score"]
		#~ print()
	#~ print()

	#~ unique_scores = sorted(set(x["score"] for x in ranking), reverse=True)
	#~ print(unique_scores)
	#~ needs_rank_column = len(unique_scores) < len(ranking)
	#~ print(needs_rank_column)
	#~ print()

	#~ if needs_rank_column:
		#~ table[0].append("Platz")
		#~ for i, row in enumerate(table[1:], start=1):
			#~ row.append(list_index_of(unique_scores, table[i][-1]) + 1)

	#~ return table

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

	table[0][1:2] = ["Name"]
	for p in players:
		table[p.rank][1:2] = [p.name]

	return table

if __name__ == "__main__":
	p, aa = parse_args()
	#~ print(aa)
	if aa.type:
		with open(aa.file, "r", encoding="utf-8") as file:
			print(determine_csv_type(file))
		exit()

	people, players = parse(aa.file)
	#~ people.print()

	players.sort_by_name(people)
	players.sort_by_score()
	players.update_placing()
	#~ players.print()

	table = crosstable(players)
	for row in table:
		print(",".join(row))
