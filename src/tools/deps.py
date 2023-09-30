import sys, os, re
import argparse

DIR_DIST = 'dist'
DIR_BUILD = 'build'

RE_BLOCK1 = re.compile(r'[{][{]\s*(.+?)\s*[}][}]|(?:href|src)="(.+?)"', re.S)
RE_BLOCK2 = re.compile(r'[{][{]\s*(.+?)\s*[}][}]', re.S)
RE_DEPS1 = re.compile(r'((?:tables|content|css|tools|img)/\S+)', re.S)
RE_DEPS2 = re.compile(r'((?:tables|content|css|tools)/\S+)', re.S)

def iterBlocks(aa):
	RE_BLOCK = RE_BLOCK1 if aa.all else RE_BLOCK2
	with open(aa.src) as file:
		for m in RE_BLOCK.finditer(file.read()):
			yield m.group(1) or m.group(2)

def findDeps(aa):
	pp = set()
	RE_DEPS = RE_DEPS1 if aa.all else RE_DEPS2
	with open(aa.src) as file:
		text = file.read()
	for block in iterBlocks(aa):
		for m in RE_DEPS.finditer(block):
			p = m.group(1)
			if not aa.strict or os.path.isfile(p):
				pp.add(p)
	return sorted(pp)

def preprocessNames(aa):
	if aa.tname is None and aa.auto_tname:
		aa.tname = os.path.join(DIR_DIST, aa.src)
	if aa.dname is None and aa.auto_dname:
		if aa.dst:
			aa.dname = aa.dst
		else:
			aa.dname = os.path.join(DIR_BUILD, aa.src)
			if aa.replace_ext:
				aa.dname = os.path.splitext(aa.dname)[0]
			aa.dname += '.d'

def parseArgs(args = sys.argv[1:]):
	p = argparse.ArgumentParser()
	p.add_argument('src', help='source file')
	p.add_argument('-o', '--dst', help='destination file')

	p.add_argument('-t', '--tname', help='rule target')
	p.add_argument('-d', '--dname', help='rule target .d file')
	p.add_argument('-T', '--auto-tname', action='store_true', help='rule target (derived from src)')
	p.add_argument('-D', '--auto-dname', action='store_true', help='rule target .d file (derived from src)')

	p.add_argument('-a', '--all', action='store_true', help='print all deps')
	p.add_argument('-m', '--multiline', action='store_true', help='print line-breaks')
	p.add_argument('-s', '--strict', action='store_true', help='list only extant deps')
	p.add_argument('-r', '--replace-ext', action='store_true', help='replace extension rather than append')

	aa = p.parse_args(args)
	preprocessNames(aa)

	return p, aa

def printDeps(aa, file = sys.stdout):
	deps = findDeps(aa)
	if not deps: return
	if aa.tname is None:
		for dep in deps:
			file.write(f'{dep}')
			file.write('\n' if aa.multiline else ' ')
	else:
		file.write(aa.tname)
		if aa.dname is not None:
			file.write(f' {aa.dname}')
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
	# print(aa)
	if aa.dst:
		with open(aa.dst, 'w') as file:
			printDeps(aa, file = file)
	else:
		printDeps(aa)

if __name__ == '__main__':
	sys.exit(main(sys.argv))
