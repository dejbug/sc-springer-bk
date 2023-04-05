from sys import argv
from os import path
from re import compile
from datetime import datetime

def getarg():
	if len(argv) >= 2:
		return path.abspath(argv[1])
	root = path.dirname(path.dirname(path.abspath(__file__)))
	contents = path.join(root, "content")
	return path.join(contents, "news.txt")

def iter(path):
	news = {}
	for key, item in parsefile(path):
		if key == 0 and news:
			yield news
			news = {}
		if key in range(3):
			news.update(parseitem(key, item))
	if news:
		yield news

def parsefile(path):
	pat = [
		compile(r'^\s*(\d\d?)\.(\d\d?).(\d{2,4})\s*.\s*(\d\d?):(\d\d?)'),
		compile(r'(.+)'),
		compile(r'\s*(?:"(.+?)")?(?:\s*(.+))?'),
	]

	state = 0
	with open(arg) as file:
		for line in file:
			line = line.strip()
			if not line: state = 0; continue
			if not state in range(3): break
			x = pat[state].match(line)
			if not x: state = 3; continue
			yield state, x.groups()
			state += 1

def parseitem(key, item):
	if key == 0: return { "time": parsetime(item) }
	if key == 1: return { "text": item[0] }
	if key == 2: return { "link": item[0], "url": item[1] }

def parsetime(seq):
	t = list(int(e) for e in seq)
	if t[2] < 2000: t[2] += 2000
	return datetime(year=t[2], month=t[1], day=t[0], hour=t[3], minute=t[4])

def printnews(news):
	print("time: |", news["time"].strftime("%Y-%m-%d / %H:%M"))
	print("text: |", news["text"])
	if "link" in news:
		print("link: |", news["link"], end="")
		if "url" in news:
			print(" => ", news["url"], end="")
		print()
	print()

if __name__ == "__main__":
	arg = getarg()
	assert path.isfile(arg)
	for news in iter(arg):
		printnews(news)
