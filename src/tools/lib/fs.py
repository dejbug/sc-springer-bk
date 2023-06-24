import collections, os, re, sys

import __main__

Signature = collections.namedtuple("Signature", "type format istabbed istournament hasmatches hascolors hasrounds needscooking")

def root(top, __file=__main__.__file__):
	"""
	>>> root("user", __file="/home/user/folder/subfolder/script.py")
	'/home/user/'
	"""
	top = "/%s/" % top
	i = __file.rfind(top)
	if i < 0: return
	i += len(top)
	root = __file[:i]
	tail = __file[i:]
	return root

def path(top, rel, __file=__main__.__file__):
	"""
	>>> path("user", "run.py", __file="/home/user/folder1/subfolder/script.py")
	'/home/user/run.py'
	"""
	if not rel.startswith("/"): rel = "/" + rel
	r = root(top, __file)
	if r: return os.path.abspath(r + rel)

def list(top, rel=None, __file=__main__.__file__):
	cwd = path(top, rel, __file)
	for t,dd,nn in os.walk(cwd):
		for n in nn:
			yield os.path.join(t, n)

def lines(fp):
	with open(fp, "r", encoding="utf8") as file:
		return [line.strip() for line in file]

def type(text):
	"""
	>>> signature("Runde,Weiss,Schwarz,Ergebnis")
	'RWSE'
	>>> signature("Runde,\\tWeiss,	Schwarz,	Ergebnis")
	'RWSE'
	>>> signature("Runde\\tWeiss\\t\\tSchwarz\\tErgebnis")
	't/RWSE'
	>>> signature("#,Name,1,2,3,4,5,Punkte")
	'#NP'
	>>> signature("#\\tName\\t1\\t2\\t3\\t4\\t5\\tPunkte")
	't/#NP'
	>>> signature("#,Name,G,S,R,V,Punkte,Buchh,Soberg")
	'#NGSRVPBS'
	>>> signature("#\\tName\\tG\\tS\\tR\\tV\\tPunkte\\tBuchh\\tSoberg")
	't/#NGSRVPBS'
	>>> signature("xyz")
	"""
	text = text.strip()

	if re.match("^#,\s*Name(,\s*\d+)+,\s*Punkte,\s*Platz$", text):
		return "#NPP"
	elif re.match("^#\t+Name(\t+\d+)+\t+Punkte\t+Platz$", text):
		return "t/#NPP"
	if re.match("^#,\s*Name(,\s*\d+)+,\s*Punkte$", text):
		return "#NP"
	elif re.match("^#\t+Name(\t+\d+)+\t+Punkte$", text):
		return "t/#NP"
	elif re.match("^#,\s*Name(,\s*\d+)+$", text):
		return "#N"
	elif re.match("^#\t+Name(\t+\d+)+$", text):
		return "t/#N"
	elif re.match("^#,\s*x\s*=\s*(,\s*\d+)+$", text):
		return "#X"
	elif re.match("^#\t+x\s*=\s*(\t+\d+)+$", text):
		return "t/#X"
	elif re.match("^Runde,\s*Weiss,\s*Schwarz,\s*Ergebnis$", text):
		return "RWSE"
	elif re.match("^Runde\t+Weiss\t+Schwarz\t+Ergebnis$", text):
		return "t/RWSE"
	elif re.match("^#,\s*Name,\s*G,\s*S,\s*R,\s*V,\s*Punkte,\s*Buchh,\s*Soberg$", text):
		return "#NGSRVPBS"
	elif re.match("^#\t+Name\t+G\t+S\t+R\t+V\t+Punkte\t+Buchh\t+Soberg$", text):
		return "t/#NGSRVPBS"
	elif re.match("^#,\s*Name,\s*Punkte(,\s*R\d+)+$", text):
		return "#NPR"
	elif re.match("^#\t+Name\t+Punkte(\t+R\d+)+$", text):
		return "t/#NPR"
	return ""

def signature(lines):
	if not lines:
		return Signature(None, "", False, False, False, False, False, False)

	t = type(lines[0])
	if not t:
		return Signature(t, "", False, False, False, False, False, False)

	tabbed = t.startswith("t/")
	format = t.split("/")[-1]

	if format == "#NPR" or format == "RWSE":
		istournament = True
		hasmatches = True
		hasrounds = True
		hascolors = True
	elif format == "#NP":
		istournament = True
		hasmatches = True
		hasrounds = False
		if len(lines) < 2: hascolors = False
		else: hascolors = lines[1].find("*") >= 0
	else:
		istournament = format == "#NGSRVPBS"
		hasmatches = False
		hasrounds = False
		hascolors = False

	needscooking = format == "RWSE"

	return Signature(t, format, tabbed, istournament, hasmatches, hascolors, hasrounds, needscooking)
