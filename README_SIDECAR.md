# Bigtable Python Client - Sidecar & Jetstream Integration

This document provides context and documentation for the integration of the Java Sidecar and Jetstream in the Python Bigtable client. This is intended for developers taking over the project.

## Context & Architecture

To improve performance (especially tail latency) for Python applications reading from Cloud Bigtable, we use a **Java Sidecar** process. The Python client communicates with this local Java process over a Unix Domain Socket (UDS). The Java sidecar handles the complex gRPC streaming and DirectPath engagement, which are more optimized in the Java client library.

**Jetstream** is a bidirectional streaming mode enabled in the Java sidecar. To use it, the Python client must inject a special gRPC metadata header (`x-use-jetstream: "true"`) in `ReadRows` requests.

## Source Code & Forks

The work for this integration is currently available in the following forks on the `sidecar` branch:
*   **Python Client**: [justinuang/python-bigtable](https://github.com/justinuang/python-bigtable/tree/sidecar)
*   **Java Sidecar**: [justinuang/java-bigtable](https://github.com/justinuang/java-bigtable/tree/sidecar)

## What Has Been Done

1.  **Sidecar Integration**: The Python client (`BigtableDataClientAsync`) can start and manage a local Java sidecar process and route data requests to it.
2.  **Jetstream Support**: Added a `use_jetstream` parameter to `BigtableDataClientAsync` and modified `_read_rows_attempt` to inject the necessary header.
3.  **Performance Optimization**: Integrated `uvloop` as the event loop in benchmarking scripts to significantly reduce Python event loop overhead, yielding performance close to the multi-threaded Ruby client.

## Key Files

*   **`google/cloud/bigtable/data/_async/client.py`**: Contains `BigtableDataClientAsync` where `use_sidecar` and `use_jetstream` are configured.
*   **`google/cloud/bigtable/data/_async/_read_rows.py`**: Where the `x-use-jetstream` header is injected into the gRPC metadata.
*   **`scripts/ycsb_benchmark.py`**: The Python YCSB benchmark script supporting direct runs and sidecar/jetstream flags.
*   **`noxfile_benchmark.py`**: Orchestrates building the wheel, deploying it to a remote GCE VM, and running benchmarks.

## How the Build System Works

The Java sidecar is built in the `google-cloud-bigtable-sidecar` directory (Maven project). The resulting shaded JAR is copied into the Python project at `google/cloud/bigtable/bin/java-sidecar.jar`.

When you build the Python wheel (`python3 setup.py bdist_wheel`), this JAR is included in the package.

> [!IMPORTANT]
> The Python package **does not** bundle a JVM. It relies on the host system having a compatible Java runtime installed to execute the sidecar JAR.

## API Changes

To use these features, pass the appropriate flags when creating the client:

```python
from google.cloud.bigtable.data import BigtableDataClientAsync

async with BigtableDataClientAsync(
    project="your-project",
    use_sidecar=True,
    use_jetstream=True
) as client:
    # Use client normally
    pass
```

## How to Run Tests and Benchmarks

### Running Locally
You can run the benchmark script directly for quick verification:
```bash
python3 scripts/ycsb_benchmark.py --use-sidecar --use-jetstream --qps=500
```

### Running on GCE VM (Remote)
To run a full benchmark suite on the configured GCE VM:
```bash
nox -f noxfile_benchmark.py -s benchmark
```
This command will automatically clean the workspace, build the wheel, upload it to the VM, and run the benchmark configurations (Sidecar, No Sidecar, Jetstream).

## Environment Details

For our testing and benchmarking, we used the following environment:
*   **GCE VM**: `ju-ruby-sidecar-c3-vm-east4` (Machine Type: **C3**, Zone: `us-east4-a`)
    *   **SSH Command**: `gcloud compute ssh ju-ruby-sidecar-c3-vm-east4 --zone=us-east4-a --project=autonomous-mote-782`
*   **Bigtable Instance**: `ju-ruby-sidecar`
*   **Bigtable Cluster**: `ju-ruby-sidecar-c3` (Zone: `us-east4-a`)
*   **Table**: `ycsb-100gb`

## Recommended Workspace Setup with Jetski

For the best experience when developing this cross-language integration using Jetski (or similar AI assistants), it is recommended to use a **multi-folder workspace**:

1.  **Include both repositories**: Add both `python-bigtable` and `java-bigtable` folders to your workspace.
2.  **Cross-Language Visibility**: This allows the AI to see both the Python consumer code and the Java sidecar provider code simultaneously, enabling it to reason about the full RPC boundary without manual context switching.
3.  **Path References**: When asking the AI to look at files or run commands, you can reference paths in either project, and it will be able to navigate between them smoothly.

## Progress Log & Future Tasks

For detailed results of past runs and the list of planned future tasks (like bundling a J-Link JVM or supporting mutations), please refer to:
*   [PROGRESS_LOG.md](file:///usr/local/google/home/justinuang/code/python-bigtable/PROGRESS_LOG.md)
