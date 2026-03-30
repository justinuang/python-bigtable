# Implementation Plan: Production Read Test using Sidecar

We want to verify that the Python client cannot only start the sidecar but also successfully proxy reads to a real production Cloud Bigtable instance via the sidecar.

## User Review Required

> [!IMPORTANT]
> This test will interact with a real Cloud Bigtable instance (`ju-ruby-sidecar`) in your environment. It will read from an existing table `ycsb-1gb`. This read operation is read-only and should not modify data.

## Proposed Changes

We will create a new integration test file that uses the packaged wheel and attempts to read from a real instance.

### New Test File

#### [NEW] [test_production_read.py](file:///usr/local/google/home/justinuang/code/python-bigtable/tests/integration/test_production_read.py)

We will create this file under `tests/integration/` or a new directory if appropriate. Since we want to test the *installed* package, we might want to run it from a separate directory like we did for the startup test.

The test will:
1.  Initialize `BigtableDataClientAsync` with `use_sidecar=True`.
2.  Use instance ID `ju-ruby-sidecar`.
3.  Target table `ycsb-1gb`.
4.  Perform a `read_rows_stream` call with a limit of 5 rows.
5.  Assert that at least one row is returned.

## Open Questions

- Should I assume the current environment has proper credentials to read from `ju-ruby-sidecar`? (My previous listing of tables suggests YES).
- Is it okay to use `ycsb-1gb` for this read test? It already exists and seems to have data.

## Verification Plan

### Manual Verification
- Run the new test script from a separate directory (e.g., `scratch_test`) to ensure it uses the installed wheel and the sidecar.
- Command: `cd scratch_test && ../.venv/bin/pytest ../tests/integration/test_production_read.py` (or similar).
