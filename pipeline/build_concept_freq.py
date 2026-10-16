"""Build per-language and combined concept frequencies.

Covers every active Concepticon concept set (retired ones are merged into
their replacement) plus our own concepts in mapping/extra_concepts.tsv.
Sources, in order of preference:
  en, es, de, zh  NoRaRe subtitle frequency lists (per million words)
  ja              Japanese WordNet lemmas (via the NoRaRe Bond-2013-OMW synset
                  mapping), looked up in wordfreq; the most frequent lemma of a
                  synset stands for the concept
  any language    otherwise: words for the concept in that language from the
                  word columns of Concepticon concept lists and NoRaRe datasets
                  (English also from the Concepticon gloss) and, for our own
                  concepts, mapping/extra_concepts.tsv, looked up in
                  wordfreq. Of the candidates, single words beat phrases, then
                  the spelling most lists agree on wins, then the most frequent.

Steps (see the discussion doc, steps 1-3):
  1. one row per concept x language: lexeme and frequency per million
  2. naive polysemy split: a lexeme mapped to k concepts gives each 1/k of its
     frequency and is flagged `ambiguous`
  3. keep concepts present in at least --min-langs languages, normalise each
     language to a probability distribution over those concepts. With
     --min-langs 0 (default) every Concepticon concept is kept; concepts with
     no data in any language (mostly compounds such as COCONUT TREE) get the
     lowest frequency in the table, so they end up with the longest words
  4. per concept, drop languages whose value is more than --outlier-factor
     times above or below the median of that concept's languages (on a log
     scale), then average the remaining languages (missing = no data, not 0)

Outputs (not committed, see ATTRIBUTION.md):
  out/concept_freq_by_lang.tsv  concept_id, gloss, lang, lexeme, freq_pm, ambiguous, source
  out/concept_freq.tsv          concept_id, gloss, p, n_langs, langs, outliers, p_<lang>...
                                (p_<lang> keeps the outlier values for inspection)

Run:  .venv/Scripts/python -X utf8 pipeline/build_concept_freq.py
"""
import argparse
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
from wordfreq import tokenize, zipf_frequency

ROOT = Path(__file__).resolve().parent.parent
NORARE = ROOT / "data/norare-data/datasets"
CONCEPTICON = ROOT / "data/concepticon-data/concepticondata"
EXTRA_CONCEPTS = ROOT / "mapping/extra_concepts.tsv"
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

# word columns for our languages in Concepticon concept lists and NoRaRe datasets
WORD_COLUMNS = {
    "en": ["ENGLISH"],
    "es": ["SPANISH"],
    "de": ["GERMAN"],
    "zh": ["CHINESE", "CHINESE_SIMPLIFIED", "CHINESE_TRADITIONAL"],
    "ja": ["JAPANESE"],
}


# read words as text: without this pandas turns words like "nan" or "null" into missing values
TEXT = dict(keep_default_na=False, na_values=[""])


def concepticon():
    return pd.read_csv(CONCEPTICON / "concepticon.tsv", sep="\t", **TEXT,
                       usecols=["ID", "GLOSS", "REPLACEMENT_ID"])


def replacements():
    """Retired concept ID -> the active concept that replaces it."""
    cs = concepticon().dropna(subset=["REPLACEMENT_ID"])
    repl = dict(zip(cs.ID, cs.REPLACEMENT_ID.astype(int)))
    for k in repl:  # follow chains of replacements
        while repl[k] in repl and repl[k] != k:
            repl[k] = repl[repl[k]]
    return repl


def extra_concepts():
    return pd.read_csv(EXTRA_CONCEPTS, sep="\t", **TEXT)


def concept_glosses():
    """Glosses of active Concepticon concepts and our own extra concepts, by ID."""
    cs = concepticon()
    cs = cs[cs.REPLACEMENT_ID.isna()]
    extra = extra_concepts()
    return pd.concat([cs.set_index("ID").GLOSS, extra.set_index("ID").GLOSS])


