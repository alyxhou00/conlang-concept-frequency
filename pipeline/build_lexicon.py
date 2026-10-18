"""Assign each concept a word made of CVC syllables, using n-ary Huffman coding.

A syllable is onset + vowel + coda. Onsets and codas may be the zero consonant,
written Ø in the options and in the `cvc` column, and as nothing in the word.

A zero onset is allowed only in a word's first syllable. Every later syllable
starts with a real consonant, so a written word splits into syllables in
exactly one way (otherwise "ana" could be an+a or a+na). At the start of a
word the zero onset is pronounced as a glottal stop [ʔ] (not written), so in
speech "et e" [ʔɛt ʔɛ] cannot be heard as "e te" [ʔɛ tɛ]. This gives
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

10% of the two-syllable words (--reserve-2syl) are kept free for words added
after a version is frozen; one-syllable words are not affected.

Only "units" get a code (see units.py): pronouns and other merged concepts
use their target's word, compounds use their parts' words.

Input:  out/concept_freq.tsv  (from pipeline/build_concept_freq.py),
        mapping/merges.tsv, mapping/compounds.tsv
Output: out/lexicon_meta.json statistics for pipeline/release.py
        out/lexicon.tsv       one row per concept: concept_id, gloss, kind (word,
                              merged, compound), p, p_word (frequency of the word
                              itself, for kind=word), syllables, letters, word,
                              word_hyphenated, cvc (with Ø), ipa

Run:  .venv/Scripts/python -X utf8 pipeline/build_lexicon.py
"""
import argparse
import json
import math
import unicodedata
from pathlib import Path

import pandas as pd

from huffman import free_slots, nary_huffman_reserving
from phonetics import pronounce
from units import Units, load_compounds, load_merges

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
ZERO = "Ø"

# /m n p t k s x ʋ ʁ l/ written m n p t k s h v r l, plus the zero onset
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


def ipa(*syllables):
    """IPA of the word said on its own, with syllable dots (sound rules in phonetics.py)."""
    return pronounce([render(*syllables)])[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--onsets", default=ONSETS, help=f"syllable-initial consonants, one letter each, {ZERO} = none (default {ONSETS})")
    ap.add_argument("--vowels", default=VOWELS, help=f"vowels, one letter each (default {VOWELS})")
    ap.add_argument("--codas", default=CODAS, help=f"syllable-final consonants, {ZERO} = none (default {CODAS})")
    ap.add_argument("--reserve-2syl", type=float, default=0.10,
                    help="share of two-syllable words kept free for later additions (default 0.10)")
    ap.add_argument("--input", type=Path, default=OUT / "concept_freq.tsv")
    ap.add_argument("--output", type=Path, default=OUT / "lexicon.tsv")
    args = ap.parse_args()

    first, later = syllable_inventory(args.onsets, args.vowels, args.codas)
    freq = pd.read_csv(args.input, sep="\t", keep_default_na=False, na_values=[""])
    p = pd.Series(freq.p.to_numpy(), index=freq.concept_id)
    gloss = pd.Series(freq.gloss.to_numpy(), index=freq.concept_id)

    units = Units(p.index, load_merges(), load_compounds())
    up = units.unit_p(p)
    codes = nary_huffman_reserving(up.to_numpy(), len(later), root_n=len(first), reserve2=args.reserve_2syl)
    sylls_of = {u: [first[c[0]], *(later[s] for s in c[1:])] for u, c in zip(up.index, codes)}

    rows = []
    for cid in p.index:
        words = [sylls_of[u] for u in units.expression(cid)]
        rows.append({
            "concept_id": cid,
            "gloss": gloss[cid],
            "kind": units.kind(cid),
            "p": p[cid],
            "p_word": up.get(cid) if units.kind(cid) == "word" else None,
            "syllables": sum(len(w) for w in words),
            "word": " ".join(render(*w) for w in words),
            "word_hyphenated": " ".join("-".join(render(x) for x in w) for w in words),
            "cvc": " ".join(".".join("".join(x) for x in w) for w in words),
            "ipa": " ".join(pronounce([render(*w) for w in words])),  # a compound is said together
        })
    lex = pd.DataFrame(rows)
    lex.insert(6, "letters", lex.word.str.replace(" ", "").str.len())
    own = lex[lex.kind == "word"]
    dupes = own.word[own.word.duplicated()]
    if len(dupes):
        raise RuntimeError(f"words spelled the same: {', '.join(dupes.head(10))}")
    lex["_order"] = lex.p_word.fillna(lex.p)
    lex = lex.sort_values(["kind", "_order"], ascending=[False, False]).drop(columns="_order")
    lex.to_csv(args.output, sep="\t", index=False, float_format="%.6g")

    avg_syl = float((own.p_word * own.syllables).sum())
    avg_let = float((own.p_word * own.letters).sum())
    entropy = -sum(x * math.log(x) for x in up if x > 0) / math.log(len(first))
    meta = {
        "concepts": len(lex),
        "own_words": len(own),
        "merged": int((lex.kind == "merged").sum()),
        "compounds": int((lex.kind == "compound").sum()),
        "words_per_syllables": {str(k): int(v) for k, v in own.syllables.value_counts().sort_index().items()},
        "free_slots_per_syllables": {str(k): v for k, v in free_slots(codes, len(later), len(first)).items()},
        "average_syllables": round(avg_syl, 4),
        "average_letters": round(avg_let, 4),
        "inventory": {"onsets": args.onsets, "vowels": args.vowels, "codas": args.codas},
        "first_syllables": len(first),
        "later_syllables": len(later),
        "reserve_2syl": args.reserve_2syl,
    }
    args.output.with_name("lexicon_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    own = own.sort_values("p_word", ascending=False)
    print(f"{len(lex)} concepts: {len(own)} with their own word, "
          f"{(lex.kind == 'merged').sum()} merged, {(lex.kind == 'compound').sum()} compounds")
    print(f"{len(first)} first syllables, {len(later)} later syllables")
    print(f"average word length {avg_syl:.3f} syllables, {avg_let:.2f} letters; "
          f"entropy lower bound {entropy:.3f} syllables")
    print("words per length:", ", ".join(f"{k} syl: {v}" for k, v in own.syllables.value_counts().sort_index().items()))
    print("free for new words:", ", ".join(f"{k} syl: {v}" for k, v in free_slots(codes, len(later), len(first)).items()))
    print("most frequent:", ", ".join(f"{g}={w}" for g, w in own[["gloss", "word_hyphenated"]].head(12).itertuples(index=False)))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
