"""Assign each concept a word made of CVC syllables, using n-ary Huffman coding.

A syllable is onset + vowel + coda. Onsets and codas may be the zero consonant,
written Ø in the options and in the `cvc` column, and as nothing in the word.

A zero onset is allowed only in a word's first syllable. Every later syllable
starts with a real consonant, so a written word splits into syllables in
exactly one way (otherwise "ana" could be an+a or a+na). This gives
  first syllable:  onsets x vowels x codas
  later syllables: (onsets - Ø) x vowels x codas

Within each node of the code tree, syllables with fewer letters go to the more
frequent concepts. That does not change the number of syllables, only makes
frequent words shorter on paper.

Input:  out/concept_freq.tsv  (from freq/build_concept_freq.py)
Output: out/lexicon.tsv       concept_id, gloss, p, syllables, letters, word, word_hyphenated, cvc

Run:  .venv/Scripts/python -X utf8 encode/build_lexicon.py
"""
import argparse
import math
import unicodedata
from pathlib import Path

import pandas as pd

from huffman import nary_huffman

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
ZERO = "Ø"

# /m n p t k ɕ x ʋ ʀ l/ written m n p t k s h v r l, plus the zero onset
ONSETS = "Ømnptkshvrl"
# /i ø ɛ u ɤ ɔ ɑ/
VOWELS = "iöeuëoa"
CODAS = "nthlØ"


def letters(s):
    return [unicodedata.normalize("NFC", c) for c in unicodedata.normalize("NFC", s)]


def syllable_inventory(onsets, vowels, codas):
    """Return (first, later): syllables as (onset, vowel, coda) tuples, fewest letters first."""
    onsets, vowels, codas = letters(onsets), letters(vowels), letters(codas)
    for name, xs in [("onsets", onsets), ("vowels", vowels), ("codas", codas)]:
        if len(set(xs)) != len(xs):
            raise ValueError(f"{name} must not repeat")
    if ZERO in vowels:
        raise ValueError("vowels cannot be zero")
    if set(vowels) & (set(onsets) | set(codas)):
        raise ValueError("a letter cannot be both a consonant and a vowel")
    first = [(o, v, c) for o in onsets for v in vowels for c in codas]
    first.sort(key=lambda s: len(render(s)))  # stable: keeps the given order within a length
    later = [s for s in first if s[0] != ZERO]
    if not later:
        raise ValueError("need at least one non-zero onset")
    return first, later


def render(*syllables):
    return "".join(x for s in syllables for x in s if x != ZERO)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--onsets", default=ONSETS, help=f"syllable-initial consonants, one letter each, {ZERO} = none (default {ONSETS})")
    ap.add_argument("--vowels", default=VOWELS, help=f"vowels, one letter each (default {VOWELS})")
    ap.add_argument("--codas", default=CODAS, help=f"syllable-final consonants, {ZERO} = none (default {CODAS})")
    ap.add_argument("--input", type=Path, default=OUT / "concept_freq.tsv")
    ap.add_argument("--output", type=Path, default=OUT / "lexicon.tsv")
    args = ap.parse_args()

    first, later = syllable_inventory(args.onsets, args.vowels, args.codas)
    freq = pd.read_csv(args.input, sep="\t")
    p = (freq.p / freq.p.sum()).to_numpy()

    codes = nary_huffman(p, len(later), root_n=len(first))
    sylls = [[first[c[0]], *(later[s] for s in c[1:])] for c in codes]
    lex = pd.DataFrame({
        "concept_id": freq.concept_id,
        "gloss": freq.gloss,
        "p": p,
        "syllables": [len(s) for s in sylls],
        "word": [render(*s) for s in sylls],
        "word_hyphenated": ["-".join(render(x) for x in s) for s in sylls],
        "cvc": [".".join("".join(x) for x in s) for s in sylls],
    })
    lex.insert(4, "letters", lex.word.str.len())
    dupes = lex.word[lex.word.duplicated()]
    if len(dupes):
        raise RuntimeError(f"words spelled the same: {', '.join(dupes.head(10))}")
    lex.to_csv(args.output, sep="\t", index=False, float_format="%.6g")

    avg_syl = float((lex.p * lex.syllables).sum())
    avg_let = float((lex.p * lex.letters).sum())
    entropy = -sum(x * math.log(x) for x in p if x > 0) / math.log(len(first))
    print(f"{len(lex)} concepts; {len(first)} first syllables, {len(later)} later syllables")
    print(f"average length {avg_syl:.3f} syllables, {avg_let:.2f} letters; entropy lower bound {entropy:.3f} syllables")
    print("words per length:", ", ".join(f"{k} syl: {v}" for k, v in lex.syllables.value_counts().sort_index().items()))
    print("most frequent:", ", ".join(f"{g}={w}" for g, w in lex[["gloss", "word_hyphenated"]].head(12).itertuples(index=False)))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
