"""Sanity checks on the downloaded concept-frequency sources.

Checks Calude-2011-200 on its own (coverage, cross-language correlation,
polysemy double-counting, outliers), then against the NoRaRe monolingual
frequency lists and wordfreq.

Calude values turn out to be log10(frequency per million), so wordfreq's
Zipf scale minus 3 is directly comparable.

Run from anywhere:  .venv/Scripts/python -X utf8 checks/check_sources.py
"""
import itertools
from pathlib import Path

import numpy as np
import pandas as pd
from wordfreq import zipf_frequency

ROOT = Path(__file__).resolve().parent.parent
CALUDE = ROOT / "data/concepticon-data/concepticondata/conceptlists/Calude-2011-200.tsv"
NORARE = ROOT / "data/norare-data/datasets"


def section(title):
    print(f"\n== {title}")


def load_norare(name):
    d = pd.read_csv(NORARE / name / f"{name}.tsv", sep="\t", low_memory=False)
    d = d.dropna(subset=["CONCEPTICON_ID"])
    return d.assign(CONCEPTICON_ID=d.CONCEPTICON_ID.astype(int))


# "-" marks a missing cell in Calude
cal = pd.read_csv(CALUDE, sep="\t", na_values=["-"])
cal["CONCEPTICON_ID"] = cal.CONCEPTICON_ID.astype(int)
F = cal.set_index("ENGLISH")[[c for c in cal.columns if c.endswith("_FREQUENCY")]]
F.columns = [c.removesuffix("_FREQUENCY") for c in F.columns]

# ---------------------------------------------------------------- Calude alone

section("Calude: coverage, distinct values, range per language")
for lang in F.columns:
    s = F[lang].dropna()
    print(f"  {lang:10s} {len(s):3d}/200 filled  {s.nunique():3d} distinct  "
          f"min={s.min():5.2f} max={s.max():5.2f}")

section("Calude: mean pairwise correlation (paper reports 0.73)")
pairs = list(itertools.combinations(F.columns, 2))
pear = [F[a].corr(F[b]) for a, b in pairs]
spear = [F[a].corr(F[b], method="spearman") for a, b in pairs]
print(f"  Pearson {np.mean(pear):.3f} (min {min(pear):.2f}, max {max(pear):.2f}), "
      f"Spearman {np.mean(spear):.3f}, {len(pairs)} pairs")
mean_r = F.corr().apply(lambda s: s.drop(s.name).mean()).sort_values()
print("  lowest per-language mean r:", ", ".join(f"{l} {r:.2f}" for l, r in mean_r.head(5).items()))

# Ties at low counts are often coincidence (same raw count -> same log value),
# so only ties at >= 2.5 (~300 per million) are listed.
section("Calude: identical values within a language, value >= 2.5 (likely polysemy double-counting)")
for lang in F.columns:
    s = F[lang].dropna()
    s = s[s >= 2.5]
    for v, g in s.groupby(s.round(10)):
        if len(g) > 1:
            print(f"  {lang:10s} {v:.2f}  {' / '.join(g.index)}")

section("Calude: known colexification pairs, languages with identical values")
for a, b in [("FOOT", "LEG"), ("MAN (MALE)", "HUSBAND"), ("WOMAN", "WIFE"),
             ("THOU", "YE"), ("TREE", "WOODS")]:
    same = [l for l in F.columns if pd.notna(F.at[a, l]) and F.at[a, l] == F.at[b, l]]
    print(f"  {a} = {b}: {', '.join(same) or '-'}")

section("Calude: biggest single-language outliers (z-score within the concept's row)")
Z = F.sub(F.mean(axis=1), axis=0).div(F.std(axis=1), axis=0)
for (concept, lang), z in Z.stack().abs().sort_values(ascending=False).head(10).items():
    print(f"  {concept:14s} {lang:10s} {F.at[concept, lang]:5.2f} (row mean {F.loc[concept].mean():.2f}, |z| {z:.1f})")

section("Calude: CHINESE column")
zh = F["CHINESE"].dropna()
print(f"  {(zh < 1.5).sum()} of {len(zh)} values are below 1.5; min {zh.min():.2f}")
print("  DAY (NOT NIGHT) per language:", ", ".join(f"{l} {v:.2f}" for l, v in F.loc["DAY (NOT NIGHT)"].items()))
print("  concepts sharing DAY's Chinese value:",
      ", ".join(zh[zh == zh["DAY (NOT NIGHT)"]].index))

# ------------------------------------------------- against NoRaRe and wordfreq

