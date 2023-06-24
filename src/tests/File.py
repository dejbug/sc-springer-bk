import init

#~ import lib.File
from lib.CsvFile import CsvFile, CsvFileError

root = init.root(__file__, "src")
tdir = init.path(__file__, "src", "tables")

for p in init.listdir(tdir):
	try: file = CsvFile(p)
	except CsvFileError as e:
		print("! %s\n" % e)
		continue

	print("%24s {%-3s} %11s [%s]" % (file.filename,
		file.type,
		file.type.format,
		",".join(file.header)
	))

	#~ print()
	#~ for rid in range(file.rowcount):
		#~ print(" ", file.name(rid))

	print()
