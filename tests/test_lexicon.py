import pytest

from build_lexicon import CODAS, ONSETS, VOWELS, ZERO, render, syllable_inventory


def test_default_inventory_sizes():
    first, later = syllable_inventory(ONSETS, VOWELS, CODAS)
    assert len(first) == 11 * 7 * 5 == 385
    assert len(later) == 10 * 7 * 5 == 350
    assert all(s[0] != ZERO for s in later)


def test_zero_consonant_is_not_written():
    assert render((ZERO, "a", ZERO)) == "a"
    assert render((ZERO, "ö", "n"), ("t", "ë", ZERO)) == "öntë"


def test_shortest_syllables_come_first():
    first, _ = syllable_inventory(ONSETS, VOWELS, CODAS)
    lengths = [len(render(s)) for s in first]
    assert lengths == sorted(lengths) and lengths[0] == 1


def test_every_one_and_two_syllable_word_is_spelled_uniquely():
    first, later = syllable_inventory(ONSETS, VOWELS, CODAS)
    words = [render(a) for a in first] + [render(a, b) for a in first for b in later]
    assert len(words) == len(set(words)) == 385 + 385 * 350


def test_zero_onset_inside_a_word_would_be_ambiguous():
    # this is why later syllables must not have a zero onset
    assert render((ZERO, "a", "n"), (ZERO, "a", ZERO)) == render((ZERO, "a", ZERO), ("n", "a", ZERO))


def test_accepts_decomposed_umlauts():
    first, _ = syllable_inventory(ONSETS, "iö", CODAS)  # o + combining diaeresis
    assert any(s[1] == "ö" for s in first)


@pytest.mark.parametrize("onsets,vowels,codas", [
    ("mna", "ai", "n"),     # a is both consonant and vowel
    ("mm", "a", "n"),       # repeated onset
    ("m", f"a{ZERO}", "n"), # zero vowel
    (ZERO, "a", "n"),       # no real onset for later syllables
])
def test_rejects_bad_inventories(onsets, vowels, codas):
    with pytest.raises(ValueError):
        syllable_inventory(onsets, vowels, codas)
