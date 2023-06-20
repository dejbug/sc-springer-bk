class History:

	class Score:
		def __init__(self, fid = None, pscore = 0, rscore = 0, rank = 0):
			self.fid = fid
			self.pscore = pscore	# point scores
			self.rscore = rscore	# ranking-based scores
			self.rank = rank

	class Player:
		def __init__(self):
			self.sid = None
			self.name = None
			self.names = []
			self.scores = []

		def ptotals(self, min_length = 3):
			for x in range(min_length, len(self.scores) + 1):
				yield sum(s.pscore for s in self.scores[:x])

		def rtotals(self, min_length = 3):
			for x in range(min_length, len(self.scores) + 1):
				yield sum(s.rscore for s in self.scores[:x])

		def sort_by_pscore(self, reverse = None):
			if reverse is None: reverse = True
			self.scores = sorted(self.scores,
				key=lambda score: score.pscore, reverse=reverse)

		def sort_by_rscore(self, reverse = None):
			if reverse is None: reverse = True
			self.scores = sorted(self.scores,
				key=lambda score: score.rscore, reverse=reverse)

		def sort_by_rank(self, reverse = None):
			if reverse is None: reverse = False
			self.scores = sorted(self.scores,
				key=lambda score: score.rank, reverse=not reverse)


	def __init__(self, names, synonyms, contiguous = False):
		self.players = []
		self.contiguous = contiguous
		self.load(names, synonyms)

	def load(self, names, synonyms):
		self.players = []
		groups = synonyms.groups(names)
		for sid, names in groups.items():
			player = self.Player()
			player.sid = sid
			player.name = synonyms.text(sid)
			player.names = names
			for name in names:
				file = name.fid.file
				rid = name.fid.id - 1

				pscore = file.pscore(rid)
				rscore = file.rscore(rid, contiguous = self.contiguous)
				rank = file.rank(rid, contiguous = self.contiguous)

				if player.name == "Messer":
					print(player.name, file.path, "| RID", rid, "| PSCORE", pscore, "| RANK", rank, "| RSCORE", rscore)

				score = self.Score(name.fid, pscore, rscore, rank)
				player.scores.append(score)
			player.sort_by_rscore()
			self.players.append(player)

	@property
	def max_scores_count(self):
		x = 0
		for player in self.players:
			x = max(x, len(player.scores))
		return x

	def sort_by_pscores(self, descending = True):
		for player in self.players:
			player.sort_by_pscore(reverse = descending)
		self.players = sorted(self.players,
			key=lambda p: [s.pscore for s in p.scores], reverse = descending)

	def sort_by_ptotals(self, min_length = 3, descending = True):
		for player in self.players:
			player.sort_by_pscore(reverse = descending)
		self.players = sorted(self.players,
			key=lambda p: tuple(p.ptotals(min_length)), reverse = descending)

	def sort_by_rscores(self, descending = True):
		for player in self.players:
			player.sort_by_rscore(reverse = descending)
		self.players = sorted(self.players,
			key=lambda p: [s.rscore for s in p.scores], reverse = descending)

	def sort_by_rtotals(self, descending = True):
		for player in self.players:
			player.sort_by_rscore(reverse = descending)
		self.players = sorted(self.players,
			key=lambda p: tuple(p.rtotals()), reverse = descending)
