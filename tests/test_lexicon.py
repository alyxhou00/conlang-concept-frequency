import pytest

from build_lexicon import CODAS, ONSETS, VOWELS, ZERO, ipa, render, syllable_inventory, vary


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


def test_each_syllable_handed_out_once():
    first, later = syllable_inventory(ONSETS, VOWELS, CODAS)
    assert len(set(first)) == len(first) and len(set(later)) == len(later)


def test_coprime_slot_counts_give_the_simple_cycle():
    # 3, 4, 5 share no factor: syllable k is (onset k, vowel k, coda k), every combination once
    o, v, c = "ptk", "aeiu", "mnslr"
    ordered, _ = vary([(x, y, z) for x in o for y in v for z in c])
    assert ordered == [(o[k % 3], v[k % 4], c[k % 5]) for k in range(60)]


def test_shared_factor_still_covers_everything_and_varies():
    # 10 and 5 share a factor, so the simple cycle would repeat; vary must not
    o, v, c = "mnptkshvrl", "iöeuëoa", "nthlg"
    every = [(x, y, z) for x in o for y in v for z in c]
    ordered, _ = vary(every)
    assert sorted(ordered) == sorted(every)
    assert all(all(x != y for x, y in zip(a, b)) for a, b in zip(ordered, ordered[1:]))


@pytest.mark.parametrize("which", [0, 1])
def test_neighbours_of_the_same_length_share_no_written_letter(which):
    sylls = syllable_inventory(ONSETS, VOWELS, CODAS)[which]
    for a, b in zip(sylls, sylls[1:]):
        if len(render(a)) == len(render(b)):
            assert not any(x == y != ZERO for x, y in zip(a, b)), (render(a), render(b))


def test_every_one_and_two_syllable_word_is_spelled_uniquely():
    first, later = syllable_inventory(ONSETS, VOWELS, CODAS)
    words = [render(a) for a in first] + [render(a, b) for a in first for b in later]
    assert len(words) == len(set(words)) == 385 + 385 * 350


def test_word_initial_zero_onset_is_a_glottal_stop():
    assert ipa((ZERO, "a", "n"), ("t", "ë", ZERO)) == "ʔɑn.tɤ"
    assert ipa(("s", "o", "h")) == "sɔx"


def test_one_and_two_syllable_word_pairs_never_sound_the_same():
    # spoken without pauses, two words must not sound like two other words
    # ("et e" vs "e te"); the glottal stop prevents that
    first, later = syllable_inventory(ONSETS, VOWELS, CODAS)
    sound = lambda *s: ipa(*s).replace(".", "")
    words = [sound(a) for a in first] + [sound(a, b) for a in first[:60] for b in later[:60]]
    pairs = [a + b for a in words[:800] for b in words[:800]]
    assert len(pairs) == len(set(pairs))


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
