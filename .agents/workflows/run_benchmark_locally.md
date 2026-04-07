---
description: Run YCSB benchmark locally and record results in PROGRESS_LOG.md
---

# Run Benchmark Locally

Follow this workflow to run a YCSB benchmark experiment and record the results.

## Steps

1.  **Clarify Intent**: Ask the user for the intention of this experiment and if there are any specific code changes or environment variables they want to test.
2.  **Run Benchmark**:
    -   Execute the benchmark script with the desired parameters.
    -   Default command: `nox -f noxfile_benchmark.py -s local_benchmark`
    -   To pass arguments to the script, use `--` followed by the arguments.
        Example: `nox -f noxfile_benchmark.py -s local_benchmark -- --use-sidecar`
    -   Set `BIGTABLE_SIDECAR_DISABLE_DIRECTPATH=true` if DirectPath should be disabled.
    -   > [!TIP]
    -   > You can run comparison experiments concurrently in the background (using `&` in bash) to save time, provided the machine has sufficient CPU and memory to avoid artificial bottlenecks.
3.  **Extract Results**: Get the throughput and latency percentiles (p50, p90, p99, p99.9) from the benchmark output.
4.  **Update `PROGRESS_LOG.md`**:
    -   Open `PROGRESS_LOG.md` in the repository root.
    -   Add a new section at the bottom for the new phase.
    -   Include the configuration used.
    -   > [!TIP]
    -   > For comparison runs (e.g., with vs without sidecar), use a Markdown table to display side-by-side results for easy reading.
    -   Include the intention and changes discussed with the user in Step 1.
5.  **Commit**: Commit the updated `PROGRESS_LOG.md` file with a descriptive message.
