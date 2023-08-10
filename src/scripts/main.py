import argparse
import traceback
import os
import sys

import init


def parse_args(args = sys.argv[1:]):
	parser = argparse.ArgumentParser()
	parser.set_defaults(cmd = '')

	subs = parser.add_subparsers()

	p = subs.add_parser('list')
	p.set_defaults(cmd = 'list')

	p.add_argument('-t', '--types', action = 'store_true')

	p.add_argument('-p', '--parse', action = 'store_true')
	p.add_argument('-n', '--names', action = 'store_true')
	p.add_argument('-s', '--sorted', action = 'store_true')
	p.add_argument('-r', '--reverse', action = 'store_true')

	p = subs.add_parser('find')
	p.set_defaults(cmd = 'find')

	p.add_argument('-y', '--year', type=int)
	p.add_argument('-m', '--month', type=int)
	p.add_argument('-t', '--type')

	p.add_argument('-p', '--parse', action = 'store_true')
	p.add_argument('-n', '--names', action = 'store_true')
	p.add_argument('-s', '--sorted', action = 'store_true')
	p.add_argument('-r', '--reverse', action = 'store_true')

	return parser, parser.parse_args(args)


def listCsvFilePaths(printTypes = False, parsePaths = False, justNames = False, sortEm = False, reverseSort = False):
	from tools.lib import fs

	nn = []

	for n in fs.list('src', 'tables'):

		pt = 0
		fts = ""
		pts = ""

		if parsePaths:
			pt = fs.ptype(n)
			if pt:
				pts = f'{pt.year}-{pt.month} / {pt.type}\t'
			else:
				pts = '*\t'

		if printTypes:
			fts = f"{fs.ftype(n) or '*':>12s}\t"

		if justNames:
			_, n = os.path.split(n)

		nn.append((pt, fts, pts, n))

	if sortEm:
		nn = sorted(nn, key = lambda n: n[0])

	if reverseSort:
		nn = reversed(nn)

	return ["".join(n[1:]) for n in nn]


def findCsvFilePaths(year = None, month = None, csvType = None, parsePaths = False, justNames = False, sortEm = False, reverseSort = False):
	from tools.lib import fs

	nn = []

	for n in fs.list('src', 'tables'):
		t = fs.ptype(n)
		if year is not None and not year == t.year: continue
		if month is not None and not month == t.month: continue
		if csvType is not None and not csvType == t.type: continue
		if justNames: _, n = os.path.split(n)
		nn.append((t, n))

	if sortEm:
		nn = sorted(nn, key = lambda n: n[0])

	if reverseSort:
		nn = reversed(nn)

	if parsePaths:
		nn = [
			[
				f"{n[0].type}{n[0].extra} / {n[0].year}-{n[0].month:02d}"
					if n[0] else f"{'':2s}\t{'':12s}",
				n[1]
			] for n in nn]
		return [f"{n[0]:>24s}\t{n[1]}" for n in nn]

	return [n[1] for n in nn]


def test_gp():
	from tools import gp

	from lib.CsvTablePath import CsvTablePath
	from lib.History import History

	# indexFilePath = init.path(__file__, "src", "tables/gp-22-08.csv")
	indexFilePath = init.path(__file__, "src", "tables/gp-23-01.csv")
	# print(indexFilePath)

	filePaths = CsvTablePath.fromIndexFile(indexFilePath)
	# for p in filePaths: print(p)

	filePaths = [p.path for p in filePaths]
	names, synonyms = gp.load_names_from_files(filePaths)

	if 0:
		for nn in synonyms.synonyms:
			for n in nn:
				print(n.text, end=", ")
				print()

		for n in names: print(n)

	his = History(names, synonyms, contiguous = False)
	his.sort_by_rscores(descending = True)

	for player in his.players:
		playerAliases = [name.text for name in player.names]
		print(player.name, playerAliases)
		for score in player.scores:
			print(score.pscore, score.rscore, score.rank, sep=' | ')
		print()



if __name__ == '__main__':
	# from tools.lib import fs
	# print(fs.root('src'))

	parser, args = parse_args()
	# print(args); exit()

	if args.cmd == 'list':
		nn = listCsvFilePaths(args.types, args.parse, args.names, args.sorted, args.reverse)
		for n in nn:
			print(n)

	elif args.cmd == 'find':
		nn = findCsvFilePaths(args.year, args.month, args.type, args.parse, args.names, args.sorted, args.reverse)
		for n in nn:
			print(n)

	# test_gp()
