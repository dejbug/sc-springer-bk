import os, re

import lib.abs

@lib.abs.reprify
@lib.abs.stringify
class CsvTablePath:
	class Error(Exception): pass

	def __init__(self, root, type, year, month, extra):
		self.root = root.strip() if root else ""
		self.type = type.strip() if type else ""
		self.year = int(year)
		self.month = int(month)
		self.extra = extra.strip() if extra else ""

		if not self.root.endswith("/"): self.root += "/"

	def __lt__(self, other):
		return self.month < other.month

	def exists(self):
		return os.path.isfile(self.path)

	@property
	def name(self):
		return "%s-%02d-%02d%s.csv" % (self.type, self.year, self.month, self.extra)

	@property
	def path(self):
		return os.path.join(self.root, self.name)

	def find(self, *aa):
		if self.exists(): return True
		root = self.root
		for a in aa:
			self.root = a
			if self.exists():
				return True
		self.root = root
		return False

	@classmethod
	def parse(cls, text):
		m = re.match(r"(.+?/)?(blitz|schnell)-(\d+)-(\d+)(-.+?)?\.csv", text)
		return cls(*m.groups())

	@classmethod
	def fromIndexFile(cls, path):
		if not os.path.isfile(path):
			raise cls.Error('index file not found: "%s"' % path)
		root = os.path.dirname(path)
		with open(path) as file:
			pp = (line.strip() for line in file)
			pp = (CsvTablePath.parse(line) for line in pp)
			pp = sorted(pp)
		pp = list(pp)
		for p in pp:
			if not p.find(root):
				raise cls.Error('csv table file not found: "%s"' % p.path)
		return pp
