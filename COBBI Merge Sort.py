from typing import List, Tuple

# ------------- Helpers for (value, seq) ordering -------------
def _le(v1, s1, v2, s2):  # (v1,s1) <= (v2,s2)
    if v1 < v2: return True
    if v1 > v2: return False
    return s1 <= s2

def _lt(v1, s1, v2, s2):  # (v1,s1) < (v2,s2)
    if v1 < v2: return True
    if v1 > v2: return False
    return s1 < s2

# ------------- COBIS insert inside a block (parallel arrays, stable) -------------
def cobis_insert_block(bv: List, bs: List[int], v, s) -> None:
    n = len(bv)
    if n == 0:
        bv.append(v); bs.append(s); return
    m = (n - 1) // 2
    # Choose half w.r.t. middle
    if _le(v, s, bv[m], bs[m]):     # go left half
        lo, hi = 0, m
    else:
        lo, hi = m + 1, n - 1
        if lo > hi:
            bv.append(v); bs.append(s); return
    # upper_bound in [lo..hi] for (v,s)
    pos = hi + 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if _le(bv[mid], bs[mid], v, s):  # go right on equals → stable
            lo = mid + 1
        else:
            pos = mid
            hi = mid - 1
    bv.insert(pos, v); bs.insert(pos, s)

# ------------- Galloping merge (stable) -------------
def _gallop_right(xv, xs, av, asq, lo, hi):
    # first idx in av[lo:hi] where (av[idx],asq[idx]) > (xv,xs)
    n = hi - lo
    if n <= 0: return lo
    if not _le(av[lo], asq[lo], xv, xs):  # av[lo] > x
        return lo
    ofs = 1; idx = lo
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
        mid = (left + right) // 2
        if _le(av[mid], asq[mid], xv, xs):
            left = mid + 1
        else:
            ans = mid
            right = mid - 1
    return ans

def _gallop_left(xv, xs, bv, bsq, lo, hi):
    # first idx in bv[lo:hi] where (bv[idx],bsq[idx]) >= (xv,xs)
    n = hi - lo
    if n <= 0: return lo
    if not _lt(bv[lo], bsq[lo], xv, xs):
        return lo
    ofs = 1; idx = lo
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
        mid = (left + right) // 2
        if _lt(bv[mid], bsq[mid], xv, xs):
            left = mid + 1
        else:
            ans = mid
            right = mid - 1
    return ans

def merge_parallel_galloping(lv: List, ls: List[int], rv: List, rs: List[int], gallop_thresh=7) -> Tuple[List, List[int]]:
    i = j = 0
    la, lb = len(lv), len(rv)
    outv: List = []
    outs: List[int] = []
    win_l = win_r = 0
    while i < la and j < lb:
        if _le(lv[i], ls[i], rv[j], rs[j]):  # stable
            outv.append(lv[i]); outs.append(ls[i]); i += 1
            win_l += 1; win_r = 0
        else:
            outv.append(rv[j]); outs.append(rs[j]); j += 1
            win_r += 1; win_l = 0
        if win_l >= gallop_thresh and j < lb:
            k = _gallop_right(rv[j], rs[j], lv, ls, i, la)
            if k > i:
                outv.extend(lv[i:k]); outs.extend(ls[i:k]); i = k
            win_l = 0
        elif win_r >= gallop_thresh and i < la:
            k = _gallop_left(lv[i], ls[i], rv, rs, j, lb)
            if k > j:
                outv.extend(rv[j:k]); outs.extend(rs[j:k]); j = k
            win_r = 0
    if i < la:
        outv.extend(lv[i:]); outs.extend(ls[i:])
    if j < lb:
        outv.extend(rv[j:]); outs.extend(rs[j:])
    return outv, outs

# ------------- COBBI (sequential) block build + optional chunked merge -------------
def cobbi_sort(arr: List, block_size: int = 64, chunk_size: int = 1024, gallop_thresh: int = 7) -> List:
    """
    COBBI: Center Oriented Blocked Binary Insertion (sequential arrays) + stable galloping merges (for chunks).
    Stable end-to-end via sequence tie-breakers.
    """
    n = len(arr)
    if n <= 1:
        return arr[:]

    def sort_chunk(chunk: List, seq_offset: int) -> Tuple[List, List[int]]:
        # blocks: list of (bv, bs)
        blocks_v: List[List] = []
        blocks_s: List[List[int]] = []
        # block maxima
        maxv: List = []
        maxs: List[int] = []

        def cmp_ge(iv: int, v, s):  # (maxv[iv],maxs[iv]) >= (v,s)?
            a, b = maxv[iv], v
            if a > b: return True
            if a < b: return False
            return maxs[iv] >= s

        def find_block(v, s) -> int:
            if not blocks_v:
                return 0
            lo, hi = 0, len(blocks_v) - 1
            ans = len(blocks_v)
            while lo <= hi:
                mid = (lo + hi) // 2
                if cmp_ge(mid, v, s):
                    ans = mid
                    hi = mid - 1
                else:
                    lo = mid + 1
            return ans

        seq = seq_offset
        for x in chunk:
            v, s = x, seq; seq += 1
            bi = find_block(v, s)
            if bi == len(blocks_v):
                blocks_v.append([v]); blocks_s.append([s])
                maxv.append(v); maxs.append(s)
            else:
                cobis_insert_block(blocks_v[bi], blocks_s[bi], v, s)
                maxv[bi] = blocks_v[bi][-1]; maxs[bi] = blocks_s[bi][-1]
                if len(blocks_v[bi]) > block_size:
                    # split block
                    bV, bS = blocks_v[bi], blocks_s[bi]
                    mid = len(bV) // 2
                    leftV, leftS = bV[:mid], bS[:mid]
                    rightV, rightS = bV[mid:], bS[mid:]
                    blocks_v[bi], blocks_s[bi] = leftV, leftS
                    blocks_v.insert(bi + 1, rightV); blocks_s.insert(bi + 1, rightS)
                    maxv[bi], maxs[bi] = leftV[-1], leftS[-1]
                    maxv.insert(bi + 1, rightV[-1]); maxs.insert(bi + 1, rightS[-1])

        # flatten blocks → parallel arrays
        outv, outs = [], []
        for bV, bS in zip(blocks_v, blocks_s):
            outv.extend(bV); outs.extend(bS)
        return outv, outs

    if n <= chunk_size:
        sv, ss = sort_chunk(arr, 0)
        return sv

    # chunk + galloping merges
    chunks_v: List[List] = []
    chunks_s: List[List[int]] = []
    seq_off = 0
    for i in range(0, n, chunk_size):
        sub = arr[i:i + chunk_size]
        sv, ss = sort_chunk(sub, seq_off)
        chunks_v.append(sv); chunks_s.append(ss)
        seq_off += len(sub)

    # pairwise merge with galloping
    while len(chunks_v) > 1:
        new_v, new_s = [], []
        for i in range(0, len(chunks_v), 2):
            if i + 1 < len(chunks_v):
                mv, ms = merge_parallel_galloping(chunks_v[i], chunks_s[i],
                                                  chunks_v[i + 1], chunks_s[i + 1],
                                                  gallop_thresh=gallop_thresh)
                new_v.append(mv); new_s.append(ms)
            else:
                new_v.append(chunks_v[i]); new_s.append(chunks_s[i])
        chunks_v, chunks_s = new_v, new_s
    return chunks_v[0]
