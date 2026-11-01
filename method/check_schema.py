# Self-check for schema.json: the schema is valid, a tiny transcription passes, a broken one fails
# Usage: python -s method/check_schema.py, or with -I: python -I -c "import site, sys, runpy; sys.path.append(site.getusersitepackages()); runpy.run_path(r'method/check_schema.py', run_name='__main__')"   (jsonschema lives in the user site)
import json, copy, pathlib
from jsonschema import Draft202012Validator

ROOT = pathlib.Path(__file__).resolve().parent.parent
schema = json.loads((ROOT / "schema.json").read_text(encoding="utf-8"))
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)

# One point of the Taquari fish matrix (Anexo I, p19), cut down to one cell
EVENT_NULLS = {key: None for key in ["event_label_as_printed", "verbatimLocality", "municipality", "stateProvince", "country", "verbatimCoordinates", "verbatimCoordinateSystem", "decimalLatitude", "decimalLongitude", "geodeticDatum", "verbatimElevation", "verbatimEventDate", "habitat", "samplingProtocol", "samplingEffort", "sampleSize_as_printed", "recordedBy_as_printed", "material_fate", "material_fate_as_printed", "source_inconsistency", "notes"]}
study = dict(EVENT_NULLS, event_id="e1", parent_event_id=None, event_level="study", verbatimEventDate="entre março e junho de 2013", material_fate="released_or_observed", material_fate_as_printed="identificados no campo, fotografados e soltos", field_pages={"verbatimEventDate": 7, "material_fate_as_printed": 9})
point = dict(EVENT_NULLS, event_id="e2", parent_event_id="e1", event_level="point", event_label_as_printed="1", verbatimCoordinates="18°14'10\"S - 55°40'41\"O", habitat="Rio Taquari", field_pages={"verbatimCoordinates": 8, "habitat": 8})
labels = {"row_identity": "espécies com cabeçalhos de ordem e família", "column_axis": "events", "presence_shown_as": "count", "absence_shown_as": None, "symbols": [], "quantity_meaning": "abundâncias, caption p19", "heading_levels": ["ORDEM", "Família"], "threat_list_as_printed": None, "footnotes": [], "source_inconsistency": None}
columns = [
	{"column_id": "c1", "header_as_printed": "Táxon", "role": "taxon_name", "event_id": None, "organismQuantityType_as_printed": None, "notes": None},
	{"column_id": "c2", "header_as_printed": "Estação / A / Pontos / 1", "role": "event_count", "event_id": "e2", "organismQuantityType_as_printed": "abundâncias", "notes": None},
]
table = {"table_id": "k1", "page": 19, "label": "Anexo I", "kind": "occurrence_matrix", "caption_summary": None, "event_ids": ["e2"], "data_cells": 1, "transcribed": 1, "skipped_cells": 0, "skipped_reason": None, "table_level_labels": labels, "columns": columns}
record = {"record_id": "r1", "event_id": "e2", "table_id": "k1", "column_id": "c2", "row_index": 1, "position_in_cell": 1, "event_detail_as_printed": None, "page": 19, "table_or_figure": "Anexo I", "value_kind": "count", "verbatimScientificName": "Abramites hypselonotus (Günther1868)", "identificationQualifier": None, "name_in_full_as_printed": None, "name_in_full_page": None, "name_status": None, "family_as_printed": "Anostomidae", "family_source": "heading_row", "order_as_printed": "CHARACIFORMES", "order_source": "heading_row", "higher_group_as_printed": None, "vernacularName": None, "occurrenceStatus": "present", "individualCount": None, "organismQuantity": 4, "organismQuantityType": "abundâncias", "value_as_printed": "4", "printed_code": None, "record_origin": "this_study", "cited_source_as_printed": None, "recording_method_as_printed": None, "voucher_as_printed": None, "threat_status_as_printed": None, "threat_status_source_as_printed": None, "line_attributes": [], "source_inconsistency": None, "notes": None}
checklist = {
	"events": [{"event_id": "e1", "field": "verbatimEventDate", "status": "filled", "page": 7}, {"event_id": "e2", "field": "verbatimEventDate", "status": "inherited", "page": 7}],
	"tables": [{"table_id": "k1", "symbols_in_cells": [], "symbols_with_meaning": [], "heading_rows_carried": True, "event_columns": 1, "event_columns_with_event_id": 1, "derived_or_total_cells_skipped": 0, "attribute_columns_in_line_attributes": None}],
	"rows": [{"table_id": "k1", "taxon_lines_printed": 1, "distinct_row_index_in_records": 1, "lines_without_records": [], "rows_match": True}],
	"codes": [],
	"totals": {"tables": 1, "data_cells": 1, "transcribed": 1, "skipped_cells": 0, "records": 1, "events": 2, "every_table_closes": True},
}
good = {"doc_id": "freydargas2014-peixes-taquari-pantanal-ms", "transcriber": "A", "schema_version": schema["version"], "events": [study, point], "tables": [table], "records": [record], "end_checklist": checklist}
errors = list(validator.iter_errors(good))
assert not errors, [error.message for error in errors]

# A computed decimal latitude is allowed by type, but a wrong occurrenceStatus or a missing page must fail
bad = copy.deepcopy(good)
bad["records"][0]["occurrenceStatus"] = "probably present"
del bad["records"][0]["page"]
assert len(list(validator.iter_errors(bad))) >= 2

# 2.0: code_meaning left the record, 'mixed' left record_origin, and the material fate is a closed class
old_style = copy.deepcopy(good)
old_style["records"][0]["code_meaning"] = "presente"
old_style["records"][0]["record_origin"] = "mixed"
old_style["events"][0]["material_fate"] = "probably kept"
assert len(list(validator.iter_errors(old_style))) >= 3
print("schema ok:", len(schema["rules"]), "rules")
