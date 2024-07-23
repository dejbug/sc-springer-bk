import sys, re

if len(sys.argv) >= 4:

	a = sys.argv[1]
	b = sys.argv[2]
	c = sys.argv[3]

	for word in c.split():
			word = re.sub(a, b, word)
			print(word)
