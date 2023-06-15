import sys

import tables

from lib.File import File
from lib.Names import Name, Synonyms, DEFAULT_SYNONYMS

filepaths = sys.argv[1:]

names = []

for filepath in filepaths:
	file = File(filepath)
	#~ print(filepath, file.type, len(file.rows))
	names.extend(Name.load(file))

synonyms = Synonyms(DEFAULT_SYNONYMS)
synonyms.classify_all(names)
#~ for name in synonyms.unclassified(names): print(name)

def score(name):
	rows = name.fid.file.rows
	rid = name.fid.id - 1	# header is not included in the rows
	return float(name.fid.file.rows[rid][-1])

groups = synonyms.groups(names)
for names in groups.values():
	total = 0
	for name in names:
		print("%7.2f" % score(name), name.fid.file.path)
		total += score(name)
	print("%7.2f" % total, name.text)
	print()
