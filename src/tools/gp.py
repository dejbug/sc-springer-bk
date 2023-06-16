import sys
import math

from lib.File import File
from lib.Names import Name, Synonyms, DEFAULT_SYNONYMS


def load_names_from_files(filepaths):
	names = []

	for filepath in filepaths:
		file = File(filepath)
		#~ print(filepath, file.type, len(file.rows))
		names.extend(Name.load(file))

	synonyms = Synonyms(DEFAULT_SYNONYMS)
	synonyms.classify_all(names)
	#~ for name in synonyms.unclassified(names): print(name)

	return names, synonyms


def score(name):
	t = name.fid.file.type
	rid = name.fid.id - 1	# header is not included in the rows
	cols = name.fid.file.rows[rid]
	if t.endswith("#NP"): cid = -1
	elif t.endswith("#NGSRVPBS"): cid = -3
	else: raise Exception("score column not found: unknown table")

	# FIXME: The scores for GP are not the tournament scores but
	#	are based on the rank. Solo first gets 10, shared first
	#	get 9 each. Second gets 8, third gets 7, etc.
	topscore = name.fid.file.rows[0][cid]
	score = name.fid.file.rows[rid][cid]
	if rid != 0 and score == topscore: return 9.0
	elif rid == 0: return 10.0
	elif rid == 1: return 8.0
	elif rid == 2: return 7.0
	elif rid == 3: return 6.0
	elif rid == 4: return 5.0
	elif rid == 5: return 4.0
	elif rid == 6: return 3.0
	elif rid == 7: return 2.0
	elif rid == 8: return 1.0
	else: return 0.0

	return float(cols[cid])


def load_history(names, synonyms):
	history = []
	groups = synonyms.groups(names)
	for sid, names in groups.items():
		scores = []
		for name in names:
			scores.append(score(name))
		scores = sorted(scores, reverse=True)
		history.append([synonyms.text(sid), scores])
	extend_scores(history)
	extend_sums(history)
	return history


def print_names(names, synonyms):
	for name in names:
		sid = synonyms.classify(name.text)
		print(" %-16s " % synonyms.text(sid), name)


def print_groups(names, synonyms):
	groups = synonyms.groups(names)
	for sid, names in groups.items():
		print(" (aka) ".join(name.text for name in names))


def print_history(history, x = 3):
	history = sorted(history, key=lambda total: sum(total[1][:x]), reverse=True)
	for name, scores, totals in history:
		print("%20s" % name, "%7.2f  " % sum(scores[:x]), scores[:x], scores[x:])


def get_column_sizes(history):
	max_scores_count = 0
	max_score_ilength = 0
	max_score_flength = 0
	max_total_ilength = 0
	max_total_flength = 0
	max_name_length = 0
	max_index_length = math.ceil(math.log(len(history)) / math.log(10))
	for entry in history:
		name = entry[0]
		scores = entry[1]
		max_scores_count = max(max_scores_count, len(scores))
		for score in scores:
			s, m = str(score).split(".")
			max_score_ilength = max(max_score_ilength, len(s))
			max_score_flength = max(max_score_flength, len(m))
		if len(entry) > 2:
			totals = entry[2]
			for score in totals:
				s, m = str(score).split(".")
				max_total_ilength = max(max_total_ilength, len(s))
				max_total_flength = max(max_total_flength, len(m))
		max_name_length = max(max_name_length, len(str(name)))

	return {
		"max_scores_count": max_scores_count,
		"max_score_ilength": max_score_ilength,
		"max_score_flength": max_score_flength,
		"max_score_length": max_score_ilength + 1 + max_score_flength,
		"max_total_ilength": max_total_ilength,
		"max_total_flength": max_total_flength,
		"max_total_length": max_total_ilength + 1 + max_total_flength,
		"max_name_length": max_name_length,
		"max_index_length": max_index_length }


def extend_scores(history):
	sizes = get_column_sizes(history)
	for _, scores in history:
		diff = sizes["max_scores_count"] - len(scores)
		scores.extend([0.0] * diff)
		#~ scores = sorted(scores, reverse=True) # scores already sorted


def sum_scores(scores, min_length = 3):
	for x in range(min_length, len(scores) + 1):
		yield sum(scores[:x])


def extend_sums(history, min_length = 3):
	for entry in history:
		entry.append(list(sum_scores(entry[1], min_length)))


def print_full_history(history):
	history = sort_by_tournament_results(history)
	sizes = get_column_sizes(history)

	sfcol = " %%%d.%df " % (
		sizes["max_score_ilength"] + 1 + sizes["max_score_flength"],
		sizes["max_score_flength"])

	sscol = " %%%ds " % (
		sizes["max_score_ilength"] + 1 + sizes["max_score_flength"])

	tfcol = " %%%d.%df " % (
		sizes["max_total_ilength"] + 1 + sizes["max_total_flength"],
		sizes["max_total_flength"])

	tccol = (
		" " * (sizes["max_total_ilength"] + 1) + "%s" +
		" " * (sizes["max_total_flength"] + 1))

	for name, scores, totals in history:
		print((" %%-%ds |" % sizes["max_name_length"]) % name, end="")
		for score in scores:
			print(sfcol % score if score else sscol % "", end="|")
		for x in range(1, sizes["max_scores_count"] + 1):
			if scores[x - 1]:
				total = sum(scores[:x])
				print(tfcol % total, end=" ")
			else:
				print(tccol % '"', end=" ")
		print()


