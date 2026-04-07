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
#
"""
Sidecar manager for Python Bigtable client.
Handles process lifecycle and FIFO readiness signaling.
"""

import os
import subprocess
import tempfile
import atexit
import signal
import logging

logger = logging.getLogger(__name__)

class SidecarManager:
    _instance = None
    _process = None
    _tmp_dir = None
    _socket_path = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SidecarManager, cls).__new__(cls)
        return cls._instance

    def start_sidecar(self) -> str:
        """
        Starts the Java sidecar process eagerly if not already running.
        Returns the path to the Unix Domain Socket.
        """
        if self._process is not None:
            logger.info("Sidecar already running.")
            return self._socket_path

        # Locate the JAR file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        jar_path = os.path.join(current_dir, "..", "bin", "java-sidecar.jar")
        
        if not os.path.exists(jar_path):
            raise FileNotFoundError(
                f"Sidecar JAR not found at {jar_path}. "
                "Please build the Java sidecar project and copy the shaded JAR to this location before running. "
                "See README_SIDECAR.md for details."
            )

        # Create temp dir for socket and FIFO
        self._tmp_dir = tempfile.mkdtemp(prefix="bigtable-sidecar-")
        self._socket_path = os.path.join(self._tmp_dir, "sidecar.sock")
        fifo_path = os.path.join(self._tmp_dir, "ready.fifo")

        try:
            os.mkfifo(fifo_path)
        except OSError as e:
            raise RuntimeError(f"Failed to create FIFO: {e}")

        # Build command
        cmd = [
            "java",
            "-jar",
            jar_path,
            self._socket_path,
            "--ready-fifo",
            fifo_path,
        ]

        logger.info(f"Starting Sidecar with command: {' '.join(cmd)}")

        
        # Start process
        log_path = os.path.join(self._tmp_dir, "sidecar.log")
        logger.info(f"Sidecar logs will be written to {log_path}")
        self._log_file = open(log_path, "w")
        
        self._process = subprocess.Popen(
            cmd,
            stdout=self._log_file,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid # Run in a new process group to avoid receiving signals meant for the parent
        )


        # Wait for readiness signal from FIFO
        logger.info("Waiting for sidecar readiness signal...")
        try:
            with open(fifo_path, "rb") as fifo:
                byte = fifo.read(1)
                if not byte:
                     raise RuntimeError("Sidecar closed FIFO without signaling readiness")
                logger.info("Sidecar signaled readiness.")
        except Exception as e:
            self.stop_sidecar()
            raise RuntimeError(f"Failed to start sidecar or wait for readiness: {e}")

        # Register atexit handler
        atexit.register(self.stop_sidecar)

        return self._socket_path

    def stop_sidecar(self):
        """Stops the sidecar process and cleans up."""
        if self._process:
            logger.info("Stopping Sidecar...")
            try:
                # Kill the process group
                os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Sidecar did not terminate, killing...")
                os.killpg(os.getpgid(self._process.pid), signal.SIGKILL)
            except Exception as e:
                logger.error(f"Error stopping sidecar: {e}")
            self._process = None

        if hasattr(self, "_log_file") and self._log_file:
            self._log_file.close()
            self._log_file = None

        if self._tmp_dir and os.path.exists(self._tmp_dir):

            import shutil
            shutil.rmtree(self._tmp_dir)
            self._tmp_dir = None
            self._socket_path = None


