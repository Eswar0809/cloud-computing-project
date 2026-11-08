"""
Runs the 2-minute Locust load test against the service on port 8000.
Generates results/loadtest_stats.csv and results/loadtest_headers.json.
"""
import os
import subprocess
import sys
import time
import urllib.request

S3_ENDPOINT = "http://127.0.0.1:8333"
PORT = 8000
SERVER_URL = f"http://127.0.0.1:{PORT}"


def wait_for_ready(timeout=30):
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            req = urllib.request.Request(f"{SERVER_URL}/readyz")
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return time.time() - t0
        except Exception:
            pass
        time.sleep(0.3)
    return None


def main():
    print("=" * 65)
    print(" TASK 4 & 7: 2-MINUTE LOCUST LOAD TEST BENCHMARK")
    print("=" * 65)

    env = os.environ.copy()
    env["MODEL_URI"] = "models/v1"
    env["MODEL_VERSION"] = "v1"
    env["S3_ENDPOINT"] = S3_ENDPOINT
    env["MAX_NEW_TOKENS"] = "1"
    env["FAULT_INJECT"] = "0"
    env["CLUSTER_SIM"] = "1"

    print(f"Starting inference service on port {PORT} with CLUSTER_SIM=1...")
    cmd = [
        sys.executable, "-m", "uvicorn", "service.app:app",
        "--host", "127.0.0.1",
        "--port", str(PORT),
        "--log-level", "warning"
    ]
    proc = subprocess.Popen(cmd, env=env)

    try:
        ready_time = wait_for_ready(30)
        if ready_time is None:
            print("ERROR: Service failed to reach ready state within 30s")
            return
        print(f"Service READY in {ready_time:.2f}s! Proceeding to Locust load test...")

        locust_cmd = [
            "locust", "-f", "tools/locustfile.py",
            "--headless",
            "--users", "4",
            "--spawn-rate", "4",
            "--run-time", "2m",
            "--host", SERVER_URL,
            "--csv", "results/loadtest"
        ]
        print(f"Executing: {' '.join(locust_cmd)}")
        locust_p = subprocess.run(locust_cmd, capture_output=True, text=True)

        print("\nLocust Output:")
        print(locust_p.stdout)
        if locust_p.stderr:
            print("Locust Stderr/Warnings:")
            print(locust_p.stderr[:500])

        print("\nBenchmark completed successfully!")

    finally:
        print("Stopping uvicorn server...")
        try:
            proc.terminate()
            proc.wait(timeout=3)
        except Exception:
            pass


if __name__ == "__main__":
    main()
