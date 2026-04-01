# Copyright 2024 Google LLC
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

import os
import time
import pytest
from google.cloud.bigtable.data._sidecar import SidecarManager

def test_sidecar_startup():
    manager = SidecarManager()
    
    try:
        print("Starting sidecar...")
        socket_path = manager.start_sidecar()
        assert socket_path is not None
        assert os.path.exists(socket_path)
        print(f"Sidecar started successfully! Socket path: {socket_path}")
        
        print("Waiting 2 seconds to ensure it stays alive...")
        time.sleep(2)
        
        # Check if process is still running
        assert manager._process.poll() is None
        
        print("Stopping sidecar...")
        manager.stop_sidecar()
        print("Sidecar stopped.")
        
        # Check if process terminated
        assert manager._process is None
        assert not os.path.exists(socket_path)
        
    except Exception as e:
        pytest.fail(f"Sidecar startup failed: {e}")
        if manager._process:
             out, err = manager._process.communicate()
             print(f"Stdout: {out}")
             print(f"Stderr: {err}")
