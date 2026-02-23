import subprocess
import os

def launch_sequence():
    engine_order = [
        "zent_quantum_engine.py",
        "szc_wallet.py",
        "cloud_orchestrator_api.py",
        "zent_engine.py"
    ]

    for script in engine_order:
        if os.path.exists(script):
            print(f"Launching: {script}")
            subprocess.run(["python", script])
        else:
            print(f"Script not found: {script}")

if __name__ == "__main__":
    launch_sequence()
