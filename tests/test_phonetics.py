import pandas as pd
import pytest

import build_docs
import phonetics
from phonetics import RULES, pronounce, syllables


def test_syllables_split_one_way():
    assert syllables("etsuhsen") == [("", "e", "t"), ("s", "u", "h"), ("s", "e", "n")]
    assert syllables("ihu") == [("", "i", ""), ("h", "u", "")]
    with pytest.raises(ValueError):
        syllables("tk")


def test_glottal_stop_keeps_words_apart():
    assert pronounce(["et", "e"]) == ["ʔɛt", "ʔɛ"]
    assert pronounce(["e", "te"]) == ["ʔɛ", "tɛ"]


def test_h_is_palatal_next_to_a_front_vowel():
    assert pronounce(["hitet"]) == ["çi.tɛt"]
    assert pronounce(["utöh"]) == ["ʔu.tøç"]
    assert pronounce(["ihu"]) == ["ʔi.çu"]
    assert pronounce(["hon"]) == ["xɔn"]
    assert pronounce(["etpëh"]) == ["ʔɛp.pɤx"]


def test_coda_t_and_n_take_the_place_of_a_labial_or_velar():
    assert pronounce(["hitet", "mö"]) == ["çi.tɛp", "mø"]
    assert pronounce(["önkën", "po"]) == ["ʔøŋ.kɤm", "pɔ"]
    assert pronounce(["etsuhsen", "hënöl"]) == ["ʔɛt.sux.sɛŋ", "xɤ.nøl"]


def test_no_assimilation_before_glottal_stop_palatal_or_other_places():
    assert pronounce(["et", "e"])[0] == "ʔɛt"
    assert pronounce(["et", "hi"])[0] == "ʔɛt"
    assert pronounce(["en", "ve", "re", "se", "le"])[0] == "ʔɛn"
    assert pronounce(["ul", "pe"])[0] == "ʔul"


# --- the docs and the lexicon must not drift apart from these rules ---

# the same placeholder parser as the docs build


def doc_examples():
    return [(src.name, m.group(2)) for src in sorted(build_docs.SRC.glob("*.md"))
            for m in build_docs.PLACEHOLDER.finditer(src.read_text(encoding="utf-8")) if m.group(1) == "say"]


def test_doc_examples_show_every_rule():
    # add an example to docs/src/01-phonology.md for each rule this names
    used = set()
    for name, arg in doc_examples():
        build_docs.Builder.say(arg, name, used)
    assert set(RULES) - used == set()


def test_changing_a_rule_breaks_the_doc_examples(monkeypatch):
    monkeypatch.setattr(phonetics, "FRONT", set("ie"))  # as if ö stopped being front
    with pytest.raises(ValueError, match="the sound rules say 'utöh' is"):
        for name, arg in doc_examples():
            build_docs.Builder.say(arg, name)


def test_latest_lexicon_matches_the_rules():
    # if this fails, the sound rules changed since the last release: release a new version
    version = build_docs.versions()[-1]
    lex = pd.read_csv(build_docs.LEXICON_DIR / f"{version}.tsv", sep="\t", keep_default_na=False, na_values=[""])
    said = lex.word.map(lambda w: " ".join(pronounce(w.split())))
    split = lex.word.map(lambda w: " ".join("-".join("".join(s) for s in syllables(x)) for x in w.split()))
    wrong = lex[(said != lex.ipa) | (split != lex.word_hyphenated)]
    assert wrong.empty, f"lexicon {version} differs from the rules in {len(wrong)} rows, e.g. {wrong.word.iloc[0]}"
