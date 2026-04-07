#!/usr/bin/env python3
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import uvloop
import os
import random
import math
import time
import argparse
import hashlib
from google.cloud.bigtable.data._async.client import BigtableDataClientAsync
from google.cloud.bigtable.data.read_rows_query import ReadRowsQuery

class ZipfianGenerator:
    def __init__(self, min_val, max_val, zipfian_constant=0.99):
        self.min = min_val
        self.max = max_val
        self.items = max_val - min_val + 1
        self.zipfian_constant = zipfian_constant
        self.alpha = 1.0 / (1.0 - zipfian_constant)
        print(f"Initializing Zipfian generator for {self.items} items... (this may take a while)")
        self.zetan = self.zeta(self.items)
        self.eta = (1.0 - math.pow(2.0 / self.items, 1.0 - zipfian_constant)) / (1.0 - self.zeta(2) / self.zetan)
        print("Generator Ready.")

    def next_val(self):
        u = random.random()
        uz = u * self.zetan
        if uz < 1.0:
            return self.min
        if uz < 1.0 + math.pow(0.5, self.zipfian_constant):
            return self.min + 1
        return self.min + int(self.items * math.pow(self.eta * u - self.eta + 1.0, self.alpha))

    def zeta(self, n):
        ans = 0.0
        # For large N, this is slow in Python.
        # But we need it to match Ruby's distribution.
        for i in range(1, n + 1):
            ans += 1.0 / math.pow(i, self.zipfian_constant)
        return ans

async def worker(worker_id, client, table_id, key_generator, options, stats):
    qps_per_worker = options.qps / options.workers
    sleep_time = 1.0 / qps_per_worker
    
    table = client.get_table(options.instance_id, table_id, app_profile_id=options.app_profile_id)
    
    end_time = time.time() + options.duration
    warmup_end = time.time() + options.warmup
    
    while time.time() < end_time:
        start_time = time.perf_counter()
        
        # Workload C: Read Point Lookup
        logical_index = key_generator.next_val()
        logical_key = f"user{logical_index:09d}"
        hash_val = hashlib.md5(logical_key.encode()).hexdigest()[:8]
        row_key = f"user{hash_val}-{logical_key}".encode()
        
        try:
            query = ReadRowsQuery(row_keys=row_key)
            # Read row
            rows = []
            async for row in await table.read_rows_stream(query):
                rows.append(row)
                
            latency_ms = (time.perf_counter() - start_time) * 1000.0
            
            if time.time() > warmup_end:
                stats['latencies'].append(latency_ms)
                stats['count'] += 1
                
        except Exception as e:
            print(f"Worker {worker_id} error: {e}")
            
        # Rate limiting
        elapsed = time.perf_counter() - start_time
        sleep_dur = sleep_time - elapsed
        if sleep_dur > 0:
            await asyncio.sleep(sleep_dur)

async def main():
    parser = argparse.ArgumentParser(description="YCSB Benchmark for Python Bigtable Client")
    parser.add_argument("--use-sidecar", action="store_true", help="Use the Java sidecar")
    parser.add_argument("--use-jetstream", action="store_true", help="Use Jetstream bidi streams")
    parser.add_argument("--qps", type=int, default=1000, help="Target total QPS")
    parser.add_argument("--workers", type=int, default=50, help="Number of concurrent workers")
    parser.add_argument("--duration", type=int, default=300, help="Benchmark duration in seconds")
    parser.add_argument("--warmup", type=int, default=30, help="Warmup period in seconds")
    parser.add_argument("--project-id", default=os.getenv("BIGTABLE_TEST_PROJECT", "autonomous-mote-782"))
    parser.add_argument("--instance-id", default=os.getenv("BIGTABLE_TEST_INSTANCE", "ju-ruby-sidecar"))
    parser.add_argument("--table-id", default="ycsb-100gb")
    parser.add_argument("--recordcount", type=int, default=100000000)
    parser.add_argument("--app-profile-id", default=None, help="App profile ID to use")
    
    args = parser.parse_args()
    
    print("Starting YCSB Benchmark with:")
    print(args)
    
    key_generator = ZipfianGenerator(0, args.recordcount - 1)
    
    stats = {'count': 0, 'latencies': []}
    
    async with BigtableDataClientAsync(project=args.project_id, use_sidecar=args.use_sidecar, use_jetstream=args.use_jetstream) as client:
        workers = []
        for i in range(args.workers):
            workers.append(asyncio.create_task(worker(i, client, args.table_id, key_generator, args, stats)))
            
        await asyncio.gather(*workers)
        
    print("========================================")
    print("Benchmark Finished!")
    print(f"Total operations recorded (post-warmup): {stats['count']}")
    
    if stats['count'] > 0:
        latencies = sorted(stats['latencies'])
        p50 = latencies[int(len(latencies) * 0.50)]
        p90 = latencies[int(len(latencies) * 0.90)]
        p99 = latencies[int(len(latencies) * 0.99)]
        p999 = latencies[int(len(latencies) * 0.999)]
        avg = sum(latencies) / len(latencies)
        
        print(f"Throughput (ops/sec): {stats['count'] / (args.duration - args.warmup)}")
        print(f"Average Latency: {avg:.4f} ms")
        print(f"p50 Latency:     {p50:.4f} ms")
        print(f"p90 Latency:     {p90:.4f} ms")
        print(f"p99 Latency:     {p99:.4f} ms")
        print(f"p99.9 Latency:   {p999:.4f} ms")

if __name__ == "__main__":
    uvloop.install()
    asyncio.run(main())