def load_norare(name):
    d = pd.read_csv(NORARE / name / f"{name}.tsv", sep="\t", encoding="utf-8-sig", low_memory=False, **TEXT)
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


def clean_words(text, lang):
    """Split a word-list cell into candidate words.

    'hermano (de la mujer)' -> ['hermano'];  'ronsoco, carpincho' -> ['ronsoco', 'carpincho'];
    '洗（衣服）' -> ['洗'];  English 'to sleep' -> ['sleep'], 'arm or hand' -> ['arm', 'hand']
    """
    text = unicodedata.normalize("NFC", str(text)).lower()
    text = re.sub(r"[(（\[【].*?[)）\]】]", " ", text)
    seps = r"[,;/，、；]" + (r"|\bor\b" if lang == "en" else "")
    words = []
    for w in re.split(seps, text):
        w = " ".join(w.split()).strip(" .?!¿¡\"'*")
        if lang == "en":
            w = re.sub(r"^to ", "", w)
        if w:
            words.append(w)
    return words


def list_words():
    """{lang: {concept_id: Counter(word -> number of lists that give it)}}."""
    words = {lang: defaultdict(Counter) for lang in WORD_COLUMNS}
    files = sorted((CONCEPTICON / "conceptlists").glob("*.tsv")) + sorted(NORARE.glob("*/*.tsv"))
    for f in files:
        try:
            header = pd.read_csv(f, sep="\t", nrows=0, encoding="utf-8-sig").columns
        except (pd.errors.ParserError, UnicodeDecodeError):
            continue
        if "CONCEPTICON_ID" not in header:
            continue
        for lang, cols in WORD_COLUMNS.items():
            for col in (c for c in cols if c in header):
                d = pd.read_csv(f, sep="\t", usecols=["CONCEPTICON_ID", col], encoding="utf-8-sig",
                                dtype=str, **TEXT).dropna()
                for cid, cell in zip(d.CONCEPTICON_ID, d[col]):
                    if cid.isdigit():
                        for w in set(clean_words(cell, lang)):
                            words[lang][int(cid)][w] += 1
    extra = extra_concepts()
    for lang, cols in WORD_COLUMNS.items():
        for col in (c for c in cols if c in extra.columns):
            for cid, cell in zip(extra.ID, extra[col]):
                if isinstance(cell, str):
                    for w in clean_words(cell, lang):
                        words[lang][int(cid)][w] += 1
    return words


def pick_word(counts, lang):
    """Best candidate as (word, zipf): single words first, then most lists, then most frequent.

    wordfreq rates a phrase almost as frequent as its rarest word ("ich und du"
    would get 2,400 per million), so phrases with spaces are not used, and for
    Japanese only single tokens count (otherwise e.g. とと scores like the particle と).
    """
    best = None
    for w, n in counts.items():
        single = len(tokenize(w, lang)) == 1
        if " " in w or (lang == "ja" and not single):
            continue
        zipf = zipf_frequency(w, lang)
        if zipf <= 0:
            continue
        key = (single, n, zipf)
        if best is None or key > best[0]:
            best = (key, w, zipf)
    return (best[1], best[2]) if best else (None, 0.0)


def wordfreq_fill(have, glosses):
    """Rows for (concept, language) pairs that have no frequency yet."""
    words = list_words()
    extra_ids = set(extra_concepts().ID)
    for cid, gloss in glosses.items():  # a Concepticon gloss is one more English candidate
        if cid not in extra_ids:     # our own glosses are labels like "PLURAL (PARTICLE)", not words
            for w in clean_words(gloss, "en"):
                words["en"][cid][w] += 0  # present, but no extra vote
    repl = replacements()
    rows = []
    for lang, by_concept in words.items():
        merged = defaultdict(Counter)  # word lists may still use retired IDs
        for cid, counts in by_concept.items():
            merged[repl.get(cid, cid)].update(counts)
        for cid, counts in merged.items():
            if (cid, lang) in have or cid not in glosses.index:
                continue
            w, zipf = pick_word(counts, lang)
            if w is None:
                continue
            source = ("our word list + wordfreq" if cid in extra_ids
                      else "Concepticon gloss + wordfreq" if counts[w] == 0 else "concept lists + wordfreq")
            rows.append((cid, lang, w, 10 ** (zipf - 3), source))
    return pd.DataFrame(rows, columns=["concept_id", "lang", "lexeme", "freq_pm", "source"])


