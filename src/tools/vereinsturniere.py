import argparse, collections, glob, io, os, re, sys

Path = collections.namedtuple("Path", "root type year month extra_")
Path.re = re.compile(r"(.*?/)(blitz|schnell|gp)-(\d+)-(\d+)(-.*?)?\.csv")
Path.gg = classmethod(lambda cls, path: cls.re.match(path).groups())
Path.tt = [os.path.normpath, str, int, int, lambda x: x]
Path.aa = classmethod(lambda cls, path: (t(g) for t,g in zip(cls.tt, cls.gg(path))))
Path.parse = classmethod(lambda cls, path: cls(*cls.aa(path)))
Path.__lt__ = lambda p, other: p.month < other.month
Path.extra = property(lambda p: p.extra_ if p.extra_ is not None else "")
Path.name = property(lambda p: "{0.type}-{0.year:02d}-{0.month:02d}{0.extra}".format(p))
Path.path = property(lambda p: os.path.join(p.root, p.name))

template = """\
{{ cat content/html-header.html }}
{{ python tools/render.py content/navbar.html active=vereinsturniere }}
{{ python tools/render.py content/header.html }}

<main>

<h1>Vereinsturniere 20%02d</h1>

<article>

%s

</article>
</main>

{{ python tools/render.py content/footer.html }}
{{ cat content/html-footer.html }}
"""

def parse_args(args=sys.argv[1:]):
	p = argparse.ArgumentParser()
	p.add_argument("--year", type=int)
	p.add_argument("--tdir", default="tables")
	p.add_argument("--pdir", default=".")
	p.add_argument("--year-from-path")
	p.add_argument("--ofile")
	p.add_argument("--list", action="store_true")
	aa = p.parse_args(args)
	if aa.year_from_path:
		m = re.match(r"(.+?/)?vereinsturniere-(\d+)\.html", aa.year_from_path)
		if not m: p.error("invalid input")
		aa.year = int(m.group(2))
		#~ root = m.group(1) or ""
		#~ if not aa.tdir: aa.tdir = os.path.join(root, "tables")
		#~ if not aa.pdir: aa.pdir = os.path.join(root, ".")
	return p, aa

def monthname(m):
	return ["", "Januar", "Februar", "März", "April", "Mai", "Juni",
		"Juli", "August", "September", "Oktober", "November", "Dezember"][m]

def monthadd(m, c):
	return (m - 1 + c) % 12 + 1

def typename(t):
	return {"blitz": "Blitz", "schnell": "Schnell"}[t]

def write_tournament(file, p):
	#~ <a name="08"></a>
	#~ <h2>August (Blitz)</h2>
	#~ <div class="table-wrapper crosstable">
	#~ {{ python tools/csv2table.py tables/blitz-22-08.csv }}
	#~ </div>
	file.write('<a name="%02d"></a>\n' % p.month)
	file.write('<h2>%s (%s)</h2>\n' % (monthname(p.month), typename(p.type)))
	file.write('<div class="table-wrapper crosstable">\n')
	file.write('{{ python tools/csv2table.py %s.csv }}\n' % p.path)
	file.write('</div>\n')

def write_grandprix(file, p):
	#~ <a name="gp-08"></a>
	#~ <h2>Grand-Prix</h2>
	#~ <p><a href="gp-22-08.html">Grand-Prix 2022 August-Dezember</a></p>
	file.write('<a name="gp-%02d"></a>\n' % p.month)
	file.write('<h2>Grand-Prix</h2>\n')
	file.write('<p><a href="%s.html">Grand-Prix 20%02d %s-%s</a></p>\n' % (
		p.name, p.year,
		monthname(p.month),
		monthname(monthadd(p.month, 4))
	))
	pass

def write_pokal(file, pokal, year):
	#~ <a name="pokal"></a>
	#~ <h2>Pokal</h2>
	#~ <p><a href="pokal-22.html">Pokalturnier 2022</a></p>
	file.write('<a name="pokal"></a>\n')
	file.write('<h2>Pokal</h2>\n')
	file.write('<p><a href="%s">Pokalturnier 20%02d</a></p>\n' % (pokal, year))
	pass

def blah(pp, gg, pokal=None):
	g = 0

	s = io.StringIO()

	for i, p in enumerate(pp):
		if g < len(gg) and gg[g].month == p.month:
			write_grandprix(s, gg[g])
			g += 1
			s.write('\n')
		write_tournament(s, p)
		s.write('\n')

	if pokal:
		write_pokal(s, pokal, pp[0].year)

	return s.getvalue()

def find_bs(aa):
	regex = re.compile(r'(blitz|schnell)-(%02d)-(\d+)(-games.*?)?(\.csv)' % aa.year)
	nn = os.listdir(aa.tdir)
	nn = (regex.match(n) for n in nn)
	nn = (os.path.join(aa.tdir, n.group(0)) for n in nn if n)
	return sorted(Path.parse(n) for n in nn)

def find_gp(aa):
	nn = glob.glob(os.path.join(aa.tdir, "gp-%02d-??.csv" % aa.year))
	return sorted(Path.parse(n) for n in nn)

def find_po(aa):
	nn = glob.glob(os.path.join(aa.pdir, "pokal-%02d.html" % aa.year))
	return os.path.normpath(nn[0]) if nn else None

def find_years(aa):
	regex = re.compile(r'(blitz|schnell)-(\d+)-(\d+)(-games.*?)?(\.csv)')
	nn = os.listdir(aa.tdir)
	nn = (regex.match(n) for n in nn)
	nn = (n for n in nn if n)
	yy = set()
	for n in nn:
		y = int(n.group(2))
		yy.add(y)
	return yy

if __name__ == "__main__":
	parser, aa = parse_args()
	#~ print(aa)

	if aa.list:
		if aa.year:
			pp = []
			pp.extend(p.path + ".csv" for p in find_bs(aa))
			pp.extend(p.path + ".csv" for p in find_gp(aa))
			po = find_po(aa)
			if po: pp.append(po)
			print(pp)
		else:
			print(" ".join(map(str, find_years(aa))))
		exit()

	pp = find_bs(aa)
	#~ for p in pp: print(p, p.path)

	gg = find_gp(aa)
	#~ for p in gg: print(p, p.path)

	po = find_po(aa)
	#~ print(po)

	out = template % (aa.year, blah(pp, gg, po))
	
	if not aa.ofile:
		print(out)
	else:
		with open(aa.ofile, "w", encoding="utf8") as file:
			file.write(out)
