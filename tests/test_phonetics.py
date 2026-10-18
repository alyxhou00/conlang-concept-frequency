import pytest

from phonetics import pronounce, syllables


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
