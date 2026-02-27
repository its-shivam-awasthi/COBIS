# COBIS (Center Oriented Binary Insertion Sort)

##COLBI & COBBI Sorting Suite
A collection of stable, adaptive sorting algorithms designed to bridge the gap between textbook sorting and real-world data patterns. This suite utilizes COBIS (Center-Oriented Binary Insertion) as a high-efficiency leaf-level engine, combined with Galloping Merges to accelerate performance on structured data.

###🚀 The Three Variations
COLBI-Iter (Iterative): A bottom-up merge sort that avoids Python's recursion depth limits. It is robust for general-purpose sorting and handles large datasets predictably.
COLBI-Rec (Recursive): A top-down implementation that is highly optimized for Python by leveraging the built-in bisect module for its leaf-sorting stage.
COBBI-Blocked (Chunked/Blocked): A hybrid approach that maintains local blocks and utilizes block-maxima metadata to quickly locate insertion points, making it ideal for clustered data or heavy duplicates.

###🧠 What is COBIS?
COBIS (Center-Oriented Binary Insertion Sort) is an optimized version of the standard binary insertion sort used as the "base case" for these algorithms.

####How it Works:
Unlike standard insertion sort which starts its search from index 0, COBIS performs a Center-Out Decision:
It compares the new element against the median of the currently sorted list.
It immediately narrows the search space to either the left half or the right half.
It then executes a standard binary search (upper bound) only within that narrowed range.
Why COBIS is Superior:
Comparison Efficiency: On average, COBIS reduces the total number of comparisons by making a high-level heuristic decision before the binary search begins.
Locality of Reference: It prioritizes the middle of the array, which is often more stable in CPU caches than the extreme ends.
Stability Integration: It is natively designed to handle parallel "sequence" arrays, ensuring that the relative order of equal elements is perfectly preserved.
---
###🛠 How COBIS Enhances the Suite
1. Leaf-Level Acceleration
In both the Iterative and Recursive versions, sorting 10,000 individual elements one-by-one is inefficient. Instead, the data is divided into Sorted Leaves (size 64 or 128). COBIS sorts these leaves with fewer comparisons than a standard sort, providing a perfectly ordered foundation for the merge steps.
2. Reducing Gallop Overhead
By using COBIS to create longer, perfectly sorted initial runs, the Galloping Merge is triggered more frequently. Galloping allows the algorithm to "leap" over large blocks of data when one run is significantly larger or smaller than another, rather than comparing elements one by one.
3. Maintaining Stability in Blocked Mode (COBBI)
In the Blocked version, COBIS manages the internal state of each block. When a block reaches its limit and needs to split, COBIS ensures the split happens at the median, keeping the entire structure balanced and stable.

###📊 Performance Benchmark (10,000 Elements)
Results based on pure Python implementation benchmarks.
Scenario COLBI-Iter COLBI-Rec COBBI-Blocked Std Merge Sort
Nearly Sorted 0.041s 0.018s 0.083s 0.061s
Heavy Duplicates 0.066s 0.035s 0.074s 0.061s
Reverse Sorted 0.031s 0.014s 0.059s 0.041s
Random Ints 0.126s 0.081s 0.134s 0.084s

###💻 Quick Start

``` Python
from colbi_iter import colbi_iter_sort
from colbi_rec import cobis_recursive_sort
from cobbi_blocked import cobbi_sort

# Sample data
data = [10, 5, 2, 5, 8, 1, 9, 5, 3]

# Best for general stability and large datasets
result_iter = colbi_iter_sort(data)

# Best for raw speed in pure Python environments
result_rec = cobis_recursive_sort(data)

# Best for clustered data or high duplicate counts
result_blocked = cobbi_sort(data)
```

###⚖️ License
This project is licensed under the MIT License.
