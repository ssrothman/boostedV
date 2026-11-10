#!/usr/bin/env python3
"""Regenerate the sample table in samples.tex from DAS (Run3Summer22EE MiniAODv4).

Usage: make_samples_table.py [--datasets FILE] [--tex samples.tex] [--cache FILE] [--refresh]
DAS results are cached in --cache and reused; --refresh discards the cache and requeries.
Needs a valid grid proxy for dasgoclient on a cache miss.
"""
import argparse
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

CAMPAIGN = "Run3Summer22EEMiniAODv4"
GT = "130X_mcRun3_2022_realistic_postEE_v6"
TIER = "MINIAODSIM"
# Only the nominal processing string: excludes FastSim, special-PU and other reprocessings.
PROCESSED_RE = re.compile(rf"^{CAMPAIGN}-{GT}(?:_(ext\d+))?-(v\d+)$")
BEGIN, END = "% BEGIN GENERATED TABLE", "% END GENERATED TABLE"
BEGIN_INCL, END_INCL = "% BEGIN GENERATED INCLUSIVE TABLE", "% END GENERATED INCLUSIVE TABLE"
# Primary-dataset tags that mark a pT, HT or jet-multiplicity slice.
BINNED_RE = re.compile(r"_(PT\w*|HT)-\d|_\dJ_")
# Decay-inclusive samples; where a process has any, its decay-split samples are left out of the
# inclusive table.
DECAY_INCLUSIVE_RE = re.compile(r"(TBbarQ|TbarBQ)_t-channel_4FS_")

T = "_TuneCP5_13p6TeV_"
FXFX, MLM = "amcatnloFXFX-pythia8", "madgraphMLM-pythia8"
PWG = "powheg-pythia8"
HIGH, MED, LOW = "High", "Medium", "Low"

