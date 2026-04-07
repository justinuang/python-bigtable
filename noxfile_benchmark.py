import nox
import os

@nox.session(python="3.13")
def benchmark(session):
    """Run YCSB benchmark on remote VM using standard venv."""
    # Step 0: Install build dependencies
    session.install("setuptools", "wheel", "--extra-index-url", "https://pypi.org/simple")
    
    # Step 1: Clean and Build Wheel
    session.run("rm", "-rf", "build/", "dist/", "*.egg-info", external=True)
    session.run("python", "setup.py", "bdist_wheel")
    
    wheel_file = [f for f in os.listdir("dist") if f.endswith(".whl")][0]
    
    vm_name = "ju-ruby-sidecar-c3-vm-east4"
    vm_zone = "us-east4-a"
    project_id = "autonomous-mote-782"
    ssh_user = "justinuang_google_com"
    
    # Step 2: Deploy to VM
    session.run(
        "gcloud", "compute", "ssh", f"{ssh_user}@{vm_name}",
        f"--zone={vm_zone}", f"--project={project_id}",
        "--command=mkdir -p ~/python_benchmark",
        external=True
    )
    
    session.run(
        "gcloud", "compute", "scp",
        f"dist/{wheel_file}", "scripts/ycsb_benchmark.py",
        f"{ssh_user}@{vm_name}:~/python_benchmark/",
        f"--zone={vm_zone}", f"--project={project_id}",
        external=True
    )
    
    # Step 3: Run on VM
    remote_commands = f"""
    cd ~/python_benchmark
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
    ./venv/bin/pip install uvloop
    ./venv/bin/pip install --force-reinstall {wheel_file}
    
    echo "Running with Sidecar..."
    ./venv/bin/python ycsb_benchmark.py --use-sidecar --app-profile-id=sidecar --qps=500 --duration=60
    
    echo "Running without Sidecar..."
    ./venv/bin/python ycsb_benchmark.py --app-profile-id=nosidecar --qps=500 --duration=60
    
    echo "Running with Jetstream..."
    ./venv/bin/python ycsb_benchmark.py --use-sidecar --use-jetstream --app-profile-id=sidecarjetstream --qps=500 --duration=60
    """
    
    session.run(
        "gcloud", "compute", "ssh", f"{ssh_user}@{vm_name}",
        f"--zone={vm_zone}", f"--project={project_id}",
        f"--command={remote_commands}",
        external=True
    )

@nox.session(python="3.13")
def local_benchmark(session):
    """Run YCSB benchmark locally."""
    session.install("uvloop", "--extra-index-url", "https://pypi.org/simple")
    session.install("-e", ".", "--extra-index-url", "https://pypi.org/simple")
    session.run("python", "scripts/ycsb_benchmark.py", *session.posargs)
