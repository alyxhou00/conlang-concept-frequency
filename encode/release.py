"""Freeze the current lexicon as a numbered version.

Writes lexicon/<version>.tsv (concepts and words, no frequencies) and
lexicon/<version>.json (statistics, sound inventory, git commit), and adds an
entry to lexicon/CHANGELOG.md. A version that already exists is never
overwritten.

Versions follow semantic versioning (see docs/00-introduction.md):
0.x are betas whose words may still change; from 1.0.0 on, existing words
never change and 1.x only adds words.

Run:  .venv/Scripts/python -X utf8 encode/release.py 0.1.0 --note "first beta"
"""
import argparse
import datetime
import json
import re
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
LEXICON_DIR = ROOT / "lexicon"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[0-9A-Za-z.-]+)?$")
COLUMNS = ["rank", "concept_id", "gloss", "kind", "status", "word", "word_hyphenated", "cvc", "ipa"]


def version_table(lex):
    """Published columns only. `rank` orders the words by frequency (1 = most
    frequent); merged and compound concepts have no rank."""
    own = lex[lex.kind == "word"].sort_values("p_word", ascending=False).copy()
    own["rank"] = range(1, len(own) + 1)
    rest = lex[lex.kind != "word"].sort_values(["kind", "gloss"]).copy()
    rest["rank"] = pd.NA
    out = pd.concat([own, rest], ignore_index=True)
    out["status"] = "active"
    out["rank"] = out["rank"].astype("Int64")
    return out[COLUMNS]


def git_commit():
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("version", help="semantic version, e.g. 0.1.0")
    ap.add_argument("--note", default="", help="one line for the changelog")
    ap.add_argument("--lexicon", type=Path, default=ROOT / "out/lexicon.tsv")
    args = ap.parse_args()

    if not SEMVER.match(args.version):
        raise SystemExit(f"{args.version!r} is not a semantic version like 0.1.0")
    tsv, meta_path = LEXICON_DIR / f"{args.version}.tsv", LEXICON_DIR / f"{args.version}.json"
    if tsv.exists() or meta_path.exists():
        raise SystemExit(f"version {args.version} already exists; versions are never overwritten")

    lex = pd.read_csv(args.lexicon, sep="\t", keep_default_na=False, na_values=[""])
    meta = json.loads(args.lexicon.with_name("lexicon_meta.json").read_text(encoding="utf-8"))
    meta = {"version": args.version, "date": datetime.date.today().isoformat(),
            "built_from_commit": git_commit(), **meta}

    LEXICON_DIR.mkdir(exist_ok=True)
    version_table(lex).to_csv(tsv, sep="\t", index=False)
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    changelog = LEXICON_DIR / "CHANGELOG.md"
    old = changelog.read_text(encoding="utf-8") if changelog.exists() else "# Lexicon changelog\n"
    head, _, rest = old.partition("\n")
    entry = (f"\n## {args.version} ({meta['date']})\n\n"
             + (f"{args.note}\n\n" if args.note else "")
             + f"- {meta['concepts']} concepts, {meta['own_words']} with their own word\n"
             + f"- average word: {meta['average_syllables']} syllables, {meta['average_letters']} letters\n"
             + "- free for new words: " + ", ".join(f"{v} with {k} syllables"
                                                    for k, v in meta["free_slots_per_syllables"].items() if v) + "\n")
    changelog.write_text(head + "\n" + entry + rest, encoding="utf-8")
    print(f"wrote {tsv}, {meta_path} and {changelog}")


if __name__ == "__main__":
    main()
