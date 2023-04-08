import sys, re
import tools

class Error(Exception): pass
class ProcessError(Exception): pass

def main(argv=sys.argv):
	p = tools.ArgParser()
	p.add("ipath", "PATH")
	p.add("-o", "--opath", "PATH", default="out.min.css")
	p.add("-d", action="store_true")
	aa = p.parse(argv)
	generate(p, aa)

def generate(p, aa):
	#~ splitter = re.compile(r'\{\{\s*(.+?)\s*\}\}')
	#~ splitter = re.compile(r'(?P<pre>[ \t]*)(?:\{\{\s*(?P<cmd>.+?)\s*\}\})(?P<post>\r\n|\r|\n)')
	splitter = re.compile(r'((?:^[ \t]+)?)\{\{\s*(.+?)\s*\}\}', re.MULTILINE)
	text = open(aa.ipath, encoding="utf-8").read()
	with tools.oopen(aa.opath, force=True) as ofile:
		for key, chunk in tools.rsplit(text, splitter):
			ofile.write(process(p, aa, chunk) if key else chunk)

def process(p, aa, groups):
	prefix, cmd = groups
	#~ print("|%s| |%s| (%d)" % (cmd, prefix, len(prefix)))
	cmd = cmd.format(p=p, aa=aa, prefix=prefix)
	out, err = tools.shell(cmd, "utf-8")
	if err: raise ProcessError(err)
	return out

if __name__ == "__main__":
	main()
