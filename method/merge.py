# Merge the adjudicated documents into event.csv, occurrence.csv (Darwin Core names) and qa/decisions.csv, and print the
# pilot numbers for RODADA.md
# Usage: python -X utf8 method/merge.py [--out DIR]   (paths are relative to the biodiversidade-piloto folder; --out writes
# event.csv, occurrence.csv and decisions.csv to DIR instead of the folder itself and qa/)
#
# Schema 2.0 (RODADA.md, "O que mudar no schema"): basisOfRecord comes from the event's material_fate, inherited like the
# other event fields; code_meaning is no longer on the record, it is joined from table_level_labels.symbols by printed_code;
# eventDate is derived here from the printed period, ISO 8601, and left empty when the period is ambiguous. A document
# transcribed in 1.0-pilot still merges: its missing 2.0 fields read as null and basisOfRecord falls back to BASIS_OF_RECORD
#
# Copied from batata/method/merge.py for the biodiversity pilot (schema 1.0-pilot). Changed: trials became events (one
# row per event in event.csv, eventID = doc_id#e1, parent first) and records became occurrences (occurrenceID = doc_id#n).
# An event field left null inherits from the nearest ancestor that prints it, written in `inherited`, except coordinates,
# effort, sample size and the event's own label, which belong to the event that prints them. basisOfRecord comes from what
# each document says about its material (BASIS_OF_RECORD). Accuracy counts events, tables and records, and names misread
# take the place of the "number misread" of the agriculture rounds. The self-checks and the long-copy check are the same
import ast
import csv
import datetime
import glob
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "method"))
import compare  # noqa: E402  only for the compared field lists
MAX_QUOTE_WORDS = 15
COMPARED_RECORD_FIELD_COUNT = len(compare.RECORD_FIELDS)
COMPARED_EVENT_FIELD_COUNT = len(compare.EVENT_FIELDS)
LICENSE_REPOSITORY = "CC BY-NC-ND 4.0 (aviso geral do repositório {repo}, não é licença do item)"
LICENSE_NO_CC = "sem licença Creative Commons: o item só diz 'Acesso Aberto' (dc.rights, {repo})"

# Schema 2.0: the class of material the study event prints -> basisOfRecord
BASIS_OF_RECORD_BY_MATERIAL_FATE = {"deposited_in_collection": "PreservedSpecimen", "released_or_observed": "HumanObservation",
	"vouchers_not_tied_to_records": "HumanObservation", "not_stated": "HumanObservation"}

# 1.0-pilot only, for documents transcribed before material_fate existed. What each document says about its material.
# Only camargo2009 keeps the specimens
BASIS_OF_RECORD = {
	"freydargas2014-peixes-taquari-pantanal-ms": "HumanObservation",  # p9: identified in the field, photographed and released
	"nunes2009-aves-nhumirim-pantanal-ms": "HumanObservation",  # field lists of four observers and literature, no specimen
	"bianconi2004-morcegos-fenix-pr": "HumanObservation",  # mist-net captures; p3 names only a small voucher series, tied to no row
	"camargo2009-saturniidae-fragmentos-cerrado-ro-go": "PreservedSpecimen",  # p13: light-trap material deposited in the CPAC collection
	"miranda1982-herpetofauna-ouricuri-pe": "HumanObservation",  # zooecological survey sheets, no collection named
	"calixto2014-fitossociologia-caatinga-petrolina-pe": "HumanObservation",  # plot tally; p3 exsiccatae only check the identification
	"sandel2000-floristica-tapajos-km69-pa": "HumanObservation",  # plot inventory, no voucher printed
	"silva2009-mamiferos-aves-pedro-peixoto-ac": "HumanObservation",  # transect sightings (p14)
}

# Pairs per document in the adjudication summaries, checked against A minus the A-only records
# Full round of 20 (01/11), from the adjudication summaries
EXPECTED_PAIRS = {"mai2010-peixes-currais-litoral-pi": 118, "queiroga2018-peixes-vereda-uberlandia-mg": 36,
	"winckler2011-peixes-arroz-capao-do-leao-rs": 12, "mauricio2018-aves-serra-dos-tapes-rs": 193,
	"carvalho2013-aves-aquaticas-iguatama-mg": 184, "silva2009b-mamiferos-aves-iracema-am": 254,
	"dias2006-mamiferos-embrapa-florestas-colombo-pr": 50, "nunes2009-mamiferos-serra-do-brigadeiro-mg": 84,
	"silveira2010-morcegos-nhumirim-ms": 36, "gordo2003-anuros-nhumirim-ms": 19, "carosini2013-anuros-serrapilheira-caratinga-mg": 84,
	"santos2019-escarabeideos-placido-de-castro-ac": 15, "rodrigues2010-besouros-coprofagos-nhumirim-ms": 35,
	"pereira2011-borboletas-araguari-mg": 27, "viana2020-esfingideos-saturnideos-pau-furado-mg": 130,
	"lopes2010-abelhas-plantas-apicolas-teresina-pi": 172, "vieira2002-fitossociologia-machadinho-ro": 70,
	"tourinho1998-manguezal-braganca-pa": 87, "pereira2012-caatinga-fazenda-tamandua-pb": 63, "rego2008-abelhas-sem-ferrao-balsas-ma": 19}

# Event fields a child takes from its parent when it prints nothing of its own (rule 5)
INHERITED_EVENT_FIELDS = ["verbatimLocality", "municipality", "stateProvince", "country", "verbatimEventDate", "habitat",
	"samplingProtocol", "recordedBy_as_printed", "material_fate", "material_fate_as_printed"]
