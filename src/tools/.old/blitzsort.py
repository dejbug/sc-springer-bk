import glob
import re
import os.path
import sys

def load_tabellensorter():
	import os.path, sys, importlib, importlib.util
	root = os.path.dirname(os.path.dirname(__file__))
	spec = importlib.util.spec_from_file_location("tabellensorter", os.path.join(root, "tabellensorter.py"))
	module = importlib.util.module_from_spec(spec)
	sys.modules["tabellensorter"] = module
	spec.loader.exec_module(module)
	return module

def iter_files():
	root = os.path.dirname(os.path.dirname(__file__))
	srcroot = os.path.join(root, "vereinsturniere\\blitz\\einzel\\tabellen\\*.csv")
	for srcfull in glob.glob(srcroot):
		srcpath, srcname = os.path.split(srcfull)
		dstpath = os.path.join(root, "vereinsturniere\\blitz\\einzel\\sortiert")
		x = re.search(r'Blitzturnier-(\d+)-(\d+)-Tabelle.csv', srcname)
		dstname = "Blitzturnier-%02d-%02d-Sortiert.csv" % tuple(map(int, x.groups()))
		dstfull = os.path.join(dstpath, dstname)

		yield srcfull, dstfull, os.path.exists(dstfull)


def main():
	tabellensorter = load_tabellensorter()

	for src, dst, exists in iter_files():
		h, t = tabellensorter.loadTable(src)
		t = tabellensorter.sortTable(t)
		tabellensorter.stripColumn(t, h, -1)
		with open(dst, "w", newline="") as file:
			tabellensorter.printCsv(t, h, file)


if __name__ == "__main__":
	main()
