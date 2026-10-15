"""Build per-language and combined concept frequencies.

Sources (all mapped to Concepticon IDs):
  en, es, de, zh  NoRaRe subtitle frequency lists (per million words)
  ja              Japanese WordNet lemmas (via the NoRaRe Bond-2013-OMW synset
                  mapping), looked up in wordfreq; the most frequent lemma of a
                  synset stands for the concept

Steps (see the discussion doc, steps 1-3):
  1. one row per concept x language: lexeme and frequency per million
  2. naive polysemy split: a lexeme mapped to k concepts gives each 1/k of its
     frequency and is flagged `ambiguous`
  3. keep concepts present in at least --min-langs languages, normalise each
     language to a probability distribution over those concepts
  4. per concept, drop languages whose value is more than --outlier-factor
     times above or below the median of that concept's languages (on a log
     scale), then average the remaining languages (missing = no data, not 0)

Outputs (not committed, see ATTRIBUTION.md):
  out/concept_freq_by_lang.tsv  concept_id, gloss, lang, lexeme, freq_pm, ambiguous, source
  out/concept_freq.tsv          concept_id, gloss, p, n_langs, langs, outliers, p_<lang>...
                                (p_<lang> keeps the outlier values for inspection)

Run:  .venv/Scripts/python -X utf8 freq/build_concept_freq.py
"""
import argparse
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from wordfreq import tokenize, zipf_frequency

ROOT = Path(__file__).resolve().parent.parent
NORARE = ROOT / "data/norare-data/datasets"
OMW_ZIP = ROOT / "data/omw-1.4.zip"
OUT = ROOT / "out"

# lang -> (NoRaRe dataset, lexeme column, frequency-per-million column)
NORARE_FREQ = {
    "en": ("Brysbaert-2009-Frequency", "ENGLISH", "ENGLISH_FREQUENCY_PM"),
    "es": ("Cuetos-2011-Frequency", "SPANISH", "SPANISH_FREQUENCY_PM"),
    "de": ("Brysbaert-2011-Frequency", "GERMAN", "GERMAN_FREQUENCY_PM"),
    "zh": ("Cai-2010-Frequency", "CHINESE", "CHINESE_FREQUENCY_PM"),
}
LANGS = [*NORARE_FREQ, "ja"]


def load_norare(name):
    d = pd.read_csv(NORARE / name / f"{name}.tsv", sep="\t", encoding="utf-8-sig", low_memory=False)
    d = d.dropna(subset=["CONCEPTICON_ID"])
    return d.assign(CONCEPTICON_ID=d.CONCEPTICON_ID.astype(int))


def norare_lang(lang):
    name, word, pm = NORARE_FREQ[lang]
    d = load_norare(name)
    return pd.DataFrame({
        "concept_id": d.CONCEPTICON_ID,
        "gloss": d.CONCEPTICON_GLOSS,
        "lang": lang,
        "lexeme": d[word].astype(str),
        "freq_pm": pd.to_numeric(d[pm], errors="coerce"),
        "source": name,
    })


def japanese():
    """Concept -> Japanese WordNet lemmas -> most frequent lemma in wordfreq."""
    with zipfile.ZipFile(OMW_ZIP) as z:
        tab = z.read("omw-1.4/jpn/wn-data-jpn.tab").decode("utf-8")
    # lemma rows have 3 fields; definition/example rows have 4, so parse by hand
    lemmas = {}
    for line in tab.splitlines():
        fields = line.split("\t")
        if len(fields) == 3 and fields[1] == "jpn:lemma":
            lemmas.setdefault(fields[0], []).append(fields[2].strip())

    omw = load_norare("Bond-2013-OMW")
    rows = []
    for _, r in omw.iterrows():
        synset = r.WORDNET_ID
        # WordNet adjective satellites are "-s" in some tables and "-a" in others
        cands = lemmas.get(synset, []) or lemmas.get(synset[:-1] + "s", [])
        # wordfreq splits multi-token strings and combines their frequencies, so
        # e.g. とと would score like the particle と; keep single-token lemmas only
        scored = [(zipf_frequency(w, "ja"), w) for w in cands if tokenize(w, "ja") == [w]]
        scored = [s for s in scored if s[0] > 0]
        if not scored:
            continue
        zipf, best = max(scored)
        rows.append((r.CONCEPTICON_ID, r.CONCEPTICON_GLOSS, best, 10 ** (zipf - 3)))
    d = pd.DataFrame(rows, columns=["concept_id", "gloss", "lexeme", "freq_pm"])
    return d.assign(lang="ja", source="Bond-2013-OMW + Japanese WordNet + wordfreq")


