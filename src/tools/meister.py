#~ import init

from lib.File import File
from lib.Names import Name, Synonyms, DEFAULT_SYNONYMS

import copy, csv, glob, math, os, sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


EST_PERF_FACTOR = 10
EST_MIN_RATING = 1550
BOTTOM_CUTOFF = 1000
MAX_GP_COUNT_GAUGE = EST_MIN_RATING - BOTTOM_CUTOFF


class Player:
	def __init__(self, name = "", confirmed = 0, dwz = 0, est = 0):
		self.name = name
		self.confirmed = confirmed
		self.dwz = dwz
		self.est = est
		self.gp_perf = 0
		self.gp_sum = 0
		self.gp_count = 0

	@property
	def xwz(self):
		return max(player.dwz, EST_MIN_RATING)

	def __getitem__(self, key):
		if isinstance(key, int):
			return list(self.__dict__.values())[key]
		if isinstance(key, str):
			return self.__dict__[key]

	def __iter__(self):
		return self.__dict__

	def __str__(self):
		confirmation = "[x]" if self.confirmed else "[ ]"
		return " %20s %s %4d  |  %4d  %5.2f = %2d / %-2d" % (
			self.name, confirmation, self.est, self.dwz,
			self.gp_perf, self.gp_sum, self.gp_count)


def load_csv(rootPath):
	#~ ipath = init.path(__file__, "src", rootPath)
	ipath = rootPath
	#~ print(ipath)
	#~ print(open(ipath, encoding="utf8").read())

	players = []
	file = open(ipath, encoding="utf8")
	header = file.readline()
	for row in csv.reader(file):
		name = row[0].strip()
		confirmed = int(row[1])
		dwz = int(row[2])
		est = 0 # int(row[3])
		players.append(Player(name, confirmed, dwz, est))
	return players


def byName(x):
	return player.name

def byNameConfirmedFirst(player):
	return 1 - player.confirmed, player.name

def byRating(player):
	return player.dwz

def byEst(player):
	return player.est

def byRest(player):
	return player[4:]


def lastname(name):
	first, last = name.split(" ")
	if last == "?": return first + " *"
	return last


def print_player(player, mode = 0):
	#~ rest = player[4:]
	#~ rest = rest = " -- " + str(rest) if rest else ""
	if mode == 0:
		print(player)
	elif mode == 1:
		confirmation = "ja" if player.confirmed else "nein"
		print("<tr> <td>%s</td> <td>%s</td> <td>%d</td> <td>%d</td> </tr>" % (
			lastname(player.name), confirmation, player.dwz, player.est))


def print_players(players, mode = 0, cmpkey = None, reverse = False):
	if cmpkey:
		players = sorted(players, key = cmpkey, reverse = reverse)

	for player in players:
		print_player(player, mode = mode)


def split_into_groups(players, groups = 0):
	if groups <= 0: return players

	count = len(players)
	cutoff = math.ceil(count / groups)

	out = []
	group = []

	index = 0
	for player in players:
		if index >= cutoff:
			index = 0
			out.append(group)
			group = []
		index += 1
		group.append(player)

	if group:
		out.append(group)

	return out


def load_tournament_files():
	#~ root = init.root(__file__, "src")
	root = ""
	nn = glob.glob(root + "tables/[sb]*[e0-9].csv")
	#~ print(len(nn), nn)

	ff = [File(n) for n in nn]

	names = []
	for f in ff:
		names.extend(Name.load(f))
	synonyms = Synonyms(DEFAULT_SYNONYMS)
	synonyms.classify_all(names)

	return ff, synonyms


def load_players(ff, synonyms):
	pp = {}
	for f in sorted(ff, key = lambda f: f.path):
		#~ print(" %-12s" % f.type, os.path.basename(f.path))
		for x in zip(f.players(), f.rscores()):
			sid = synonyms.classify(x[0][1])
			name = synonyms.text(sid)
			rank = x[1]
			if name not in pp:
				pp[name] = [(rank, f.path)]
			else:
				pp[name].append((rank, f.path))

	#~ for n, rr in pp.items():
		#~ print(n)
		#~ for r in sorted(rr, reverse=True, key = lambda x: x[0]):
			#~ print("    ", r)

	return pp


def load_totals(pp):
	max_gp_count = max(len(history) for name, history in pp.items())
	#~ print(max_gp_count)
	totals = [(n, sum(r[0] for r in rr), len(rr)) for n, rr in pp.items()]
	#~ cmpkey = lambda x: (x[1], -(x[2] if x[2] else max_gp_count))
	def cmpkey(x):
		name, gp_sum, gp_count = x
		if not gp_count: gp_count = max_gp_count
		# The more tournaments played to get the same sum, the worse was the performance.
		return gp_sum, -gp_count
	totals = sorted(totals, key = cmpkey, reverse = True)
	return totals


