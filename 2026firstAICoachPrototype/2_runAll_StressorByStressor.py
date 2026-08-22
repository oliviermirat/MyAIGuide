"""
Super-master script: runs multiple 2_*.py pipeline scripts in parallel.
Updated to support command-line arguments for child scripts.
"""
import os
import subprocess
import sys
from pathlib import Path

# --- Single switch: when True, all child runs use CONFIG_GRID_DEBUG; when False, each uses its own setting ---
USE_DEBUG_GRID = False

SCRIPT_DIR = Path(__file__).resolve().parent

# Each entry is a list: ["script_name.py", "arg1", "arg2", ...]
CHILD_SCRIPTS = [
    ["2_oneStressorOnly.py", "numberOfSteps"],
    ["2_oneStressorOnly.py", "manicTimeRealTime"],
    ["2_oneStressorOnly.py", "timeSpentDriving"],
    ["2_oneStressorOnly.py", "numberOfHeartBeatsAbove110_lowerBodyActivity_cycling"],
    ["2_oneStressorOnly.py", "timeSpentRidingCar"],
    ["2_oneStressorOnly.py", "phoneTime"],
    ["2_oneStressorOnly.py", "numberOfComputerClicksAndKeyStrokes"],
    ["2_oneStressorOnly.py", "surfCumBpmAbove110"],
    ["2_oneStressorOnly.py", "numberOfHeartBeatsAbove110_upperBodyActivity"],
    ["2_oneStressorOnly.py", "climbingMaxEffortIntensity"],
    ["2_oneStressorOnly.py", "score"],
    ["2_oneStressorOnly.py", "rhr"],
    ["2_oneStressorOnly.py", "generalMood"],
]

# Enough "y\n" to pass the initial "Continue?" and any "WARNING: ... Continue?" prompts in child scripts
STDIN_YES = b"y\n" * 20


def main() -> None:
    print("")
    print("2_runAll: will run the following scripts in parallel:")
    for cmd_list in CHILD_SCRIPTS:
        print(f"  - {' '.join(cmd_list)}")
    
    print("")
    print("USE_DEBUG_GRID (overrides all children):", USE_DEBUG_GRID)
    response = input("Continue? (y/n): ")
    if response.lower() != "y":
        print("Aborting.")
        return

    env = os.environ.copy()
    env["RUNALL_MASTER_DEBUG_GRID"] = "true" if USE_DEBUG_GRID else "false"

    processes = []
    for cmd_list in CHILD_SCRIPTS:
        script_name = cmd_list[0]
        script_args = cmd_list[1:]
        
        path = SCRIPT_DIR / script_name
        if not path.exists():
            print(f"ERROR: Script not found: {path}", file=sys.stderr)
            continue

        # Construct the full command: [python_executable, script_path, arg1, arg2...]
        full_command = [sys.executable, str(path)] + script_args

        p = subprocess.Popen(
            full_command,
            cwd=str(SCRIPT_DIR),
            env=env,
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        processes.append((script_name, p))

    # Feed "y" to all prompts in each child so they don't block
    for script_name, p in processes:
        if p.stdin is not None:
            try:
                p.stdin.write(STDIN_YES)
                p.stdin.flush()
                p.stdin.close()
            except (BrokenPipeError, OSError):
                pass

    failed = []
    for script_name, p in processes:
        code = p.wait()
        if code != 0:
            failed.append((script_name, code))

    print("")
    if failed:
        print("Completed with errors:")
        for script_name, code in failed:
            print(f"  {script_name}: exit code {code}")
        sys.exit(1)
        
    print(f"All {len(CHILD_SCRIPTS)} runs completed successfully.")


if __name__ == "__main__":
    main()