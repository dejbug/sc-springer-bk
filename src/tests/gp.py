import init

from tools import gp

from lib.CsvTablePath import CsvTablePath
from lib.History import History

#~ indexFilePath = init.path(__file__, "src", "tables/gp-22-08.csv")
indexFilePath = init.path(__file__, "src", "tables/gp-23-01.csv")
#~ print(indexFilePath)

filePaths = CsvTablePath.fromIndexFile(indexFilePath)
#~ for p in filePaths: print(p)

filePaths = [p.path for p in filePaths]
names, synonyms = gp.load_names_from_files(filePaths)

#~ for nn in synonyms.synonyms:
	#~ for n in nn:
		#~ print(n.text, end=", ")
	#~ print()

#~ for n in names: print(n)

his = History(names, synonyms, contiguous = False)