# (process, regex on primary dataset, priority, comment)
FAMILIES = [
    (r"Z($\ell\ell$)+jets", rf"DYto2L-2Jets_MLL-50(_[012]J|_PTLL-\d+)?{T}{FXFX}", HIGH,
     r"NLO; inclusive, jet-multiplicity and $p_T^{\ell\ell}$ bins; $\ell=e,\mu,\tau$"),
    (r"Z($\ell\ell$)+jets", rf"DYto2L-4Jets_MLL-50(_PTLL-\d+(to\d+)?)?{T}{MLM}", HIGH,
     r"LO alternative; inclusive and $p_T^{\ell\ell}$ bins"),
    (r"Z($q\bar q$)+jets", rf"Zto2Q-2Jets_PTQQ-\d+(to\d+)?(_[12]J)?{T}{FXFX}", MED,
     r"NLO; $p_T^{qq}$ bins"),
    (r"Z($q\bar q$)+jets", rf"Zto2Q-4Jets_HT-\d+(to\d+)?{T}{MLM}", MED, r"LO alternative; $H_T$ bins"),
    (r"W($\ell\nu$)+jets", rf"WtoLNu-2Jets(_[012]J|_PTLNu-\d+(to\d+)?(_[12]J)?)?{T}{FXFX}", MED,
     r"NLO; inclusive, jet-multiplicity and $p_T^{\ell\nu}$ bins"),
    (r"W($\ell\nu$)+jets", rf"WtoLNu-4Jets(_MLNu-0to120_HT-\d+(to\d+)?)?{T}{MLM}", MED,
     r"LO alternative; inclusive and $H_T$ bins ($m_{\ell\nu}<120$)"),
    (r"W($q\bar q'$)+jets", rf"Wto2Q-2Jets_PTQQ-\d+(to\d+)?(_[12]J)?{T}{FXFX}", MED,
     r"NLO; $p_T^{qq}$ bins"),
    (r"W($q\bar q'$)+jets", rf"Wto2Q-3Jets_HT-\d+(to\d+)?{T}{MLM}", MED, r"LO alternative; $H_T$ bins"),
    (r"ZZ: Z($\ell\ell$)Z($q\bar q$)", rf"ZZto2L2Q{T}{PWG}", HIGH, "NLO"),
    (r"ZZ: Z($\ell\ell$)Z($q\bar q$)", rf"ZZto2L2Q-1Jets{T}{FXFX}", HIGH,
     "NLO alternative (no LO sample)"),
    (r"ZZ: Z($q\bar q$)Z($q\bar q$)", rf"ZZto4Q-1Jets{T}{FXFX}", LOW, "NLO; only sample"),
    (r"WZ: W($q\bar q'$)Z($\ell\ell$)", rf"WZto2L2Q{T}{PWG}", HIGH, "NLO; only sample"),
    (r"WZ: W($\ell\nu$)Z($q\bar q$)", rf"WZtoLNu2Q{T}{PWG}", LOW, "NLO"),
    (r"WZ: W($\ell\nu$)Z($q\bar q$)", rf"WZtoLNu2Q-1Jets-4FS{T}{FXFX}", LOW,
     "NLO alternative (no LO sample)"),
    (r"WZ: W($q\bar q'$)Z($q\bar q$)", rf"WZto4Q-1Jets-4FS{T}{FXFX}", LOW, "NLO; only sample"),
    (r"WW: W($\ell\nu$)W($q\bar q'$)", rf"WWtoLNu2Q{T}{PWG}", LOW, "NLO"),
    (r"WW: W($\ell\nu$)W($q\bar q'$)", rf"WWtoLNu2Q-1Jets-4FS{T}{FXFX}", LOW,
     "NLO alternative (no LO sample)"),
    (r"WW: W($q\bar q'$)W($q\bar q'$)", rf"WWto4Q{T}{PWG}", LOW, "NLO"),
    (r"WW: W($q\bar q'$)W($q\bar q'$)", rf"WWto4Q-1Jets-4FS{T}{FXFX}", LOW,
     "NLO alternative (no LO sample)"),
    (r"$\gamma$+jets", rf"GJ_PTG-\d+(to\d+)?{T}amcatnlo-pythia8", MED, r"NLO; $p_T^\gamma$ bins"),
    (r"$\gamma$+jets", rf"G-4Jets_HT-\d+(to\d+)?{T}{MLM}", MED, r"LO alternative; $H_T$ bins"),
    (r"$\gamma$+W($q\bar q'$)", rf"WGto2QG-1Jets(_PTG-\d+(to\d+)?)?{T}{FXFX}", LOW,
     r"NLO; inclusive and $p_T^\gamma$ bins"),
    (r"$\gamma$+Z($q\bar q$)", rf"ZGto2QG-1Jets(_PTG-\d+(to\d+)?)?{T}{FXFX}", LOW,
     r"NLO; inclusive and $p_T^\gamma$ bins"),
    (r"$t\bar t$", rf"TTto(2L2Nu|LNu2Q|4Q){T}{PWG}", MED, "NLO; split by decay"),
    (r"$t\bar t$", rf"TTto(2L2Nu|LplusNu2Q|LminusNu2Q|4Q)-3Jets{T}{MLM}", MED,
     "LO alternative; split by decay"),
    ("Single top, $t$-channel", rf"(TBbarQ|TbarBQ)(to(LNu|2Q)-|_)t-channel[-_]4FS{T}powheg-madspin-pythia8",
     LOW, "NLO, 4FS; split by $t$/$\\bar t$; decay-inclusive and split by W decay"),
    ("Single top, $tW$", rf"(TWminus|TbarWplus)to(2L2Nu|LNu2Q|4Q){T}{PWG}", LOW,
     "NLO, diagram removal; split by decay"),
    ("Single top, $s$-channel",
     rf"((TBbartoLplusNuBbar|TbarBtoLminusNuB)-s-channel-4FS{T}amcatnlo-pythia8|TBbarto2Q-s-channel{T}{PWG})",
     LOW, "NLO; no hadronic $\\bar t$ sample"),
    ("QCD multijet", rf"QCD_PT-(?!15to7000)\d+(to\d+)?{T}pythia8", MED, r"LO; $\hat p_T$ bins"),
    ("QCD multijet", rf"QCD-4Jets_HT-\d+(to\d+)?{T}{MLM}", MED, r"LO alternative; $H_T$ bins"),
    ("Higgs, ggH", rf"GluGluHto(2B|2C|CC)(_PT-200)?_M-125{T}powheg-minlo-pythia8", LOW,
     r"$H\to b\bar b$, $c\bar c$; inclusive and $p_T^H>200$"),
    ("Higgs, ggH", rf"GluGluHto2(WtoLNu2Q_M-125{T}powheg-JHUGenV752|Zto2L2Q_M-125{T}powheg-jhugenv7520)-pythia8",
     LOW, r"$H\to WW^*\to\ell\nu qq$, $ZZ^*\to\ell\ell qq$"),
    ("Higgs, ggH", rf"GluGluHtoGG_M-125{T}{FXFX}", LOW,
     r"$H\to gg$ (gluons; decay not verified from generator settings)"),
    ("Higgs, ggH", rf"GluGluHto2Tau_M-125{T}{FXFX}", LOW, r"$H\to\tau\tau$"),
    ("Higgs, ggZH", rf"ggZH_Hto2(B|C|Glu)_Zto2(L|Q)_M-125{T}{PWG}", LOW,
     r"$gg\to ZH$ only; $H\to b\bar b, c\bar c, gg$"),
    ("Higgs, ggZH", rf"GluGluZH_Zto2(L|Q)_Hto2Wto(4Q|LNu2Q)_M-125{T}powheg-jhugen-pythia8", LOW,
     r"$gg\to ZH$ only; $H\to WW^*$ (semi-)hadronic"),
    (r"Higgs, $t\bar tH$", rf"TTH(_Hto2B|toNon2B)_M-125{T}{PWG}", LOW,
     r"$H\to b\bar b$ and all other decays"),
    ("Higgs, VBF", rf"VBFHto2(B|C)_M-125{T}{PWG}", LOW, r"$H\to b\bar b$, $c\bar c$"),
    ("Higgs, VBF", rf"VBFHto2WtoLNu2Q_M-125{T}powheg-JHUGenV752-pythia8", LOW, r"$H\to WW^*\to\ell\nu qq$"),
    ("Higgs, VBF", rf"VBFHtoGG_M-125{T}amcatnlo-pythia8", LOW, r"$H\to gg$ (gluons; decay not verified from generator settings)"),
    ("Higgs, $WH$", rf"W(plus|minus)H_Hto2(B|C)_Wto(2Q|LNu)_M-125{T}{PWG}", LOW,
     r"$H\to b\bar b, c\bar c$; W$\to qq'$, $\ell\nu$"),
    ("Higgs, $WH$", rf"W(plus|minus)H_Hto2Glu_WtoLNu_M-125{T}powheg-minlo-pythia8", LOW,
     r"$H\to gg$; W$\to\ell\nu$"),
    ("Higgs, $WH$", rf"W(plus|minus)H_Wto(2Q|LNu)_Hto2Wto(4Q|LNu2Q)_M-125{T}powheg-minlo-jhugen-pythia8", LOW,
     r"$H\to WW^*$ (semi-)hadronic"),
    (r"Higgs, $q\bar q\to ZH$", rf"ZH_Hto2(B|C)_Zto2(L|Q)_M-125{T}{PWG}", LOW,
     r"$H\to b\bar b, c\bar c$; Z$\to\ell\ell$, $qq$"),
    (r"Higgs, $q\bar q\to ZH$", rf"ZH_Hto2Glu_Zto2L_M-125{T}powheg-minlo-pythia8", LOW,
     r"$H\to gg$; Z$\to\ell\ell$"),
    (r"Higgs, $q\bar q\to ZH$", rf"ZH_Zto2(L|Q)_Hto2Wto(4Q|LNu2Q)_M-125{T}powheg-minlo-jhugen-pythia8", LOW,
     r"$H\to WW^*$ (semi-)hadronic"),
    (r"BSM Z$'\to b\bar b$", rf"ZprimeTobb_M1000{T}pythia8", LOW,
     "Only mass point in 20--1000 GeV; 2--9 TeV also exist"),
    ("Triboson", rf"(WWW_4F{T}amcatnlo-madspin|(WWZ_4F|WZZ|ZZZ){T}amcatnlo)-pythia8", LOW,
     "NLO; inclusive decays"),
]

