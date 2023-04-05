import sys, codecs, copy, csv

# python gesamttabelle.py Blitzturnier-22-*-Tabelle.csv

def loadTable(filepath):
	t = []

	reader = csv.reader(codecs.open(filepath, 'r', 'utf8'))
	for row in reader:
		t.append([col.strip() for col in row])
	assert len(t) >= 3

	h = t[0]
	t = t[1:]
	assert len(t) + 3 == len(t[0]) or len(t) + 4 == len(t[0])

	return h, t

def printTable(t):
	form1 = "{0[0]:>2s} | {0[1]:<%ds} |" % getLongestNameLength(t)
	form2 = " %%-%ds |" % getLongestResultLength(t)
	for i, r in enumerate(t):
		line = ""
		for col in r[2:]:
			line += form2 % col
		print(form1.format(r), line)

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

def totals():
	# Use this with Blitzturnier-*-Sortiert.csv files.

	acc = {}

	for fn in sys.argv[1:]:
		#print(fn)
		h,t = loadTable(fn)
		#printTable(t)
		for r in t:
			n = r[1]
			p = float(r[-1])
			if n not in acc:
				acc[n] = []
			acc[n].append(p)
		for k,v in acc.items():
			acc[k] = sorted(v, reverse=True)
		#for k,v in acc.items():
		#	print(k, v[:3])


def grandtotal():

	ttt = []
	for fn in sorted(sys.argv[1:]):
		#print(fn)
		h,t = loadTable(fn)
		#printTable(t)
		pp = [0] * 10 + list(range(0, 9))
		tt = []
		for i,r in enumerate(t):
			n = r[1]
			p = float(r[-2])
			r = int(r[-1])
			tt.append([r, n, p])

		tt = sorted(tt)
		#print(tt, "\n")

		if tt[0][0] == tt[1][0]:
			# Shared first place! Both get only 9 points.
			pp.append(9)
		else:
			pp.append(10)

		for t in tt:
			t.append(pp.pop())

		#for t in tt:
		#	print(t)

		ttt.append(tt)
	return ttt


def accumulate(ttt, columns=10):
	acc = {}
	for tt in ttt:
		for t in tt:
			n = t[1]
			x = t[-1]
			if n not in acc:
				acc[n] = [x]
			else:
				acc[n].append(x)

	for k,xx in acc.items():
		xx = sorted(xx, reverse=True)
		zz = []
		for i in range(columns):
			s = sum(xx[:(3+i)])
			if i > 0 and zz[i-1] == s:
				break
			zz.append(s)
		acc[k] = [zz, xx]

	return acc


#def drop_redundant_cumulative_scores(acc):
#	acc = copy.deepcopy(acc)
#	nzzxx = sort_by_cumulative_score(acc)
#	for r in range(len(nzzxx) - 1):
#		cur = nzzxx[r + 0][1][0]
#		nxt = nzzxx[r + 1][1][0]
#		for c in range(len(cur)):
#			if cur[c] > nxt[c] or sum(cur) == sum(nxt):
#				#nzzxx[r + 0][1][0] = nzzxx[r + 0][1][0][:c+1]
#				break
#	return acc


def sort_by_highest_tournament_score(acc):
	nzzxx = sorted(acc.items(), key=lambda x: x[0])
	nzzxx = sorted(nzzxx, key=lambda x: x[1][1], reverse=True)
	return nzzxx

def sort_by_cumulative_score(acc):
	nzzxx = sorted(acc.items(), key=lambda x: x[0])
	nzzxx = sorted(nzzxx, key=lambda x: x[1][0], reverse=True)
	return nzzxx

def print_highest_tournament_scores(acc):
	for nzzxx in sort_by_highest_tournament_score(acc):
		n, zzxx = nzzxx
		zz, xx = zzxx
		print("%20s" % n, end=": ")
		print(" ".join("%2d" % x for x in xx))
	print()

def print_highest_tournament_scores_csv(acc):
	for i,nzzxx in enumerate(sort_by_highest_tournament_score(acc)):
		n, zzxx = nzzxx
		zz, xx = zzxx
		print(i+1, n, sep=",", end=",")
		print(",".join(str(x) for x in xx))
	print()

def print_cumulative_scores(acc):
	for nzzxx in sort_by_cumulative_score(acc):
		n, zzxx = nzzxx
		zz, xx = zzxx
		print("%20s" % n, end=": ")
		print(" ".join("%2d" % z for z in zz))
	print()

def print_cumulative_scores_csv(acc):
	for i,nzzxx in enumerate(sort_by_cumulative_score(acc)):
		n, zzxx = nzzxx
		zz, xx = zzxx
		print(i+1, n, sep=",", end=",")
		print(",".join(str(z) for z in zz))
	print()


ttt = grandtotal()
acc = accumulate(ttt)
print_highest_tournament_scores(acc)
print_cumulative_scores(acc)
# print_highest_tournament_scores_csv(acc)
# print_cumulative_scores_csv(acc)

