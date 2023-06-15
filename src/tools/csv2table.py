import argparse
import csv
import re
import sys

import tables

def get_max_score_lengths(rr):
	# FIXME: We want to run this only on the scores!
	# TODO: Write a data class that is smart enough to grokk the header.
	ilength = 0
	flength = 0
	for row in rr[1:]:
		for cell in row[2:]:
			try: score = float(cell)
			except: continue
			#~ i, f = str(score).strip("0").split(".")
			i, f = str(score).split(".")
			ilength = max(ilength, len(i))
			flength = max(flength, len(f))
	return ilength, flength


def normalize_score(c, ilength, flength, fractions=True, padding=False):
	# TODO: If the len of all the integers is 1 and all the fractions have the
	#	integer part equal 0, then we don't need padding.
	#	See: ../blitz-23-01.html

	fsep = ""

	#~ c = c.strip()
	#~ m = re.match(r"(?:(\d*\.(?:5|25))0*|(\d+))", c)
	#~ if not m: return c
	#~ if m.group(1):
		#~ i, f = m.group(1).split(".")
	#~ else:
		#~ i = m.group(2)
		#~ f = "0"

	try: c = str(float(c))
	except: return c

	i, f = c.split(".")
	#~ if len(cc) == 1: i, f = cc[0], "0"
	#~ elif len(cc) == 2: i, f = cc

	span = lambda s: '<span class="padding">%s</span>' % s

	#~ pad = lambda count: "&nbsp;" * count
	#~ pad = lambda count, dot = False: span(("." if dot else "") + "0" * count) if count else ""

	lpad = lambda count: '<span style="padding-left: %dex"></span>' % count if count else ""
	rpad = lambda count: '<span style="padding-right: %dex"></span>' % count if count else ""

	frac = lambda f: "&frac12;" if f == "5" else "&frac14;" if f == "25" else ""

	if padding:

		if i == "0" and f != "0":
			idiff = ilength
			if fractions:
				#~ c = pad(idiff) + " " + frac(f)
				c = lpad(idiff) + fsep + frac(f)
			else:
				fdiff = max(0, flength - len(f))
				#~ c = pad(idiff) + "." + f + pad(fdiff)
				c = lpad(idiff) + "." + f + rpad(fdiff)
		elif i != "0" and f == "0":
			idiff = max(0, ilength - len(i))
			fdiff = flength
			#~ c = pad(idiff) + i + pad(fdiff, True)
			c = lpad(idiff) + i + rpad(fdiff + 1)
		elif i == "0" and f == "0":
			c = lpad(ilength - 1) + "0" + rpad(flength)
		else:
			if fractions:
				idiff = max(0, ilength - len(i))
				#~ c = pad(idiff) + i + " " + frac(f)
				c = lpad(idiff) + i + fsep + frac(f)
			else:
				idiff = max(0, ilength - len(i))
				fdiff = max(0, flength - len(f))
				#~ c = pad(idiff) + i + "." + f + pad(fdiff)
				c = lpad(idiff) + i + "." + f + rpad(fdiff)

	elif fractions:

		if f == "0": c = i
		elif i == "0": c = frac(f)
		else: c = i + fsep + frac(f)

	return c


def isscorecol(rr, i):
	cc = len(rr[0])
	h = ",".join(rr[0])
	t = tables.determine_csv_type(h)
	if not t: return False
	if t.endswith("#NP"):
		return i >= 2 and i < cc
	if t.endswith("#NPP"):
		return i >= 2 and i < cc - 1
	if t.endswith("#N") or t.endswith("#X") or t.endswith("#NGSRVPBS"):
		return i >= 2 and i < cc
	return False


def csv2table(inpath, o=sys.stdout, fractions=True, padding=False):
	try:
		people, players, crosstable = tables.render(inpath)
		rr = crosstable
	except:
		t = tables.determine_csv_type(inpath)
		if t and t.startswith("t/"):
			file = open(inpath, "r", encoding="utf-8")
			lines = (tables.collapse_tabs(line.strip()) for line in file)
			reader = csv.reader(lines)
		else:
			reader = csv.reader(open(inpath, "r", encoding="utf-8"))
		rr = [r for r in reader]

	ilength, flength = get_max_score_lengths(rr)

	o.write("<table>\n\t<thead>\n")
	#~ rr = [r for r in csv.reader(open(inpath, "r", encoding="utf-8"))]
	o.write("\t\t<tr>\n")
	for c in rr[0]:
		c = c.strip()
		o.write("\t\t\t<th>%s</th>\n" % c)
	o.write("\t\t</tr>\n\t</thead>\n\t<tbody>")
	for r in rr[1:]:
		o.write("\t\t<tr>\n")
		for i, c in enumerate(r):
			c = c.strip()
			attr = ""
			if c == "-":
				attr = ' class="missing"'
			elif c == "=":
				attr = ' class="identity"'
			#~ elif i >= 2:
			elif isscorecol(rr, i):
				# FIXME: A score column can only be 1, 0, or 0.5.
				#	So we can use fractions and center the text.
				#	There are other numeric cell types (e.g. totals)
				#	which can have multi-digit floats. These will
				#	have to be padded, and only these.
				#	See: ../schnell-23-06.html
				attr = ' class="score"'
				m = re.match(r"([.0-9]+)(?:/([.0-9]+))?", c)
				if m:
					a, b = m.groups()
					c = normalize_score(a, ilength, flength, fractions, padding)
					if b:
						c += "<br>"
						c += normalize_score(b, ilength, flength, fractions, padding)
			o.write("\t\t\t<td%s>%s</td>\n" % (attr, c))
		o.write("\t\t</tr>\n")
	o.write("\t</tbody>\n</table>\n")


if __name__ == "__main__":
	p = argparse.ArgumentParser()
	p.add_argument("file")
	p.add_argument("--no-fractions", action="store_true")
	#~ p.add_argument("--no-padding", action="store_true")
	p.add_argument("--padding", action="store_true")
	aa = p.parse_args(sys.argv[1:])
	#~ print(aa)
	csv2table(aa.file,
		fractions=not aa.no_fractions,
		#~ padding=not aa.no_padding
		padding=aa.padding
	)
