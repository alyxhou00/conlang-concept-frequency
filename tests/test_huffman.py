import math
import random

import pytest

from huffman import code_from_profile, free_slots, nary_huffman, nary_huffman_reserving


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


# --- different number of symbols in the first position (root_n) -------------

def brute_force_best(w, n, root_n, max_len=8):
    """Smallest average length over all length assignments that fit the tree."""
    best = math.inf
    order = sorted(range(len(w)), key=lambda i: -w[i])
    def fits(lens):  # Kraft-type condition for root_n first symbols and n later ones
        return sum(1 / (root_n * n ** (L - 1)) for L in lens) <= 1 + 1e-12
    def rec(i, prev, lens):
        nonlocal best
        if i == len(order):
            if fits(lens):
                best = min(best, sum(w[order[k]] * L for k, L in enumerate(lens)) / sum(w))
            return
        for L in range(prev, max_len + 1):  # more frequent items are never longer
            rec(i + 1, L, lens + [L])
    rec(0, 1, [])
    return best


@pytest.mark.parametrize("n,root_n", [(2, 3), (3, 2), (2, 5), (3, 4)])
def test_root_n_is_optimal_on_small_cases(n, root_n):
    rnd = random.Random(n * 10 + root_n)
    for _ in range(20):
        w = [rnd.paretovariate(1.0) for _ in range(rnd.randint(2, 8))]
        codes = nary_huffman(w, n, root_n=root_n)
        assert avg_len(w, codes) == pytest.approx(brute_force_best(w, n, root_n))


@pytest.mark.parametrize("N", [1, 5, 385, 386, 1875, 5000])
def test_root_n_symbol_ranges_and_prefix_free(N):
    rnd = random.Random(N)
    w = [rnd.paretovariate(1.2) for _ in range(N)]
    codes = nary_huffman(w, 350, root_n=385)
    assert is_prefix_free(codes)
    assert all(c[0] < 385 and all(s < 350 for s in c[1:]) for c in codes)
    assert sum(1 / (385 * 350 ** (len(c) - 1)) for c in codes) <= 1 + 1e-12


def test_root_n_count_of_one_syllable_words():
    # 1875 concepts, 385 first syllables, 350 later ones: (385 - k) * 350 >= 1875 - k
    # allows at most k = 380 one-syllable words
    w = [1 / (i + 1) for i in range(1875)]
    lens = [len(c) for c in nary_huffman(w, 350, root_n=385)]
    assert lens.count(1) == 380 and lens.count(2) == 1495


def test_reservation_keeps_two_symbol_slots_free_and_ones_unchanged():
    rnd = random.Random(7)
    w = sorted((rnd.paretovariate(1.1) for _ in range(3000)), reverse=True)
    plain = nary_huffman(w, 50, root_n=60)
    reserved = nary_huffman_reserving(w, 50, root_n=60, reserve2=0.10)
    assert is_prefix_free(reserved)
    assert all(c[0] < 60 and all(s < 50 for s in c[1:]) for c in reserved)
    ones = sum(len(c) == 1 for c in plain)
    assert sum(len(c) == 1 for c in reserved) == ones
    two_slots = (60 - ones) * 50
    free = free_slots(reserved, 50, 60)
    assert free[1] == 0                      # no first symbol is left entirely free
    assert free[2] >= 0.10 * two_slots
    assert avg_len(w, reserved) >= avg_len(w, plain) - 1e-12
    lens = [len(c) for c in reserved]
    assert lens == sorted(lens)  # more frequent items are never longer


def test_profile_from_huffman_lengths_is_as_short_as_huffman():
    rnd = random.Random(3)
    w = [rnd.paretovariate(1.2) for _ in range(800)]
    plain = nary_huffman(w, 20, root_n=25)
    counts = [sum(len(c) == d for c in plain) for d in range(1, max(map(len, plain)) + 1)]
    rebuilt = code_from_profile(w, counts, [0] * len(counts), 20, 25)
    assert is_prefix_free(rebuilt)
    assert avg_len(w, rebuilt) == pytest.approx(avg_len(w, plain))


def test_no_reservation_is_plain_huffman():
    w = [5, 4, 3, 2, 1] * 40
    assert nary_huffman_reserving(w, 7, root_n=9, reserve2=0) == nary_huffman(w, 7, root_n=9)


def test_free_slots_count_unused_leaves():
    codes = [(0,), (1, 0), (1, 1)]  # n=3: (2,) unused at length 1, (1, 2) unused at length 2
    assert free_slots(codes, 3) == {1: 1, 2: 1}


def test_root_n_equal_to_n_is_plain_huffman():
    rnd = random.Random(0)
    w = [rnd.random() for _ in range(300)]
    assert avg_len(w, nary_huffman(w, 7, root_n=7)) == pytest.approx(avg_len(w, nary_huffman(w, 7)))