# (NoRaRe dataset, word column, per-million column or None for raw counts, wordfreq lang)
NORARE_FREQ = [
    ("Brysbaert-2009-Frequency", "ENGLISH", "ENGLISH_FREQUENCY_PM", "en"),
    ("Cuetos-2011-Frequency", "SPANISH", "SPANISH_FREQUENCY_PM", "es"),
    ("Cai-2010-Frequency", "CHINESE", "CHINESE_FREQUENCY_PM", "zh"),
    ("Dimitropoulou-2010-Frequency", "GREEK", "GREEK_FREQUENCY_PM", "el"),
    ("Mandera-2015-Frequency", "POLISH", None, "pl"),
    ("Brysbaert-2011-Frequency", "GERMAN", "GERMAN_FREQUENCY_PM", "de"),
    ("Keuleers-2010-Frequency", "DUTCH", "DUTCH_FREQUENCY_PM", "nl"),
    ("Crepaldi-2015-Frequency", "ITALIAN", None, "it"),
]

section("NoRaRe frequency lists vs Calude vs wordfreq (Pearson r on log10 per million)")
print(f"  {'dataset':30s} {'concepts':>8s} {'∩Calude':>8s} {'Cal~NoRaRe':>11s} {'Cal~wf':>7s} {'NoRaRe~wf':>10s}")
cal_by_id = cal.set_index("CONCEPTICON_ID")
all_ids = set()
cai = None
for name, wcol, pm, wl in NORARE_FREQ:
    d = load_norare(name)
    all_ids |= set(d.CONCEPTICON_ID)
    if pm is None:  # raw counts only: normalise within the list
        counts = pd.to_numeric(d[f"{wcol}_FREQUENCY"], errors="coerce")
        d["logpm"] = np.log10(counts / counts.sum() * 1e6)
    else:
        d["logpm"] = np.log10(pd.to_numeric(d[pm], errors="coerce"))
    d["wf"] = [zipf_frequency(str(w), wl) - 3 for w in d[wcol]]
    d.loc[d.wf <= -3, "wf"] = np.nan  # zipf 0 = word unknown to wordfreq
    g = d.set_index("CONCEPTICON_ID")
    inter = g.index.intersection(cal_by_id.index)
    ccol = f"{wcol}_FREQUENCY"
    if ccol in cal_by_id.columns:
        c = cal_by_id.loc[inter, ccol]
        cmp = f"{c.corr(g.loc[inter, 'logpm']):11.2f} {c.corr(g.loc[inter, 'wf']):7.2f}"
    else:
        cmp = f"{'(not in Calude)':>19s}"
    print(f"  {name:30s} {len(g):8d} {len(inter):8d} {cmp} {g.logpm.corr(g.wf):10.2f}")
    if wcol == "CHINESE":
        cai = g.loc[inter, [wcol, "logpm", "wf"]].join(cal_by_id.loc[inter, ["ENGLISH", ccol]].rename(columns={ccol: "CALUDE"}))
print(f"  union of concepts across these lists: {len(all_ids)} (covers {len(all_ids & set(cal_by_id.index))} of Calude-200)")

section("Chinese: largest gaps between Calude and SUBTLEX-CH (Cai-2010)")
cai["gap"] = cai.CALUDE - cai.logpm
print(f"  {'concept':18s} {'Calude':>6s}  word {'Cai':>5s} {'wf':>5s}")
for _, r in cai.reindex(cai.gap.abs().sort_values(ascending=False).index).head(8).iterrows():
    print(f"  {r.ENGLISH:18s} {r.CALUDE:6.2f}  {r.CHINESE:4s} {r.logpm:5.2f} {r.wf:5.2f}")

section("Chinese: single vs two-character words in wordfreq for concepts at Calude's 1.34")
for concept, words in [("DAY (NOT NIGHT)", ["天", "白天", "日"]), ("BLOOD", ["血", "血液"]),
                       ("EGG", ["蛋", "鸡蛋"]), ("FEATHER (LARGE)", ["毛", "羽毛"]),
                       ("TO SMELL (PERCEIVE ODOR)", ["闻", "闻到"])]:
    print(f"  {concept:26s} Calude {F.at[concept, 'CHINESE']:.2f}  "
          + "  ".join(f"{w} {zipf_frequency(w, 'zh') - 3:.2f}" for w in words))

section("English: Calude vs wordfreq on the gloss itself (strips 'TO' and parentheses)")
w = (F.index.str.replace(r"\(.*\)", "", regex=True)
     .str.replace(r"^TO ", "", regex=True).str.strip().str.lower())
wf = pd.Series([zipf_frequency(x, "en") - 3 for x in w], index=F.index)
print(f"  r = {F.ENGLISH.corr(wf):.2f}; mean(wordfreq - Calude) = {(wf - F.ENGLISH).mean():+.2f} "
      "(near 0, so Calude is log10 per million)")

section("Wu-2020 core vocabulary (dictionary coverage) vs mean Calude frequency")
wu = load_norare("Wu-2020-CoreVocabulary").groupby("CONCEPTICON_ID").TRANSLATION_COUNT.max()
m = cal_by_id[[c for c in cal_by_id.columns if c.endswith("_FREQUENCY")]].mean(axis=1)
i = m.index.intersection(wu.index)
print(f"  {len(wu)} concepts, {len(i)} shared with Calude, Spearman {m[i].corr(wu[i], method='spearman'):.2f}")