# Processes with no central Run3Summer22EE sample: (process, priority, comment)
MISSING = [
    (r"$gg\to H$", LOW, r"Private production; $H\to WW^*\to 4q$; $H\to ZZ^*\to\nu\nu q\bar q$, $4q$"),
    (r"VBF $H$", LOW, r"Private production; $H\to\tau\tau$; $H\to WW^*\to 4q$; "
     r"$H\to ZZ^*\to\ell\ell q\bar q$, $\nu\nu q\bar q$, $4q$"),
    (r"$W^\pm H$", LOW, r"Private production; $H\to\tau\tau$; $H\to ZZ^*\to\ell\ell q\bar q$, $\nu\nu q\bar q$, $4q$; $H\to gg$ with $W\to q\bar q'$"),
    (r"$q\bar q\to ZH$", LOW, r"Private production; $H\to\tau\tau$; $H\to ZZ^*\to\ell\ell q\bar q$, $\nu\nu q\bar q$, $4q$; $H\to gg$ with $Z\to q\bar q$"),
    (r"$gg\to ZH$", LOW, r"Private production; $H\to\tau\tau$; $H\to ZZ^*\to\ell\ell q\bar q$, $\nu\nu q\bar q$, $4q$; $H\to gg$ with $Z\to q\bar q$"),
    (r"BSM V$'\to q\bar q$ (+V, jets, $\gamma$)", LOW, "Private production; mass points TBD"),
]

