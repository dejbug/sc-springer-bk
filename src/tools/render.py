import sys, re, io, os
import tools
import traceback, pprint

class Error(Exception): pass
class ProcessError(Exception): pass

def main(argv=sys.argv):
	p = tools.ArgParser()
	p.add("ipath", "PATH")
	p.add("args", "KEY=VAL", nargs="*")
	p.add("-o", "--opath", "PATH", default=None)
	p.add("-e", "--epath", "PATH", default=tools.root("dist", "render.log"))
	p.add("-d", action="store_true")
	aa = p.parse(argv)
	#~ if aa.epath is None: aa.epath = aa.ipath + ".log" # tools.noext(aa.ipath) + ".log"
	aa.args = {k : v for k, v in (s.split("=") for s in aa.args if "=" in s)}
	generate(p, aa)

def generate(p, aa):
	#~ splitter = re.compile(r'\{\{\s*(.+?)\s*\}\}')
	#~ splitter = re.compile(r'(?P<pre>[ \t]*)(?:\{\{\s*(?P<cmd>.+?)\s*\}\})(?P<post>\r\n|\r|\n)')
	splitter = re.compile(r'((?:^[ \t]+)?)\{\{\s*(.+?)\s*\}\}', re.MULTILINE)
	text = open(aa.ipath, encoding="utf-8").read()
	with tools.oopen(aa.opath, force=True) as ofile:
		for key, chunk in tools.rsplit(text, splitter):
			ofile.write(process(p, aa, chunk) if key else chunk)

def log(p, aa, e):
	if aa.epath:
		ferr = open(aa.epath, "a", encoding="utf-8")
		ferr.write("-" * 101 + "\n")
		#~ pprint.pprint(aa.__dict__, stream=ferr, sort_dicts=False)
		pprint.pprint(aa.__dict__, stream=ferr)
		ferr.write("\n")
		traceback.print_exception(e, file=ferr)

def process(p, aa, groups):
	prefix, cmd = groups
	#~ print("|%s| |%s| (%d)" % (cmd, prefix, len(prefix)))
	try: cmd = cmd.format(p=p, aa=aa, prefix=prefix, **aa.args)
	except KeyError as e:
		log(p, aa, e)
		return ""
	out, err = tools.shell(cmd, "utf-8")
	if err: raise ProcessError(err)
	return out

if __name__ == "__main__":
	main()
