import sys

import init
import lib.fs


def main():

	tables_dir = lib.fs.path("src", "tests")
	#~ print(tables_dir)

	for p in lib.fs.list("src", "tables"):
		print(p)
		print()

		lines = lib.fs.lines(p)

		sig = lib.fs.signature(lines)
		if not sig.istournament: continue
		print(sig)
		print()

		for line in lines:
			print(line)
		print()

if __name__ == "__main__":
	sys.exit(main())