GENERATORS = {
    "amcatnloFXFX-pythia8": r"MG5\_aMC@NLO (FxFx) + Pythia8",
    "amcatnlo-pythia8": r"MG5\_aMC@NLO + Pythia8",
    "amcatnlo-madspin-pythia8": r"MG5\_aMC@NLO + MadSpin + Pythia8",
    "madgraphMLM-pythia8": r"MG5\_aMC LO (MLM) + Pythia8",
    "powheg-pythia8": "POWHEG + Pythia8",
    "powheg-madspin-pythia8": "POWHEG + MadSpin + Pythia8",
    "powheg-minlo-pythia8": "POWHEG MiNLO + Pythia8",
    "powheg-JHUGenV752-pythia8": "POWHEG + JHUGen + Pythia8",
    "powheg-jhugenv7520-pythia8": "POWHEG + JHUGen + Pythia8",
    "powheg-jhugen-pythia8": "POWHEG + JHUGen + Pythia8",
    "powheg-minlo-jhugen-pythia8": "POWHEG MiNLO + JHUGen + Pythia8",
    "pythia8": "Pythia8",
}


def parse_dataset(name):
    """Split a DAS name into (primary, ext, version); None if not a nominal campaign dataset."""
    parts = name.split("/")
    if len(parts) != 4 or parts[0] or parts[3] != TIER:
        return None
    m = PROCESSED_RE.match(parts[2])
    return (parts[1], m.group(1), m.group(2)) if m else None


MULTI = {"2L2Nu": r"2\ell2\nu", "LNu2Q": r"\ell\nu 2q", "LplusNu2Q": r"\ell^+\nu 2q",
         "LminusNu2Q": r"\ell^-\bar\nu 2q", "4Q": "4q"}
W_DECAY = {"LNu": r"\ell\nu", "2Q": r"q\bar q'"}
Z_DECAY = {"2L": r"\ell\ell", "2Q": r"q\bar q"}
H_DECAY = {"GG": "gg", "2Tau": r"\tau\tau", "2B": r"b\bar b", "Non2B": r"\textrm{non-}b\bar b", "2C": r"c\bar c", "CC": r"c\bar c",
           "2Glu": "gg",
           "2WtoLNu2Q": r"WW^*\to\ell\nu q\bar q'", "2Wto4Q": r"WW^*\to 4q",
           "2Zto2L2Q": r"ZZ^*\to\ell\ell q\bar q"}
# Longest prefix first: "ZH_" is also a suffix of "ggZH_".
H_PRODUCTION = [("GluGluZH_", r"$gg\to ZH$"), ("ggZH_", r"$gg\to ZH$"), ("GluGluH", r"$gg\to H$"),
                ("VBFH", r"VBF $H$"), ("TTH", r"$t\bar tH$"), ("WplusH_", r"$W^+H$"),
                ("WminusH_", r"$W^-H$"), ("ZH_", r"$q\bar q\to ZH$")]
