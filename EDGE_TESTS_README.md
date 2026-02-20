# Edge Test Cases Documentation

This document describes the edge test cases created for the virtual memory simulator to ensure comprehensive testing.

## Key Edge Cases Identified

### 1. Memory Pressure Test (tlb_fifo_stress.txt)

**Problem**: Tests behavior when many unique pages compete for limited physical memory.

**Test**: 20 different pages with only 4 physical frames, then revisit first 10 pages

- Pages accessed: 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,1,2,3,4,5,6,7,8,9,10
- Every access after the first 4 causes page eviction
- Tests that evicted pages also have TLB entries removed

**Command**: `py ./memSim.py tests/tlb_fifo_stress.txt 4 FIFO`

**Expected Results**:

- Number of Translated Addresses = 30
- Page Faults = 30 (all accesses cause page faults due to only 4 frames vs 20 unique pages)
- Page Fault Rate = 1.000
- TLB Hits = 0 (all revisited pages were evicted from RAM, so also from TLB)
- TLB Misses = 30
- TLB Hit Rate = 0.000

### 2. Minimum Physical Memory (one_frame.txt)

**Problem**: With only 1 frame, every new page access should cause a page fault and frame eviction.

**Test**: 9 addresses accessing different pages with 1 frame

- Pages accessed: 1,2,3,1,4,2,3,5,1
- Every new page causes immediate eviction
- Tests extreme memory pressure

**Command**: `py ./memSim.py tests/one_frame.txt 1 FIFO`

**Expected Results**:

- Number of Translated Addresses = 9
- Page Faults = 9 (every access causes page fault with only 1 frame)
- Page Fault Rate = 1.000
- TLB Hits = 0 (no pages remain in memory long enough for TLB hits)
- TLB Misses = 9
- TLB Hit Rate = 0.000

### 3. Page Boundaries (boundary_pages.txt)

**Problem**: Edge cases at page boundaries (page 0, page 255).

**Test**: Accesses to page 0 and page 255

- Addresses: 0, 255, 65535, 0, 65280, 255, 32768, 0
- Pages accessed: 0,0,255,0,255,0,128,0 (only 3 unique pages: 0,255,128)
- Tests edge cases in page number calculations

**Command**: `py ./memSim.py tests/boundary_pages.txt 3 FIFO`

**Expected Results**:

- Number of Translated Addresses = 8
- Page Faults = 3 (one for each unique page: 0,255,128)
- Page Fault Rate = 0.375
- TLB Hits = 5 (repeated accesses to same pages)
- TLB Misses = 3
- TLB Hit Rate = 0.625

### 4. TLB Hit Rate Optimization (high_tlb_hit.txt)

**Problem**: With repetitive access to few pages, TLB should have high hit rate.

**Test**: 20 accesses to only 5 unique pages

- Pages accessed: 1,2,3,4,5,1,2,3,4,5,1,2,3,4,5,3,1,4,2,5
- Tests TLB effectiveness with repetitive access

**Command**: `py ./memSim.py tests/high_tlb_hit.txt 5 FIFO`

**Expected Results**:

- Number of Translated Addresses = 20
- Page Faults = 5 (one for each unique page)
- Page Fault Rate = 0.250
- TLB Hits = 15 (all repeated accesses)
- TLB Misses = 5
- TLB Hit Rate = 0.750

### 5. Offset Boundaries (offset_boundary.txt)

**Problem**: Different offsets within the same page should reuse TLB entry.

**Test**: Multiple addresses within page 1 (256-511)

- Addresses: 256, 257, 511, 384, 300, 256, 510, 257
- All map to page 1 with different offsets
- Tests offset handling vs page handling

**Command**: `py ./memSim.py tests/offset_boundary.txt 2 FIFO`

**Expected Results**:

- Number of Translated Addresses = 8
- Page Faults = 1 (only first access to page 1)
- Page Fault Rate = 0.125
- TLB Hits = 7 (all subsequent accesses to same page)
- TLB Misses = 1
- TLB Hit Rate = 0.875

### 6. LRU Algorithm Specificity (lru_specific.txt)

**Problem**: LRU should evict truly least recently used page.

**Test**: Specific access pattern designed to test LRU vs FIFO differences

- Pages accessed: 1,2,3,4,1,2,5,3,1,6,2
- With 3 frames, tests true LRU behavior
- Each access causes eviction due to challenging pattern

**Command**: `py ./memSim.py tests/lru_specific.txt 3 LRU`

**Expected Results**:

- Number of Translated Addresses = 11
- Page Faults = 11 (challenging pattern causes all misses)
- Page Fault Rate = 1.000
- TLB Hits = 0 (pages don't stay in memory long enough)
- TLB Misses = 11
- TLB Hit Rate = 0.000

### 7. OPT Algorithm Verification (opt_specific.txt)

**Problem**: OPT should perform optimally by looking at future accesses.

**Test**: Pattern where OPT should outperform FIFO/LRU

- Pages accessed: 1,2,3,4,5,1,2,3,1,2,1
- OPT should make better eviction choices based on future knowledge
- Demonstrates optimal algorithm efficiency

**Command**: `py ./memSim.py tests/opt_specific.txt 3 OPT`

**Expected Results**:

- Number of Translated Addresses = 11
- Page Faults = 6 (OPT makes optimal eviction choices)
- Page Fault Rate = 0.545
- TLB Hits = 5 (better than LRU due to optimal replacement)
- TLB Misses = 6
- TLB Hit Rate = 0.455

### 8. Sequential Access (sequential.txt)

**Problem**: Sequential access within and across pages.

**Test**: Sequential addresses within pages

- Addresses: 256,257,258,259,260,512,513,514,515,516,768,769,770,771,772
- Pages accessed: 1,1,1,1,1,2,2,2,2,2,3,3,3,3,3 (only 3 unique pages)
- Tests cache behavior with sequential access

**Command**: `py ./memSim.py tests/sequential.txt 3 FIFO`

**Expected Results**:

- Number of Translated Addresses = 15
- Page Faults = 3 (one for each unique page)
- Page Fault Rate = 0.200
- TLB Hits = 12 (excellent locality within pages)
- TLB Misses = 3
- TLB Hit Rate = 0.800

### 9. True TLB FIFO Test (true_tlb_fifo.txt)

**Problem**: Test actual TLB FIFO behavior when TLB capacity < RAM capacity.

**Test**: Access 21 different pages with 25 frames

- Pages accessed: 1,2,3,...,21,1
- RAM can hold all 21 pages, but TLB can only hold 16 mappings
- Final access to page 1: TLB miss (evicted by FIFO) but page table hit (still in RAM)

**Command**: `py ./memSim.py tests/true_tlb_fifo.txt 25 FIFO`

**Expected Results**:

- Number of Translated Addresses = 22
- Page Faults = 21 (one for each unique page)
- Page Fault Rate = 0.955
- TLB Hits = 0 (page 1 was evicted from TLB when pages 17-21 were accessed)
- TLB Misses = 22 (all accesses miss TLB)
- TLB Hit Rate = 0.000
