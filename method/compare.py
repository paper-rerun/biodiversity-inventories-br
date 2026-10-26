# Compare the two blind transcriptions of the biodiversity pilot (A/*.json and B/*.json, schema 1.0-pilot:
# {events, tables, records, end_checklist})
# Output: method/diff_<doc_id>.csv (or diff.csv for every doc in both folders) with every event field
# disagreement first, then table, label and column disagreements, then every record field disagreement and
# every record present on one side only
#
# Adapted from batata/method/compare.py (schema v8). What changed for Darwin Core occurrences:
# - trials became events, paired by event_label_as_printed (then parent and level) and B ids rewritten to A ids,
#   so a record event_id only shows up when the two sides put the cell in a different event
# - tables paired by (page, label) as before; columns paired by the (name, value) cells they share, then by header
# - records paired inside each (table, page) group by event + verbatimScientificName, with row_index, column and
#   printed value as tie-breakers. The name decides; a typo on one side still pairs (similarity >= 0.6)
# - names, qualifiers, codes and printed values are compared exactly (spaces collapsed): the schema copies them as
#   printed, so a lost accent or a dropped '.' is a real difference. Other text is compared loosely (norm)
# - end_checklist is not compared, it is recomputed from the final records
#
# Usage: python compare.py [doc_id ...]   (paths are relative to this file); python compare.py --check runs the asserts
import csv
import difflib
import glob
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
A_DIR = os.path.join(ROOT, "A")
B_DIR = os.path.join(ROOT, "B")

# event_id is the pairing key and notes is free text, so neither is compared
EVENT_FIELDS = ["parent_event_id", "event_level", "event_label_as_printed", "verbatimLocality", "municipality", "stateProvince",
	"country", "verbatimCoordinates", "verbatimCoordinateSystem", "decimalLatitude", "decimalLongitude", "geodeticDatum",
	"verbatimElevation", "verbatimEventDate", "habitat", "samplingProtocol", "samplingEffort", "sampleSize_as_printed",
	"recordedBy_as_printed", "field_pages", "source_inconsistency"]
# caption_summary and skipped_reason are free text and are not compared
TABLE_FIELDS = ["kind", "event_ids", "data_cells", "transcribed", "skipped_cells"]
LABEL_FIELDS = ["row_identity", "column_axis", "presence_shown_as", "absence_shown_as", "symbols", "quantity_meaning",
	"heading_levels", "threat_list_as_printed", "footnotes", "source_inconsistency"]
COLUMN_FIELDS = ["header_as_printed", "role", "event_id", "organismQuantityType_as_printed"]
# record_id is a running number and notes is free text
RECORD_FIELDS = ["event_id", "table_id", "column_id", "row_index", "position_in_cell", "event_detail_as_printed", "page",
	"table_or_figure", "value_kind", "verbatimScientificName", "identificationQualifier", "family_as_printed", "family_source",
	"order_as_printed", "order_source", "higher_group_as_printed", "vernacularName", "occurrenceStatus", "individualCount",
	"organismQuantity", "organismQuantityType", "value_as_printed", "printed_code", "code_meaning", "code_legend_page",
	"record_origin", "cited_source_as_printed", "recording_method_as_printed", "voucher_as_printed", "threat_status_as_printed",
	"threat_status_source_as_printed", "line_attributes", "source_inconsistency"]
# Copied as printed, so compared character by character
EXACT_FIELDS = {"verbatimScientificName", "identificationQualifier", "value_as_printed", "printed_code", "verbatimCoordinates",
	"event_label_as_printed", "header_as_printed", "family_as_printed", "order_as_printed", "vernacularName"}
MIN_NAME_SIMILARITY = 0.6


def norm(text):
	if text is None:
		return ""
	# field_pages, symbols, footnotes and line_attributes are dicts or lists; key order does not count
	if isinstance(text, (dict, list)):
		text = json.dumps(text, sort_keys=True, ensure_ascii=False)
	text = unicodedata.normalize("NFKD", str(text))
	text = "".join(ch for ch in text if not unicodedata.combining(ch))
	return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def exact(text):
	if text is None:
		return ""
	return re.sub(r"\s+", " ", unicodedata.normalize("NFC", str(text))).strip()


def norm_label(text):
	return re.sub(r"^fig(?:ura)?\b", "figura", norm(text))


def similarity(a, b):
	a, b = norm(a), norm(b)
	if a == b:
		return 1.0
	return difflib.SequenceMatcher(None, a, b).ratio()


def number_tokens(text):
	return set(re.findall(r"\d+(?:[.,]\d+)?", text or ""))


