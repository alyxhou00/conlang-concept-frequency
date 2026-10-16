import pandas as pd
import pytest

from units import Units

# concepts: 1 I, 2 ME, 3 WE, 4 WE (EXCL), 5 WE (INCL), 6 TREE, 7 COCONUT, 8 COCONUT TREE, 9 YOU TWO, 10 TWO
MERGES = {2: [(1, 1.0)], 3: [(4, 0.5), (5, 0.5)], 9: [(5, 1.0)]}
COMPOUNDS = {8: [6, 7], 9: [10, 5]}


def units():
    return Units(range(1, 11), MERGES, COMPOUNDS)


def test_kinds():
    u = units()
    assert [u.kind(c) for c in (1, 2, 8)] == ["word", "merged", "compound"]
    assert u.units == [1, 4, 5, 6, 7, 10]


def test_merge_wins_over_compound():
    assert units().kind(9) == "merged"


def test_merged_frequency_is_added_and_split_by_share():
    p = pd.Series({1: 0.1, 2: 0.1, 3: 0.2, 4: 0.1, 5: 0.1, 6: 0.1, 7: 0.1, 8: 0.1, 9: 0.05, 10: 0.05})
    up = units().unit_p(p)
    assert up.sum() == pytest.approx(1)
    raw = {1: 0.2, 4: 0.2, 5: 0.25, 6: 0.2, 7: 0.2, 10: 0.05}  # before normalising
    total = sum(raw.values())
    for u, x in raw.items():
        assert up[u] == pytest.approx(x / total)


def test_expression():
    u = units()
    assert u.expression(2) == [1]        # ME is said with I's word
    assert u.expression(3) == [4]        # equal shares: the first target
    assert u.expression(8) == [6, 7]     # COCONUT TREE -> TREE COCONUT


def test_parts_missing_from_the_concept_set_keep_the_compound_as_a_word():
    u = Units([6, 8], {}, COMPOUNDS)     # COCONUT (7) missing
    assert u.kind(8) == "word"


def test_loop_is_reported():
    u = Units([1, 2], {1: [(2, 1.0)], 2: [(1, 1.0)]}, {})
    with pytest.raises(ValueError):
        u.weights(1)
