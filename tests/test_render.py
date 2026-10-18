import pandas as pd
import pytest

import warnings

from render import Lexicon, MisreadWarning, render_text


@pytest.fixture
def lexicon(tmp_path):
    path = tmp_path / "lexicon.tsv"
    pd.DataFrame({
        "concept_id": [1209, 1583, 900002, 42, 1215, 1213, 2312],
        "gloss": ["I", "SEE", "RIGHT (ENTITLEMENT)", "NA", "THOU", "YOU", "YOU (OBLIQUE CASE OF YOU)"],
        "word": ["ö", "ken", "lih", "nan", "a", "së", "së"],
        "ipa": ["ʔø", "kɛn", "lix", "nɑn", "ʔɑ", "sɤ", "sɤ"],
    }).to_csv(path, sep="\t", index=False)
    return Lexicon(path)


def test_glosses_ids_and_punctuation(lexicon):
    [(comments, text, ipa, gloss)] = render_text("# a comment\nI see #900002 .", lexicon)
    assert comments == ["a comment"]
    assert text == "ö ken lih."
    assert ipa == "ʔø kɛn liç"
    assert gloss == "I SEE RIGHT_(ENTITLEMENT) ."


def test_underscores_stand_for_spaces(lexicon):
    assert render_text("RIGHT_(ENTITLEMENT)", lexicon)[0][1] == "lih"


def test_words_like_nan_and_glosses_like_na_survive_reading(lexicon):
    assert render_text("NA", lexicon)[0][1] == "nan"


def test_unknown_concept_suggests_close_glosses(lexicon):
    with pytest.raises(KeyError, match="did you mean SEE"):
        render_text("SEEE", lexicon)


def test_ipa_uses_the_sound_rules_and_stops_at_pauses(lexicon):
    # ken lih: n before l stays; lih has [ç] after i. A comma is a pause, so no assimilation across it.
    assert render_text("SEE I", lexicon)[0][2] == "kɛn ʔø"
    assert render_text("NA , SEE", lexicon)[0][2] == "nɑn kɛn"
    assert render_text("NA SEE", lexicon)[0][2] == "nɑŋ kɛn"


def test_clear_labels_for_thou_and_you(lexicon):
    # YOU_(SINGULAR) is THOU, YOU_(PLURAL) is YOU; the gloss line shows the clear labels
    [(_, text, _, gloss)] = render_text("I SEE YOU_(SINGULAR) , THOU , you_(plural) , #1213 .", lexicon)
    assert text == "ö ken a, a, së, së."
    assert gloss == "I SEE YOU_(SINGULAR) , YOU_(SINGULAR) , YOU_(PLURAL) , YOU_(PLURAL) ."


def test_clear_labels_raise_no_warning(lexicon):
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        render_text("THOU SEE YOU_(PLURAL) #1213 YOU_(SINGULAR)", lexicon)


@pytest.mark.parametrize("token", ["YOU", "you", "YOU_(OBLIQUE_CASE_OF_YOU)"])
def test_plural_you_that_reads_like_one_person_warns(lexicon, token):
    with pytest.warns(MisreadWarning, match=r"you, several people.*YOU_\(PLURAL\)"):
        [(_, text, _, _)] = render_text(f"I SEE {token}", lexicon)
    assert text == "ö ken së"  # still rendered


def test_clear_label_must_not_be_a_gloss(tmp_path):
    path = tmp_path / "lexicon.tsv"
    pd.DataFrame({"concept_id": [1, 1215], "gloss": ["YOU (SINGULAR)", "THOU"],
                  "word": ["x", "a"], "ipa": ["x", "ʔɑ"]}).to_csv(path, sep="\t", index=False)
    with pytest.raises(ValueError, match=r"YOU \(SINGULAR\) is a gloss"):
        Lexicon(path)
