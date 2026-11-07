"""Harvest INSPIRE records into literature/corpus.md.

Usage:
  python3 inspire.py refs   <arXiv-id> [--corpus PATH]   # papers cited by the paper
  python3 inspire.py cites  <arXiv-id> [--corpus PATH]   # papers citing the paper
  python3 inspire.py search "<INSPIRE query>" [--corpus PATH] [--size N]
Without --corpus, rows are printed instead of merged.
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

API = "https://inspirehep.net/api/literature"
FIELDS = "control_number,titles.title,arxiv_eprints.value"
HEADER = "| recid | arXiv | short title | found-via | tags | verdict | reason | status |"
_last_call = [0.0]


def _get(params):
    # INSPIRE allows 15 requests per 5 s per IP; stay well below it.
    wait = 0.5 - (time.monotonic() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    url = API + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=60) as resp:
        _last_call[0] = time.monotonic()
        return json.load(resp)


def _clean(text):
    return " ".join(text.replace("|", "/").split())


def record_row(meta, via):
    arx = meta.get("arxiv_eprints") or [{}]
    titles = meta.get("titles") or [{}]
    return {"recid": str(meta["control_number"]), "arxiv": arx[0].get("value", ""),
            "title": _clean(titles[0].get("title", ""))[:100], "via": via}


def unlinked_row(ref, via):
    """Row for a reference INSPIRE could not match to a record."""
    r = ref.get("reference", {})
    title = (r.get("title") or {}).get("title") or " ".join(r.get("misc", []))
    return {"recid": "", "arxiv": r.get("arxiv_eprint", ""),
            "title": _clean(title)[:100] or "(unparsed reference)", "via": via}


def key(row):
    return row["recid"] or ("arXiv:" + row["arxiv"] if row["arxiv"] else "title:" + row["title"].lower())


def _records(query, size=250):
    out, page = [], 1
    while True:
        d = _get({"q": query, "size": size, "page": page, "fields": FIELDS})
        out += [h["metadata"] for h in d["hits"]["hits"]]
        if len(out) >= d["hits"]["total"] or not d["hits"]["hits"]:
            return out
        page += 1


def _recid_of(arxiv):
    hits = _get({"q": f"arxiv:{arxiv}", "fields": "control_number"})["hits"]["hits"]
    if len(hits) != 1:
        sys.exit(f"expected one INSPIRE record for arXiv:{arxiv}, got {len(hits)}")
    return hits[0]["metadata"]["control_number"]


def refs_rows(arxiv):
    recid = _recid_of(arxiv)
    meta = _get({"q": f"recid:{recid}", "fields": "references.record,references.reference"})
    refs = meta["hits"]["hits"][0]["metadata"].get("references", [])
    via = f"ref:{arxiv}"
    rows = [record_row(m, via) for m in _records(f"citedby:recid:{recid}")]
    rows += [unlinked_row(r, via) for r in refs if "record" not in r]
    return rows, len(refs)


def cites_rows(arxiv):
    recid = _recid_of(arxiv)
    rows = [record_row(m, f"cites:{arxiv}") for m in _records(f"refersto:recid:{recid}")]
    return rows, len(rows)


def search_rows(query, size):
    d = _get({"q": query, "size": size, "fields": FIELDS, "sort": "mostrecent"})
    rows = [record_row(h["metadata"], f"search:{query}") for h in d["hits"]["hits"]]
    return rows, d["hits"]["total"]


def parse_corpus(text):
    """Return (lines, {key: line index}) for the data rows of the corpus table."""
    lines = text.splitlines()
    index = {}
    for i, line in enumerate(lines):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not line.startswith("|") or len(cells) != 8 or cells[0] in ("recid", "---"):
            continue
        index[key({"recid": cells[0], "arxiv": cells[1], "title": cells[2]})] = i
    return lines, index


def merge(text, rows):
    """Append unseen rows; for seen rows add the new found-via tag. Returns (text, n_new)."""
    lines, index = parse_corpus(text)
    n_new = 0
    for row in rows:
        k = key(row)
        if k in index:
            cells = lines[index[k]].strip().strip("|").split("|")
            vias = [v.strip() for v in cells[3].split(";")]
            if row["via"] not in vias:
                cells[3] = " " + "; ".join(vias + [row["via"]]) + " "
                lines[index[k]] = "|" + "|".join(cells) + "|"
            continue
        lines.append(f"| {row['recid']} | {row['arxiv']} | {row['title']} | {row['via']} |  |  |  | new |")
        index[k] = len(lines) - 1
        n_new += 1
    return "\n".join(lines) + "\n", n_new


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("mode", choices=["refs", "cites", "search"])
    p.add_argument("target")
    p.add_argument("--corpus")
    p.add_argument("--size", type=int, default=50)
    a = p.parse_args(argv)
    if a.mode == "refs":
        rows, total = refs_rows(a.target)
    elif a.mode == "cites":
        rows, total = cites_rows(a.target)
    else:
        rows, total = search_rows(a.target, a.size)
    if not a.corpus:
        for r in rows:
            print(f"| {r['recid']} | {r['arxiv']} | {r['title']} | {r['via']} |")
        print(f"hits={total} rows={len(rows)}")
        return
    with open(a.corpus) as f:
        text = f.read()
    text, n_new = merge(text, rows)
    with open(a.corpus, "w") as f:
        f.write(text)
    print(f"hits={total} rows={len(rows)} new={n_new}")


if __name__ == "__main__":
    main()
