# Adjudicated JSON = a transcription plus provenance fields (origin, decision_ids, adjudicated_on, origin_rule); without them every file must pass schema.json
# Usage: python -I method/check_adjudicated.py E:/Ciencia/dados/biodiversidade
import json, glob, sys, site
sys.path.append(site.getusersitepackages())
from jsonschema import Draft202012Validator
from collections import Counter
root = sys.argv[1]
v = Draft202012Validator(json.load(open(root + "/schema.json", encoding="utf-8")))
PROV = {"origin", "decision_ids", "adjudicated_on", "origin_rule"}
def strip(x, where, seen):
    if isinstance(x, dict):
        for k in list(x):
            if k in PROV:
                seen[(where, k)] += 1
                del x[k]
            else:
                strip(x[k], where if where != "top" else k, seen)
    elif isinstance(x, list):
        for e in x: strip(e, where, seen)
seen = Counter(); bad = 0
for f in sorted(glob.glob(root + "/adjudicated/*.json")):
    d = json.load(open(f, encoding="utf-8"))
    strip(d, "top", seen)
    errs = list(v.iter_errors(d))
    if errs:
        bad += 1
        print(f.split("/")[-1], len(errs), errs[0].message[:150], list(errs[0].path)[:4])
print(seen); print("files with errors after strip:", bad)
assert bad == 0