def field_differs(field, value_a, value_b):
	if isinstance(value_a, (int, float)) or isinstance(value_b, (int, float)):
		return value_a != value_b
	if field.split(".")[-1] in EXACT_FIELDS:
		return exact(value_a) != exact(value_b)
	return norm(value_a) != norm(value_b)


def kind_of(field, value_a, value_b):
	if field in ("value_as_printed", "individualCount", "organismQuantity"):
		return "value_mismatch"
	if field == "verbatimScientificName":
		return "name_mismatch"
	if value_a in (None, "", []) or value_b in (None, "", []):
		return "null_vs_text"
	if number_tokens(str(value_a)) != number_tokens(str(value_b)):
		return "numbers_differ"
	return "wording"


def pair_events(events_a, events_b):
	# Each A event takes the B event with the same label, level and parent label; ids as fallback.
	# Returns {B id: A id}
	labels_a = {event["event_id"]: event.get("event_label_as_printed") for event in events_a}
	labels_b = {event["event_id"]: event.get("event_label_as_printed") for event in events_b}
	# Best scores pair first over all candidates, so 'Área I' is not taken by 'Área II' just for coming first
	candidates = []
	for event_a in events_a:
		for event_b in events_b:
			score = 3.0 * similarity(event_a.get("event_label_as_printed"), event_b.get("event_label_as_printed"))
			score += 1.0 if event_a.get("event_level") == event_b.get("event_level") else 0.0
			score += 1.0 if norm(labels_a.get(event_a.get("parent_event_id"))) == norm(labels_b.get(event_b.get("parent_event_id"))) else 0.0
			score += 0.1 if event_a["event_id"] == event_b["event_id"] else 0.0
			if score >= 3.5:
				candidates.append((score, event_a["event_id"], event_b["event_id"]))
	candidates.sort(key=lambda c: (-c[0], c[1], c[2]))
	new_id_for_b, used_a = {}, set()
	for score, event_id_a, event_id_b in candidates:
		if event_id_a in used_a or event_id_b in new_id_for_b:
			continue
		used_a.add(event_id_a)
		new_id_for_b[event_id_b] = event_id_a
	return new_id_for_b


def rewrite_event_ids_b(new_id_for_b, events_b, tables_b, records_b):
	def mapped(event_id):
		return new_id_for_b.get(event_id, event_id + "?B" if event_id else event_id)
	for event in events_b:
		event["event_id"] = mapped(event["event_id"])
		event["parent_event_id"] = mapped(event.get("parent_event_id")) if event.get("parent_event_id") else None
	for table in tables_b:
		table["event_ids"] = [mapped(event_id) for event_id in table.get("event_ids") or []]
		for column in table.get("columns") or []:
			if column.get("event_id"):
				column["event_id"] = mapped(column["event_id"])
	for record in records_b:
		record["event_id"] = mapped(record.get("event_id"))


def pair_columns(table_a, table_b, records_a, records_b):
	# Columns are paired by the (name, value) cells their records share, best overlap first, then by header
	def footprints(table, records):
		cells = {column["column_id"]: set() for column in table.get("columns") or []}
		for record in records:
			if record.get("table_id") == table["table_id"] and record.get("column_id") in cells:
				cells[record["column_id"]].add((norm(record.get("verbatimScientificName")), exact(record.get("value_as_printed"))))
		return cells
	cells_a, cells_b = footprints(table_a, records_a), footprints(table_b, records_b)
	headers_b = {column["column_id"]: column.get("header_as_printed") for column in table_b.get("columns") or []}
	candidates = []
	for column_a in table_a.get("columns") or []:
		for column_id_b in cells_b:
			overlap = len(cells_a[column_a["column_id"]] & cells_b[column_id_b])
			header_score = similarity(column_a.get("header_as_printed"), headers_b[column_id_b])
			candidates.append((overlap, header_score, column_a["column_id"] == column_id_b, column_a["column_id"], column_id_b))
	candidates.sort(key=lambda c: (-c[0], -c[1], not c[2], c[3], c[4]))
	pairs, used_b = {}, set()
	for overlap, header_score, bSameId, column_id_a, column_id_b in candidates:
		if column_id_a in pairs or column_id_b in used_b:
			continue
		if overlap == 0 and header_score < 0.6:
			continue
		pairs[column_id_a] = column_id_b
		used_b.add(column_id_b)
	return pairs


