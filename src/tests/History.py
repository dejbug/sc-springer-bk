#~ import sys, os.path
#~ sys.path.insert(1, os.path.dirname(__file__) + "/dejlib.zip")
#~ from include import include
#~ abs = include("src", "tools.gp")
#~ print(abs)
#~ exit()

import init

import gp

from lib.tool import ftos
from lib.History import History

filepaths = [
	init.path(__file__, "src", "/tables/blitz-23-01.csv"),
	init.path(__file__, "src", "/tables/schnell-23-02.csv"),
	init.path(__file__, "src", "/tables/blitz-23-03.csv"),
	init.path(__file__, "src", "/tables/schnell-23-04.csv"),
	init.path(__file__, "src", "/tables/blitz-23-05.csv"),
]

names, synonyms = gp.load_names_from_files(filepaths)
#~ for name in names: print(name)

history = History(names, synonyms)
#~ history.sort_by_ptotals()	#~ history.sort_by_pscores()
history.sort_by_rtotals()	#~ history.sort_by_rscores()
for player in history.players:
	print(player.name)
	for score in player.scores:
		print("%4s | %4s | %4s   %s" % (ftos(score.pscore), ftos(score.rscore), ftos(score.rank), score.fid.file.path))