def split_polysemy(df):
    """A lexeme mapped to k concepts in one language gives each concept 1/k of its frequency."""
    k = df.groupby(["lang", df.lexeme.str.casefold()]).concept_id.transform("nunique")
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


def combine(df, min_langs, outlier_factor, glosses):
    wide = df.pivot_table(index="concept_id", columns="lang", values="freq_pm", aggfunc="sum")
    if min_langs == 0:
        wide = wide.reindex(wide.index.union(glosses.index))
    wide = wide[wide.notna().sum(axis=1) >= min_langs]
    p_lang = wide / wide.sum()                      # each language sums to 1 over kept concepts
    outliers = outlier_mask(p_lang, outlier_factor)
    p = p_lang.mask(outliers).mean(axis=1, skipna=True)  # missing = no data, not 0
    p = p.fillna(p.min())  # concepts with no data at all: lowest frequency
    p = p / p.sum()
    gloss = glosses
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
    ap.add_argument("--min-langs", type=int, default=0,
                    help="keep concepts that have data in at least this many languages "
                         "(default 0: all Concepticon concepts, those without data get the lowest frequency)")
    ap.add_argument("--outlier-factor", type=float, default=10,
                    help="per concept, ignore a language whose value is more than this many times above or "
                         "below the median of the concept's languages (default 10; 0 turns it off)")
    args = ap.parse_args()

    glosses = concept_glosses()
    parts = [norare_lang(l) for l in NORARE_FREQ] + [japanese()]
    df = pd.concat(parts, ignore_index=True).dropna(subset=["freq_pm"])
    df["concept_id"] = df.concept_id.replace(replacements())  # retired concepts count for their replacement
    df = df[(df.freq_pm > 0) & df.concept_id.isin(glosses.index)]
    have = set(zip(df.concept_id, df.lang))
    df = pd.concat([df, wordfreq_fill(have, glosses)], ignore_index=True)
    df["gloss"] = df.concept_id.map(glosses)
    df = split_polysemy(df)

    OUT.mkdir(exist_ok=True)
    cols = ["concept_id", "gloss", "lang", "lexeme", "freq_pm", "ambiguous", "source"]
    df[cols].sort_values(["lang", "freq_pm"], ascending=[True, False]).to_csv(
        OUT / "concept_freq_by_lang.tsv", sep="\t", index=False)
    combined = combine(df, args.min_langs, args.outlier_factor, glosses)
    combined.to_csv(OUT / "concept_freq.tsv", sep="\t", index=False, float_format="%.6g")

    print("per language: concepts (frequency list + filled from wordfreq), ambiguous lexemes, "
          "outliers dropped in the average")
    for lang in LANGS:
        d = df[df.lang == lang]
        filled = d.source.isin(["concept lists + wordfreq", "Concepticon gloss + wordfreq",
                                "our word list + wordfreq"])
        dropped = combined.outliers.str.split(",").apply(lambda x: lang in x).sum()
        print(f"  {lang}  {len(d):5d} ({len(d) - filled.sum()} + {filled.sum()})  {d.ambiguous.sum():4d}  {dropped:4d}")
    print(f"combined: {len(combined)} of {len(glosses)} concepts (Concepticon + our own) "
          f"in >= {args.min_langs} languages")
    print("languages per concept:", combined.n_langs.value_counts().sort_index().to_dict())
    print("top 15:", ", ".join(combined.gloss.head(15)))
    print(f"wrote {OUT / 'concept_freq_by_lang.tsv'} and {OUT / 'concept_freq.tsv'}")


if __name__ == "__main__":
    main()