def compare_tables(doc_id, tables_a, tables_b, records_a, records_b):
	rows = []
	by_key_b = {}
	for table in tables_b:
		by_key_b.setdefault((table["page"], norm_label(table["label"])), []).append(table)
	new_table_for_b, new_column_for_b = {}, {}
	for table_a in tables_a:
		candidates = by_key_b.get((table_a["page"], norm_label(table_a["label"])), [])
		same_kind = [table for table in candidates if table["kind"] == table_a["kind"]]
		table_b = (same_kind or candidates or [None])[0]
		if table_b is None:
			rows.append(row(doc_id, table_a["page"], table_a["label"], "only_in_A", "table", table_a["table_id"], ""))
			continue
		candidates.remove(table_b)
		new_table_for_b[table_b["table_id"]] = table_a["table_id"]
		fields = [("table_id", table_a["table_id"], table_b["table_id"])]
		fields += [(field, table_a.get(field), table_b.get(field)) for field in TABLE_FIELDS]
		labels_a, labels_b = table_a.get("table_level_labels") or {}, table_b.get("table_level_labels") or {}
		fields += [("table_level_labels." + field, labels_a.get(field), labels_b.get(field)) for field in LABEL_FIELDS]
		column_pairs = pair_columns(table_a, table_b, records_a, records_b)
		columns_b = {column["column_id"]: column for column in table_b.get("columns") or []}
		for column_a in table_a.get("columns") or []:
			column_b = columns_b.pop(column_pairs.get(column_a["column_id"]), None)
			if column_b is None:
				rows.append(row(doc_id, table_a["page"], table_a["label"], "only_in_A", "column", table_a["table_id"] + "." + column_a["column_id"], ""))
				continue
			new_column_for_b[(table_b["table_id"], column_b["column_id"])] = column_a["column_id"]
			fields += [("columns.%s.%s" % (column_a["column_id"], field), column_a.get(field), column_b.get(field)) for field in COLUMN_FIELDS]
		for column_id in columns_b:
			rows.append(row(doc_id, table_a["page"], table_a["label"], "only_in_B", "column", "", table_b["table_id"] + "." + column_id))
		for field, value_a, value_b in fields:
			if field_differs(field, value_a, value_b):
				rows.append(row(doc_id, table_a["page"], table_a["label"], kind_of(field, value_a, value_b), field,
					table_a["table_id"], table_b["table_id"], value_a=value_a, value_b=value_b))
	for table_b in [table for candidates in by_key_b.values() for table in candidates]:
		rows.append(row(doc_id, table_b["page"], table_b["label"], "only_in_B", "table", "", table_b["table_id"]))
	# B records take the A table and column ids, so a record only flags them when the cell really sits elsewhere
	for record in records_b:
		key = (record.get("table_id"), record.get("column_id"))
		if key in new_column_for_b:
			record["column_id"] = new_column_for_b[key]
		if record.get("table_id") in new_table_for_b:
			record["table_id"] = new_table_for_b[record["table_id"]]
	return rows


def record_pair_score(a, b):
	name_score = similarity(a.get("verbatimScientificName"), b.get("verbatimScientificName"))
	if name_score < MIN_NAME_SIMILARITY:
		return None
	score = 4.0 * name_score
	score += 3.0 if a.get("event_id") == b.get("event_id") else 0.0
	score += 1.0 if a.get("row_index") == b.get("row_index") else 0.0
	score += 0.5 if a.get("column_id") == b.get("column_id") else 0.0
	score += 0.5 if exact(a.get("value_as_printed")) == exact(b.get("value_as_printed")) else 0.0
	score += 0.5 if exact(a.get("printed_code")) == exact(b.get("printed_code")) else 0.0
	score += 0.25 if a.get("position_in_cell") == b.get("position_in_cell") else 0.0
	return score


def pair_records(records_a, records_b):
	# Groups by (table, page); inside a group the best scores pair first, ties keep file order
	groups = {}
	for side, records in (("a", records_a), ("b", records_b)):
		for index, record in enumerate(records):
			groups.setdefault((record.get("table_id"), record.get("page")), {"a": [], "b": []})[side].append(index)
	pairs, only_a, only_b = [], [], []
	for key in sorted(groups, key=lambda k: (str(k[0]), k[1] or 0)):
		indexes_a, indexes_b = groups[key]["a"], groups[key]["b"]
		candidates = []
		for ia in indexes_a:
			for ib in indexes_b:
				score = record_pair_score(records_a[ia], records_b[ib])
				if score is not None:
					candidates.append((score, ia, ib))
		candidates.sort(key=lambda c: (-c[0], c[1], c[2]))
		used_a, used_b = set(), set()
		for score, ia, ib in candidates:
			if ia in used_a or ib in used_b:
				continue
			used_a.add(ia)
			used_b.add(ib)
			pairs.append((score, ia, ib))
		only_a += [ia for ia in indexes_a if ia not in used_a]
		only_b += [ib for ib in indexes_b if ib not in used_b]
	return sorted(pairs, key=lambda p: p[1]), only_a, only_b


