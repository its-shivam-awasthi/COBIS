import bisect

"""
OCOBIS: Oscillating Center Oriented/Out Binary Insertion Sort
A hybrid insertion sort that builds a "sorted island" from the center 
of the array outward. It utilizes binary search for position finding 
and an "Extreme Swap" heuristic to handle reversed data efficiently.
"""

def ocobis(arr, lo=None, hi=None):
    """
    Main entry point for OCOBIS.
    :param arr: The list to be sorted.
    :param lo: Starting index (defaults to 0).
    :param hi: Ending index (defaults to len-1).
    """
    if lo is None: lo = 0
    if hi is None: hi = len(arr) - 1
    
    n = hi - lo + 1
    if n < 2:
        return arr

    # 1. INITIALIZE THE CENTER CORE
    # mid1 is the left-center, mid2 is the right-center.
    mid1 = lo + (n - 1) // 2
    if n % 2 == 0:
        mid2 = mid1 + 1
        # Initial sort of the two-element core
        if arr[mid1] > arr[mid2]:
            arr[mid1], arr[mid2] = arr[mid2], arr[mid1]
    else:
        mid2 = mid1

    # Counters track how far the "Sorted Island" has expanded from mid
    l_count = 0 
    r_count = 0

    # 2. OSCILLATING EXPANSION
    # We pulse outward: pick one from the left, then one from the right.
    for i in range(1, (n // 2) + 1):
        
        # --- Process Leftward Element ---
        left_idx = mid1 - i
        if left_idx >= lo:
            l_count = _sort_left(arr, left_idx, mid1, mid2, l_count, r_count)
        
        # --- Process Rightward Element ---
        right_idx = mid2 + i
        if right_idx <= hi:
            r_count = _sort_right(arr, right_idx, mid1, mid2, l_count, r_count)
            
    return arr

def _sort_left(arr, pos, mid1, mid2, l_count, r_count):
    """Inserts the element at 'pos' into the sorted island expanding to the right."""
    x = pos
    y = mid2 + r_count # Current boundary of the sorted island on the right
    
    # HEURISTIC: Extreme Swap
    # If the new left element is larger than the far right of the island,
    # swap them to move the "heavy" value toward the correct half immediately.
    if arr[x] > arr[y]:
        arr[x], arr[y] = arr[y], arr[x]
        
    # STABILITY/BEST CASE: Already Sorted Check
    # If it's already smaller than or equal to its right neighbor, it's in place.
    if arr[x] <= arr[x + 1]:
        return l_count + 1
    
    # BINARY INSERTION
    # Pop the value and find its spot within the current sorted island [x+1, y]
    key = arr.pop(x)
    ins_point = bisect.bisect_left(arr, key, lo=x, hi=y)
    arr.insert(ins_point, key)
    
    return l_count + 1

def _sort_right(arr, pos, mid1, mid2, l_count, r_count):
    """Inserts the element at 'pos' into the sorted island expanding to the left."""
    x = mid1 - l_count # Current boundary of the sorted island on the left
    y = pos
    
    # HEURISTIC: Extreme Swap
    if arr[x] > arr[y]:
        arr[x], arr[y] = arr[y], arr[x]
        
    # STABILITY/BEST CASE: Already Sorted Check
    if arr[y] >= arr[y - 1]:
        return r_count + 1
    
    # BINARY INSERTION
    # Pop the value and find its spot within the current sorted island [x, y-1]
    key = arr.pop(y)
    ins_point = bisect.bisect_left(arr, key, lo=x, hi=y)
    arr.insert(ins_point, key)
    
    return r_count + 1
  
