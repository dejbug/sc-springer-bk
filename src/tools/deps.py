import sys, os, re
import argparse

REGEX = re.compile(r'\{\{.*?\s+((?:tables|content|css)/\S+)', re.S)

def iterDeps(path, strict = True):
	with open(path) as file:
		for m in REGEX.finditer(file.read()):
			p = m.group(1)
			if not strict or os.path.isfile(p):
				yield p

def parseArgs(args = sys.argv[1:]):
	p = argparse.ArgumentParser()
	p.add_argument('src', help='source file')
	p.add_argument('-o', '--dst', help='destination file')
	p.add_argument('-t', '--tname', nargs='?', const='', help='rule target file')
	p.add_argument('-d', '--dname', nargs='?', const='', help='associate with .d file')
	p.add_argument('-m', '--multiline', action='store_true', help='print line-breaks')
	p.add_argument('-s', '--strict', action='store_true', help='list only extant deps')
	p.add_argument('-r', '--replace-ext', action='store_true', help='replace extension rather than append')
	return p, p.parse_args(args)

def makeNames(aa):
	tname, dname = None, None
	if aa.tname is not None:
		tname = aa.tname or aa.src
		if aa.dname is not None:
			if aa.dname:
				dname = aa.dname
			elif aa.dst:
				dname = aa.dst
			else:
				if aa.replace_ext:
					dname = os.path.splitext(tname)[0] + '.d'
				else:
					dname = tname + '.d'
	return tname, dname

def printDeps(aa, file = sys.stdout):
	deps = list(iterDeps(aa.src, strict = aa.strict))
	if not deps: return
	tname, dname = makeNames(aa)
	if tname is None:
		for dep in deps:
			file.write(f'{dep}')
			file.write('\n' if aa.multiline else ' ')
	else:
		file.write(tname)
		if dname is not None:
			file.write(f' {dname}')
		if aa.multiline:
			file.write(f' :\\\n')
		else:
			file.write(f' : ')
		if aa.multiline:
			last = len(deps) - 1
			for i, dep in enumerate(deps):
				file.write(f'\t{dep}')
				if i != last:
					file.write('\\')
				file.write('\n')
		else:
			file.write(' '.join(deps))

def main(argv):
	parser, aa = parseArgs(argv[1:])
	# if aa.dst:
	# 	with open(aa.dst, 'w') as file:
	# 		printDeps(aa, file = file)
	printDeps(aa)

if __name__ == '__main__':
	sys.exit(main(sys.argv))
