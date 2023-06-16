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

	def check(self):
		if not self.path: raise self.ArgError
		if not os.path.isfile(self.path): raise self.NotFoundError
		return True

	@property
	def header(self):
		self.check()
		if not self._header:
			with open(self.path, "r", encoding="utf8") as file:
				self._header = file.readline().strip()
		return self._header

	@property
	def rows(self):
		self.check()
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
		if re.match("^#,\s*Name(,\s*\d+)+,\s*Punkte$", text):
			return "#NP"
		elif re.match("^#\t+Name(\t+\d+)+\t+Punkte$", text):
			return "t/#NP"
		elif re.match("^#,\s*Name(,\s*\d+)+$", text):
			return "#NP"
		elif re.match("^#\t+Name(\t+\d+)+$", text):
			return "t/#NP"
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
