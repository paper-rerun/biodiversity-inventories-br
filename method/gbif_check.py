# GBIF check for one candidate: datasets by text, then 3 species near the site in the years of the document
# Usage: python -I gbif_check.py check.json out.json   (check.json: {"id", "dataset_queries": [...], "species": [...], "years": "2005,2007", "state": "Mato Grosso do Sul", "lat": -19.5, "lon": -57.0, "radius_deg": 0.5, "recorded_by": ["Pott"]})
import sys, json, urllib.request, urllib.parse

API = "https://api.gbif.org/v1/"


def get(path, params):
	url = API + path + "?" + urllib.parse.urlencode(params, doseq=True)
	with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "PaperRerun-OpenTables"}), timeout=60) as response:
		return url, json.loads(response.read().decode("utf-8"))


check = json.load(open(sys.argv[1], encoding="utf-8"))
out = {"id": check["id"], "datasets": [], "species": []}
# Dataset search by title words, institution and author
for query in check.get("dataset_queries", []):
	url, data = get("dataset/search", {"q": query, "limit": 10})
	hits = [{"key": each["key"], "title": each.get("title"), "publisher": each.get("publishingOrganizationTitle")} for each in data.get("results", [])]
	out["datasets"].append({"query": query, "url": url, "count": data.get("count"), "top": hits})
# Occurrences of each species near the site and in the document years
for species in check.get("species", []):
	params = {"scientificName": species, "country": "BR", "limit": 5}
	if check.get("years"):
		params["year"] = check["years"]
	if check.get("lat") is not None:
		radius = check.get("radius_deg", 0.5)
		params["decimalLatitude"] = f"{check['lat'] - radius},{check['lat'] + radius}"
		params["decimalLongitude"] = f"{check['lon'] - radius},{check['lon'] + radius}"
	elif check.get("state"):
		params["stateProvince"] = check["state"]
	url, data = get("occurrence/search", params)
	sample = [{"dataset": each.get("datasetName") or each.get("datasetKey"), "recordedBy": each.get("recordedBy"), "year": each.get("year"), "locality": each.get("locality"), "basisOfRecord": each.get("basisOfRecord")} for each in data.get("results", [])]
	# Same place and years, any taxon, full-text match on an author surname (recordedBy only matches the exact full string)
	by_author = {}
	for name in check.get("recorded_by", []):
		author_params = {key: value for key, value in params.items() if key != "scientificName"}
		author_params["q"] = name
		author_url, author_data = get("occurrence/search", author_params)
		by_author[name] = author_data.get("count")
	out["species"].append({"name": species, "url": url, "count": data.get("count"), "sample": sample, "count_recorded_by_author": by_author})
open(sys.argv[2], "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, indent=1))
