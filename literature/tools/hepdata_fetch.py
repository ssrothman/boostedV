"""Serially download HEPData records and all their tables (JSON) into the literature cache.

Usage:
  python3 hepdata_fetch.py <cache_root> <nid>=<inspire_recid> [<nid>=<recid> ...]
Writes <cache_root>/<nid>/hepdata/record.json and tables/<safe name>.json; existing files are skipped.
Writes <cache_root>/<nid>/hepdata/NONE when HEPData has no record.
"""
import json
import re
import sys
import subprocess
import time
import urllib.parse
import urllib.request

PAUSE = 6.0


def safe_name(name):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_")[:120] or "table"


def is_json(body):
    """HEPData sometimes serves an HTML error page with HTTP 200."""
    try:
        json.loads(body)
        return True
    except ValueError:
        return False


def table_urls(record):
    """[(table name, json download URL)] from a HEPData record JSON."""
    out = []
    for t in record.get("data_tables", []):
        url = (t.get("data") or {}).get("json")
        if url:
            parts = urllib.parse.urlsplit(url)
            # HEPData pre-encodes "%" and "\" (as %25, %5C) but not spaces or braces; keep "%" so they are not double-encoded.
            path = urllib.parse.quote(parts.path, safe="/%")
            out.append((t.get("name", ""), urllib.parse.urlunsplit(parts._replace(path=path))))
    return out


def get(url, tries=5):
    """(HTTP code, body) via curl with its default User-Agent; Cloudflare on hepdata.net rejects urllib."""
    for k in range(tries):
        time.sleep(PAUSE)
        r = subprocess.run(["curl", "-s", "-L", "--max-time", "120", "-w", "\n%{http_code}", url], capture_output=True)
        body, _, code = r.stdout.rpartition(b"\n")
        code = int(code or 0)
        if code == 200 and is_json(body):
            return 200, body
        if code == 404:
            return 404, b""
        if (code in (429, 503) or code == 200) and k < tries - 1:
            time.sleep(60 * (k + 1))
            continue
        return code, b""
    return 0, b""


def fetch(root, nid, recid):
    import pathlib
    d = pathlib.Path(root) / nid / "hepdata"
    (d / "tables").mkdir(parents=True, exist_ok=True)
    rec_path = d / "record.json"
    if not rec_path.exists():
        code, body = get(f"https://www.hepdata.net/record/ins{recid}?format=json")
        if code == 404:
            (d / "NONE").write_text("no HEPData record\n")
            return "none", 0, 0
        if code != 200:
            return f"record HTTP {code}", 0, 0
        rec_path.write_bytes(body)
    record = json.loads(rec_path.read_text())
    urls = table_urls(record)
    ok = 0
    for name, url in urls:
        p = d / "tables" / (safe_name(name) + ".json")
        if p.exists():
            ok += 1
            continue
        code, body = get(url)
        if code == 200:
            p.write_bytes(body)
            ok += 1
    return "ok", ok, len(urls)


if __name__ == "__main__":
    root = sys.argv[1]
    for arg in sys.argv[2:]:
        nid, recid = arg.split("=")
        print(nid, *fetch(root, nid, recid), flush=True)
