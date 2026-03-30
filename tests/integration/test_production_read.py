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
import os
import pytest

from google.cloud.bigtable.data._async.client import BigtableDataClientAsync
from google.cloud.bigtable.data.read_rows_query import ReadRowsQuery

# We use the instance and table provided by the user
INSTANCE_ID = "ju-ruby-sidecar"
TABLE_ID = "ycsb-1gb"

@pytest.mark.asyncio
async def test_production_read():
    # Make sure we are not using emulator
    if os.getenv("BIGTABLE_EMULATOR_HOST"):
         pytest.skip("This test requires a real Bigtable instance, not emulator.")

    print(f"Connecting to instance: {INSTANCE_ID}, table: {TABLE_ID} using sidecar...")
    
    # Initialize client with sidecar
    async with BigtableDataClientAsync(use_sidecar=True) as client:
        table = client.get_table(INSTANCE_ID, TABLE_ID)
        
        # Create a query to read a few rows
        query = ReadRowsQuery(limit=5)
        
        print("Sending read_rows request...")
        rows = []
        async for row in await table.read_rows_stream(query):
             rows.append(row)
             print(f"Read row: {row.row_key}")


             
        print(f"Total rows read: {len(rows)}")
        assert len(rows) > 0, "No rows were read from the table!"
        assert len(rows) <= 5, f"Read more than requested limit! {len(rows)}"
        
        print("Production read test passed!")

if __name__ == "__main__":
    asyncio.run(test_production_read())
