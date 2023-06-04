import os, sys, io, glob
import functools, contextlib
import subprocess
import argparse

class Error(Exception): pass
class OverwriteError(Error): pass

def root(*parts):
	file = os.path.abspath(__file__)
	root = os.path.dirname(os.path.dirname(file))
	return functools.reduce(os.path.join, parts, root)

def argParser():
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
	prevCheck = getattr(p, "check") if hasattr(p, "check") else lambda aa: None
	def check(aa):
		print("* prev checks")
		prevCheck(aa)
		print("* check IOF")
		if not aa.ipath or not os.path.isfile(aa.ipath):
			p.error('no such input file: "%s"' % aa.ipath)
		else:
			aa.ipath = os.path.abspath(aa.ipath)
		if aa.opath and not aa.force and os.path.exists(aa.opath):
			p.error('output file exits: "%s"; delete manually (or use -f)' % aa.o)
	setattr(p, "check", check)
	return p

class ArgParser(argparse.ArgumentParser):
	def __init__(self):
		super(ArgParser, self).__init__()

	def add(self, *aa, **kk):
		if len(aa) > 1 and not aa[-1].startswith("-"):
			metavar = aa[-1]
			aa = aa[:-1]
			if "action" not in kk and "metavar" not in kk:
				kk.update({"metavar": metavar})
		return self.add_argument(*aa, **kk)

	def parse(self, args, argv=True):
		args, argv = (args, argv) if args else (sys.argv, True)
		aa = self.parse_args(args[1:] if argv else args)
		self.check(aa)
		return aa

	def check(self, aa):
		return True

class ArgParserC(argparse.ArgumentParser):
	def __init__(self, idef=None, odef=None):
		super(ArgParserC, self).__init__()
		if isinstance(idef, str): idef = glob.glob(idef)
		self.add_argument("ipaths", nargs="*" if idef else "+", metavar="PATH", default=idef)
		self.add_argument("-o", "--opath", metavar="PATH", default=odef)
		self.add_argument("-d", "--deps", action="store_true")

	def parse(self, args, argv=True):
		args, argv = (args, argv) if args else (sys.argv, True)
		aa = self.parse_args(args[1:] if argv else args)
		self.check(aa)
		return aa

	def check(self, aa):
		if not aa: return False
		for i in range(len(aa.ipaths)):
			if not os.path.isfile(aa.ipaths[i]):
				self.error('no such input file: "%s"' % aa.ipaths[i])
			else:
				aa.ipaths[i] = os.path.abspath(aa.ipaths[i])

@contextlib.contextmanager
def oopen(opath=None, force=False):
	if opath:
		if not force and os.path.exists(opath):
			raise OverwriteError('output file exits: "%s";'
				' delete manually (or use -f)' % opath)
		with open(opath, "w") as ofile:
			yield ofile
	else:
		ofile = io.StringIO()
		yield ofile
		print(ofile.getvalue(), end="")

def shell(cmd, encoding=None):
	p = subprocess.Popen(cmd, shell=True,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	if encoding:
		out = out.decode(encoding)
		err = err.decode(encoding)
	return out, err

def split(text, splitter):
	chunks = splitter.split(text)
	state = 0
	for chunk in chunks:
		yield state, chunk
		state = (state + 1) % 2

def rsplit(text, splitter, key=lambda x: x.groups()):
	offset = 0
	for x in splitter.finditer(text):
		if x.start(0) > offset:
			yield 0, text[offset:x.start(0)]
		yield 1, key(x)
		offset = x.end(0)
	if len(text) > offset:
		yield 0, text[offset:]

def noext(path):
	return os.path.splitext(path)[0]