HEADER = ["diff_id", "doc_id", "page", "table_or_figure", "kind", "field", "a_index", "b_index",
	"name_a", "name_b", "event_a", "event_b", "a_value", "b_value", "value_as_printed_a", "value_as_printed_b", "match_score"]


def row(doc_id, page, table_or_figure, kind, field, a_index, b_index, name_a="", name_b="", event_a="", event_b="",
	value_a="", value_b="", printed_a="", printed_b="", score=""):
	def cell(value):
		if isinstance(value, (dict, list)):
			return json.dumps(value, ensure_ascii=False, sort_keys=True)
		return "" if value is None else value
	return [doc_id, page, table_or_figure, kind, field, a_index, b_index, name_a, name_b, event_a, event_b,
		cell(value_a), cell(value_b), cell(printed_a), cell(printed_b), score]


def compare_document(name):
	doc_id = name[:-5]
	with open(os.path.join(A_DIR, name), encoding="utf-8") as handle:
		data_a = json.load(handle)
	with open(os.path.join(B_DIR, name), encoding="utf-8") as handle:
		data_b = json.load(handle)
	events_a, tables_a, records_a = data_a["events"], data_a["tables"], data_a["records"]
	events_b, tables_b, records_b = data_b["events"], data_b["tables"], data_b["records"]
	rows = []
	# Events first, B ids rewritten to the paired A ids
	new_event_for_b = pair_events(events_a, events_b)
	original_b_ids = {new_event_for_b.get(event["event_id"], event["event_id"] + "?B"): event["event_id"] for event in events_b}
	rewrite_event_ids_b(new_event_for_b, events_b, tables_b, records_b)
	events_by_id_b = {event["event_id"]: event for event in events_b}
	for event_a in events_a:
		event_b = events_by_id_b.pop(event_a["event_id"], None)
		if event_b is None:
			rows.append(row(doc_id, "", "events", "only_in_A", "event", event_a["event_id"], ""))
			continue
		for field in EVENT_FIELDS:
			if field_differs(field, event_a.get(field), event_b.get(field)):
				rows.append(row(doc_id, "", "events", kind_of(field, event_a.get(field), event_b.get(field)), field,
					event_a["event_id"], original_b_ids[event_b["event_id"]], value_a=event_a.get(field), value_b=event_b.get(field)))
	for event_id in events_by_id_b:
		rows.append(row(doc_id, "", "events", "only_in_B", "event", "", original_b_ids[event_id]))
	# Tables second, then records
	rows += compare_tables(doc_id, tables_a, tables_b, records_a, records_b)
	pairs, only_a, only_b = pair_records(records_a, records_b)
	for score, ia, ib in pairs:
		a, b = records_a[ia], records_b[ib]
		for field in RECORD_FIELDS:
			if field_differs(field, a.get(field), b.get(field)):
				rows.append(row(doc_id, a["page"], a["table_or_figure"], kind_of(field, a.get(field), b.get(field)), field,
					a["record_id"], b["record_id"], a["verbatimScientificName"], b["verbatimScientificName"], a["event_id"], b["event_id"],
					a.get(field), b.get(field), a.get("value_as_printed"), b.get("value_as_printed"), round(score, 2)))
	for ia in only_a:
		a = records_a[ia]
		rows.append(row(doc_id, a["page"], a["table_or_figure"], "only_in_A", "record", a["record_id"], "",
			a["verbatimScientificName"], "", a["event_id"], "", printed_a=a.get("value_as_printed")))
	for ib in only_b:
		b = records_b[ib]
		rows.append(row(doc_id, b["page"], b["table_or_figure"], "only_in_B", "record", "", b["record_id"],
			"", b["verbatimScientificName"], "", b["event_id"], printed_b=b.get("value_as_printed")))
	return rows, len(records_a), len(records_b), len(pairs)


