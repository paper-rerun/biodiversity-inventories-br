# Check, not data: match every distinct printed name of occurrence.csv against the GBIF backbone and write qa/name_match.csv
# The dataset is not touched. One request at a time, with a pause, so the run stays light
# Usage: python -X utf8 method/name_match.py   (paths are relative to the biodiversidade-piloto folder)
import csv
import json
import os
import re
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATCH_URL = "https://api.gbif.org/v1/species/match?"
PAUSE_SECONDS = 0.3
# Kingdom hint per document, so a plant genus does not match an animal homonym
PLANT_DOCUMENTS = {"calixto2014-fitossociologia-caatinga-petrolina-pe", "sandel2000-floristica-tapajos-km69-pa",
	"vieira2002-fitossociologia-machadinho-ro", "tourinho1998-manguezal-braganca-pa", "pereira2012-caatinga-fazenda-tamandua-pb"}
# Bees and plants in one document: the plants are Tabela 5 and the 12 trees of the site descriptions (text)
# silva2009b: the 6 palms of the p15 text
PLANT_TABLES = {("lopes2010-abelhas-plantas-apicolas-teresina-pi", "Tabela 5"), ("lopes2010-abelhas-plantas-apicolas-teresina-pi", "text"),
	("silva2009b-mamiferos-aves-iracema-am", "text")}
# A match that stops at one of these ranks found nothing in that kingdom: the other kingdom is tried (rego2008 names
# bees and the plants they nest in, in one text block)
NOTHING_FOUND_RANKS = {"KINGDOM", "PHYLUM", "CLASS", ""}
# Printed qualifiers that leave the name above species on purpose ('Inga sp.', 'Astyanax aff. ...')
OPEN_QUALIFIERS = ("sp.", "spp.", "sp ", "aff.", "cf.", "gr.")


def KingdomOf(doc_id, table_or_figure=""):
	return "Plantae" if doc_id in PLANT_DOCUMENTS or (doc_id, table_or_figure) in PLANT_TABLES else "Animalia"


def MatchName(name, kingdom):
	query = urllib.parse.urlencode({"name": name, "kingdom": kingdom, "verbose": "false"})
	request = urllib.request.Request(MATCH_URL + query, headers={"User-Agent": "open-tables-pilot (name check)"})
	with urllib.request.urlopen(request, timeout=30) as response:
		return json.load(response)


def QueryName(name):
	# Morphospecies like 'Ataenius sp.1' go to GBIF as the genus alone, or the fuzzy match picks a real species by the letters
	morphospecies = re.match(r"^(\S+)\s+spp?\.", name)
	return morphospecies.group(1) if morphospecies else name


def ResultClass(match_type, qualifier, name):
	# EXACT and FUZZY as GBIF says; HIGHERRANK split into names printed above species on purpose and the rest
	if match_type == "HIGHERRANK":
		if qualifier or any(each in name + " " for each in OPEN_QUALIFIERS):
			return "higherrank_open_name"
		return "higherrank"
	# A morphospecies sent as its genus comes back EXACT, but the name is still above species
	if match_type == "EXACT" and QueryName(name) != name:
		return "higherrank_open_name"
	return match_type.lower()


def main():
	names = defaultdict(lambda: {"docs": set(), "records": 0, "qualifier": ""})
	for row in csv.DictReader(open(os.path.join(ROOT, "occurrence.csv"), encoding="utf-8")):
		# An empty name cell (illegible, or no name printed) has nothing to match
		if not row["scientificName"]:
			continue
		entry = names[(row["scientificName"], KingdomOf(row["doc_id"], row["table_or_figure"]))]
		entry["docs"].add(row["doc_id"])
		entry["records"] += 1
		entry["qualifier"] = entry["qualifier"] or row["identificationQualifier"]
	output_rows = []
	for (name, kingdom_hint), entry in sorted(names.items()):
		kingdom = kingdom_hint
		match = MatchName(QueryName(name), kingdom)
		time.sleep(PAUSE_SECONDS)
		if match.get("rank", "") in NOTHING_FOUND_RANKS:
			other_kingdom = "Animalia" if kingdom == "Plantae" else "Plantae"
			retry = MatchName(QueryName(name), other_kingdom)
			time.sleep(PAUSE_SECONDS)
			if retry.get("rank", "") not in NOTHING_FOUND_RANKS:
				match, kingdom = retry, other_kingdom + " (retry)"
		output_rows.append({"verbatimScientificName": name, "kingdom_hint": kingdom_hint, "doc_ids": "; ".join(sorted(entry["docs"])),
			"records": entry["records"], "kingdom_used": kingdom, "identificationQualifier": entry["qualifier"], "matchType": match.get("matchType", ""),
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
	assert ResultClass("EXACT", "", "Augochlora sp. 1") == "higherrank_open_name"
	assert QueryName("Ataenius sp.1") == "Ataenius" and QueryName("Megachile sp. 2") == "Megachile" and QueryName("Rhea americana") == "Rhea americana"
	assert KingdomOf("lopes2010-abelhas-plantas-apicolas-teresina-pi", "Tabela 5") == "Plantae"
	assert KingdomOf("lopes2010-abelhas-plantas-apicolas-teresina-pi", "Tabela 1") == "Animalia"


if __name__ == "__main__":
	main()
