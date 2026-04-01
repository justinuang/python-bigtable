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
import uuid

from google.cloud.bigtable.data._async.client import BigtableDataClientAsync
from google.cloud.bigtable.data.read_rows_query import ReadRowsQuery
from google.cloud.bigtable.data.mutations import SetCell
from . import TEST_FAMILY, TEST_FAMILY_2, TEST_AGGREGATE_FAMILY

@pytest.fixture(scope="session")
def client():
    from google.cloud.bigtable.client import Client
    return Client()

@pytest.fixture(scope="session")
def cluster_config(project_id):
    from google.cloud.bigtable_admin_v2 import types
    cluster = {
        "test-cluster": types.Cluster(
            location=f"projects/{project_id}/locations/us-central1-b",
            serve_nodes=1,
        )
    }
    return cluster

@pytest.fixture(scope="session")
def column_family_config():
    from google.cloud.bigtable_admin_v2 import types

    int_aggregate_type = types.Type.Aggregate(
        input_type=types.Type(int64_type={"encoding": {"big_endian_bytes": {}}}),
        sum={},
    )
    return {
        TEST_FAMILY: types.ColumnFamily(),
        TEST_FAMILY_2: types.ColumnFamily(),
        TEST_AGGREGATE_FAMILY: types.ColumnFamily(
            value_type=types.Type(aggregate_type=int_aggregate_type)
        ),
    }

@pytest.fixture(scope="session")
def init_table_id():
    return f"test-table-{uuid.uuid4().hex[:6]}"

@pytest.mark.asyncio
async def test_sidecar_read(instance_id, table_id):
    # Make sure we are not using emulator
    if os.getenv("BIGTABLE_EMULATOR_HOST"):
         pytest.skip("This test requires a real Bigtable instance, not emulator.")

    print(f"Connecting to instance: {instance_id}, table: {table_id} using sidecar...")
    
    # Initialize client with sidecar
    async with BigtableDataClientAsync(use_sidecar=True) as client:
        table = client.get_table(instance_id, table_id)
        
        # Write a row to ensure data exists
        row_key = f"test-sidecar-read-{uuid.uuid4().hex[:6]}".encode()
        print(f"Writing test row: {row_key}")
        
        mutation = SetCell(family=TEST_FAMILY, qualifier=b"q", new_value=b"test-value")
        await table.mutate_row(row_key, mutation)
        print("Row written.")

        # Create a query to read that specific row
        query = ReadRowsQuery(row_keys=row_key)
        
        print("Sending read_rows request...")
        rows = []
        async for row in await table.read_rows_stream(query):
             rows.append(row)
             print(f"Read row: {row.row_key}")

        print(f"Total rows read: {len(rows)}")
        assert len(rows) == 1, "Failed to read the row back!"
        assert rows[0].row_key == row_key
        
        print("Sidecar read test passed!")
