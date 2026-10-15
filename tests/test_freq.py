import numpy as np
import pandas as pd

from build_concept_freq import outlier_mask


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
