import math
import random

import pytest

from huffman import nary_huffman
from build_lexicon import cvc_syllables


def is_prefix_free(codes):
    s = set(codes)
    return len(s) == len(codes) and not any(c[:k] in s for c in codes for k in range(1, len(c)))


def avg_len(w, codes):
    return sum(x * len(c) for x, c in zip(w, codes)) / sum(w)


def test_binary_textbook_example():
    # classic example: optimal average length is 2.2 bits
    w = [0.4, 0.2, 0.2, 0.1, 0.1]
    assert avg_len(w, nary_huffman(w, 2)) == pytest.approx(2.2)


def test_ternary_needs_dummy_symbols():
    # N=4, n=3: (4-1) % 2 != 0, so one dummy is added and the top item gets length 1
    codes = nary_huffman([0.4, 0.3, 0.2, 0.1], 3)
    assert sorted(len(c) for c in codes) == [1, 1, 2, 2]
    assert len(codes[0]) == 1


@pytest.mark.parametrize("n", [2, 3, 5, 48, 720])
@pytest.mark.parametrize("N", [1, 2, 7, 200, 3000])
def test_prefix_free_and_within_entropy_bounds(n, N):
    rnd = random.Random(N * 1000 + n)
    w = [rnd.paretovariate(1.2) for _ in range(N)]
    codes = nary_huffman(w, n)
    assert len(codes) == N
    assert all(0 <= s < n for c in codes for s in c)
    assert is_prefix_free(codes)
    assert sum(n ** -len(c) for c in codes) <= 1 + 1e-12  # Kraft inequality
    p = [x / sum(w) for x in w]
    h = -sum(x * math.log(x, n) for x in p if x > 0)
    assert avg_len(w, codes) >= h - 1e-9  # Shannon lower bound
    if N > 1:  # a single item still needs a 1-symbol word although its entropy is 0
        assert avg_len(w, codes) < h + 1


def test_more_symbols_than_items_gives_length_one():
    codes = nary_huffman([5, 4, 3, 2, 1], 720)
    assert all(len(c) == 1 for c in codes)


def test_most_frequent_never_longer():
    w = [100, 50, 20, 10, 5, 2, 1, 1, 1]
    codes = nary_huffman(w, 2)
    lens = [len(c) for c in codes]
    assert lens == sorted(lens)  # weights are sorted descending, so lengths must not decrease


def test_cvc_inventory_default_size():
    syl = cvc_syllables("ptkbdgmnslfh", "aeiou")
    assert len(syl) == 12 * 5 * 12 == len(set(syl))
    assert all(len(s) == 3 for s in syl)


def test_cvc_rejects_overlapping_letters():
    with pytest.raises(ValueError):
        cvc_syllables("pta", "aei")