TOP = {"TBbarQ": (r"$t$", r"t\to b"), "TbarBQ": (r"$\bar t$", r"\bar t\to\bar b"),
       "TWminus": r"tW^-", "TbarWplus": r"\bar tW^+"}
NAMED = {
    "TBbarto2Q-s-channel": r"$s$-channel $t$: $t\to bq\bar q'$",
    "TBbartoLplusNuBbar-s-channel-4FS": r"$s$-channel $t$: $t\bar b\to\ell^+\nu b\bar b$",
    "TbarBtoLminusNuB-s-channel-4FS": r"$s$-channel $\bar t$: $\bar tb\to\ell^-\bar\nu\bar bb$",
    "WWW_4F": "WWW", "WWZ_4F": "WWZ", "WZZ": "WZZ", "ZZZ": "ZZZ",
}


def higgs_name(stem):
    prod = next(label for prefix, label in H_PRODUCTION if stem.startswith(prefix))
    parts = [r"$H\to %s$" % H_DECAY[re.search(r"Hto([^_]+)", stem).group(1)]]
    v = re.search(r"_(W|Z)to([^_]+)_", stem)
    if v:
        boson, dec = v.groups()
        parts.insert(0, rf"${boson}\to {(W_DECAY if boson == 'W' else Z_DECAY)[dec]}$")
    return f"{prod}: {', '.join(parts)}"


def process_name(family, primary):
    """Table label naming the sample's production and decay; family label if that is already all."""
    stem = primary.split("_TuneCP5", 1)[0]
    if stem in NAMED:
        return NAMED[stem]
    if m := re.fullmatch(r"TTto([A-Za-z0-9]+)(-3Jets)?", stem):
        return rf"$t\bar t\to {MULTI[m.group(1)]}$"
    if m := re.fullmatch(r"(TBbarQ|TbarBQ)(?:to(LNu|2Q)-|_)t-channel[-_]4FS", stem):
        top, decay = TOP[m.group(1)]
        if m.group(2) is None:
            return f"$t$-channel {top}"
        return rf"$t$-channel {top}: ${decay}{W_DECAY[m.group(2)]}$"
    if m := re.fullmatch(r"(TWminus|TbarWplus)to(\w+)", stem):
        return rf"${TOP[m.group(1)]}\to {MULTI[m.group(2)]}$"
    if m := re.fullmatch(r"ZprimeTobb_M(\d+)", stem):
        return rf"{family}, $m_{{Z'}}={m.group(1)}$ GeV"
    if family.startswith("Higgs"):
        return higgs_name(stem)
    return family


def generator(primary):
    return GENERATORS[primary.split("_13p6TeV_", 1)[1]]


def select(datasets):
    """Return rows (process, priority, comment, dataset) for every family, in FAMILIES order."""
    parsed = [(d, parse_dataset(d)) for d in sorted(datasets)]
    rows = []
    for process, regex, prio, comment in FAMILIES:
        pat = re.compile(regex)
        hits = [(d, p) for d, p in parsed if p and pat.fullmatch(p[0])]
        if not hits:
            raise ValueError(f"no dataset matches family {regex!r}")
        for d, (_, ext, _) in hits:
            rows.append((process, prio, comment + (f"; {ext}" if ext else ""), d))
    return rows


def latex_row(process, gen, xsec, nevents, status, comment, das, prio):
    das_tex = r"\nolinkurl{%s}" % das if das else "---"
    nev = f"{nevents:,}".replace(",", r"\,") if nevents is not None else "---"
    return f"{process} & {gen} & {xsec} & {nev} & {status} & {comment} & {das_tex} & {prio} \\\\"


def render(rows, nevents):
    lines = []
    prev = None
    for process, prio, comment, das in rows:
        if prev is not None and process != prev:
            lines.append(r"\midrule")
        prev = process
        primary = parse_dataset(das)[0]
        lines.append(latex_row(process_name(process, primary), generator(primary), "TBD", nevents[das],
                               "Available", "Central; " + comment, das, prio))
    lines.append(r"\midrule")
    for process, prio, comment in MISSING:
        lines.append(latex_row(process, "---", "---", None, "To be produced", comment, None, prio))
    return "\n".join(lines)


