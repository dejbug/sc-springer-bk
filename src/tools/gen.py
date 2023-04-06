from sys import argv
from os import path
from re import compile
from io import StringIO
from argparse import ArgumentParser
from contextlib import contextmanager

from news import printhtml

re_field = compile(r'((?:[ \t]+)(?:\{\{.+\}\}))')
re_key = compile(r'([ \t]*)\{\{(.+)\}\}')

def parseargs(args=argv[1:]):
	p = ArgumentParser()
	p.add_argument("-i", metavar="PATH", default=path.join(getroot(), "index.html"))
	p.add_argument("-o", metavar="PATH")
	p.add_argument("-f", action="store_true")
	aa = p.parse_args(args)

	if not path.isfile(aa.i):
		p.error('no such input file: "%s"' % aa.i)

	if aa.o and not aa.f and path.exists(aa.o):
		p.error('output file exits: "%s"; delete manually (or use -f)' % aa.o)

	return p, aa

def getroot():
	return path.dirname(path.dirname(path.abspath(__file__)))

def iter(ipath):
	with open(ipath) as file:
		for x in re_field.finditer(file.read()):
			yield x

def handler(ofile, key):
	prefix, key = parsekey(key)
	if key == "news":
		ipath = path.join(getroot(), "content/news.txt")
		printhtml(ipath, ofile, prefix)

def parsekey(key):
	x = re_key.match(key)
	return x.groups() if x else (None, None)

@contextmanager
def oopen(opath, force=True):
	if opath and (force or not path.exists(opath)):
		with open(opath, "w") as ofile:
			yield ofile
	else:
		ofile = StringIO()
		yield ofile
		print(ofile.getvalue())

def generate(ofile, ipath, callback=handler):
	text = open(ipath).read()
	state = 0
	for chunk in re_field.split(text):
		ofile.write(chunk) if state == 0 else callback(ofile, chunk)
		state = (state + 1) % 2

if __name__ == "__main__":
	p, aa = parseargs()
	#~ print(aa); exit()
	with oopen(aa.o) as ofile:
		generate(ofile, aa.i)
