import sys, re
from datetime import datetime

import tools

def iter(ipath):
	news = {}
	for block in iter_blocks(ipath):
		yield parse_block(block)

def iter_blocks(ipath):
	block = []
	with open(ipath, encoding="utf8") as file:
		for line in file:
			line = line.strip()
			if line:
				block.append(line)
			else:
				if block: yield block
				block = []
	if block: yield block

def parse_block(block):
	news = {}

	m = re.match(r'^\s*(\d\d?)\.(\d\d?).(\d{2,4})\s*(?:.\s*(\d\d?):(\d\d?))?', block[0])
	if m: news["time"] = parsetime(m.groups())

	m = re.match(r'^\s*"(.+?)"(?:\s*=>\s*(.+))?', block[-1])
	if m:
		news["link"] = m.group(1)
		news["url"] = m.group(2)

	news["lines"] = [line.strip() for line in block[1:(-1 if "link" in news else None)]]
	news["text"] = " ".join(news["lines"])

	return news

def parsetime(seq):
	t = list(int(e) for e in seq if e is not None)
	if t[2] < 2000: t[2] += 2000
	assert len(t) in (3,5)
	if len(t) == 3:
		return datetime(year=t[2], month=t[1], day=t[0], hour=0, minute=0)
	else:
		return datetime(year=t[2], month=t[1], day=t[0], hour=t[3], minute=t[4])

def germandate(t):
	months = ["", "Januar", "Februar", "März", "April", "Mai", "Juni",
		"Juli", "August", "September", "Oktober", "November", "Dezember"]
	s = "%d. %s %4d" % (t.day, months[t.month], t.year)
	if t.hour: s += " / %02d:%02d" % (t.hour, t.minute)
	return s

def printnews(ipath):
	for news in iter(ipath):
		#~ print("time: |", news["time"].strftime("%Y-%m-%d / %H:%M"))
		print("time: |", germandate(news["time"]))
		print("text: |", news["text"])
		if "link" in news:
			print("link: |", news["link"], end="")
			if "url" in news:
				print(" => ", news["url"], end="")
			print()
		print()

def printhtml(ipath, ofile=sys.stdout, prefix=""):
	last_date = None
	for news in iter(ipath):
		cls = "news"
		#~ if len(news["text"]) < 200:
			#~ cls += " card"
		if len(news["lines"]) > 1:
			text = "\t<p>" + "</p>\n\t<p>".join(news["lines"]) + "</p>\n"
		else:
			cls += " card"
			text = "\t<p>%s</p>\n" % news["text"]
		ofile.write(prefix + '<article class="%s">\n' % cls)
		ofile.write(prefix + '\t<time datetime="%s">%s</time>\n' % (
			news["time"].strftime("%Y-%m-%dT%H:%M:00"),
			# news["time"].strftime("%Y-%m-%d / %H:%M")
			germandate(news["time"])
		))
		ofile.write(prefix + text)
		if "link" in news:
			ofile.write(prefix + '\t<a href="%s">%s</a>\n' % (
				news["url"] or "",
				news["link"]
			))
		ofile.write(prefix + '</article>\n')

if __name__ == "__main__":
	p = tools.argParser()
	tools.argParserIOF(p, idef=tools.root("content", "news.txt"))
	p.add("--mode", choices=["list","html"], default="list")
	p.add("--prefix", default="")
	p, aa = p.parse()
	#~ print(aa); exit()

	if aa.mode == "list":
		printnews(aa.ipath)
	elif aa.mode == "html":
		with tools.oopen(aa.opath, aa.force) as ofile:
			printhtml(aa.ipath, ofile, aa.prefix)
