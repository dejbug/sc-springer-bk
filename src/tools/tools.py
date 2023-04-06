import os, sys, io
import functools, contextlib
import subprocess
import argparse

class Error(Exception): pass
class OverwriteError(Error): pass

def root(*paths):
	file = os.path.abspath(__file__)
	root = os.path.dirname(os.path.dirname(file))
	return functools.reduce(os.path.join, paths, root)

def argParser(idef=None, odef=None, fdef=False):
	p = argparse.ArgumentParser()
	def add(name_or_flags, metavar_="", **kk):
		if "metavar" not in kk: kk.update({"metavar": metavar_})
		return p.add_argument(name_or_flags, **kk)
	def parse(args=None, argv=True):
		args, argv = (args, argv) if args else (sys.argv, True)
		aa = p.parse_args(args[1:] if argv else args)
		return p, aa
	setattr(p, "add", add)
	setattr(p, "parse", parse)
	return p

def argParserIOF(p, idef=None, odef=None, fdef=False):
	p.add_argument("-i", "--ipath", metavar="PATH", default=idef)
	p.add_argument("-o", "--opath", metavar="PATH", default=odef)
	p.add_argument("-f", "--force", action="store_false" if fdef else "store_true")
	prevCheck = getattr(p, "check") if hasattr(p, "check") else lambda: None
	def check():
		print("* prev checks")
		prevCheck()
		print("* check IOF")
		if not aa.ipath or not os.path.isfile(aa.ipath):
			p.error('no such input file: "%s"' % aa.ipath)
		else:
			aa.ipath = os.path.abspath(aa.ipath)
		if aa.opath and not aa.force and os.path.exists(aa.opath):
			p.error('output file exits: "%s"; delete manually (or use -f)' % aa.o)
	setattr(p, "check", check)
	return p

@contextlib.contextmanager
def oopen(opath, force=False):
	if opath:
		if not force and os.path.exists(opath):
			raise OverwriteError('output file exits: "%s";'
				' delete manually (or use -f)' % opath)
		with open(opath, "w") as ofile:
			yield ofile
	else:
		ofile = io.StringIO()
		yield ofile
		print(ofile.getvalue())

def shell(cmd):
	p = subprocess.Popen(cmd, shell=True,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	return out, err
