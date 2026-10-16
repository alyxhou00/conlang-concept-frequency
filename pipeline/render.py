"""Turn a concept-tagged text into our language, using out/lexicon.tsv.

Text format (see texts/):
  - one sentence per line; lines starting with "# " are comments
  - a token is a concept gloss with "_" for spaces (BE_BORN, SPIRIT_(ATTITUDE)),
    case does not matter, or "#" + a concept ID (#1209)
  - . , ? ! ; : are kept as punctuation

Because the text names concepts, not words, it stays valid when the lexicon is
rebuilt: render it again and it uses the new words.

Run:  .venv/Scripts/python -X utf8 pipeline/render.py texts/udhr-article-1.txt
"""
import argparse
import difflib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PUNCTUATION = set(".,?!;:")


class Lexicon:
    def __init__(self, path=ROOT / "out/lexicon.tsv"):
        lex = pd.read_csv(path, sep="\t", keep_default_na=False, na_values=[""])
        dupes = lex.gloss[lex.gloss.str.upper().duplicated()]
        if len(dupes):
            raise ValueError(f"glosses used twice: {', '.join(dupes)}")
        self.by_id = lex.set_index("concept_id")
        self.id_of = {g.upper(): cid for g, cid in zip(lex.gloss, lex.concept_id)}

    def lookup(self, token):
        """Lexicon row for a token (gloss with _ for spaces, or #ID)."""
        if token.startswith("#") and token[1:].isdigit():
            cid = int(token[1:])
            if cid not in self.by_id.index:
                raise KeyError(f"no concept with ID {cid}")
            return self.by_id.loc[cid]
        gloss = token.replace("_", " ").upper()
        if gloss not in self.id_of:
            close = difflib.get_close_matches(gloss, self.id_of, n=3)
            hint = f"; did you mean {', '.join(c.replace(' ', '_') for c in close)}?" if close else ""
            raise KeyError(f"unknown concept {token!r}{hint}")
        return self.by_id.loc[self.id_of[gloss]]


def render_line(line, lexicon):
    """(text in our language, IPA, glosses) for one tagged line."""
    words, ipas, glosses = [], [], []
    for token in line.split():
        if token in PUNCTUATION:
            if words:
                words[-1] += token
            glosses.append(token)
            continue
        row = lexicon.lookup(token)
        words.append(row.word)
        ipas.append(row.ipa)
        glosses.append(row.gloss.replace(" ", "_"))
    return " ".join(words), " ".join(ipas), " ".join(glosses)


def render_text(text, lexicon):
    """Rendered sentences: (comment lines before it, text, IPA, glosses)."""
    out, comments = [], []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            comments.append(line[2:])
            continue
        out.append((comments, *render_line(line, lexicon)))
        comments = []
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("text", type=Path, help="concept-tagged text file")
    ap.add_argument("--lexicon", type=Path, default=ROOT / "out/lexicon.tsv")
    args = ap.parse_args()

    for comments, text, ipa_line, glosses in render_text(args.text.read_text(encoding="utf-8"), Lexicon(args.lexicon)):
        for c in comments:
            print(f"# {c}")
        print(text)
        print(f"[{ipa_line}]")
        print(glosses)
        print()


if __name__ == "__main__":
    main()
