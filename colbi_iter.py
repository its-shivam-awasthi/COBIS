from typing import List, Tuple

# ============================================================
# COLBI-Iter: Center-Oriented Leaf Binary Insertion + Iterative Merges
#   - Stable: (value, seq) ordering preserves original order on equals
#   - Leaf step: COBIS (center-half decision + upper_bound insertion)
#   - Merge step: stable merge with optional "galloping" (exponential probe)
#
# Public:
#   colbi_iter_sort(values: List, leaf_size: int = 128, gallop_thresh: int = 7) -> List
#
# Notes:
#   - Works for any Python-comparable types (ints, floats, strings, tuples...).
#   - Stability guaranteed by "seq" (original position) as tie-breaker.
#   - Galloping helps on partially-sorted / skewed inputs; overhead is low on random.
# ============================================================

# ---------- (value, seq) comparators ----------
def _le(v1, s1, v2, s2) -> bool:
    """(v1, s1) <= (v2, s2) — stable on equals."""
    if v1 < v2:
        return True
    if v1 > v2:
        return False
    return s1 <= s2

def _lt(v1, s1, v2, s2) -> bool:
    """(v1, s1) < (v2, s2)."""
    if v1 < v2:
        return True
    if v1 > v2:
        return False
    return s1 < s2

# ---------- Leaf sorter: COBIS on parallel arrays (stable) ----------
def cobis_insert_sorted(outv: List, outs: List[int], v, s) -> None:
    """
    Insert (v, s) into sorted (outv, outs) using:
      - center-oriented half choice
      - upper_bound within half (stable: equals go to the right)
    """
    n = len(outv)
    if n == 0:
        outv.append(v)
        outs.append(s)
        return

    mid = (n - 1) // 2
    if _le(v, s, outv[mid], outs[mid]):  # search left half [0..mid]
        lo, hi = 0, mid
    else:                                 # search right half [mid+1..n-1]
        lo, hi = mid + 1, n - 1
        if lo > hi:                       # append fast-path
            outv.append(v)
            outs.append(s)
            return

    # upper_bound in [lo..hi]: first index where existing > new (stable insert to the right on equals)
    pos = hi + 1
    while lo <= hi:
        m = (lo + hi) // 2
        if _le(outv[m], outs[m], v, s):   # move right on equals
            lo = m + 1
        else:
            pos = m
            hi = m - 1

    outv.insert(pos, v)
    outs.insert(pos, s)

def sort_block_cobis(vals: List, seq: List[int]) -> Tuple[List, List[int]]:
    """Sort one leaf block with COBIS. Returns (sorted_values, sorted_seq)."""
    n = len(vals)
    if n <= 1:
        return vals[:], seq[:]

    outv: List = []
    outs: List[int] = []
    for i in range(n):
        cobis_insert_sorted(outv, outs, vals[i], seq[i])
    return outv, outs

# ---------- Galloping merge (stable) ----------
def _gallop_right(xv, xs, av, asq, lo: int, hi: int) -> int:
    """First index in av[lo:hi] where (av[idx], asq[idx]) > (xv, xs)."""
    n = hi - lo
    if n <= 0:
        return lo
    if not _le(av[lo], asq[lo], xv, xs):  # av[lo] > x
        return lo

    ofs = 1
    idx = lo
    while ofs < n and _le(av[lo + ofs], asq[lo + ofs], xv, xs):
        idx = lo + ofs
        ofs = (ofs << 1) + 1
        if lo + ofs >= hi:
            ofs = n - 1
            break

    left = idx + 1
    right = min(lo + ofs, hi - 1)
    ans = right + 1
    while left <= right:
        m = (left + right) // 2
        if _le(av[m], asq[m], xv, xs):
            left = m + 1
        else:
            ans = m
            right = m - 1
    return ans

def _gallop_left(xv, xs, bv, bsq, lo: int, hi: int) -> int:
    """First index in bv[lo:hi] where (bv[idx], bsq[idx]) >= (xv, xs)."""
    n = hi - lo
    if n <= 0:
        return lo
    if not _lt(bv[lo], bsq[lo], xv, xs):
        return lo

    ofs = 1
    idx = lo
    while ofs < n and _lt(bv[lo + ofs], bsq[lo + ofs], xv, xs):
        idx = lo + ofs
        ofs = (ofs << 1) + 1
        if lo + ofs >= hi:
            ofs = n - 1
            break

    left = idx + 1
    right = min(lo + ofs, hi - 1)
    ans = right + 1
    while left <= right:
        m = (left + right) // 2
        if _lt(bv[m], bsq[m], xv, xs):
            left = m + 1
        else:
            ans = m
            right = m - 1
    return ans

