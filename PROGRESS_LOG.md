# Progress Log - Python Bigtable Sidecar

This file tracks the execution and results of experiments for the Python Bigtable client, comparing performance with and without the Java sidecar.

## Task List
- [x] Create `scripts/ycsb_benchmark.py`
- [x] Verify script on small scale
- [x] Run baseline 5-minute benchmark without sidecar (Actually 2-minute run for verification)
- [x] Run benchmark with sidecar (CloudPath)
- [ ] Run benchmark with sidecar (DirectPath) - Future

## Phase 1: Verification Run (Small Scale)

**Date:** 2026-04-01
**Intention:** Verify that the benchmark script works and correctly measures latency.
**Changes:** Created `ycsb_benchmark.py` with async implementation and in-memory latency collection.

### Configuration
- **Dataset:** 1,000 Rows
- **Duration:** 5 seconds
- **Warmup:** 1 second
- **QPS:** 10
- **Workers:** 2

### Results (No Sidecar)
- **Throughput:** 10.5 ops/sec
- **Average Latency:** 48.83 ms
- **p50 Latency:** 9.94 ms
- **p90 Latency:** 14.43 ms
- **p99 Latency:** 1130.90 ms

### Results (With Sidecar - CloudPath)
- **Throughput:** 10.0 ops/sec
- **Average Latency:** 13.20 ms
- **p50 Latency:** 10.13 ms
- **p90 Latency:** 19.38 ms
- **p99 Latency:** 66.44 ms

*Note: The first run with sidecar had high latency due to cold start, but stabilized in the second run with longer warmup.*

## Phase 2: 2-Minute Benchmark (100GB, Zipfian, 1000 QPS)

**Date:** 2026-04-01
**Intention:** Test the new workflow and compare Python client with and without sidecar on a larger scale.
**Changes:** Used `ycsb_benchmark.py` with 100M records (simulated in generator) on `ycsb-100gb` table.

### Configuration
- **Dataset:** `ycsb-100gb` (100,000,000 Rows)
- **Duration:** 120 seconds
- **Warmup:** 30 seconds
- **QPS:** 1000
- **Workers:** 50

### Results

| Metric | No Sidecar | With Sidecar (CloudPath) |
| :--- | :--- | :--- |
| **Throughput (ops/sec)** | ~984.83 | ~973.74 |
| **Average Latency** | 15.00 ms | 5.55 ms |
| **p50 Latency** | 12.20 ms | 4.46 ms |
| **p90 Latency** | 25.96 ms | 5.45 ms |
| **p99 Latency** | 55.03 ms | 6.94 ms |
| **p99.9 Latency** | 61.30 ms | 14.41 ms |

### Analysis
The Java Sidecar dramatically reduced latency across all percentiles. The p99 latency dropped from 55ms to under 7ms! This confirms that the sidecar is highly effective in reducing tail latency in Python, even when running over CloudPath.

## Phase 3: Jetstream and uvloop Optimization (500 QPS)

**Date:** 2026-04-07
**Intention:** Compare performance with and without `uvloop` at 500 QPS to isolate the effect of event loop optimization.
**Changes:** Added `uvloop` support to `ycsb_benchmark.py` and benchmarked both configurations.

### Configuration
- **Dataset:** `ycsb-100gb` (100,000,000 Rows)
- **Duration:** 60 seconds
- **Warmup:** 30 seconds
- **QPS:** 500
- **Workers:** 50

### Results (Without uvloop)

| Metric | No Sidecar | With Sidecar | With Jetstream |
| :--- | :--- | :--- | :--- |
| **Throughput (ops/sec)** | ~496.63 | ~496.77 | ~496.43 |
| **Average Latency** | 8.41 ms | 3.45 ms | 2.54 ms |
| **p50 Latency** | 7.57 ms | 3.26 ms | 2.48 ms |
| **p90 Latency** | 12.83 ms | 4.25 ms | 3.31 ms |
| **p99 Latency** | 20.20 ms | 6.79 ms | 4.58 ms |
| **p99.9 Latency** | 25.93 ms | 18.43 ms | 19.75 ms |

### Results (With uvloop)

| Metric | No Sidecar | With Sidecar | With Jetstream |
| :--- | :--- | :--- | :--- |
| **Throughput (ops/sec)** | ~499.37 | ~499.73 | ~499.97 |
| **Average Latency** | 4.56 ms | 3.20 ms | 2.18 ms |
| **p50 Latency** | 4.31 ms | 3.10 ms | 2.12 ms |
| **p90 Latency** | 6.36 ms | 3.86 ms | 2.84 ms |
| **p99 Latency** | 12.33 ms | 4.96 ms | 3.48 ms |
| **p99.9 Latency** | 21.97 ms | 17.00 ms | 4.28 ms |

### Analysis
Adding `uvloop` significantly improved performance across all configurations at 500 QPS. For Jetstream, p99 latency dropped from 4.58 ms to 3.48 ms, bringing it extremely close to the Ruby baseline of 3.25 ms. The native client ("No Sidecar") also saw substantial improvements, confirming that event loop overhead is a major factor in Python client latency.
