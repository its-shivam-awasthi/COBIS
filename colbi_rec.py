import bisect
from typing import List, Tuple

def pure_cobis_stable_parallel(arr: List[int], seqs: List[int]) -> Tuple[List[int], List[int]]:
    """Leaf sort: COBIS center-out logic on parallel arrays (stable)."""
    res_val: List[int] = []
    res_seq: List[int] = []
    for v, s in zip(arr, seqs):
        n = len(res_val)
        if n == 0:
            res_val.append(v)
            res_seq.append(s)
            continue

        # 1) COBIS center-out decision
        mid = (n - 1) // 2
        if v < res_val[mid]:
            lo, hi = 0, mid
        else:
            lo, hi = mid + 1, n

        # 2) upper_bound in chosen half (stable on equals)
        pos = bisect.bisect_right(res_val, v, lo, hi)
        res_val.insert(pos, v)
        res_seq.insert(pos, s)
    return res_val, res_seq

# ---------- Galloping primitives (values only; stability via left-first on equals) ----------

def _gallop_right(x: int, a: List[int], lo: int, hi: int) -> int:
    """First index in a[lo:hi] where a[idx] > x."""
    n = hi - lo
    if n <= 0:
        return lo
    if a[lo] > x:
        return lo
    # Exponential search
    ofs = 1
    idx = lo
    while ofs < n and a[lo + ofs] <= x:
        idx = lo + ofs
        ofs = (ofs << 1) + 1
        if lo + ofs >= hi:
            ofs = n - 1
            break
    # Binary search in (idx, lo+ofs]
    left = idx + 1
    right = min(lo + ofs, hi - 1)
    ans = right + 1
    while left <= right:
        mid = (left + right) // 2
        if a[mid] <= x:
            left = mid + 1
        else:
            ans = mid
            right = mid - 1
    return ans

def _gallop_left(x: int, a: List[int], lo: int, hi: int) -> int:
    """First index in a[lo:hi] where a[idx] >= x (stable: keeps equals on the other side)."""
    n = hi - lo
    if n <= 0:
        return lo
    if a[lo] >= x:
        return lo
    # Exponential search
    ofs = 1
    idx = lo
    while ofs < n and a[lo + ofs] < x:
        idx = lo + ofs
        ofs = (ofs << 1) + 1
        if lo + ofs >= hi:
            ofs = n - 1
            break
    # Binary search in (idx, lo+ofs]
    left = idx + 1
    right = min(lo + ofs, hi - 1)
    ans = right + 1
    while left <= right:
        mid = (left + right) // 2
        if a[mid] < x:
            left = mid + 1
        else:
            ans = mid
            right = mid - 1
    return ans

# ---------- Galloping merge WITH threshold ----------

def galloping_merge_threshold(
    l_val: List[int],
    l_seq: List[int],
    r_val: List[int],
    r_seq: List[int],
    gallop_thresh: int = 7
) -> Tuple[List[int], List[int]]:
    """
    Stable merge with galloping. After 'gallop_thresh' consecutive wins from one side,
    switch to gallop mode for bulk copy. Stability: left-first on equals.
    """
    i = j = 0
    la, lb = len(l_val), len(r_val)
    out_v: List[int] = []
    out_s: List[int] = []

    win_l = 0   # consecutive wins from left
    win_r = 0   # consecutive wins from right

    append = out_v.append
    append_s = out_s.append
    extend = out_v.extend
    extend_s = out_s.extend

    while i < la and j < lb:
        # Base comparison (stable): left wins on equals
        if l_val[i] <= r_val[j]:
            append(l_val[i]); append_s(l_seq[i]); i += 1
            win_l += 1; win_r = 0
        else:
            append(r_val[j]); append_s(r_seq[j]); j += 1
            win_r += 1; win_l = 0

        # Gallop on the side that is winning repeatedly
        if win_l >= gallop_thresh and j < lb:
            # Find first in left > r_val[j], copy left[i:k]
            k = _gallop_right(r_val[j], l_val, i, la)
            if k > i:
                extend(l_val[i:k]); extend_s(l_seq[i:k]); i = k
            win_l = 0
        elif win_r >= gallop_thresh and i < la:
            # Find first in right >= l_val[i], copy right[j:k]
            k = _gallop_left(l_val[i], r_val, j, lb)
            if k > j:
                extend(r_val[j:k]); extend_s(r_seq[j:k]); j = k
            win_r = 0

    # Drain remainder
    if i < la: extend(l_val[i:]); extend_s(l_seq[i:])
    if j < lb: extend(r_val[j:]); extend_s(r_seq[j:])
    return out_v, out_s

# ---------- Recursive COBIS sorter using galloping merge ----------

def cobis_recursive_sort(arr: List[int], gallop_thresh: int = 7) -> List[int]:
    """
    Recursively split until size <= 64, sort leaf with COBIS center-out (stable),
    then merge children with stable galloping merge.
    """
    n = len(arr)
    if n <= 1:
        return arr[:]
    seqs = list(range(n))

    def worker(v_list: List[int], s_list: List[int]) -> Tuple[List[int], List[int]]:
        m = len(v_list)
        if m <= 64:
            return pure_cobis_stable_parallel(v_list, s_list)
        mid = m // 2
        lv, ls = worker(v_list[:mid], s_list[:mid])
        rv, rs = worker(v_list[mid:], s_list[mid:])
        return galloping_merge_threshold(lv, ls, rv, rs, gallop_thresh=gallop_thresh)

    sorted_vals, _ = worker(arr, seqs)
    return sorted_vals
