"""Assign each concept a word made of CVC syllables, using n-ary Huffman coding.

n = consonants x vowels x consonants. Every syllable is 3 letters, so a word's
length in letters is always 3 x its number of syllables.

Input:  out/concept_freq.tsv  (from freq/build_concept_freq.py)
Output: out/lexicon.tsv       concept_id, gloss, p, syllables, word, word_hyphenated

Run:  .venv/Scripts/python -X utf8 encode/build_lexicon.py
"""
import argparse
import math
from pathlib import Path

import pandas as pd

from huffman import nary_huffman

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"


def cvc_syllables(consonants, vowels):
    if len(set(consonants)) != len(consonants) or len(set(vowels)) != len(vowels):
        raise ValueError("consonants and vowels must not repeat")
    if set(consonants) & set(vowels):
        raise ValueError("a letter cannot be both a consonant and a vowel")
    return [c1 + v + c2 for c1 in consonants for v in vowels for c2 in consonants]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--consonants", default="ptkbdgmnslfh", help="one letter per consonant (default: 12)")
    ap.add_argument("--vowels", default="aeiou", help="one letter per vowel (default: 5)")
    ap.add_argument("--input", type=Path, default=OUT / "concept_freq.tsv")
    ap.add_argument("--output", type=Path, default=OUT / "lexicon.tsv")
    args = ap.parse_args()

    syllables = cvc_syllables(args.consonants, args.vowels)
    n = len(syllables)
    freq = pd.read_csv(args.input, sep="\t")
    p = (freq.p / freq.p.sum()).to_numpy()

    codes = nary_huffman(p, n)
    lex = pd.DataFrame({
        "concept_id": freq.concept_id,
        "gloss": freq.gloss,
        "p": p,
        "syllables": [len(c) for c in codes],
        "word": ["".join(syllables[s] for s in c) for c in codes],
        "word_hyphenated": ["-".join(syllables[s] for s in c) for c in codes],
    })
    lex.to_csv(args.output, sep="\t", index=False, float_format="%.6g")

    avg = float((lex.p * lex.syllables).sum())
    entropy = -sum(x * math.log(x) for x in p if x > 0) / math.log(n)
    print(f"{len(lex)} concepts, {len(args.consonants)} x {len(args.vowels)} x {len(args.consonants)} = {n} CVC syllables")
    print(f"average length {avg:.3f} syllables ({3 * avg:.2f} letters); entropy lower bound {entropy:.3f}")
    print("words per length:", ", ".join(f"{k} syl: {v}" for k, v in lex.syllables.value_counts().sort_index().items()))
    print("most frequent:", ", ".join(f"{g}={w}" for g, w in lex[["gloss", "word_hyphenated"]].head(10).itertuples(index=False)))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
