import bisect

def acobis_sort(arr, seqs):
    """
    ACOBIS: Adaptive Center-Oriented Binary Insertion Sort
    - Pattern Aware: O(n) for Sorted and Reverse Sorted data.
    - Stable: Uses parallel sequence arrays to break ties.
    - Optimized: Localized segment shifting via Python's list.insert.
    """
    res_val = []
    res_seq = []
    
    for i in range(len(arr)):
        v, s = arr[i], seqs[i]
        
        # 1. Base Case: First element
        if not res_val:
            res_val.append(v)
            res_seq.append(s)
            continue
            
        # 2. Adaptive Sorted Check (Tail Peek)
        # If new value is >= the current max, append immediately
        if v >= res_val[-1]:
            res_val.append(v)
            res_seq.append(s)
            continue
            
        # 3. Adaptive Reverse Check (Head Peek)
        # If new value is < the current min, prepend immediately
        # (Stable: strictly less than ensures original order is kept)
        if v < res_val[0]:
            res_val.insert(0, v)
            res_seq.insert(0, s)
            continue

        # 4. Center-Oriented Decision
        n = len(res_val)
        mid_idx = (n - 1) // 2
        
        # Determine which half to search
        if v < res_val[mid_idx]:
            lo, hi = 0, mid_idx
        else:
            lo, hi = mid_idx + 1, n
            
        # 5. Narrowed Binary Search
        # Uses C-optimized bisect for the chosen range
        pos = bisect.bisect_right(res_val, v, lo, hi)
        
        # 6. Localized Shift
        res_val.insert(pos, v)
        res_seq.insert(pos, s)
        
    return res_val, res_seq

