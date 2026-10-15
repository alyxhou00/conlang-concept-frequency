"""Assign each concept a word made of CVC syllables, using n-ary Huffman coding.

A syllable is onset + vowel + coda. Onsets and codas may be the zero consonant,
written Ø in the options and in the `cvc` column, and as nothing in the word.

A zero onset is allowed only in a word's first syllable. Every later syllable
starts with a real consonant, so a written word splits into syllables in
exactly one way (otherwise "ana" could be an+a or a+na). This gives
  first syllable:  onsets x vowels x codas
  later syllables: (onsets - Ø) x vowels x codas

Syllable order (which syllables the most frequent concepts get, within each
node of the code tree):
  1. fewer letters first: this does not change the number of syllables, only
     makes frequent words shorter on paper
  2. within the same number of letters, each slot cycles: the next syllable
     takes the onset, vowel and coda used least recently, so neighbours differ
     as much as possible (i, e, u ... then ön, et, uh ... instead of in, it, ih).
     When the onset, vowel and coda counts share no common factor this is the
     simple walk k -> (onset k, vowel k, coda k); otherwise it still covers
     every syllable once.

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


def vary(sylls, last_used=None):
    """Order syllables so that each slot cycles through its values.

    At every step take the syllable whose onset, vowel and coda were used least
    recently (compare the most recently used slot first; ties go to the
    earliest syllable in the input). `last_used` maps (slot, value) to the step
    it was last used, so the cycle can continue from a previous group.
    Returns (ordered syllables, updated last_used).
    """
    last = dict(last_used or {})
    start = max(last.values(), default=-1) + 1
    remaining = list(sylls)
    ordered = []
    for step in range(start, start + len(sylls)):
        def ages(s):
            return sorted(step - last.get((i, x), -math.inf) for i, x in enumerate(s))
        j = max(range(len(remaining)), key=lambda j: (ages(remaining[j]), -j))
        s = remaining.pop(j)
        ordered.append(s)
        for i, x in enumerate(s):
            last[(i, x)] = step
    return ordered, last


def by_letters_then_varied(sylls):
    """Fewer letters first; within each length, cycle the slots (see vary)."""
    ordered, last = [], {}
    for n in sorted({len(render(s)) for s in sylls}):
        group, last = vary([s for s in sylls if len(render(s)) == n], last)
        ordered += group
    return ordered


def syllable_inventory(onsets, vowels, codas):
    """Return (first, later): syllables as (onset, vowel, coda) tuples, in the order they are handed out."""
    onsets, vowels, codas = letters(onsets), letters(vowels), letters(codas)
    for name, xs in [("onsets", onsets), ("vowels", vowels), ("codas", codas)]:
        if len(set(xs)) != len(xs):
            raise ValueError(f"{name} must not repeat")
    if ZERO in vowels:
        raise ValueError("vowels cannot be zero")
    if set(vowels) & (set(onsets) | set(codas)):
        raise ValueError("a letter cannot be both a consonant and a vowel")
    every = [(o, v, c) for o in onsets for v in vowels for c in codas]
    later = [s for s in every if s[0] != ZERO]
    if not later:
        raise ValueError("need at least one non-zero onset")
    return by_letters_then_varied(every), by_letters_then_varied(later)


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