def print_totals():
	ff, synonyms = load_tournament_files()
	pp = load_players(ff, synonyms)
	totals = load_totals(pp)
	for t in totals:
		print(t)


def extend_players_with_totals(players):
	ff, synonyms = load_tournament_files()
	pp = load_players(ff, synonyms)
	totals = load_totals(pp)
	for player in players:
		sid = synonyms.classify(player[0])
		player_name = synonyms.text(sid)
		extended = False
		for t in totals:
			totals_name = t[0]
			if totals_name == player_name:
				player.gp_perf = t[1] / t[2] if t[2] else 0
				player.gp_sum = t[1]
				player.gp_count = t[2]
				extended = True
				break
		if not extended:
			player.gp_perf = 0
			player.gp_sum = 0
			#~ player.gp_count = len(ff)
			player.gp_count = 0
	return len(ff)


def estimate_ratings(players):
	players = sorted(players, key = byRating, reverse = True)
	for player in players:
		player.est = max(player.dwz, EST_MIN_RATING) + EST_PERF_FACTOR * player.gp_perf
	#~ players = copy.deepcopy(players)
	#~ players = sorted(players, key = lambda player: player.est, reverse = True)
	#~ for player in players: print(player)


def plot1(players):
	players = sorted(players, key = lambda p: max(p.dwz, p.est), reverse = True)
	fig, ax = plt.subplots(layout="constrained")

	x = range(len(players))
	yy = [p.dwz for p in players]
	zz = [p.est for p in players]
	for i, p in enumerate(players):
		bar = ax.bar(i * (10 + 4), yy[i], width=10, color="blue", label="dwz")
		if zz[i]:
			ax.bar(i * (10 + 4), zz[i]-yy[i], width=10, color="red", bottom=yy[i], label="est")
		#~ ax.bar_label(bar, labels=[p.name], label_type="edge")
	ax.set_xticks(np.arange(len(players)) * (10 + 4), [p.name for p in players])
	plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize="13")
	plt.show()


def plot2(players, tournament_count = 0):
	players = sorted(players, key = lambda p: max(p.dwz, p.est), reverse = True)
	fig, ax = plt.subplots(layout="constrained", figsize=(14,5))

	bar_width = 20
	bar_gap = 2
	group_width = 2 * (bar_width + bar_gap) - bar_gap
	group_gap = 10

	max_est = 0
	if tournament_count:
		max_gp_count = tournament_count
	else:
		max_gp_count = 0
		for p in players:
			max_gp_count = max(max_gp_count, p.gp_count)
			max_est = max(max_est, p.est)

	max_gp_factor = MAX_GP_COUNT_GAUGE / max_gp_count

	def add_bar(hh=None, cc=None, bb=None):
		return ax.bar(positions, width=bar_width, align="edge",
			height = hh, color = cc, bottom = bb)

	def add_label(bar, tt=None, c=None, s=None):
		ax.bar_label(bar, label_type="center", labels=tt, color=c, fontsize=s)

	group_count = 2
	group_size = math.ceil(len(players) / group_count)

	for i, player in enumerate(players):
		bottom = player.dwz
		middle = EST_MIN_RATING - player.dwz if player.dwz < EST_MIN_RATING else 0
		top = player.est - bottom - middle

		offset = i * (group_width + group_gap)
		positions = [offset + 0, offset + bar_width + bar_gap]
		ax.text(offset, player.est + 30, int(player.est))

		if i > 0 and i % group_size == 0:
			ax.axvline(offset - group_gap / 2, zorder=0, color="grey")

		if bottom:
			bar = add_bar(
				[bottom, BOTTOM_CUTOFF + max_gp_factor * player.gp_count],
				["black", "green"]
			)
			if player.gp_count:
				add_label(bar, ["", player.gp_count], "white")
		if middle:
			bar = add_bar(
				[middle, 0 if bottom else BOTTOM_CUTOFF + max_gp_factor * player.gp_count],
				["grey", "green"],
				[bottom, 0]
			)
			if not bottom and player.gp_count:
				add_label(bar, ["", player.gp_count], "white")
			bottom += middle
		bar = add_bar(
			[top, max_gp_factor * (max_gp_count - player.gp_count)],
			["orange", "lightgrey"],
			[bottom, BOTTOM_CUTOFF + max_gp_factor * player.gp_count]
		)
		#~ addition = int(player.est - max(player.dwz, EST_MIN_RATING))
		#~ if addition: add_label(bar, [addition, ""], "black")

	ax.axhline(EST_MIN_RATING, zorder=0, color="grey")
	ax.axhline(BOTTOM_CUTOFF + MAX_GP_COUNT_GAUGE + 1, zorder=0, color="lightgrey")
	ax.set_ylim(bottom = BOTTOM_CUTOFF)

	ii = range(len(players))
	positions = [i * (group_width + group_gap) + bar_width for i in ii]
	ax.set_xticks(positions, [p.name for p in players])
	plt.setp(ax.get_xticklabels(), rotation=30, ha="right", fontsize="13")

	plt.show()


