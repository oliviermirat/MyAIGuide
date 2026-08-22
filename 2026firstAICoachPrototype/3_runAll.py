"""
Super-master script: runs multiple 2_*.py pipeline scripts in parallel.
Set USE_DEBUG_GRID below to override the grid config in every child script.
"""
import os
import subprocess
import sys
from pathlib import Path

# --- Single switch: when True, all child runs use CONFIG_GRID_DEBUG; when False, each uses its own setting ---
USE_DEBUG_GRID = False

SCRIPT_DIR = Path(__file__).resolve().parent
CHILD_SCRIPTS = [
    "3_createFigure1.py",
    "3_explorePercentilesDuringFlares.py",
    "3_runAll_pearsonCorrelations.py",
    "3_write_paperResults.py",
    "3_pearson_residualRemovals.py --only_negative True",
    "3_pearson_residualRemovals.py",
    "3_pearson_residualRemovals_moodAndSleepOnly.py",
]

# Enough "y\n" to pass the initial "Continue?" and any "WARNING: ... Continue?" prompts in child scripts
STDIN_YES = b"y\n" * 20


def main() -> None:
    print("")
    print("2_runAll: will run the following scripts in parallel:")
    for s in CHILD_SCRIPTS:
        print("  -", s)
    print("")
    print("USE_DEBUG_GRID (overrides all children):", USE_DEBUG_GRID)
    response = input("Continue? (y/n): ")
    if response.lower() != "y":
        print("Aborting.")
        return

    env = os.environ.copy()
    env["RUNALL_MASTER_DEBUG_GRID"] = "true" if USE_DEBUG_GRID else "false"

    processes = []
    for script_cmd in CHILD_SCRIPTS:
        cmd_parts = script_cmd.split()
        script_file = cmd_parts[0]
        script_args = cmd_parts[1:]
        
        path = SCRIPT_DIR / script_file
        if not path.exists():
            print(f"ERROR: Script not found: {path}", file=sys.stderr)
            continue
            
        # Construct the final command list for Popen
        command = [sys.executable, str(path)] + script_args
        
        p = subprocess.Popen(
            command,
            cwd=str(SCRIPT_DIR),
            env=env,
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )
        # Store the full command string for easier debugging/logging
        processes.append((script_cmd, p))

    # Feed "y" to all prompts in each child so they don't block
    for script_cmd, p in processes:
        if p.stdin is not None:
            try:
                p.stdin.write(STDIN_YES)
                p.stdin.flush()
                p.stdin.close()
            except (BrokenPipeError, OSError):
                pass

    failed = []
    for script_cmd, p in processes:
        code = p.wait()
        if code != 0:
            failed.append((script_cmd, code))

    print("")
    if failed:
        print("Completed with errors:")
        for script_cmd, code in failed:
            print(f"  {script_cmd}: exit code {code}")
        sys.exit(1)
    print(f"All {len(CHILD_SCRIPTS)} runs completed successfully.")


if __name__ == "__main__":
    main()