def inclusive(rows):
    """Minimal unbinned subset of rows: (rows, processes without any unbinned sample).

    Per process, takes every unbinned primary dataset of its families whose comment does not say
    "alternative" (falling back to those that do), one dataset per primary with the non-ext one preferred.
    """
    found = {}
    for row in rows:
        primary, ext, _ = parse_dataset(row[3])
        if BINNED_RE.search(primary):
            continue
        alt = "alternative" in row[2]
        found.setdefault(row[0], {}).setdefault(alt, {}).setdefault(primary, []).append(
            (ext is not None, ext or "", row))
    chosen, missing = [], []
    for process in dict.fromkeys(r[0] for r in rows):
        groups = found.get(process, {})
        primaries = groups.get(False) or groups.get(True)
        if primaries:
            if any(DECAY_INCLUSIVE_RE.match(p) for p in primaries):
                primaries = {p: c for p, c in primaries.items() if DECAY_INCLUSIVE_RE.match(p)}
            chosen += [min(cands)[2] for cands in primaries.values()]
        else:
            missing.append(process)
    return chosen, missing


def render_inclusive(rows, missing, nevents):
    lines = []
    for process, _, _, das in rows:
        nev = f"{nevents[das]:,}".replace(",", r"\,")
        primary = parse_dataset(das)[0]
        lines.append(f"{process_name(process, primary)} & {generator(primary)} & {nev} & "
                     f"\\nolinkurl{{{das}}} \\\\")
    lines.append(r"\midrule")
    for process in missing:
        lines.append(f"{process} & --- & --- & No inclusive sample; binned samples only \\\\")
    for process, _, comment in MISSING:
        lines.append(f"{process} & --- & --- & {comment} \\\\")
    return "\n".join(lines)


def splice(text, body, begin=BEGIN, end=END):
    """Replace the text between the begin/end markers with body."""
    head, sep, rest = text.partition(begin + "\n")
    _, sep2, tail = rest.partition(end)
    if not sep or not sep2:
        raise ValueError("generated-table markers not found")
    return head + begin + "\n" + body + "\n" + end + tail


def das(query):
    out = subprocess.run(["dasgoclient", "-query", query, "-json"], check=True,
                         capture_output=True, text=True).stdout
    return json.loads(out)


def list_datasets(query):
    return [r["dataset"][0]["name"] for r in das(query)]


def summary_of(query):
    (summary,) = [s for r in das(query) for s in r["summary"]]
    return summary


def cached(cache, query, fetch):
    """Return cache[query], filling it with fetch(query) on a miss."""
    if query not in cache:
        cache[query] = fetch(query)
    return cache[query]


def load_cache(path, refresh):
    return {} if refresh or not path.exists() else json.loads(path.read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--datasets", help="file with one DAS dataset per line (default: query DAS)")
    ap.add_argument("--tex", default=str(Path(__file__).with_name("samples.tex")))
    ap.add_argument("--cache", default=str(Path(__file__).with_name("das_cache.json")))
    ap.add_argument("--refresh", action="store_true", help="ignore the cache and requery DAS")
    args = ap.parse_args()
    cache_path = Path(args.cache)
    cache = load_cache(cache_path, args.refresh)
    try:
        if args.datasets:
            datasets = Path(args.datasets).read_text().split()
        else:
            datasets = cached(cache, f"dataset=/*/{CAMPAIGN}*/{TIER}", list_datasets)
        rows = select(datasets)
        names = [r[3] for r in rows]
        with ThreadPoolExecutor(8) as pool:
            summaries = pool.map(lambda d: cached(cache, f"summary dataset={d}", summary_of), names)
            counts = {d: s["nevents"] for d, s in zip(names, summaries)}
    finally:
        # Saved even on failure so completed queries are not repeated.
        cache_path.write_text(json.dumps(cache, indent=1, sort_keys=True))
    tex = Path(args.tex)
    incl, no_incl = inclusive(rows)
    text = splice(tex.read_text(), render(rows, counts))
    tex.write_text(splice(text, render_inclusive(incl, no_incl, counts), BEGIN_INCL, END_INCL))
    print(f"wrote {len(rows)} central rows + {len(MISSING)} missing rows to {tex}")
    print(f"wrote {len(incl)} inclusive rows; no inclusive sample for: {', '.join(no_incl) or 'none'}")


if __name__ == "__main__":
    main()
