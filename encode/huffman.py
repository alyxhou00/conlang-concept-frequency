"""n-ary Huffman coding, optionally with a different number of first symbols.

With n symbols per position (here: n CVC syllables), frequent items get short
codewords. `root_n` lets the first position of a codeword use a different
number of symbols than later positions (e.g. syllables with a zero onset are
allowed word-initially only).

Dummy zero-weight leaves are added so that every node except the root is full
and the root has exactly root_n children once N > root_n; otherwise codes would
be longer than needed.
"""
import heapq
import itertools


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
