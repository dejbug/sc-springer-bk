import os, re

import init
import tools.lib.File

for n in os.listdir("tables"):
	p = "tables/" + n
	file = tools.lib.File.File(p)
	t = file.type
	h = re.sub(r"\s*", "", file.header)
	print("%35s | %12s | %s" % (n, t, h))
