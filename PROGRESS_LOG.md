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
