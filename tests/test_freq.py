from collections import Counter

import numpy as np
import pandas as pd
import pytest

from build_concept_freq import clean_words, combine, outlier_mask, pick_word


def frame(rows):
    return pd.DataFrame(rows, columns=["de", "en", "ja"], dtype=float)


def test_value_ten_times_off_the_median_is_dropped():
    m = outlier_mask(frame([[1e-3, 1.2e-3, 2e-2]]), 10)
    assert m.values.tolist() == [[False, False, True]]


def test_values_within_the_factor_are_kept():
    m = outlier_mask(frame([[1e-3, 1.2e-3, 8e-3]]), 10)
    assert not m.values.any()


def test_missing_values_are_not_outliers():
    m = outlier_mask(frame([[1e-3, np.nan, 1e-1]]), 10)
    assert not m.values.any()  # median of two values is between them, but all-dropped rows keep everything


def test_never_drops_every_language():
    p = pd.DataFrame([[1e-5, 1e-5, 1e-1, 1e-1]], columns=list("abcd"))
    assert not outlier_mask(p, 10).values.any()


def test_factor_one_or_less_disables():
    assert not outlier_mask(frame([[1e-6, 1e-3, 1e-1]]), 0).values.any()


# --- word candidates from concept lists ---------------------------------------


def test_clean_words_drops_notes_and_splits_alternatives():
    assert clean_words("hermano (de la mujer)", "es") == ["hermano"]
    assert clean_words("ronsoco, carpincho", "es") == ["ronsoco", "carpincho"]
    assert clean_words("洗（衣服）", "zh") == ["洗"]
    assert clean_words("to sleep", "en") == ["sleep"]
    assert clean_words("ARM OR HAND", "en") == ["arm", "hand"]
    assert clean_words("¿Cuántos?", "es") == ["cuántos"]


def test_pick_word_prefers_single_words_then_agreement():
    assert pick_word(Counter({"ich und du": 5, "wir": 1}), "de")[0] == "wir"
    assert pick_word(Counter({"melone": 3, "wassermelone": 1}), "de")[0] == "melone"
    assert pick_word(Counter({"ich und du": 5}), "de")[0] is None  # phrases are not used


def test_concepts_without_data_get_the_lowest_frequency():
    df = pd.DataFrame({"concept_id": [1, 2, 1, 2], "lang": ["en", "en", "de", "de"],
                       "freq_pm": [100.0, 10.0, 80.0, 20.0]})
    glosses = pd.Series({1: "A", 2: "B", 3: "C"})
    out = combine(df, 0, 10, glosses).set_index("gloss")
    assert out.loc["C", "n_langs"] == 0
    assert out.loc["C", "p"] == pytest.approx(out.loc["B", "p"])
    assert out.p.sum() == pytest.approx(1)
    assert "C" not in combine(df, 1, 10, glosses).gloss.values
