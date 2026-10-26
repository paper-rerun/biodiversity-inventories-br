# Check, not data: match every distinct printed name of occurrence.csv against the GBIF backbone and write qa/name_match.csv
# The dataset is not touched. One request at a time, with a pause, so the run stays light
# Usage: python -X utf8 method/name_match.py   (paths are relative to the biodiversidade-piloto folder)
import csv
import json
import os
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATCH_URL = "https://api.gbif.org/v1/species/match?"
PAUSE_SECONDS = 0.3
# Kingdom hint per document, so a plant genus does not match an animal homonym
PLANT_DOCUMENTS = {"calixto2014-fitossociologia-caatinga-petrolina-pe", "sandel2000-floristica-tapajos-km69-pa"}
# Printed qualifiers that leave the name above species on purpose ('Inga sp.', 'Astyanax aff. ...')
OPEN_QUALIFIERS = ("sp.", "spp.", "sp ", "aff.", "cf.", "gr.")


def KingdomOf(doc_id):
	return "Plantae" if doc_id in PLANT_DOCUMENTS else "Animalia"


def MatchName(name, kingdom):
	query = urllib.parse.urlencode({"name": name, "kingdom": kingdom, "verbose": "false"})
	request = urllib.request.Request(MATCH_URL + query, headers={"User-Agent": "open-tables-pilot (name check)"})
	with urllib.request.urlopen(request, timeout=30) as response:
		return json.load(response)


def ResultClass(match_type, qualifier, name):
	# EXACT and FUZZY as GBIF says; HIGHERRANK split into names printed above species on purpose and the rest
	if match_type == "HIGHERRANK":
		if qualifier or any(each in name + " " for each in OPEN_QUALIFIERS):
			return "higherrank_open_name"
		return "higherrank"
	return match_type.lower()


def main():
	names = defaultdict(lambda: {"docs": set(), "records": 0, "qualifier": ""})
	for row in csv.DictReader(open(os.path.join(ROOT, "occurrence.csv"), encoding="utf-8")):
		entry = names[(row["scientificName"], KingdomOf(row["doc_id"]))]
		entry["docs"].add(row["doc_id"])
		entry["records"] += 1
		entry["qualifier"] = entry["qualifier"] or row["identificationQualifier"]
	output_rows = []
	for (name, kingdom), entry in sorted(names.items()):
		match = MatchName(name, kingdom)
		time.sleep(PAUSE_SECONDS)
		output_rows.append({"verbatimScientificName": name, "kingdom_hint": kingdom, "doc_ids": "; ".join(sorted(entry["docs"])),
			"records": entry["records"], "identificationQualifier": entry["qualifier"], "matchType": match.get("matchType", ""),
			"result": ResultClass(match.get("matchType", ""), entry["qualifier"], name), "confidence": match.get("confidence", ""),
			"gbif_scientificName": match.get("scientificName", ""), "gbif_rank": match.get("rank", ""),
			"gbif_status": match.get("status", ""), "gbif_usageKey": match.get("usageKey", ""),
			"gbif_family": match.get("family", ""), "gbif_note": match.get("note", "")})
	os.makedirs(os.path.join(ROOT, "qa"), exist_ok=True)
	with open(os.path.join(ROOT, "qa", "name_match.csv"), "w", encoding="utf-8", newline="") as output_file:
		writer = csv.DictWriter(output_file, fieldnames=list(output_rows[0].keys()))
		writer.writeheader()
		writer.writerows(output_rows)

	# Numbers for RODADA.md: per name, per record and per document
	print("names:", len(output_rows), Counter(row["result"] for row in output_rows))
	print("records:", sum(row["records"] for row in output_rows), Counter({result: sum(row["records"] for row in output_rows if row["result"] == result) for result in {row["result"] for row in output_rows}}))
	print("status of exact and fuzzy:", Counter(row["gbif_status"] for row in output_rows if row["result"] in ("exact", "fuzzy")))
	per_doc = defaultdict(Counter)
	for row in output_rows:
		for doc_id in row["doc_ids"].split("; "):
			per_doc[doc_id][row["result"]] += 1
	for doc_id, counts in sorted(per_doc.items()):
		print(doc_id, sum(counts.values()), dict(counts))
	for row in output_rows:
		if row["result"] in ("fuzzy", "higherrank", "none"):
			print(f"  {row['result']}: {row['verbatimScientificName']} -> {row['gbif_scientificName']} ({row['gbif_rank']}, {row['confidence']})")

	# Self-check: one row per printed name and kingdom, and the class rule on the three kinds of HIGHERRANK
	assert len({(row["verbatimScientificName"], row["kingdom_hint"]) for row in output_rows}) == len(output_rows)
	assert ResultClass("HIGHERRANK", "sp.", "Inga sp.") == "higherrank_open_name"
	assert ResultClass("HIGHERRANK", "", "Bufo paracnemis") == "higherrank"
	assert ResultClass("EXACT", "", "Rhea americana") == "exact"


if __name__ == "__main__":
	main()