def main(doc_ids):
	if doc_ids:
		names = [doc_id + ".json" for doc_id in doc_ids]
		out_path = os.path.join(HERE, "diff_%s.csv" % doc_ids[0]) if len(doc_ids) == 1 else os.path.join(HERE, "diff_selected.csv")
	else:
		names = sorted(os.path.basename(p) for p in glob.glob(os.path.join(A_DIR, "*.json")) if os.path.exists(os.path.join(B_DIR, os.path.basename(p))))
		out_path = os.path.join(HERE, "diff.csv")
	out_rows = []
	for name in names:
		rows, count_a, count_b, count_pairs = compare_document(name)
		out_rows += rows
		print("%s: A records %d, B records %d, matched pairs %d, diff rows %d" % (name[:-5], count_a, count_b, count_pairs, len(rows)))
	with open(out_path, "w", encoding="utf-8", newline="") as handle:
		writer = csv.writer(handle)
		writer.writerow(HEADER)
		for number, out_row in enumerate(out_rows, 1):
			writer.writerow(["D%04d" % number] + out_row)
	print("wrote " + out_path)


def self_check():
	assert norm("Área I") == "area i" and norm_label("FIG. 1") == norm_label("Figura 1")
	# Names are exact: a lost accent or a dropped period is a difference; other text is loose
	assert field_differs("verbatimScientificName", "Myracrodruon urundeuva Allemão", "Myracrodruon urundeuva Allemao")
	assert not field_differs("verbatimScientificName", "Croton  sp.", "Croton sp.")
	assert not field_differs("habitat", "Caatinga.", "caatinga")
	assert field_differs("individualCount", 15, 16) and not field_differs("field_pages", {"a": 1, "b": 2}, {"b": 2, "a": 1})
	# Events numbered in another order pair by label, and B records take the A ids
	events_a = [{"event_id": "e1", "parent_event_id": None, "event_level": "study", "event_label_as_printed": None},
		{"event_id": "e2", "parent_event_id": "e1", "event_level": "site", "event_label_as_printed": "Área I"},
		{"event_id": "e3", "parent_event_id": "e1", "event_level": "site", "event_label_as_printed": "Área II"}]
	events_b = [{"event_id": "e1", "parent_event_id": None, "event_level": "study", "event_label_as_printed": None},
		{"event_id": "e2", "parent_event_id": "e1", "event_level": "site", "event_label_as_printed": "Área II"},
		{"event_id": "e3", "parent_event_id": "e1", "event_level": "site", "event_label_as_printed": "Área I"}]
	new_ids = pair_events(events_a, events_b)
	assert new_ids == {"e1": "e1", "e3": "e2", "e2": "e3"}
	records_b = [{"event_id": "e3"}]
	rewrite_event_ids_b(new_ids, events_b, [], records_b)
	assert records_b[0]["event_id"] == "e2"
	# Records pair by name and event inside (table, page); a one-letter typo still pairs, another species does not
	records_a = [{"table_id": "k1", "page": 4, "event_id": "e2", "verbatimScientificName": "Croton conduplicatus", "row_index": 3},
		{"table_id": "k1", "page": 4, "event_id": "e3", "verbatimScientificName": "Croton conduplicatus", "row_index": 3}]
	records_b = [{"table_id": "k1", "page": 4, "event_id": "e3", "verbatimScientificName": "Croton conduplicatus", "row_index": 3},
		{"table_id": "k1", "page": 4, "event_id": "e2", "verbatimScientificName": "Croton conduplicatos", "row_index": 3},
		{"table_id": "k1", "page": 4, "event_id": "e2", "verbatimScientificName": "Aspidosperma pyrifolium", "row_index": 4}]
	pairs, only_a, only_b = pair_records(records_a, records_b)
	assert [(ia, ib) for score, ia, ib in pairs] == [(0, 1), (1, 0)] and only_a == [] and only_b == [2]
	# Columns numbered in another order pair by shared cells
	table_a = {"table_id": "k2", "columns": [{"column_id": "c2", "header_as_printed": "NI A"}, {"column_id": "c3", "header_as_printed": "NI B"}]}
	table_b = {"table_id": "k2", "columns": [{"column_id": "c2", "header_as_printed": "NI B"}, {"column_id": "c3", "header_as_printed": "NI A"}]}
	records_a = [{"table_id": "k2", "column_id": "c2", "verbatimScientificName": "X y", "value_as_printed": "15"},
		{"table_id": "k2", "column_id": "c3", "verbatimScientificName": "X y", "value_as_printed": "4"}]
	records_b = [{"table_id": "k2", "column_id": "c3", "verbatimScientificName": "X y", "value_as_printed": "15"},
		{"table_id": "k2", "column_id": "c2", "verbatimScientificName": "X y", "value_as_printed": "4"}]
	assert pair_columns(table_a, table_b, records_a, records_b) == {"c2": "c3", "c3": "c2"}


if __name__ == "__main__":
	self_check()
	if "--check" not in sys.argv:
		main([arg for arg in sys.argv[1:] if not arg.startswith("--")])