def main1():
	mode = 0

	players = load_csv("tables/meister-23-players.csv")

	asked = len(players)
	confirmed = sum(it[1] for it in players)
	print("  (", confirmed, "of", asked, "are confirmed )\n")

	#~ print_players(players, mode = mode, cmpkey = byName)
	#~ print_players(players, mode = mode, cmpkey = byNameConfirmedFirst)
	#~ print_players(players, mode = mode, cmpkey = byRating, reverse = True)

	#~ players = sorted(players, key = byRating, reverse = True)
	#~ players = sorted(players, key = byEst)
	#~ print_players(players, mode = mode)

	#~ print_totals()
	tournament_count = extend_players_with_totals(players)
	estimate_ratings(players)
	#~ print(tournament_count)

	#~ players = sorted(players, key = byRest, reverse = True)
	#~ players = sorted(players, key = byRating, reverse = True)
	#~ print_players(players, mode = mode)

	players = sorted(players, key = lambda player: player.est, reverse = True)

	unconfirmed = [player for player in players if not player.confirmed]
	players = [player for player in players if player.confirmed]

	groups = split_into_groups(players, 2)
	for group in groups:
		print_players(group, mode = mode)
		print()

	for player in unconfirmed:
		print_player(player, mode = mode)

	#~ plot1(players)
	#~ plot2(players)


def main2():
	mode = 0

	players = load_csv("tables/meister-23-players.csv")

	asked = len(players)
	confirmed = sum(it[1] for it in players)
	print("  (", confirmed, "of", asked, "are confirmed )\n")

	#~ print_players(players, mode = mode, cmpkey = byName)
	#~ print_players(players, mode = mode, cmpkey = byNameConfirmedFirst)
	#~ print_players(players, mode = mode, cmpkey = byRating, reverse = True)

	#~ players = sorted(players, key = byRating, reverse = True)
	#~ players = sorted(players, key = byEst)
	#~ print_players(players, mode = mode)

	#~ print_totals()
	tournament_count = extend_players_with_totals(players)
	estimate_ratings(players)

	#~ players = sorted(players, key = byRest, reverse = True)
	#~ players = sorted(players, key = byRating, reverse = True)
	#~ print_players(players, mode = mode)

	players = sorted(players, key = lambda player: player.est, reverse = True)

	unconfirmed = [player for player in players if not player.confirmed]
	#~ players = [player for player in players if player.confirmed]

	groups = split_into_groups(players, 2)
	for group in groups:
		print_players(group, mode = mode)
		print()

	for player in unconfirmed:
		print_player(player, mode = mode)

	#~ plot1(players)
	plot2(players, tournament_count)


def main3():
	mode = 1

	players = load_csv("tables/meister-23-players.csv")

	#~ asked = len(players)
	#~ confirmed = sum(it[1] for it in players)
	#~ print("  (", confirmed, "of", asked, "are confirmed )\n")

	#~ print_totals()
	extend_players_with_totals(players)
	estimate_ratings(players)

	#~ players = sorted(players, key = byRest, reverse = True)
	#~ players = sorted(players, key = byRating, reverse = True)
	#~ print_players(players, mode = mode)

	players = sorted(players, key = lambda player: player.est, reverse = True)
	print_players(players, mode = mode)

	#~ unconfirmed = [player for player in players if not player.confirmed]
	#~ players = [player for player in players if player.confirmed]

	#~ groups = split_into_groups(players, 2)
	#~ for group in groups:
		#~ print_players(group, mode = mode)
		#~ print()

	#~ for player in unconfirmed:
		#~ print_player(player, mode = mode)

	#~ plot1(players)
	#~ plot2(players)


if __name__ == "__main__":
	main = main3
	sys.exit(main())