def split_polysemy(df):
    """A lexeme mapped to k concepts in one language gives each concept 1/k of its frequency."""
    k = df.groupby(["lang", "lexeme"]).concept_id.transform("nunique")
    return df.assign(freq_pm=df.freq_pm / k, ambiguous=k > 1)


def outlier_mask(p_lang, factor):
    """True where a language's value is more than `factor` times above or below
    the median of that concept's languages. factor <= 1 disables the check."""
    if factor <= 1:
        return p_lang.notna() & False
    log = np.log10(p_lang)
    mask = log.sub(log.median(axis=1), axis=0).abs() > np.log10(factor)
    # with an even number of languages the median lies between two values, so
    # every language can be "far" from it; then keep them all
    all_dropped = mask.sum(axis=1) == p_lang.notna().sum(axis=1)
    mask[all_dropped] = False
    return mask


def combine(df, min_langs, outlier_factor):
    wide = df.pivot_table(index="concept_id", columns="lang", values="freq_pm", aggfunc="sum")
    wide = wide[wide.notna().sum(axis=1) >= min_langs]
    p_lang = wide / wide.sum()                      # each language sums to 1 over kept concepts
    outliers = outlier_mask(p_lang, outlier_factor)
    p = p_lang.mask(outliers).mean(axis=1, skipna=True)  # missing = no data, not 0
    p = p / p.sum()
    gloss = df.drop_duplicates("concept_id").set_index("concept_id").gloss
    langs_where = lambda m: m.apply(lambda r: ",".join(l for l in m.columns if r[l]), axis=1)
    out = pd.DataFrame({
        "gloss": gloss.reindex(p.index),
        "p": p,
        "n_langs": wide.notna().sum(axis=1),
        "langs": langs_where(wide.notna()),
        "outliers": langs_where(outliers),
    })
    out = out.join(p_lang.add_prefix("p_"))
    return out.sort_values("p", ascending=False).rename_axis("concept_id").reset_index()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--min-langs", type=int, default=3,
                    help="keep concepts that have data in at least this many languages (default 3)")
    ap.add_argument("--outlier-factor", type=float, default=10,
                    help="per concept, ignore a language whose value is more than this many times above or "
                         "below the median of the concept's languages (default 10; 0 turns it off)")
    args = ap.parse_args()

    parts = [norare_lang(l) for l in NORARE_FREQ] + [japanese()]
    df = pd.concat(parts, ignore_index=True).dropna(subset=["freq_pm"])
    df = df[df.freq_pm > 0]
    df = split_polysemy(df)

    OUT.mkdir(exist_ok=True)
    cols = ["concept_id", "gloss", "lang", "lexeme", "freq_pm", "ambiguous", "source"]
    df[cols].sort_values(["lang", "freq_pm"], ascending=[True, False]).to_csv(
        OUT / "concept_freq_by_lang.tsv", sep="\t", index=False)
    combined = combine(df, args.min_langs, args.outlier_factor)
    combined.to_csv(OUT / "concept_freq.tsv", sep="\t", index=False, float_format="%.6g")

    print("per language: concepts, ambiguous lexemes, outliers dropped in the average")
    for lang in LANGS:
        d = df[df.lang == lang]
        dropped = combined.outliers.str.split(",").apply(lambda x: lang in x).sum()
        print(f"  {lang}  {len(d):5d}  {d.ambiguous.sum():4d}  {dropped:4d}")
    print(f"combined: {len(combined)} concepts in >= {args.min_langs} languages")
    print("top 15:", ", ".join(combined.gloss.head(15)))
    print(f"wrote {OUT / 'concept_freq_by_lang.tsv'} and {OUT / 'concept_freq.tsv'}")


if __name__ == "__main__":
    main()
