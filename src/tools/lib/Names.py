import copy, hashlib, re
from collections import namedtuple

from . import abs

FileId = namedtuple("FileId", "file id")
FileId.__repr__ = FileId.__str__ = lambda self: 'FileId(%d => "%s")' % (self.id, self.file.path)

# TODO: Add a Names class which automatically resolves added names (i.e.
#		turn a names list into a names set).

@abs.stringify
class Name:
	def __init__(self, text, fid):
		self.text = text
		self.fid = fid
		self.sid = None

	def __lt__(self, other):
		return self.sid < other.sid

	@classmethod
	def load(cls, file):
		#~ header = re.split(r',\s*|\s+', file.header)
		#~ print(file.type)
		#~ assert header[0].strip() in ("#", "Nr", "Nr.", "Platz")
		#~ assert header[1].strip() in ("Name", "Spieler")

		#~ for row in file.rows:
		for i, n in file.players():
			#~ i = int(row[0])
			#~ n = row[1]
			yield Name(n, FileId(file, i))

class Synonyms:
	def __init__(self, synonyms):
		self.synonyms = copy.deepcopy(synonyms)
		self.unresolved = []
		for synonym in self.synonyms:
			for i, name in enumerate(synonym):
				synonym[i] = HashedName(synonym[i])

	def text(self, sid, index = 0):
		if sid >= 0:
			if sid < len(self.synonyms):
				if index >= 0 and index < len(self.synonyms[sid]):
					return self.synonyms[sid][index].text
		else:
			sid = -sid-1
			if sid < len(self.unresolved):
				return self.unresolved[sid].text

	def classify(self, name):
		assert isinstance(name, (Name, str))
		name1 = HashedName(name.text if isinstance(name, Name) else name)
		for i, synonym in enumerate(self.synonyms):
			for name2 in synonym:
				if name1 == name2:
					return i
		for i, name3 in enumerate(self.unresolved):
			if name1 == name3:
				return -(i+1)
		self.unresolved.append(name1)
		return -len(self.unresolved)

	def classify_all(self, names):
		for name in names:
			name.sid = self.classify(name)

	@classmethod
	def classified(cls, names):
		return filter(lambda name: name.sid is not None, names)

	@classmethod
	def unclassified(cls, names):
		return filter(lambda name: name.sid is None, names)

	@classmethod
	def groups(cls, names):
		groups = {}
		for name in names:
			if name.sid in groups:
				groups[name.sid].append(name)
			else:
				groups[name.sid] = [name]
		return groups

class HashedName:
	def __init__(self, text):
		self.text = text
		self.name = self.normalize_name(self.text)
		self.hash = self.hash_name(self.name)

	def __eq__(self, other):
		if self.hash != other.hash: return False
		if self.name != other.name: return False
		return True

	@staticmethod
	def normalize_name(name):
		return re.sub(r"\s+", " ", name.strip()).lower()

	@staticmethod
	def hash_name(name):
		return hashlib.sha256(name.encode("utf8")).digest()

# TODO: Move synonyms into an external textfile.
DEFAULT_SYNONYMS = [
	["Anton", "Daniel Anton"],
	["Brunner", "Ben Brunner", "Benedikt Brunner", "Ben"],
	["Budimir", "Dejan Budimir", "Dejan"],
	["Hentzner", "Bernd Hentzner"],
	["Heusel", "Bernd Heusel", "Bernd"],
	["Hügelschäfer", "Patrick Hügelschäfer", "Patty Hügelschäfer"],
	["Iwanicki", "Marcel Iwanicki", "Marcel"],
	["Messer", "Reiner Messer", "Reiner"],
	["Petersen", "Hein Petersen", "Heinrich Petersen"],
	["Pfeiffer", "Willi Pfeiffer", "Willi", "Willy"],
	["Sauer", "Bruno Sauer", "Bruno"],
	["Reinhold", "Manuel Reinhold"],
	["Schmidt", "Rudolf Schmidt"],
	["Schupp", "Reinhold Schupp"],
	["Talin", "Talin Hoffmann"],
	["Wenzel", "Donald Wenzel", "Donald"],
	["Bechtold S.", "Sebastian Bechtold", "Sebastian B."],
	["Bechtold B.", "Horst Bechtold", "Horst"],
]
