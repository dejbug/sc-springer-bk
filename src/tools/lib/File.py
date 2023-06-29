import re, csv, os.path
from . import abs

class File:
	class Error(Exception): pass
	class ArgError(Error): pass
	class NotFoundError(Error): pass

	def __init__(self, path = None):
		self.path = path
		self._header = None
		self._rows = None

	@classmethod
	def check(cls, path):
		if not path: raise cls.ArgError
		if not os.path.isfile(path): raise cls.NotFoundError
		return True

	@property
	def header(self):
		self.check(self.path)
		if not self._header:
			with open(self.path, "r", encoding="utf8") as file:
				self._header = file.readline().strip()
		return self._header

	@property
	def rows(self):
		self.check(self.path)
		if not self._rows:
			with open(self.path, "r", encoding="utf8") as file:
				self._header = file.readline().strip()
				t = self.htype(self._header)
				if not t:
					raise Exception("unknown CSV type")
				elif t.startswith("t/"):
					reader = csv.reader(self.tabs2comma(line.strip()) for line in file)
					self._rows = [line for line in reader]
				else:
					reader = csv.reader(line.strip() for line in file)
					self._rows = [line for line in reader]
			for i in range(len(self._rows)):
				self._rows[i] = [cell.strip() for cell in self._rows[i]]
		return self._rows

	@property
	def type(self):
		return self.htype(self.header)

	@classmethod
	def tabs2comma(self, text):
		return re.sub(r"\t+", ",", text)

	@classmethod
	def htype(cls, text):
		"""
		>>> File.htype("Runde,Weiss,Schwarz,Ergebnis")
		'RWSE'
		>>> File.htype("Runde,\\tWeiss,	Schwarz,	Ergebnis")
		'RWSE'
		>>> File.htype("Runde\\tWeiss\\t\\tSchwarz\\tErgebnis")
		't/RWSE'
		>>> File.htype("#,Name,1,2,3,4,5,Punkte")
		'#NP'
		>>> File.htype("#\\tName\\t1\\t2\\t3\\t4\\t5\\tPunkte")
		't/#NP'
		>>> File.htype("#,Name,G,S,R,V,Punkte,Buchh,Soberg")
		'#NGSRVPBS'
		>>> File.htype("#\\tName\\tG\\tS\\tR\\tV\\tPunkte\\tBuchh\\tSoberg")
		't/#NGSRVPBS'
		>>> File.htype("xyz")
		"""
		text = text.strip()
		if re.match("^#,\s*Name(,\s*\d+)+,\s*Punkte,\s*Platz$", text):
			return "#NPP"
		elif re.match("^#\t+Name(\t+\d+)+\t+Punkte\t+Platz$", text):
			return "t/#NPP"
		if re.match("^#,\s*Name(,\s*\d+)+,\s*Punkte$", text):
			return "#NP"
		elif re.match("^#\t+Name(\t+\d+)+\t+Punkte$", text):
			return "t/#NP"
		elif re.match("^#,\s*Name(,\s*\d+)+$", text):
			return "#N"
		elif re.match("^#\t+Name(\t+\d+)+$", text):
			return "t/#N"
		elif re.match("^#,\s*x\s*=\s*(,\s*\d+)+$", text):
			return "#X"
		elif re.match("^#\t+x\s*=\s*(\t+\d+)+$", text):
			return "t/#X"
		elif re.match("^Runde,\s*Weiss,\s*Schwarz,\s*Ergebnis$", text):
			return "RWSE"
		elif re.match("^Runde\t+Weiss\t+Schwarz\t+Ergebnis$", text):
			return "t/RWSE"
		elif re.match("^#,\s*Name,\s*G,\s*S,\s*R,\s*V,\s*Punkte,\s*Buchh,\s*Soberg$", text):
			return "#NGSRVPBS"
		elif re.match("^#\t+Name\t+G\t+S\t+R\t+V\t+Punkte\t+Buchh\t+Soberg$", text):
			return "t/#NGSRVPBS"
		elif re.match("^#,\s*Name,\s*Punkte(,\s*R\d+)+$", text):
			return "#NPR"
		elif re.match("^#\t+Name\t+Punkte(\t+R\d+)+$", text):
			return "t/#NPR"

	def points_column_index(self):
		# TODO: Add more types!
		t = self.type
		if t.endswith("#NP"): return -1
		if t.endswith("#NPR"): return 2
		if t.endswith("#NGSRVPBS"): return -3
		raise Exception("score column not found: unknown table")

	def tiebreaks_column_index(self):
		if self.type.endswith("#NGSRVPBS"): return [-2, -1]
		return []

	def ranks(self, contiguous = False, roworder = False):
		#~ pscores = self.pscores()
		#~ pscores = sorted(pscores, reverse = True)
		#~ lut = range(len(pscores))
		#~ lut = sorted(lut, reverse = True, key = lambda i: pscores[i])
		#~ print(lut)

		ranks = ((i, s) for i, s in enumerate(self.pscores(tiebreaks = True)))
		ranks = sorted(ranks, reverse = True, key = lambda x: x[1])
		#~ print("ranks (sorted)   ", ranks)

		last = None
		for index, rowindex_score in enumerate(ranks):
			rowindex, score = rowindex_score
			if score != last:
				last = score
				rank = rank + 1 if contiguous else index + 1
			else:
				rank = index
			ranks[index] = (rowindex, rank)

		if roworder:
			ranks = sorted(ranks, reverse = False, key = lambda x: x[0])
			#~ print("ranks (de-sorted)", ranks)

		#~ print(self.path, ranks)
		return ranks

	def pscores(self, tiebreaks = False, shift = 100):
		i = self.points_column_index()
		ss = [float(row[i]) for row in self.rows]
		if tiebreaks:
			ii = self.tiebreaks_column_index()
			if ii:
				ss = [[s] for s in ss]
				for j, row in enumerate(self.rows):
					for i in ii:
						ss[j].append(float(row[i]))
				if shift:
					ss = [p * shift * shift + bu * shift + so * shift for p, bu, so in ss]
		return ss

	def rscores(self, contiguous = False):
		ranks = self.ranks(contiguous = contiguous, roworder = True)
		if len(ranks) == 0: return None
		if len(ranks) == 1: return 10.0
		topscore = 9.0 if ranks[0][1] == ranks[1][1] else 10.0
		ranks = [topscore if r[1] == 1 else max(0.0, 10.0 - r[1]) for r in ranks]
		return ranks

	def rank(self, rid, contiguous = False):
		ranks = self.ranks(contiguous = contiguous)
		for i, r in ranks:
			if i == rid:
				return r

	def pscore(self, rid):
		i = self.points_column_index()
		return float(self.rows[rid][i])

	def rscore(self, rid, contiguous = False):
		return self.rscores(contiguous = contiguous)[rid]

	def players(self):
		t = self.type
		t = t.lstrip("t/")
		#~ print(t)
		if t.startswith("#N"):
			for row in self.rows:
				yield int(row[0]), row[1]
		#~ elif t.startswith("RWSE"):
			#~ d = set()
			#~ for row in self.rows:
				#~ d.add(row[1])
				#~ d.add(row[2])
			#~ for i, n in enumerate(sorted(d), start=1):
				#~ yield i, n
