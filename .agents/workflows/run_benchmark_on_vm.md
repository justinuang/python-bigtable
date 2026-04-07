---
description: Run YCSB benchmark on remote GCE VM using Nox
---

# Run Benchmark on VM Workflow

Follow this workflow to run a YCSB benchmark experiment on a remote GCE VM using the automated Nox session.

## Steps

1.  **Clarify Intent**: Ask the user for the intention of this experiment and if there are any specific code changes or environment variables they want to test.
2.  **Run Benchmark via Nox**:
    -   Execute the Nox benchmark session from the repository root.
    -   Command: `nox -f noxfile_benchmark.py -s benchmark`
    -   > [!NOTE]
    -   > This command will automatically:
    -   > 1. Clean previous build artifacts.
    -   > 2. Build a fresh Python wheel (including the Java sidecar JAR).
    -   > 3. SSH into the GCE VM, upload the wheel and benchmark script.
    -   > 4. Run the benchmark configurations (Sidecar, No Sidecar, Jetstream).
3.  **Monitor Output**: Wait for the Nox session to complete. It usually takes about 4 minutes.
4.  **Extract Results**: Look at the output of the Nox session to find the throughput and latency percentiles for each configuration.
5.  **Update `PROGRESS_LOG.md`**:
    -   Open `PROGRESS_LOG.md` in the repository root.
    -   Add a new section at the bottom for the new phase.
    -   Include the configuration used.
    -   Use a Markdown table to display side-by-side results for easy reading.
6.  **Commit**: Commit the updated `PROGRESS_LOG.md` file with a descriptive message.
