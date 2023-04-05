import argparse, codecs, copy, csv, sys

def parseArgs(args=sys.argv[1:]):
	p = argparse.ArgumentParser(
		description='Sort a round-robin chess tournament CSV by rank.'
	)
	p.add_argument('filepath', help='path to the csv file')
	p.add_argument('-p', action='store_true', help='pretty-print the csv')
	p.add_argument('-s', action='store_true', help='sort the csv')
	p.add_argument('-c', action='store_true', help='cut the rank column')
	p.add_argument('-v', action='store_true', help='be verbose')
	p.add_argument('-d', action='store_true', help='debug output')
	p.add_argument('-o', help='output to file')
	a = p.parse_args(args)
	return p, a
	

def loadTable(filepath):
	t = []

	reader = csv.reader(codecs.open(filepath, 'r', 'utf8'))
	for row in reader:
		t.append([col.strip() for col in row])

	assert len(t) >= 3

	h = t[0]
	t = t[1:]
	
	assert len(t) + 4 == len(t[0])

	return h, t

def getLongestNameLength(t):
	longest = 0
	for r in t:
		current = len(r[1])
		if longest < current:
			longest = current
	return longest

def getLongestResultLength(t):
	longest = 0
	for r in t:
		for c in r[2:]:
			current = len(c)
			if longest < current:
				longest = current
	return longest

def printTable(t, debug=False, file=sys.stdout):
	form1 = "{0[0]:>2s} | {0[1]:<%ds} |" % getLongestNameLength(t)
	form2 = " %%-%ds |" % getLongestResultLength(t)
	for i, r in enumerate(t):
		if debug:
			r = copy.deepcopy(r)
			r[0] = str(int(r[0]) - 1)
			r[-1] = str(int(r[-1]) - 1)
		line = ""
		for col in r[2:]:
			line += form2 % col
		print(form1.format(r), line, file=file)

def swap(t, i, j):
	tmp = t[i]
	t[i] = t[j]
	t[j] = tmp

def swapk(t, i, j, k):
	tmp = t[i][k]
	t[i][k] = t[j][k]
	t[j][k] = tmp

def swapRows(t, i, j):
	swap(t, i, j)
	swapk(t, i, j, 0)

def swapCols(t, i, j):
	for r in t:
		swap(r, i+2, j+2)

def swapPositions(t, i, j):
	swapRows(t, i, j)
	swapCols(t, i, j)

class Move:
	def __init__(self, name, src, dst):
		self.name = name
		self.src = src
		self.dst = dst
	def __repr__(self):
		return str(self)
	def __str__(self):
		return "%s(%d>%d)" % (self.name, self.src, self.dst)

def deriveMapping(t):
	mm = []
	for i in range(len(t)):
		mm.append(Move(t[i][1], i, int(t[i][-1])-1))
	mm = sortMapping(mm)
	mm = disambiguateMapping(mm)
	return mm

def disambiguateMapping(mm):
	if not mm: return mm
	for i, m in enumerate(sorted(mm, key=lambda m: m.dst)):
		m.dst = i
	return mm

def sortMapping(mm):
	mm = sorted(mm, key=lambda m: m.name)
	mm = sorted(mm, key=lambda m: m.dst)
	return mm

def updateMappingAfterSwap(mm, i, debug=False):
	for j,m in enumerate(mm):
		if j != i and m.src == mm[i].dst:
			if debug: print("Updating %s's src from %d to %s's %d\n" % (
				m.name, m.src, mm[i].name, mm[i].src))
			m.src = mm[i].src
			break
	mm[i].src = mm[i].dst

def sortTable(t, verbose=False, debug=False):
	mapping = deriveMapping(t)

	if debug:
		print("The original table:")
		printTable(t, debug=debug)

	for i,m in enumerate(mapping):
		if debug:			
			print("\nThe mapping:")
			print(mapping)
			print()
			print(m)
			print()
		#tmp = copy.deepcopy(t)
		swapPositions(t, m.src, m.dst)
		updateMappingAfterSwap(mapping, i, debug)
		#t2.append(copy.deepcopy(tmp[i]))

		if debug:
			print("After step %d:" % (i+1))
			printTable(t, debug=debug)
			print()

	return t

def stripColumn(t, h, i):
	del h[i]
	for r in t:
		del r[i]

def printCsv(t, h, file=sys.stdout):
	writer = csv.writer(file)
	writer.writerow(h)
	writer.writerows(t)

def groupSequence(seq):
	seq = tuple(seq)
	gg = []
	g = 0
	for i in range(len(seq)):
		hasPrev = i >= 1
		hasNext = i < len(seq) - 1
		likePrev = hasPrev and seq[i] == seq[i - 1]
		likeNext = hasNext and seq[i] == seq[i + 1]
		inGroup = likePrev or likeNext
		lastOfGroup = likePrev and not likeNext
		if inGroup: g += 1
		gg.append(g)
		if lastOfGroup: g = 0
	return gg

def relabelIndexByRank(t, h):
	pass
	# TODO: When there are shared places, we want to label them
	#	1a, 1b, etc. Use groupSequence().

def main():
	p, a = parseArgs()
	h, t = loadTable(a.filepath)

	# print(relabelIndexByRank(t, h))

	file = sys.stdout
	if a.o: file = open(a.o, "w", newline="")

	if a.s:
		t = sortTable(t, a.v, a.d)

	if a.c:
		stripColumn(t, h, -1)

	if a.p:
		if not a.v:
			printTable(t, debug=a.d, file=file)
	else:
		printCsv(t, h, file=file)

	if a.o: file.close()

if __name__ == "__main__":
	main()
