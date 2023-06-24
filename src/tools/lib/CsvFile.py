import csv, os, re

class CsvFileError(Exception): pass
class CsvFileTypeError(CsvFileError): pass
class LineNormalizationError(CsvFileTypeError): pass

class CsvFileType:

	def __init__(self, line0, line1):
		line0 = self.normalizeLine(line0)

		self.type = self.fromHeaderLine(line0)
		if not self.type:
			raise CsvFileTypeError(line0)

		self.istabbed = self.type.startswith("t/")
		self.format = self.type.split("/")[-1]

		if self.format == "#NPR" or self.format == "RWSE":
			self.hasmatches = True
			self.hasrounds = True
			self.hascolors = True
		elif self.format == "#NP":
			self.hasmatches = True
			self.hasrounds = False
			line1 = self.normalizeLine(line1)
			self.hascolors = line1.find("*") >= 0
		else:
			self.hasmatches = False
			self.hasrounds = False
			self.hascolors = False

		self.needscooking = self.format == "RWSE"

	@classmethod
	def normalizeLine(cls, text):
		if isinstance(text, str):
			return text.strip()
		try:
			return ",".join(text).strip()
		except:
			raise LineNormalizationError(text)

	@classmethod
	def fromFile(cls, file):
		line1 = file.rows[0] if len(file.rows) else ""
		return cls(file.header, line1)

	@classmethod
	def fromLines(cls, lines):
		if len(lines) < 2: return cls("", "")
		return cls(lines[0], lines[1])

	def __str__(self):
		return "%s%s%s" % (
			"M" if self.hasmatches else ".",
			"C" if self.hascolors else ".",
			"R" if self.hasrounds else ".",
		)

	@classmethod
	def fromHeaderLine(cls, text):
		"""
		>>> CsvFileType.fromHeaderLine("Runde,Weiss,Schwarz,Ergebnis")
		'RWSE'
		>>> CsvFileType.fromHeaderLine("Runde,\\tWeiss,	Schwarz,	Ergebnis")
		'RWSE'
		>>> CsvFileType.fromHeaderLine("Runde\\tWeiss\\t\\tSchwarz\\tErgebnis")
		't/RWSE'
		>>> CsvFileType.fromHeaderLine("#,Name,1,2,3,4,5,Punkte")
		'#NP'
		>>> CsvFileType.fromHeaderLine("#\\tName\\t1\\t2\\t3\\t4\\t5\\tPunkte")
		't/#NP'
		>>> CsvFileType.fromHeaderLine("#,Name,G,S,R,V,Punkte,Buchh,Soberg")
		'#NGSRVPBS'
		>>> CsvFileType.fromHeaderLine("#\\tName\\tG\\tS\\tR\\tV\\tPunkte\\tBuchh\\tSoberg")
		't/#NGSRVPBS'
		>>> CsvFileType.fromHeaderLine("xyz")
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


class CsvFile:

	def __init__(self, path):
		self.filepath = path
		self.cookednames = []
		self.cookedpoints = []
		self.type, self.header, self.rows = self.load(path)

	@property
	def filename(self): return os.path.basename(self.filepath)

	@property
	def rowcount(self):
		return len(self.rows)

	@property
	def colcount(self):
		return len(self.header)

	def name(self, rid):
		if self.type.needscooking:
			if not self.cooked:
				self.cook()
			return self.cooked.names[rid]
		return self.rows[rid][1]

	def cooknames(self):
		self.cookednames = range(100)

	@classmethod
	def load(cls, path):
		with open(path, "r", encoding="utf8") as file:
			lines = [line.strip() for line in file]

		type = CsvFileType.fromLines(lines)

		if type.istabbed:
			reader = csv.reader(re.sub(r"\t+", ",", line) for line in lines)
			rows = [line for line in reader]
		else:
			reader = csv.reader(line.strip() for line in lines)
			rows = [line for line in reader]

		for i in range(len(rows)):
			rows[i] = [cell.strip() for cell in rows[i]]

		header = rows[0]
		rows = rows[1:]

		return type, header, rows