# schema event field -> event.csv column
EVENT_COLUMNS = {"event_level": "eventType", "event_label_as_printed": "event_label_as_printed",
	"verbatimLocality": "verbatimLocality", "municipality": "municipality", "stateProvince": "stateProvince", "country": "country",
	"verbatimCoordinates": "verbatimCoordinates", "verbatimCoordinateSystem": "verbatimCoordinateSystem",
	"decimalLatitude": "decimalLatitude", "decimalLongitude": "decimalLongitude", "geodeticDatum": "geodeticDatum",
	"verbatimElevation": "verbatimElevation", "verbatimEventDate": "verbatimEventDate", "habitat": "habitat",
	"samplingProtocol": "samplingProtocol", "samplingEffort": "samplingEffort", "sampleSize_as_printed": "sampleSize_as_printed",
	"recordedBy_as_printed": "recordedBy", "material_fate": "material_fate", "material_fate_as_printed": "material_fate_as_printed",
	"notes": "eventRemarks", "source_inconsistency": "source_inconsistency",
	"field_pages": "field_pages"}
# schema record field -> occurrence.csv column. Darwin Core names first, then ours for what Darwin Core has no term for
RECORD_COLUMNS = {"verbatimScientificName": "scientificName", "identificationQualifier": "identificationQualifier",
	"name_in_full_as_printed": "name_in_full_as_printed", "name_in_full_page": "name_in_full_page", "name_status": "name_status", "family_as_printed": "family", "order_as_printed": "order", "higher_group_as_printed": "higherClassification",
	"vernacularName": "vernacularName", "occurrenceStatus": "occurrenceStatus", "individualCount": "individualCount",
	"organismQuantity": "organismQuantity", "organismQuantityType": "organismQuantityType", "notes": "occurrenceRemarks",
	"line_attributes": "dynamicProperties", "value_kind": "value_kind", "value_as_printed": "value_as_printed",
	"printed_code": "printed_code", "event_detail_as_printed": "event_detail_as_printed",
	"record_origin": "record_origin", "cited_source_as_printed": "cited_source_as_printed",
	"threat_status_as_printed": "threat_status_as_printed", "threat_status_source_as_printed": "threat_status_source_as_printed",
	"source_inconsistency": "source_inconsistency"}
DECISION_TEXT_COLUMNS = ["a_value", "b_value", "final_value", "evidence"]
NOT_SOURCE_TEXT = {"bibliographicCitation", "license", "occurrenceID", "eventID", "parentEventID", "doc_id", "source_file",
	"decision_ids", "inherited", "eventDate", "eventDate_derivation", "basisOfRecord_source"}

