import pandas as pd
import pytest

import build_docs
from release import SEMVER, version_table


def test_version_table_ranks_words_and_hides_frequencies():
    lex = pd.DataFrame({
        "concept_id": [1, 2, 3, 4], "gloss": ["A", "B", "ME", "TREE COCONUT"],
        "kind": ["word", "word", "merged", "compound"],
        "p": [0.1, 0.5, 0.2, 0.2], "p_word": [0.2, 0.6, None, None],
        "word": ["a", "e", "a", "e a"], "word_hyphenated": ["a", "e", "a", "e a"],
        "cvc": ["ØaØ", "ØeØ", "ØaØ", "ØeØ ØaØ"], "ipa": ["ʔɑ", "ʔɛ", "ʔɑ", "ʔɛ ʔɑ"],
    })
    out = version_table(lex)
    assert "p" not in out.columns and "p_word" not in out.columns
    assert out.gloss.tolist()[:2] == ["B", "A"] and out["rank"].tolist()[:2] == [1, 2]
    assert out["rank"].isna().sum() == 2
    assert set(out.status) == {"active"}


@pytest.mark.parametrize("v,ok", [("0.1.0", True), ("1.0.0", True), ("1.0.0-beta.1", True),
                                  ("1.0", False), ("v1.0.0", False), ("01.0.0", False)])
def test_semantic_versions(v, ok):
    assert bool(SEMVER.match(v)) == ok


def test_versions_sort_numerically_and_prereleases_first(tmp_path, monkeypatch):
    for v in ["0.10.0", "0.2.0", "1.0.0", "1.0.0-beta.1"]:
        (tmp_path / f"{v}.tsv").write_text("")
    monkeypatch.setattr(build_docs, "LEXICON_DIR", tmp_path)
    assert build_docs.versions() == ["0.2.0", "0.10.0", "1.0.0-beta.1", "1.0.0"]


def test_docs_are_up_to_date_with_the_latest_version():
    # fails when docs/src or a new lexicon version was changed without running docs/build_docs.py
    stale = [p.name for p, content in build_docs.build().items()
             if not p.exists() or p.read_text(encoding="utf-8") != content]
    assert not stale, f"run docs/build_docs.py; out of date: {stale}"


def test_escaped_placeholder_stays_literal():
    b = build_docs.Builder(build_docs.versions()[-1])
    assert b.fill(r"use \{{w: I}} for {{w: I}}", "x.md").endswith("use {{w: I}} for *" + b.words("I") + "*")
