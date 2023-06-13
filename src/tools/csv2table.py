import sys
import csv

import tables

def csv2table(inpath, o=sys.stdout):
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

	o.write("<table>\n\t<thead>\n")
	#~ rr = [r for r in csv.reader(open(inpath, "r", encoding="utf-8"))]
	o.write("\t\t<tr>\n")
	for c in rr[0]:
		o.write("\t\t\t<th>%s</th>\n" % c)
	o.write("\t\t</tr>\n\t</thead>\n\t<tbody>")
	for r in rr[1:]:
		o.write("\t\t<tr>\n")
		for c in r:
			# if c == "0.5": c = "&frac12;"
			# elif c.endswith(".5"): c = c.replace(".5", " &frac12;")
			c = c.replace("0.5", "&frac12;")
			c = c.replace("0.25", "&frac14;")
			c = c.replace(".5", " &frac12;")
			c = c.replace(".25", " &frac14;")
			c = c.replace("/", "<br>")
			a = ' class="identity"' if c == "=" else ""
			o.write("\t\t\t<td%s>%s</td>\n" % (a, c))
		o.write("\t\t</tr>\n")
	o.write("\t</tbody>\n</table>\n")


if __name__ == "__main__":
	if len(sys.argv) < 2:
		exit(1)
	csv2table(sys.argv[1])
