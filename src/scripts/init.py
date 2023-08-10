import sys, os.path
root = os.path.dirname(__file__)
path = os.path.abspath(root + "/../tools/")
sys.path.insert(1, path)
path = os.path.abspath(root + "/../")
sys.path.insert(1, path)

def root(path, part):
	"""
	>>> root("/home/user/folder/subfolder/script.py", "user")
	'/home/user/'
	"""
	part = "/%s/" % part
	i = path.rfind(part)
	if i < 0: return
	i += len(part)
	root = path[:i]
	tail = path[i:]
	return root

def path(path, part, rel):
	"""
	>>> path("/home/user/folder1/subfolder/script.py", "user", "run.py")
	'/home/user/run.py'
	"""
	if not rel.startswith("/"): rel = "/" + rel
	r = root(path, part)
	if r: return os.path.abspath(r + rel)

def listdir(path):
	for t,dd,nn in os.walk(path):
		for n in nn:
			yield os.path.join(t, n)
