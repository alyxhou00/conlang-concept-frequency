"""Find Concepticon concepts that can be said with existing words, and write
mapping/compounds.tsv for review.

A concept is a compound when its gloss has several words (ignoring notes in
brackets) and each word is itself the gloss of an active concept, e.g.
COCONUT TREE = COCONUT + TREE. Glosses with OR (BLACK OR DARK) are
alternatives, not compounds, and are skipped.

Our language puts the head first, so the order is
  things, properties etc.:  reversed (English compounds end in the head)
                            COCONUT TREE -> TREE COCONUT, MARRIED MAN -> MAN MARRIED
  actions and numbers:      kept (the head already comes first)
                            GIVE BIRTH -> GIVE BIRTH, NINETY SIX -> NINETY SIX
and then NOT and adpositions move after the word they belong to, because our
particles and adpositions follow their word:
                            NOT HAVE -> HAVE NOT, PUT IN ORDER -> PUT ORDER IN

The output is meant to be edited by hand: delete a row to give the concept its
own word, or change PARTS. build_lexicon.py reads the file as it is.

Run:  .venv/Scripts/python -X utf8 mapping/find_compounds.py
"""
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CONCEPTICON = ROOT / "data/concepticon-data/concepticondata/concepticon.tsv"
OUT = ROOT / "mapping/compounds.tsv"
KEEP_ORDER = {"Action/Process", "Number"}
# words that precede their word in English but follow it in our language
MOVE_AFTER = {"NOT", "AT", "IN", "ON", "FOR", "WITH", "FROM", "TO", "BY", "UNDER", "OVER", "ABOVE",
              "BELOW", "BEHIND", "NEAR", "TOWARDS", "THROUGH", "WITHOUT", "AFTER", "BEFORE",
              "INSIDE", "OUTSIDE", "BETWEEN", "AROUND", "AGAINST", "INTO", "OUT OF"}


def move_particles_after(words):
    """['PUT', 'IN', 'ORDER'] -> ['PUT', 'ORDER', 'IN'];  ['NOT', 'HAVE'] -> ['HAVE', 'NOT']"""
    words = list(words)
    i = 0
    while i < len(words) - 1:
        if words[i] in MOVE_AFTER and words[i + 1] not in MOVE_AFTER:
            words[i], words[i + 1] = words[i + 1], words[i]
            i += 2
        else:
            i += 1
    return words


def parts_of(gloss, by_gloss):
    """Concept IDs of the words in `gloss`, in English order, or None."""
    text = re.sub(r"\(.*?\)", " ", gloss)
    if re.search(r"\bOR\b", text):
        return None
    words = [w.removesuffix("'S") for w in text.split()]
    if len(words) < 2 or not all(w in by_gloss for w in words):
        return None
    return [by_gloss[w] for w in words]


def find_compounds(cs):
    cs = cs[cs.REPLACEMENT_ID.isna()]
    by_gloss = dict(zip(cs.GLOSS, cs.ID))
    gloss_of = dict(zip(cs.ID, cs.GLOSS))
    rows = []
    for _, r in cs.iterrows():
        parts = parts_of(r.GLOSS, by_gloss)
        if parts is None or r.ID in parts:
            continue
        if r.ONTOLOGICAL_CATEGORY not in KEEP_ORDER:
            parts = parts[::-1]
        else:
            moved = move_particles_after(gloss_of[p] for p in parts)
            parts = [by_gloss[w] for w in moved]
        rows.append((r.ID, r.GLOSS, " ".join(map(str, parts)), " + ".join(gloss_of[p] for p in parts),
                     r.ONTOLOGICAL_CATEGORY))
    return pd.DataFrame(rows, columns=["ID", "GLOSS", "PARTS", "PARTS_GLOSS", "CATEGORY"])


def main():
    cs = pd.read_csv(CONCEPTICON, sep="\t", keep_default_na=False, na_values=[""])
    out = find_compounds(cs)
    out.to_csv(OUT, sep="\t", index=False)
    print(f"{len(out)} compounds written to {OUT}")


if __name__ == "__main__":
    main()
