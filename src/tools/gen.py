import sys, re

import tools, news

re_field = re.compile(r'((?:[ \t]*)(?:\{\{.+\}\}))')
re_key = re.compile(r'([ \t]*)\{\{(.+)\}\}')

#~ def iter(ipath):
	#~ with open(ipath) as file:
		#~ for x in re_field.finditer(file.read()):
			#~ yield x

def parsekey(key, env={}):
	x = re_key.match(key)
	if not x: return (None, None)
	prefix, key = x.groups()
	env.update({"prefix":'"%s"' % prefix})
	key = key.format(**env)
	return prefix, key

def callback(ofile, chunk, env={}):
	prefix, key = parsekey(chunk, env)
	out, err = tools.shell(key)
	otext = out.decode("utf8")
	#~ print(otext)
	ofile.write(otext)

def generate(ipath, opath, force, callback=callback):
	text = open(ipath, encoding="utf-8").read()
	chunks = re_field.split(text)
	env = {
		"ipath": ipath,
		"opath": opath,
		"force": force,
	}
	state = 0
	with tools.oopen(opath, force) as ofile:
		for chunk in chunks:
			ofile.write(chunk) if state == 0 else callback(ofile, chunk, env)
			state = (state + 1) % 2

def main(argv=sys.argv):
	p = tools.argParser()
	tools.argParserIOF(p)
	p, aa = p.parse(argv)
	#~ print(aa); exit()
	generate(aa.ipath, aa.opath, aa.force)

if __name__ == "__main__":
	main()
