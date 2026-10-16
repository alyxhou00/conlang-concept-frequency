import pandas as pd
import pytest

from render import Lexicon, render_text


@pytest.fixture
def lexicon(tmp_path):
    path = tmp_path / "lexicon.tsv"
    pd.DataFrame({
        "concept_id": [1209, 1583, 900002, 42],
        "gloss": ["I", "SEE", "RIGHT (ENTITLEMENT)", "NA"],
        "word": ["ö", "ken", "lih", "nan"],
        "ipa": ["ʔø", "kɛn", "lix", "nɑn"],
    }).to_csv(path, sep="\t", index=False)
    return Lexicon(path)


def test_glosses_ids_and_punctuation(lexicon):
    [(comments, text, ipa, gloss)] = render_text("# a comment\nI see #900002 .", lexicon)
    assert comments == ["a comment"]
    assert text == "ö ken lih."
    assert ipa == "ʔø kɛn lix"
    assert gloss == "I SEE RIGHT_(ENTITLEMENT) ."


def test_underscores_stand_for_spaces(lexicon):
    assert render_text("RIGHT_(ENTITLEMENT)", lexicon)[0][1] == "lih"


def test_words_like_nan_and_glosses_like_na_survive_reading(lexicon):
    assert render_text("NA", lexicon)[0][1] == "nan"


def test_unknown_concept_suggests_close_glosses(lexicon):
    with pytest.raises(KeyError, match="did you mean SEE"):
        render_text("SEEE", lexicon)
