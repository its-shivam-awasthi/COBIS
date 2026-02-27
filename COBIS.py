function center_oriented_binary_insertion_sort(A):
    n = length(A)
    if n <= 1: return

    if n is odd:
        mid = (n - 1) // 2
        place A[0] at A[mid]  // shift others appropriately, or swap into an empty workspace
        left_count = 1; right_count = 0
    else:
        midL = n//2 - 1
        midR = n//2
        a = A[0]; b = A[n-1]
        if a <= b:
            place a at A[midL]
            place b at A[midR]
        else:
            place b at A[midL]
            place a at A[midR]
        left_count = 1; right_count = 1

    // Now process remaining elements, ideally alternating from ends
    i = 1
    j = n - 2  // or j = n - 1 if odd case
    while elements remain outside [mid-left_count+1 .. mid+right_count]:
        // choose next x from left side or right side (your policy)
        x = next element
        if x <= boundary_value:  // choose side by comparing to current boundary
            // binary search in left segment for insert index
            idx = lower_bound(A[ mid-left_count+1 .. mid ]) for x (stable rule)
            shift A[idx .. mid] right by 1
            A[idx] = x
            left_count += 1
        else:
            idx = upper_bound(A[ mid+1 .. mid+right_count ]) for x (stable rule)
            shift A[mid+1 .. idx-1] left by 1
            A[idx] = x
            right_count += 1

    // array is sorted
