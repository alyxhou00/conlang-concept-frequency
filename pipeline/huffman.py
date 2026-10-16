"""n-ary Huffman coding, optionally with a different number of first symbols.

With n symbols per position (here: n CVC syllables), frequent items get short
codewords. `root_n` lets the first position of a codeword use a different
number of symbols than later positions (e.g. syllables with a zero onset are
allowed word-initially only).

Dummy zero-weight leaves are added so that every node except the root is full
and the root has exactly root_n children once N > root_n; otherwise codes would
be longer than needed.

`nary_huffman_reserving` keeps part of the two-symbol codewords free for words
added later: unused leaves can take new words without changing any existing
codeword and without breaking the prefix property.
"""
import heapq
import itertools
import math


def nary_huffman(weights, n, root_n=None):
    """Return one codeword per weight, as a tuple of symbol indices.

    The first symbol is in range(root_n), later symbols in range(n). Within
    each node the heaviest child gets symbol 0, so the most frequent items also
    get the lowest symbol indices.
    """
    root_n = n if root_n is None else root_n
    if n < 2 or root_n < 2:
        raise ValueError("need at least 2 symbols")
    N = len(weights)
    if N == 0:
        return []

    tiebreak = itertools.count()
    # heap entries: (weight, tiebreak, node); node is an int leaf, None (dummy) or a list of children
    heap = [(w, next(tiebreak), i) for i, w in enumerate(weights)]
    if N > root_n:
        # each merge removes n - 1 nodes; pad so the merges end at exactly root_n nodes
        heap += [(0.0, next(tiebreak), None) for _ in range((-(N - root_n)) % (n - 1))]
    heapq.heapify(heap)
    while len(heap) > root_n:
        children = [heapq.heappop(heap) for _ in range(n)]  # lightest first
        heapq.heappush(heap, (sum(c[0] for c in children), next(tiebreak), children[::-1]))
    root = sorted(heap, reverse=True)  # heaviest first

    codes = [None] * N
    stack = [(root, ())]
    while stack:
        node, prefix = stack.pop()
        if isinstance(node, list):
            for symbol, (_, _, child) in enumerate(node):
                stack.append((child, prefix + (symbol,)))
        elif node is not None:
            codes[node] = prefix
    return codes


def reserved_profile(n_items, ones, n, root_n, reserve2):
    """How many codewords of each length when a share of the two-symbol slots stays free.

    `ones` (codewords of length 1) is kept as given. At length 2, `reserve2` of
    the slots stay free; the rest are filled with the most frequent remaining
    items, and only as many slots as needed become prefixes for longer ones.
    Returns (counts, reserved), one entry per length starting at 1.
    """
    counts, reserved = [ones], [0]
    remaining, parents, depth = n_items - ones, root_n - ones, 2
    while remaining > 0:
        if parents <= 0:
            raise ValueError("no room for the remaining codewords")
        slots = parents * n
        r = math.ceil(reserve2 * slots) if depth == 2 else 0
        usable = slots - r
        if remaining <= usable:
            counts.append(remaining)
            reserved.append(r)
            break
        nxt = min(usable, math.ceil((remaining - usable) / (n - 1)))  # prefixes for longer codewords
        counts.append(usable - nxt)
        reserved.append(r)
        remaining -= usable - nxt
        parents, depth = nxt, depth + 1
    return counts, reserved


def code_from_profile(weights, counts, reserved, n, root_n):
    """Prefix code where the most frequent items get the shortest codewords,
    with counts[d-1] codewords of length d and reserved[d-1] free slots at that
    length. Within each node the heaviest child gets symbol 0."""
    order = sorted(range(len(weights)), key=lambda i: -weights[i])
    if sum(counts) != len(weights):
        raise ValueError("profile does not match the number of items")
    levels, k = [], 0
    for c in counts:
        levels.append(order[k:k + c])
        k += c
    # internal nodes at each length: slots - codewords - reserved
    parents, slots = [], root_n
    for d in range(len(counts) - 1):
        parents.append(slots - counts[d] - reserved[d])
        slots = parents[-1] * n

    below = []  # (weight, children) nodes built for the level underneath
    for d in range(len(counts), 0, -1):
        items = sorted([(weights[i], i) for i in levels[d - 1]] + below, key=lambda x: -x[0])
        n_slots = root_n if d == 1 else parents[d - 2] * n
        if len(items) > n_slots:
            raise ValueError(f"{len(items)} items do not fit in {n_slots} slots at length {d}")
        free = n_slots - len(items)  # reserved or unused slots
        if d == 1:
            root = items + [(0.0, None)] * free
            continue
        # spread the free slots over all parents (at the end of each), so that no
        # parent is left entirely free: that would free a shorter codeword
        n_parents, pos, below = n_slots // n, 0, []
        for k in range(n_parents):
            f = free // n_parents + (k >= n_parents - free % n_parents)
            group = items[pos:pos + n - f] + [(0.0, None)] * f
            pos += n - f
            below.append((sum(w for w, _ in group), group))

    codes = [None] * len(weights)
    stack = [(root, ())]
    while stack:
        node, prefix = stack.pop()
        if isinstance(node, list):
            for symbol, (_, child) in enumerate(node):
                stack.append((child, prefix + (symbol,)))
        elif node is not None:
            codes[node] = prefix
    return codes


def nary_huffman_reserving(weights, n, root_n=None, reserve2=0.0):
    """Like nary_huffman, but keeps `reserve2` of the two-symbol codewords free.
    The number of length-1 codewords is the same as without reservation; the
    least frequent items that no longer fit at length 2 move to length 3."""
    root_n = n if root_n is None else root_n
    codes = nary_huffman(weights, n, root_n)
    if reserve2 <= 0 or len(weights) <= root_n:
        return codes
    ones = sum(len(c) == 1 for c in codes)
    counts, reserved = reserved_profile(len(weights), ones, n, root_n, reserve2)
    return code_from_profile(weights, counts, reserved, n, root_n)


def free_slots(codes, n, root_n=None):
    """{length: number of unused codewords of that length} in the code tree.
    Each unused codeword can take a new word, or become the prefix of n longer ones."""
    root_n = n if root_n is None else root_n
    free, depth = {}, 1
    max_len = max(len(c) for c in codes)
    while depth <= max_len:
        parents = 1 if depth == 1 else len({c[:depth - 1] for c in codes if len(c) >= depth})
        slots = root_n if depth == 1 else parents * n
        free[depth] = slots - len({c[:depth] for c in codes if len(c) >= depth})
        depth += 1
    return free
