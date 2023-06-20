def ftos(f):
	s = str(f)
	s = s.rstrip("0")
	s = s.rstrip(".")
	return s

def upfind(p):
	# TODO: Test this.
	cwd = os.getcwd()
	last = None
	while len(cwd) != last:
		path = os.path.join(cwd, p)
		#~ print(path, file=sys.stderr)
		if os.path.isfile(path):
			return path
		last = len(cwd)
		cwd = os.path.dirname(cwd)