# Printed period -> ISO 8601 eventDate. Only the shapes below are read; anything else stays empty
MONTH_NUMBER = {"janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4, "maio": 5, "junho": 6, "julho": 7,
	"agosto": 8, "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12}
MONTH_PATTERN = "(janeiro|fevereiro|março|marco|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)"
DATE_PATTERNS = [
	# '3 de maio e 16 de junho de 2006', 'julho de 2002 e junho de 2003', 'dezembro a março de 1981'
	("month_range", re.compile(rf"(?:(\d{{1,2}}) de )?{MONTH_PATTERN}(?: de (\d{{4}}))? (?:e|a|até) (?:(\d{{1,2}}) de )?{MONTH_PATTERN} de (\d{{4}})")),
	# '2002 a 2003'
	("year_range", re.compile(r"(\d{4}) (?:a|e|até|-|–) (\d{4})")),
	# '16 de junho de 2006', 'março de 2013'
	("month", re.compile(rf"(?:(\d{{1,2}}) de )?{MONTH_PATTERN} de (\d{{4}})")),
	("year", re.compile(r"(\d{4})")),
]

NAME_FIELDS = {"verbatimScientificName", "identificationQualifier"}
HIGHER_TAXON_FIELDS = {"family_as_printed", "order_as_printed", "higher_group_as_printed", "family_source", "order_source"}
NUMBER_FIELDS = {"individualCount", "organismQuantity", "value_as_printed"}
CODE_FIELDS = {"printed_code", "code_meaning", "code_legend_page"}

# Quotes: 'x', "x", ‘x’, “x”. The single quote must not touch a letter, so "B's" is not a quote
QUOTE_PATTERN = re.compile(r"(?<![\w])'([^']{3,}?)'(?![\w])|\"([^\"]{3,}?)\"|‘([^’]+)’|“([^”]+)”")


def NormalizeWord(word):
	return re.sub(r"^[^\w]+|[^\w]+$", "", word.lower())


def LoadPdfWordShingles(pdf_path):
	# Text layer of the whole PDF, with line-break hyphens joined, as a set of 16-word sequences
	pdf_text = subprocess.run(["pdftotext", "-enc", "UTF-8", pdf_path, "-"], capture_output=True).stdout.decode("utf-8", "replace")
	pdf_text = re.sub(r"-\s*\n\s*", "", pdf_text)
	pdf_words = [NormalizeWord(word) for word in pdf_text.split()]
	pdf_words = [word for word in pdf_words if word]
	shingle_size = MAX_QUOTE_WORDS + 1
	return {tuple(pdf_words[index:index + shingle_size]) for index in range(len(pdf_words) - shingle_size + 1)}


def CopiedRuns(text, pdf_shingles):
	# Word runs of the text found in the PDF text layer with more than MAX_QUOTE_WORDS words in a row
	words = text.split()
	normalized = [NormalizeWord(word) for word in words]
	shingle_size = MAX_QUOTE_WORDS + 1
	runs = []
	index = 0
	while index + shingle_size <= len(words):
		if tuple(normalized[index:index + shingle_size]) in pdf_shingles and "" not in normalized[index:index + shingle_size]:
			run_end = index + shingle_size
			while run_end < len(words) and tuple(normalized[run_end - shingle_size + 1:run_end + 1]) in pdf_shingles:
				run_end += 1
			runs.append(" ".join(words[index:run_end]))
			index = run_end
		else:
			index += 1
	return runs


def LongQuotes(text):
	return [quoted for quoted in (next(group for group in match.groups() if group) for match in QUOTE_PATTERN.finditer(text))
		if len(quoted.split()) > MAX_QUOTE_WORDS]


def StringLeaves(value):
	# A cell that holds a dict or list (JSON, or the Python repr the adjudicators wrote in a_value and b_value) is
	# checked string by string: the quotes around each string are syntax, not a quotation of the source
	if isinstance(value, str):
		if value[:1] in "{[":
			for parser in (json.loads, ast.literal_eval):
				try:
					return StringLeaves(parser(value))
				except (ValueError, SyntaxError, TypeError, MemoryError, RecursionError):
					continue
		return [value]
	if isinstance(value, dict):
		return [leaf for each_value in value.values() for leaf in StringLeaves(each_value)]
	if isinstance(value, list):
		return [leaf for each_value in value for leaf in StringLeaves(each_value)]
	return []


def FindLongCopies(text, pdf_shingles):
	if not isinstance(text, str) or not text:
		return []
	return [copy for leaf in StringLeaves(text) for copy in CopiedRuns(leaf, pdf_shingles) + LongQuotes(leaf)]


def BuildCitation(document):
	authors = "; ".join(document["authors"]).rstrip(".")
	title = document["title"].rstrip(".")
	# University dissertations (DSpace 7): the item's own citation repeats author and title, sometimes in English, so
	# the citation is built from the metadata, with the university from the repository name
	if document["type"].startswith("Disserta"):
		university = document["repository"].split()[-1]
		return f"{authors}. {title}. {document['year']}. Dissertação (Mestrado) - {university}. Disponível em: {document['record_url']}"
	return f"{authors}. {title}. {document['citation'].rstrip('.')}. Disponível em: {document['record_url']}"


def BuildLicense(document):
	license_text = LICENSE_REPOSITORY.format(repo=document["repository"])
	# UFU, UFV and UFMG items carry only dc.rights 'Acesso Aberto', no Creative Commons footer
	if "Creative Commons" not in (document.get("license_shown") or ""):
		license_text = LICENSE_NO_CC.format(repo=document["repository"])
	copyright_found = document.get("publisher_copyright_in_pdf") or ""
	# miranda1982 is an image scan: the search could not run, which is not a printed notice
	if "image scan" in copyright_found:
		license_text += "; PDF só imagem, aviso de direitos não pesquisável"
	elif copyright_found and not copyright_found.startswith("none found"):
		license_text += "; o PDF imprime 'Todos os direitos reservados'" if "direitos reservados" in copyright_found else "; o PDF imprime '© Embrapa'"
	if document["type"] == "Artigo de periódico":
		license_text += "; artigo de periódico, valem os termos da revista (não conferidos)"
	return license_text


def DecisionIds(item):
	ids = item.get("decision_ids")
	if isinstance(ids, list):
		return "; ".join(str(each_id) for each_id in ids)
	return ids or ""


def SideOfError(decision):
	# Which side a decision counts against. corrected = both sides lost something on that item
	if decision == "B_right":
		return ("A",)
	if decision == "A_right":
		return ("B",)
	if decision in ("both_wrong", "corrected"):
		return ("A", "B")
	return ()


def CategoryOf(row):
	# event, column, label, record, table (one-sided entry), inventory or checklist
	field, index = row["field"], row["a_index"] or row["b_index"]
	if row["table_or_figure"] == "events":
		return "event"
	if row["table_or_figure"] == "end_checklist":
		return "checklist"
	if field.startswith("columns."):
		return "column"
	if field.startswith("table_level_labels."):
		return "label"
	# table_id is also a record field: a record row carries the record index (r12), a table row the table id (k5)
	if field == "record" or index.startswith("r"):
		return "record"
	return "inventory"


def CellText(value):
	if value is None:
		return ""
	if isinstance(value, (list, dict)):
		return json.dumps(value, ensure_ascii=False) if value else ""
	return value


def DeriveEventDate(printed_date):
	# ISO 8601 date or interval from the printed period; "" when the print is ambiguous or has a shape we do not read
	if not printed_date:
		return ""
	text = re.sub(r"\s+", " ", printed_date.lower())
	for shape, pattern in DATE_PATTERNS:
		match = pattern.search(text)
		if match is None:
			continue
		# Another year or month outside the match means two periods or a partial one: do not pick one
		rest = text[:match.start()] + " " + text[match.end():]
		if re.search(r"\d{4}", rest) or re.search(MONTH_PATTERN, rest):
			return ""
		groups = match.groups()
		if shape == "month_range":
			start_day, start_month, start_year, end_day, end_month, end_year = groups
			# 'dezembro a março de 1981' prints one year: the start takes it, and a start after the end is then ambiguous
			start = (int(start_year or end_year), MONTH_NUMBER[start_month], int(start_day) if start_day else None)
			end = (int(end_year), MONTH_NUMBER[end_month], int(end_day) if end_day else None)
		elif shape == "year_range":
			start, end = (int(groups[0]), None, None), (int(groups[1]), None, None)
		elif shape == "month":
			start = end = (int(groups[2]), MONTH_NUMBER[groups[1]], int(groups[0]) if groups[0] else None)
		else:
			start = end = (int(groups[0]), None, None)
		points = []
		for year, month, day in (start, end):
			if not 1800 <= year <= 2100:
				return ""
			try:
				datetime.date(year, month or 1, day or 1)
			except ValueError:
				return ""
			points.append(f"{year:04d}" + (f"-{month:02d}" if month else "") + (f"-{day:02d}" if day else ""))
		if (start[0], start[1] or 0, start[2] or 0) > (end[0], end[1] or 0, end[2] or 0):
			return ""
		return points[0] if points[0] == points[1] else f"{points[0]}/{points[1]}"
	return ""


def CodeMeaning(printed_code, table_symbols, document_symbols):
	# Meaning of the printed code from table_level_labels.symbols: the table's own list first, then any table of the
	# document (a continued table often lists its symbols on the first page only). A cell with several codes ('n t')
	# gets each one, split by ' | ' so two meanings are never read as one run of source text
	if not printed_code:
		return ""
	def MeaningOf(code):
		for symbols in (table_symbols, document_symbols):
			for symbol in symbols:
				if symbol["symbol"] == code and symbol["meaning_as_printed"]:
					return symbol["meaning_as_printed"]
		return None
	whole = MeaningOf(printed_code)
	if whole:
		return whole
	codes = [code for code in re.split(r"[\s,;]+", printed_code) if code]
	return " | ".join(f"{code}: {MeaningOf(code)}" for code in codes if MeaningOf(code))


def EventRows(doc_id, events, citation, license_text):
	events_by_id = {event["event_id"]: event for event in events}
	rows = []
	for event in events:
		row = {"eventID": f"{doc_id}#{event['event_id']}",
			"parentEventID": f"{doc_id}#{event['parent_event_id']}" if event["parent_event_id"] else ""}
		for field, column in EVENT_COLUMNS.items():
			row[column] = CellText(event[field])
		# Null field: walk up to the first ancestor that prints it
		inherited = []
		date_event_id = event["event_id"]
		for field in INHERITED_EVENT_FIELDS:
			ancestor = event
			while ancestor[field] is None and ancestor["parent_event_id"]:
				ancestor = events_by_id[ancestor["parent_event_id"]]
			if ancestor is not event and ancestor[field] is not None:
				row[EVENT_COLUMNS[field]] = CellText(ancestor[field])
				inherited.append(f"{field}:{ancestor['event_id']}")
				if field == "verbatimEventDate":
					date_event_id = ancestor["event_id"]
		# eventDate is ours, derived from the printed period, and says so in eventDate_derivation
		row["eventDate"] = DeriveEventDate(row["verbatimEventDate"])
		if row["eventDate"]:
			row["eventDate_derivation"] = f"derived by merge.py from verbatimEventDate of {date_event_id}"
		elif row["verbatimEventDate"]:
			row["eventDate_derivation"] = "not derived: printed period ambiguous or in a shape merge.py does not read"
		else:
			row["eventDate_derivation"] = ""
		row["countryCode"] = "BR"
		row["inherited"] = "; ".join(inherited)
		row["doc_id"] = doc_id
		row["origin"] = event.get("origin") or ""
		row["decision_ids"] = DecisionIds(event)
		row["bibliographicCitation"] = citation
		row["license"] = license_text
		rows.append(row)
	return rows


def main():
	# --out DIR keeps the folder's own CSVs untouched (test runs)
	out_dir = os.path.abspath(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else None
	schema = json.load(open(os.path.join(ROOT, "schema.json"), encoding="utf-8"))
	record_fields = schema["$defs"]["record"]["required"]
	event_fields = schema["$defs"]["event"]["required"]
	legacy_fields_filled = Counter()
	sources = json.load(open(os.path.join(ROOT, "sources.json"), encoding="utf-8"))
	documents_by_id = {document["id"]: document for document in sources["documents"]}

	shingles_by_doc = {}
	occurrence_rows = []
	event_rows = []
	stats = defaultdict(dict)
	for adjudicated_path in sorted(glob.glob(os.path.join(ROOT, "adjudicated", "*.json"))):
		doc_id = os.path.basename(adjudicated_path)[:-5]
		document = documents_by_id[doc_id]
		shingles_by_doc[doc_id] = LoadPdfWordShingles(os.path.join(ROOT, document["pdf_path"]))
		adjudicated = json.load(open(adjudicated_path, encoding="utf-8"))
		assert adjudicated["doc_id"] == doc_id
		# A document transcribed in an older schema has no 2.0 fields: they read as null, and the count is printed
		is_legacy = adjudicated.get("schema_version") != schema["version"]
		if is_legacy:
			for items, fields in ((adjudicated["events"], event_fields), (adjudicated["records"], record_fields)):
				for item in items:
					for field in fields:
						if field not in item:
							item[field] = None
							legacy_fields_filled[(adjudicated.get("schema_version"), field)] += 1
		citation, license_text = BuildCitation(document), BuildLicense(document)
		events_by_id = {event["event_id"]: event for event in adjudicated["events"]}
		# Every event has every schema field, and its parent is an event of the same document
		for event in adjudicated["events"]:
			assert all(field in event for field in event_fields), (doc_id, event.get("event_id"))
			assert event["parent_event_id"] is None or event["parent_event_id"] in events_by_id, (doc_id, event["event_id"])
		event_rows += EventRows(doc_id, adjudicated["events"], citation, license_text)
		event_row_by_id = {row["eventID"]: row for row in event_rows if row["doc_id"] == doc_id}
		tables_by_id = {table["table_id"]: table for table in adjudicated["tables"]}
		document_symbols = [symbol for table in adjudicated["tables"] for symbol in (table.get("table_level_labels") or {}).get("symbols") or []]
		for record_number, record in enumerate(adjudicated["records"], start=1):
			# Every schema field is there, and the record points to an event, a table and a column of this document
			assert all(field in record for field in record_fields), (doc_id, record_number)
			assert record["event_id"] in events_by_id, (doc_id, record_number, record["event_id"])
			assert record["table_id"] in tables_by_id, (doc_id, record_number, record["table_id"])
			columns_by_id = {column["column_id"]: column for column in tables_by_id[record["table_id"]].get("columns") or []}
			# A species-list line has no event column (miranda1982 Anexo 1, sandel2000 Anexo 1)
			assert not columns_by_id or record["column_id"] in columns_by_id or (record["column_id"] is None and record["value_kind"] == "list_line"), (doc_id, record_number, record["table_id"], record["column_id"])
			# An empty name cell is kept when it is illegible (rule 27) or prints no name at all (rule 12, name_status)
			assert record["verbatimScientificName"] or record["value_kind"] == "illegible" or record["name_status"] == "incomplete_in_print", (doc_id, record_number)
			event_id = f"{doc_id}#{record['event_id']}"
			event_row = event_row_by_id[event_id]
			# basisOfRecord from the material fate the event prints (inherited from the study event)
			if event_row["material_fate"]:
				basis_of_record = BASIS_OF_RECORD_BY_MATERIAL_FATE[event_row["material_fate"]]
				basis_source = f"material_fate {event_row['material_fate']}"
			else:
				assert is_legacy, f"{doc_id}: no material_fate on {record['event_id']} or its parents"
				basis_of_record = BASIS_OF_RECORD[doc_id]
				basis_source = f"merge.py BASIS_OF_RECORD, schema {adjudicated.get('schema_version')} has no material_fate"
			row = {"occurrenceID": f"{doc_id}#{record_number}", "eventID": event_id, "basisOfRecord": basis_of_record,
				"basisOfRecord_source": basis_source, "eventDate": event_row["eventDate"],
				"eventDate_derivation": event_row["eventDate_derivation"]}
			for field, column in RECORD_COLUMNS.items():
				row[column] = CellText(record[field])
				if column == "scientificName":
					row["recordedBy"] = event_row["recordedBy"]
			table_symbols = (tables_by_id[record["table_id"]].get("table_level_labels") or {}).get("symbols") or []
			row["code_meaning"] = CodeMeaning(record["printed_code"], table_symbols, document_symbols)
			row["doc_id"] = doc_id
			row["page"] = record["page"]
			row["table_or_figure"] = record["table_or_figure"]
			row["origin"] = record.get("origin") or ""
			row["decision_ids"] = DecisionIds(record)
			row["bibliographicCitation"] = citation
			row["license"] = license_text
			occurrence_rows.append(row)
		stats[doc_id]["final"] = len(adjudicated["records"])
		stats[doc_id]["events"] = len(adjudicated["events"])
		stats[doc_id]["tables"] = len(adjudicated["tables"])
		stats[doc_id]["record_tables"] = sum(1 for table in adjudicated["tables"] if table.get("table_level_labels"))
		stats[doc_id]["columns"] = sum(len(table.get("columns") or []) for table in adjudicated["tables"])

	event_columns = ["eventID", "parentEventID"] + list(EVENT_COLUMNS.values()) + ["eventDate", "eventDate_derivation", "countryCode",
		"inherited", "doc_id", "origin", "decision_ids", "bibliographicCitation", "license"]
	csv_dir = out_dir or ROOT
	os.makedirs(csv_dir, exist_ok=True)
	with open(os.path.join(csv_dir, "event.csv"), "w", encoding="utf-8", newline="") as output_file:
		writer = csv.DictWriter(output_file, fieldnames=event_columns)
		writer.writeheader()
		writer.writerows(event_rows)
	occurrence_columns = list(occurrence_rows[0].keys())
	with open(os.path.join(csv_dir, "occurrence.csv"), "w", encoding="utf-8", newline="") as output_file:
		writer = csv.DictWriter(output_file, fieldnames=occurrence_columns)
		writer.writeheader()
		writer.writerows(occurrence_rows)

	# Concatenate the decision files as they are, union of columns (the adjudicators wrote name/event in three ways)
	decision_rows = []
	decision_columns = ["source_file"]
	for decisions_path in sorted(glob.glob(os.path.join(ROOT, "adjudicated", "*_decisions.csv"))):
		for row in csv.DictReader(open(decisions_path, encoding="utf-8-sig", newline="")):
			row = {"source_file": "adjudicated/" + os.path.basename(decisions_path), **row}
			for key in row:
				if key not in decision_columns:
					decision_columns.append(key)
			decision_rows.append(row)
	for row in decision_rows:
		for column in decision_columns:
			row.setdefault(column, "")
	decisions_dir = out_dir or os.path.join(ROOT, "qa")
	os.makedirs(decisions_dir, exist_ok=True)
	with open(os.path.join(decisions_dir, "decisions.csv"), "w", encoding="utf-8", newline="") as output_file:
		writer = csv.DictWriter(output_file, fieldnames=decision_columns)
		writer.writeheader()
		writer.writerows(decision_rows)

	# Source text copied past 15 words, or quoted past 15 words, anywhere in the three files
	long_copies = []
	for file_name, rows, key_of in (("event.csv", event_rows, lambda row: row["eventID"]),
			("occurrence.csv", occurrence_rows, lambda row: row["occurrenceID"]),
			("qa/decisions.csv", decision_rows, lambda row: f"{row['source_file']} {row['diff_id']}")):
		for row in rows:
			for column, text in row.items():
				if column in NOT_SOURCE_TEXT:
					continue
				for copy in FindLongCopies(text, shingles_by_doc[row["doc_id"]]):
					long_copies.append((file_name, key_of(row), column, copy))
	unique_copies = sorted({(file_name, key.split("#")[0] if file_name == "occurrence.csv" else key, column, copy) for file_name, key, column, copy in long_copies})
	print(f"long copies: {len(long_copies)} cells, {len(unique_copies)} distinct")
	for copy in unique_copies:
		print("  COPY", copy)

	# Per side and per category: field errors, omissions, spurious entries, names and numbers misread
	field_errors_by_side = Counter()
	error_types = Counter()
	error_examples = {}
	for doc_id in stats:
		a_document = json.load(open(os.path.join(ROOT, "A", doc_id + ".json"), encoding="utf-8"))
		b_document = json.load(open(os.path.join(ROOT, "B", doc_id + ".json"), encoding="utf-8"))
		doc_stats = stats[doc_id]
		doc_stats.update(a_records=len(a_document["records"]), b_records=len(b_document["records"]),
			a_events=len(a_document["events"]), b_events=len(b_document["events"]),
			a_tables=len(a_document["tables"]), b_tables=len(b_document["tables"]))
		counts = Counter()
		wrong = {(side, category): set() for side in "AB" for category in ("record", "event", "label", "inventory", "column", "checklist")}
		for row in decision_rows:
			if row["doc_id"] != doc_id:
				continue
			counts["decision_" + row["decision"]] += 1
			kind, field = row["kind"], row["field"]
			if kind.startswith("only_in") or kind == "missing_in_both":
				unit = field if field in ("event", "table", "column") else "record"
				if kind == "missing_in_both":
					for side in ("both", "A", "B"):
						counts[f"{side}_{unit}_omitted"] += 1
					continue
				present_side = kind[-1]
				missing_side = "B" if present_side == "A" else "A"
				if row["decision"] in (present_side + "_right", "ambiguous_print"):
					counts[f"{missing_side}_{unit}_omitted"] += 1
					error_type = row[missing_side.lower() + "_error_type"] or row[present_side.lower() + "_error_type"] or f"{unit}_omitted"
					error_types[(missing_side, error_type)] += 1
				elif row["decision"] == missing_side + "_right":
					counts[f"{present_side}_{unit}_spurious"] += 1
					error_types[(present_side, row[present_side.lower() + "_error_type"] or f"{unit}_spurious")] += 1
				else:
					counts[f"{present_side}_{unit}_optional"] += 1
				if unit == "record" and present_side == "A":
					counts["a_only_records"] += 1
				continue
			category = CategoryOf(row)
			for side in SideOfError(row["decision"]):
				counts[f"{side}_{category}_field_errors"] += 1
				wrong[(side, category)].add(row[side.lower() + "_index"] or row["a_index"] or row["b_index"])
				field_errors_by_side[(side, category, re.sub(r"^columns\.[^.]+\.", "", field))] += 1
				error_type = row[side.lower() + "_error_type"] or "(sem tipo)"
				error_types[(side, error_type)] += 1
				error_examples.setdefault((side, error_type), f"{doc_id[:14]} {row['table_or_figure']} {field}: {row['evidence'][:110]}")
				if category == "record" and field in NAME_FIELDS:
					counts[f"{side}_name_errors"] += 1
				if category == "record" and field in NUMBER_FIELDS:
					counts[f"{side}_number_errors"] += 1
				if category == "record" and field in HIGHER_TAXON_FIELDS:
					counts[f"{side}_higher_taxon_errors"] += 1
		doc_stats.update(counts)
		for (side, category), units in wrong.items():
			doc_stats[f"{side}_wrong_{category}"] = len(units)
		for side in "AB":
			# A table with a label, inventory or column error counts once
			doc_stats[f"{side}_wrong_table"] = len(wrong[(side, "label")] | wrong[(side, "inventory")] | wrong[(side, "column")])
		doc_stats["pairs"] = doc_stats["a_records"] - counts["a_only_records"]
		assert doc_stats["pairs"] == EXPECTED_PAIRS[doc_id], (doc_id, doc_stats["pairs"])
		doc_stats["required"] = doc_stats["pairs"] + counts["A_record_omitted"] + counts["B_record_omitted"] - counts["both_record_omitted"]

	totals = Counter()
	print("doc_id;final;required;pairs;events;tables;A_rec;B_rec;A_wrong_rec;B_wrong_rec;A_omit;B_omit;A_spur;B_spur;"
		"A_wrong_event;B_wrong_event;A_wrong_table;B_wrong_table;A_tab_omit;B_tab_omit;A_errors;B_errors;A_names;B_names;A_numbers;B_numbers")
	for doc_id, doc_stats in sorted(stats.items()):
		for key, value in doc_stats.items():
			totals[key] += value
		a_errors = doc_stats.get("decision_B_right", 0) + doc_stats.get("decision_both_wrong", 0) + doc_stats.get("decision_corrected", 0)
		b_errors = doc_stats.get("decision_A_right", 0) + doc_stats.get("decision_both_wrong", 0) + doc_stats.get("decision_corrected", 0)
		print(f"{doc_id};{doc_stats['final']};{doc_stats['required']};{doc_stats['pairs']};{doc_stats['events']};{doc_stats['tables']};"
			f"{doc_stats['a_records']};{doc_stats['b_records']};{doc_stats['A_wrong_record']};{doc_stats['B_wrong_record']};"
			f"{doc_stats.get('A_record_omitted', 0)};{doc_stats.get('B_record_omitted', 0)};{doc_stats.get('A_record_spurious', 0)};"
			f"{doc_stats.get('B_record_spurious', 0)};{doc_stats['A_wrong_event']};{doc_stats['B_wrong_event']};"
			f"{doc_stats['A_wrong_table']};{doc_stats['B_wrong_table']};{doc_stats.get('A_table_omitted', 0)};{doc_stats.get('B_table_omitted', 0)};"
			f"{a_errors};{b_errors};{doc_stats.get('A_name_errors', 0)};{doc_stats.get('B_name_errors', 0)};"
			f"{doc_stats.get('A_number_errors', 0)};{doc_stats.get('B_number_errors', 0)}")
	print(dict(sorted(totals.items())))

	# Accuracy per record, event and table, counting omissions, with and without the largest document
	largest_doc = max(stats, key=lambda doc_id: stats[doc_id]["required"])
	for side in ("A", "B"):
		required = totals["required"]
		omitted = totals[side + "_record_omitted"]
		wrong_records = totals[side + "_wrong_record"]
		paired = totals["pairs"]
		record_field_errors = totals[side + "_record_field_errors"]
		print(f"{side} records: right {required - omitted - wrong_records}/{required} = {100 * (required - omitted - wrong_records) / required:.1f}%"
			f" | omitted {omitted} | with error {wrong_records} | spurious {totals[side + '_record_spurious']}"
			f" | fields {record_field_errors}/{paired * COMPARED_RECORD_FIELD_COUNT} = {100 * record_field_errors / (paired * COMPARED_RECORD_FIELD_COUNT):.2f}%"
			f" | names misread {totals[side + '_name_errors']} | numbers misread {totals[side + '_number_errors']}"
			f" | family/order fields {totals[side + '_higher_taxon_errors']}")
		largest = stats[largest_doc]
		required_rest = required - largest["required"]
		right_rest = required_rest - (omitted - largest.get(side + "_record_omitted", 0)) - (wrong_records - largest[side + "_wrong_record"])
		print(f"{side} records without {largest_doc}: {right_rest}/{required_rest} = {100 * right_rest / required_rest:.1f}%")
		event_total = totals["events"]
		event_omitted = totals[side + "_event_omitted"]
		wrong_events = totals[side + "_wrong_event"]
		event_fields_compared = (event_total - event_omitted) * COMPARED_EVENT_FIELD_COUNT
		print(f"{side} events: right {event_total - event_omitted - wrong_events}/{event_total} = {100 * (event_total - event_omitted - wrong_events) / event_total:.1f}%"
			f" | omitted {event_omitted} | with error {wrong_events}"
			f" | fields {totals[side + '_event_field_errors']}/{event_fields_compared} = {100 * totals[side + '_event_field_errors'] / event_fields_compared:.2f}%")
		table_total = totals["tables"]
		table_omitted = totals[side + "_table_omitted"]
		wrong_tables = totals[side + "_wrong_table"]
		print(f"{side} tables: right {table_total - table_omitted - wrong_tables}/{table_total} = {100 * (table_total - table_omitted - wrong_tables) / table_total:.1f}%"
			f" | omitted {table_omitted} | spurious {totals[side + '_table_spurious']} | with error {wrong_tables}"
			f" | label fields {totals[side + '_label_field_errors']} | inventory fields {totals[side + '_inventory_field_errors']}"
			f" | column fields {totals[side + '_column_field_errors']} | checklist fields {totals[side + '_checklist_field_errors']}")
	print("field errors by side:", sorted(field_errors_by_side.items(), key=lambda item: -item[1]))
	print("error types by side:", sorted(error_types.items(), key=lambda item: -item[1]))
	for key, example in sorted(error_examples.items()):
		print("  EXAMPLE", key, example)
	print("decision rows:", len(decision_rows), Counter(row["decision"] for row in decision_rows))
	print("decision rows by category:", sorted(Counter((CategoryOf(row), row["decision"]) for row in decision_rows).items()))
	print("both_acceptable fields:", Counter(row["field"] for row in decision_rows if row["decision"] == "both_acceptable").most_common(12))
	print("origin:", Counter(row["origin"] for row in occurrence_rows))
	print("basisOfRecord:", Counter((row["basisOfRecord"], row["basisOfRecord_source"]) for row in occurrence_rows))
	print("eventDate:", sum(1 for row in event_rows if row["eventDate"]), "of", len(event_rows), "events,",
		sum(1 for row in occurrence_rows if row["eventDate"]), "of", len(occurrence_rows), "occurrences;",
		Counter((row["verbatimEventDate"], row["eventDate"]) for row in event_rows if row["verbatimEventDate"] and not row["inherited"].count("verbatimEventDate")).most_common(8))
	print("code_meaning joined from symbols:", sum(1 for row in occurrence_rows if row["code_meaning"]), "of",
		sum(1 for row in occurrence_rows if row["printed_code"]), "with printed_code")
	print("fields missing in older-schema documents, read as null:", dict(legacy_fields_filled))
	print("occurrenceStatus:", Counter(row["occurrenceStatus"] for row in occurrence_rows))
	print("value_kind:", Counter(row["value_kind"] for row in occurrence_rows))
	print("record_origin:", Counter(row["record_origin"] for row in occurrence_rows))
	print("individualCount filled:", sum(1 for row in occurrence_rows if row["individualCount"] != ""),
		"organismQuantity filled:", sum(1 for row in occurrence_rows if row["organismQuantity"] != ""))
	print("identificationQualifier filled:", sum(1 for row in occurrence_rows if row["identificationQualifier"]),
		"family:", sum(1 for row in occurrence_rows if row["family"]), "order:", sum(1 for row in occurrence_rows if row["order"]),
		"vernacularName:", sum(1 for row in occurrence_rows if row["vernacularName"]),
		"threat status:", sum(1 for row in occurrence_rows if row["threat_status_as_printed"]))
	print("source_inconsistency filled, occurrence:", sum(1 for row in occurrence_rows if row["source_inconsistency"]),
		"event:", sum(1 for row in event_rows if row["source_inconsistency"]))
	print("from text:", sum(1 for row in occurrence_rows if row["table_or_figure"] == "text"),
		"from figure:", sum(1 for row in occurrence_rows if row["table_or_figure"].lower().startswith("fig")))
	print("distinct names:", len({row["scientificName"] for row in occurrence_rows}),
		"per doc:", {doc_id[:14]: len({row["scientificName"] for row in occurrence_rows if row["doc_id"] == doc_id}) for doc_id in stats})
	print("eventType:", Counter(row["eventType"] for row in event_rows))
	# What GBIF asks for, per event and per occurrence (through its event)
	event_of = {row["eventID"]: row for row in event_rows}
	for column in ("verbatimCoordinates", "decimalLatitude", "verbatimEventDate", "habitat", "samplingProtocol", "samplingEffort",
			"recordedBy", "stateProvince", "municipality", "verbatimLocality"):
		filled_events = sum(1 for row in event_rows if row[column])
		filled_occurrences = sum(1 for row in occurrence_rows if event_of[row["eventID"]][column])
		print(f"event {column}: {filled_events}/{len(event_rows)} events, {filled_occurrences}/{len(occurrence_rows)} occurrences")
	print("inherited:", Counter(entry.split(":")[0] for row in event_rows for entry in row["inherited"].split("; ") if entry))
	print("empty decision_ids:", sum(1 for row in occurrence_rows if not row["decision_ids"]))

	# Self-check: every adjudicated record once, every occurrence points to an event, and no long copy is left
	assert len(occurrence_rows) == sum(doc_stats["final"] for doc_stats in stats.values())
	assert len({row["occurrenceID"] for row in occurrence_rows}) == len(occurrence_rows)
	assert len(event_of) == len(event_rows)
	assert all(row["eventID"] in event_of for row in occurrence_rows)
	assert all(not row["parentEventID"] or row["parentEventID"] in event_of for row in event_rows)
	assert all(row["basisOfRecord"] in ("HumanObservation", "PreservedSpecimen") for row in occurrence_rows)
	assert all(row["occurrenceStatus"] in ("present", "absent") for row in occurrence_rows)
	assert len(decision_rows) == sum(sum(1 for _ in csv.DictReader(open(path, encoding="utf-8-sig"))) for path in glob.glob(os.path.join(ROOT, "adjudicated", "*_decisions.csv")))
	# A 16-word copy is caught, a 15-word copy is not, and a 16-word quote is caught even when it is not in the PDF
	test_words = [f"w{index}" for index in range(30)]
	test_shingles = {tuple(test_words[index:index + MAX_QUOTE_WORDS + 1]) for index in range(len(test_words) - MAX_QUOTE_WORDS)}
	assert CopiedRuns(" ".join(test_words[:16]) + " x", test_shingles) == [" ".join(test_words[:16])]
	assert CopiedRuns(" ".join(test_words[:15]) + " x", test_shingles) == []
	assert LongQuotes("as in '" + " ".join(["z"] * 16) + "' here") and not LongQuotes("B's and '" + " ".join(["z"] * 15) + "'")
	# A dict repr with a long string of our own words is not a quote, but a long quote inside one of its strings still is
	assert not FindLongCopies(repr({"notes": " ".join(["z"] * 16)}), set())
	assert FindLongCopies(repr({"notes": "p3 says '" + " ".join(["z"] * 16) + "'"}), set())
	# table_id on a record row (r51) is a record error, on a table row (k5) an inventory error
	table_id_row = {"field": "table_id", "table_or_figure": "Anexo I", "kind": "wording", "a_index": "r51", "b_index": "r51"}
	assert CategoryOf(table_id_row) == "record"
	assert CategoryOf({**table_id_row, "a_index": "k5", "b_index": "k5"}) == "inventory"
	# A child event with no date takes its parent's and says so; coordinates never pass down
	test_events = [{"event_id": "e1", "parent_event_id": None, **{field: None for field in EVENT_COLUMNS}},
		{"event_id": "e2", "parent_event_id": "e1", **{field: None for field in EVENT_COLUMNS}}]
	test_events[0].update(verbatimEventDate="março de 2013", verbatimCoordinates="18°S")
	child = EventRows("t", test_events, "", "")[1]
	assert child["verbatimEventDate"] == "março de 2013" and child["inherited"] == "verbatimEventDate:e1" and child["verbatimCoordinates"] == ""
	assert child["eventDate"] == "2013-03" and child["eventDate_derivation"].endswith("of e1")
	# eventDate: the pilot's printed periods, and the ambiguous ones stay empty
	assert DeriveEventDate("entre março e junho de 2013") == "2013-03/2013-06"
	assert DeriveEventDate("entre julho de 2002 e junho de 2003") == "2002-07/2003-06"
	assert DeriveEventDate("31 dias, compreendido entre 3 de maio e 16 de junho de 2006") == "2006-05-03/2006-06-16"
	assert DeriveEventDate("2004") == "2004" and DeriveEventDate("2002 a 2003") == "2002/2003"
	assert DeriveEventDate("dezembro a março de 1981") == ""  # which December?
	assert DeriveEventDate("iniciados em 1999 ... concluídos em 2001 ... sempre no período entre julho e dezembro") == ""
	assert DeriveEventDate("iniciados em 1999 ... sempre no período entre julho e dezembro") == ""
	assert DeriveEventDate("Dia 1") == "" and DeriveEventDate("31 de fevereiro de 2006") == ""
	# code_meaning: the table's symbol first, the document's next, several codes split
	symbols = [{"symbol": "n", "meaning_as_printed": "campo de A.P. Nunes"}, {"symbol": "t", "meaning_as_printed": "campo de F. Tizianel"}]
	assert CodeMeaning("n", symbols, []) == "campo de A.P. Nunes" and CodeMeaning("n", [], symbols) == "campo de A.P. Nunes"
	assert CodeMeaning("n t", symbols, []) == "n: campo de A.P. Nunes | t: campo de F. Tizianel" and CodeMeaning("SCS", symbols, []) == ""
	assert not long_copies, f"{len(long_copies)} cells copy more than {MAX_QUOTE_WORDS} words of the source: rewrite them in adjudicated/"


if __name__ == "__main__":
	main()
