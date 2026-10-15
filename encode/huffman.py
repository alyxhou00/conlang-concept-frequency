"""n-ary Huffman coding.

With n symbols per position (here: n CVC syllables), frequent items get short
codewords. Dummy zero-weight leaves are added so that (N - 1) % (n - 1) == 0;
otherwise the root would not be full and codes would be longer than needed.
"""
import heapq
import itertools


def nary_huffman(weights, n):
    """Return one codeword per weight, as a tuple of symbol indices in range(n).

    Within each merge the heaviest child gets symbol 0, so the most frequent
    items also get the lowest symbol indices.
    """
    if n < 2:
        raise ValueError("need at least 2 symbols")
    N = len(weights)
    if N == 0:
        return []
    if N == 1:
        return [(0,)]

    tiebreak = itertools.count()
    # heap entries: (weight, tiebreak, node); node is an int leaf, None (dummy) or a list of children
    heap = [(w, next(tiebreak), i) for i, w in enumerate(weights)]
    heap += [(0.0, next(tiebreak), None) for _ in range((-(N - 1)) % (n - 1))]
    heapq.heapify(heap)
    while len(heap) > 1:
        children = [heapq.heappop(heap) for _ in range(n)]  # lightest first
        heapq.heappush(heap, (sum(c[0] for c in children), next(tiebreak), children[::-1]))

    codes = [None] * N
    stack = [(heap[0][2], ())]
    while stack:
        node, prefix = stack.pop()
        if isinstance(node, list):
            for symbol, (_, _, child) in enumerate(node):
                stack.append((child, prefix + (symbol,)))
        elif node is not None:
            codes[node] = prefix
    return codes
