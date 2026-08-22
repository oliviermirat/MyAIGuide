import subprocess
import sys
import concurrent.futures
import os
import shutil
from pathlib import Path

# Ensure this exactly matches the name of your modified script
TARGET_SCRIPT = "4_runInferenceOnExtendedTestSet.py"

# 1. Define the multipliers you want to test
multipliers = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.65, 0.7, 0.8, 0.9, 1.0]

def run_experiment(output_name: str, apply_scaling: bool, multiplier: float) -> dict:
    """Helper function to build and execute the command in an isolated thread."""
    
    command = [
        sys.executable,
        TARGET_SCRIPT,
        "--output_run_name", output_name,
        "--multiplier", str(multiplier)
    ]
    
    if apply_scaling:
        command.append("--apply_scaling")
        
    # Force UTF-8 encoding to prevent Windows cp1252 UnicodeEncodeErrors
    custom_env = os.environ.copy()
    custom_env["PYTHONIOENCODING"] = "utf-8"
        
    try:
        # Pass the custom environment and set encoding="utf-8" for the captured output
        result = subprocess.run(
            command, 
            check=True, 
            capture_output=True, 
            text=True, 
            env=custom_env,
            encoding="utf-8"
        )
        return {"name": output_name, "success": True, "output": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"name": output_name, "success": False, "error": e.stderr, "code": e.returncode}

def main() -> None:
    print("Starting parallel batch runs...")
    print("=" * 40)

    tasks = []
    
    for mult in multipliers:
        tasks.append({
            "output_name": f"extendedTestSet_Scaled_{mult}",
            "apply_scaling": True,
            "multiplier": mult
        })

    tasks.append({
        "output_name": "extendedTestSet_NoScaling",
        "apply_scaling": False,
        "multiplier": 1.0 
    })

    max_workers = min(len(tasks), (os.cpu_count() or 1) + 4)
    print(f"Executing {len(tasks)} runs using up to {max_workers} parallel workers...\n")

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(
                run_experiment, 
                task["output_name"], 
                task["apply_scaling"], 
                task["multiplier"]
            ): task["output_name"] for task in tasks
        }
        
        for future in concurrent.futures.as_completed(future_to_task):
            task_name = future_to_task[future]
            try:
                result = future.result()
                if result["success"]:
                    print(f"[SUCCESS] Finished run: {result['name']}")
                else:
                    print(f"[ERROR] Script failed during run '{result['name']}'. Exit code: {result['code']}")
                    if result["error"]:
                        print(f"Error details:\n{result['error']}")
            except Exception as exc:
                print(f"[FATAL] Run '{task_name}' generated an exception: {exc}")

    print("=" * 40)
    print("All batch runs completed!")

    ###
    
    # Base paths
    base_results_dir = Path("results")
    destination_dir = base_results_dir / "extendedTestSetFaceCounterfactual"
    
    # Create the destination directory if it doesn't already exist
    destination_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Gathering files into: {destination_dir}\n")
    print("-" * 50)
    
    # 2. Iterate through runs and copy files
    for mult in multipliers:
        run_name = f"extendedTestSet_Scaled_{mult}"
        source_dir = base_results_dir / run_name / "bestHyperparametersSetResults"
        
        # We look for both png and pdf
        for ext in [".png", ".pdf"]:
            source_filename = f"trafficLights_facePain{ext}"
            source_file = source_dir / source_filename
            
            if source_file.is_file():
                # Append the multiplier to the filename to prevent overwriting
                new_filename = f"trafficLights_facePain_{mult}{ext}"
                dest_file = destination_dir / new_filename
                
                # copy2 preserves file metadata
                shutil.copy2(source_file, dest_file)
                print(f"Copied: {source_file.relative_to(base_results_dir)} -> {new_filename}")
            else:
                print(f"Missing: {source_file.relative_to(base_results_dir)} (File not found)")
                
    print("-" * 50)
    print("Done gathering files!")


if __name__ == "__main__":
    main()