"""Batch-fetch Wikimedia Commons files as 2560-px thumbnails (one API call, slow downloads) and log licences to SOURCES.jsonl."""
import json, re, sys, time, urllib.parse, urllib.request
UA = "lemo-opuscar/1.0 (https://github.com/lemomo-ai/lemo-opuscar)"
def get(u):
    for k in range(6):
        try:
            return urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": UA}), timeout=90).read()
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(30 * (k + 1))
    raise SystemExit("429 persists")
strip = lambda s: re.sub(r"<[^>]+>", "", s or "").strip()
items = [l.split("\t") for l in open(sys.argv[1]).read().strip().splitlines()]
api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "titles": "|".join("File:" + t for _, t in items),
      "prop": "imageinfo", "iiprop": "url|size|extmetadata", "iiurlwidth": 1920, "format": "json"})
pages = {p["title"]: p for p in json.loads(get(api))["query"]["pages"].values()}
norm = {n["from"]: n["to"] for n in json.loads(get(api)).get("query", {}).get("normalized", [])} if False else {}
log = open("SOURCES.jsonl", "a")
for name, t in items:
    p = pages.get("File:" + t) or next((v for k, v in pages.items() if k.replace("_", " ") == "File:" + t.replace("_", " ")), None)
    if not p or "imageinfo" not in p: print("MISSING", t); continue
    ii = p["imageinfo"][0]; em = ii.get("extmetadata", {}); v = lambda k: strip(em.get(k, {}).get("value", ""))
    url = ii.get("thumburl") or ii["url"]; ext = "jpg"
    open(f"raw/{name}.{ext}", "wb").write(get(url)); time.sleep(12)
    rec = dict(name=name, file=f"raw/{name}.{ext}", title="File:" + t, page=ii.get("descriptionurl"), date=v("DateTimeOriginal"),
               credit=v("Artist") or v("Credit"), license=v("LicenseShortName"), license_url=v("LicenseUrl"), size=f"{ii['width']}x{ii['height']}")
    log.write(json.dumps(rec, ensure_ascii=False) + "\n"); print(name, rec["license"], "|", rec["credit"][:60], "|", rec["date"][:20])