def merge_parallel_galloping(
    lv: List, ls: List[int],
    rv: List, rs: List[int],
    gallop_thresh: int = 7
) -> Tuple[List, List[int]]:
    """Stable merge of (lv,ls) and (rv,rs), with galloping after threshold wins."""
    i = j = 0
    la, lb = len(lv), len(rv)
    outv: List = []
    outs: List[int] = []
    win_l = win_r = 0

    # main merge
    while i < la and j < lb:
        if _le(lv[i], ls[i], rv[j], rs[j]):   # stable (left wins on equals)
            outv.append(lv[i]); outs.append(ls[i]); i += 1
            win_l += 1; win_r = 0
        else:
            outv.append(rv[j]); outs.append(rs[j]); j += 1
            win_r += 1; win_l = 0

        # Gallop on left streak
        if win_l >= gallop_thresh and j < lb:
            k = _gallop_right(rv[j], rs[j], lv, ls, i, la)
            if k > i:
                outv.extend(lv[i:k]); outs.extend(ls[i:k]); i = k
            win_l = 0

        # Gallop on right streak
        elif win_r >= gallop_thresh and i < la:
            k = _gallop_left(lv[i], ls[i], rv, rs, j, lb)
            if k > j:
                outv.extend(rv[j:k]); outs.extend(rs[j:k]); j = k
            win_r = 0

    # drain tails
    if i < la:
        outv.extend(lv[i:]); outs.extend(ls[i:])
    if j < lb:
        outv.extend(rv[j:]); outs.extend(rs[j:])
    return outv, outs

# ---------- COLBI-Iter: bottom-up driver ----------
def colbi_iter_sort(values: List, leaf_size: int = 128, gallop_thresh: int = 7) -> List:
    """
    Iterative COLBI:
      1) Partition into leaf blocks of size 'leaf_size'
      2) Sort each leaf with COBIS (stable on (value, seq))
      3) Bottom-up pairwise merges with stable galloping
    Returns a new sorted list of 'values'.
    """
    n = len(values)
    if n <= 1:
        return values[:]

    # 1) Build leaves (sorted by COBIS)
    seq = list(range(n))
    runs_v: List[List] = []
    runs_s: List[List[int]] = []

    for i in range(0, n, leaf_size):
        vs = values[i:i + leaf_size]
        ss = seq[i:i + leaf_size]
        lv, ls = sort_block_cobis(vs, ss)
        runs_v.append(lv)
        runs_s.append(ls)

    # 2) Bottom-up merges
    while len(runs_v) > 1:
        new_v: List[List] = []
        new_s: List[List[int]] = []
        for i in range(0, len(runs_v), 2):
            if i + 1 < len(runs_v):
                mv, ms = merge_parallel_galloping(
                    runs_v[i], runs_s[i],
                    runs_v[i + 1], runs_s[i + 1],
                    gallop_thresh=gallop_thresh
                )
                new_v.append(mv); new_s.append(ms)
            else:
                new_v.append(runs_v[i]); new_s.append(runs_s[i])
        runs_v, runs_s = new_v, new_s

    # 3) Return only the values
    return runs_v[0]


# ============================================================
# Smoke tests (run this file directly to verify)
# ============================================================
if __name__ == "__main__":
    import random

    def check_case(arr: List):
        got = colbi_iter_sort(arr, leaf_size=128, gallop_thresh=7)
        assert got == sorted(arr), f"Mismatch!\nGot:  {got[:50]}\nRef:  {sorted(arr)[:50]}"

    # Random integers
    for seed in (1, 2, 3, 4, 5):
        random.seed(seed)
        a = [random.randint(0, 100_000) for _ in range(10_000)]
        check_case(a)

    # Nearly sorted (few swaps)
    a = list(range(10_000))
    random.seed(42)
    for _ in range(500):
        i, j = random.randrange(10_000), random.randrange(10_000)
        a[i], a[j] = a[j], a[i]
    check_case(a)

    # Reverse
    a = list(range(9_999, -1, -1))
    check_case(a)

    # Many duplicates
    random.seed(7)
    a = [random.randrange(100) for _ in range(10_000)]
    check_case(a)

    # Strings
    random.seed(9)
    letters = [chr(ord('A') + i) for i in range(26)]
    a = [random.choice(letters) for _ in range(10_000)]
    check_case(a)

    print("All COLBI-Iter smoke tests passed ✔")
