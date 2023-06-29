import init


def test1():
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


def test2():
	from lib.File import File

	f = File(init.path(__file__, "src", "tables/schnell-23-02.csv"))
	print(f.type)
	print("pscores", f.pscores())
	print("ranks  ", f.ranks())
	print("rscores", f.rscores())
	#~ for p in f.players(): print(p)


if __name__ == "__main__":
	#~ test1()
	test2()
