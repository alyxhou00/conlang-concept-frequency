"""Which concepts get a word of their own, and how the others are said.

mapping/merges.tsv     a concept is said with another concept's word (ME -> I).
                       SHARE splits its frequency when it goes to several
                       targets (WE -> half WE (EXCLUSIVE), half WE (INCLUSIVE)).
mapping/compounds.tsv  a concept is said with several existing words
                       (COCONUT TREE -> TREE COCONUT); each word gets the
                       compound's full frequency on top of its own, because
                       saying the compound uses every one of them.

Everything else is a "unit": a concept with its own word in the Huffman code.
"""
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
MERGES = ROOT / "mapping/merges.tsv"
COMPOUNDS = ROOT / "mapping/compounds.tsv"
TEXT = dict(keep_default_na=False, na_values=[""])


def load_merges(path=MERGES):
    """{source ID: [(target ID, share), ...]}, without rows that map a concept to itself."""
    merges = defaultdict(list)
    for r in pd.read_csv(path, sep="\t", **TEXT).itertuples():
        if r.SOURCE_ID != r.TARGET_ID:
            merges[int(r.SOURCE_ID)].append((int(r.TARGET_ID), float(r.SHARE)))
    return dict(merges)


def load_compounds(path=COMPOUNDS):
    """{compound ID: [part ID, ...]} in our word order."""
    return {int(r.ID): [int(x) for x in r.PARTS.split()]
            for r in pd.read_csv(path, sep="\t", **TEXT).itertuples()}


class Units:
    def __init__(self, concepts, merges, compounds):
        concepts = set(concepts)
        self.merges = {s: t for s, t in merges.items()
                       if s in concepts and all(x in concepts for x, _ in t)}
        # a merge wins over a compound (YOU TWO is merged into YOU, not said as TWO YOU)
        self.compounds = {c: parts for c, parts in compounds.items()
                          if c in concepts and c not in self.merges and all(x in concepts for x in parts)}
        self.units = sorted(concepts - set(self.merges) - set(self.compounds))

    def kind(self, cid):
        return "merged" if cid in self.merges else "compound" if cid in self.compounds else "word"

    def weights(self, cid, _depth=0):
        """{unit: how many times it is used} each time `cid` is said (shares for merges)."""
        if _depth > 20:
            raise ValueError(f"merges/compounds loop at concept {cid}")
        out = defaultdict(float)
        if cid in self.merges:
            for target, share in self.merges[cid]:
                for u, w in self.weights(target, _depth + 1).items():
                    out[u] += share * w
        elif cid in self.compounds:
            for part in self.compounds[cid]:
                for u, w in self.weights(part, _depth + 1).items():
                    out[u] += w
        else:
            out[cid] = 1.0
        return dict(out)

    def expression(self, cid, _depth=0):
        """Units, in order, that say `cid`. A merge with several targets uses the
        largest share (the first one listed on a tie)."""
        if _depth > 20:
            raise ValueError(f"merges/compounds loop at concept {cid}")
        if cid in self.merges:
            target = max(self.merges[cid], key=lambda t: t[1])[0]
            return self.expression(target, _depth + 1)
        if cid in self.compounds:
            return [u for part in self.compounds[cid] for u in self.expression(part, _depth + 1)]
        return [cid]

    def unit_p(self, p):
        """Frequency of each unit: its own plus what merged and compound concepts add."""
        total = defaultdict(float)
        for cid, x in p.items():
            for u, w in self.weights(cid).items():
                total[u] += w * x
        s = pd.Series(total)
        return (s / s.sum()).sort_values(ascending=False)
