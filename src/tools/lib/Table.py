from .File import File

class Table:
	def __init__(self, filler=None):
		self.filler = filler
		self.rows = []

	def set(self, row, col, data):
		self.ensure_row_exits(row)
		self.ensure_col_exists(col)
		self.rows[row][col] = data

	def ensure_row_exits(self, row):
		colcount = self.colcount
		need = row + 1 - len(self.rows)
		if need > 0:
			for _ in range(need):
				self.rows.append([self.filler] * colcount)

	def ensure_col_exists(self, col):
		colcount = len(self.rows[0]) if self.rows else 0
		need = col + 1 - colcount
		if need > 0:
			for row in self.rows:
				row.extend([self.filler] * need)

	@property
	def rowcount(self):
		return len(self.rows)

	@property
	def colcount(self):
		return len(self.rows[0]) if self.rows else 0

	def __str__(self):
		s = io.StringIO()
		s.write("Table %d %d\n" % (self.rowcount, self.colcount))
		for i, row in enumerate(self.rows):
			s.write("%d:" % i)
			for cell in row:
				s.write(" %s" % cell)
			s.write("\n")
		return s.getvalue()