def sort_by_tournament_results(history):
	def key(player):
		name, scores, totals = player
		hash = 0
		for score in scores:
			hash += score
			hash *= 100
		return hash
	return sorted(history, key=key, reverse=True)


def sort_by_cumulative_results(history):
	def key(player):
		name, scores, totals = player
		hash = 0
		for score in totals:
			hash += score
			hash *= 100
		return hash
	return sorted(history, key=key, reverse=True)


def print_best_tournament_results(history):
	history = sort_by_tournament_results(history)

	sizes = get_column_sizes(history)
	#~ print(sizes)

	for name, scores, totals in history:
		print((" %%-%ds |" % sizes["max_name_length"]) % name, end="")
		for score in scores:
			print(" %2.2f" % score if score else "     ", end=" |")
		print()


def print_best_tournament_results_html(history, file=sys.stdout):
	history = sort_by_tournament_results(history)

	sizes = get_column_sizes(history)
	#~ print(sizes)

	file.write('<table>\n\t<thead>\n\t\t<tr>\n')

	header_items = ["#", "Name"] + [i + 1 for i in range(sizes["max_scores_count"])]
	for s in header_items:
		file.write('\t\t\t<th>%s</th>\n' % str(s))

	file.write('\t\t</tr>\n\t</thead>\n\t<tbody>\n')

	place = 0
	for name, scores, totals in history:
		place += 1
		file.write('\t\t<tr>\n')
		file.write('\t\t\t<td>%d</td>\n' % place)
		file.write('\t\t\t<td>%s</td>\n' % name)
		for score in scores:
			file.write('\t\t\t<td>%s</td>\n' % str(score))
		file.write('\t\t</tr>\n')

	file.write('\t</tbody>\n</table>\n')


def score_to_string(score, ilength, flength, strip = True):
	if not score:
		return "%s0 %s" % (" " * (ilength - 1), " " * flength)
	s = ("%%%d.%df" % (ilength, flength)) % score
	s = ("%%%ds" % (ilength + 1 + flength)) % s
	if strip:
		s = s.rstrip("0")
		s = s.rstrip(".")
	return s + " " * (ilength + 1 + flength - len(s))


def print_best_tournament_results_csv(history, file=sys.stdout):
	history = sort_by_tournament_results(history)

	sizes = get_column_sizes(history)
	#~ print(sizes)

	fcol = [
		"%%%ds" % sizes["max_index_length"],
		"%%%ds" % max(len("Name"), sizes["max_name_length"]),
		"%%%dd" % sizes["max_score_length"],
		"%%%ds" % sizes["max_score_length"],
		"%%%d.%df" % (sizes["max_score_length"], sizes["max_score_flength"]),
	]

	file.write(fcol[0] % "#" + ", ")
	file.write(fcol[1] % "Name")

	for i in range(1, sizes["max_scores_count"] + 1):
		file.write(", " + fcol[2] % i)
	file.write("\n")

	place = 0
	for name, scores, totals in history:
		place += 1
		file.write(fcol[0] % place + ", ")
		file.write(fcol[1] % name)
		for score in scores:
			if not score:
				file.write(", " + fcol[3] % "")
			else:
				#~ file.write(", " + fcol[4] % score)
				file.write(", " + score_to_string(score, sizes["max_score_ilength"], sizes["max_score_flength"]))
		file.write("\n")


def print_cumulative_tournament_results_csv(history, file=sys.stdout):
	history = sort_by_cumulative_results(history)

	sizes = get_column_sizes(history)
	#~ print(sizes)

	fcol = [
		"%%%ds" % sizes["max_index_length"],
		"%%%ds" % max(len("x = "), sizes["max_name_length"]),
		"%%%dd" % sizes["max_total_length"],
		"%%%ds" % sizes["max_total_length"],
		"%%%d.%df" % (sizes["max_total_length"], sizes["max_total_flength"]),
	]

	file.write(fcol[0] % "#" + ", ")
	file.write(fcol[1] % "x = ")

	for i in range(3, sizes["max_scores_count"] + 1):
		file.write(", " + fcol[2] % i)
	file.write("\n")

	place = 0
	for name, scores, totals in history:
		place += 1
		file.write(fcol[0] % place + ", ")
		file.write(fcol[1] % name)
		last_score = None
		for score in totals:
			if score == last_score:
				file.write(", " + fcol[3] % "")
			else:
				last_score = score
				#~ file.write(", " + fcol[4] % score)
				file.write(", " + score_to_string(score, sizes["max_total_ilength"], sizes["max_total_flength"]))
		file.write("\n")


if __name__ == "__main__":
	filepaths = sys.argv[1:]
	if not filepaths: exit()

	names, synonyms = load_names_from_files(filepaths)
	history = load_history(names, synonyms)

	#~ print_names(names, synonyms)
	#~ print_groups(names, synonyms)
	#~ print_history(history, 3)
	#~ print_full_history(history)

	#~ print_best_tournament_results(history)
	#~ print_best_tournament_results_html(history)

	#~ print_best_tournament_results_csv(history)
	print_cumulative_tournament_results_csv(history)
