import re, sys, codecs
import urllib.request

encoding = 'utf8'

tabelle1 = 'https://www.schachklub-bad-homburg.de/LigaOrakel/LigaOrakel.php?staffel=BEZ6_BZK&team=SC+Springer+Bad+K%F6nig+I&tabformat=L'

tabelle2 = 'https://www.schachklub-bad-homburg.de/LigaOrakel/LigaOrakel.php?staffel=BEZ6_KKB&team=SC+Springer+Bad+K%F6nig+II&tabformat=L'


def stripHtmlTags(text):
	return re.sub('</?.+?>', '|', text).strip()


def translate(text):
	if text == '&nbsp;':
		return '='
	elif text.startswith('||'):
		return '-'
	elif text.startswith('|'):
		return text.strip('|')
	else:
		x = re.match('(\d+)(?:,(\d+))?\.?', text)
		if x:
			if x.group(2):
				return "%d.%d" % (int(x.group(1)), int(x.group(2)))
			elif x.group(1):
				return "%d" % (int(x.group(1)), )
	return text


def fetchTable(url, filename):
	with urllib.request.urlopen(url) as page:
		assert page.status == 200
		with open(filename, 'wb') as file:
			file.write(page.read())


def parseTable(filename):
	with codecs.open(filename, 'rb', 'latin1') as file:
		text = file.read()
	x = re.search('(<td>Platz</td>)', text)
	text = text[x.start():]
	for x in re.finditer('<(td)[^>]*>(.+?)</td>|<(tr)', text):
		if x.group(1):
			yield ("TD", translate(stripHtmlTags(x.group(2))))
		elif x.group(3):
			yield ("TR", None)


def printTable(filename, file=sys.stdout):
	line = ""
	for k,v in parseTable(filename):
		if k == "TR":
			print(line.lstrip(','), file=file)
			line = ""
		elif k == "TD":
			line += ",\"%s\"" % v


if __name__ == '__main__':
	fetchTable(tabelle1, 'tabelle1.html')
	fetchTable(tabelle2, 'tabelle2.html')
	
	with codecs.open('tabelle1.csv', 'w', encoding) as file:
		printTable("tabelle1.html", file)
	with codecs.open('tabelle2.csv', 'w', encoding) as file:
		printTable("tabelle2.html", file)
