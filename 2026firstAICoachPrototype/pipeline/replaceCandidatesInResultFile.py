import pandas as pd
import sys
from pathlib import Path
from typing import Dict, List
from .gridConfigs import get_candidate_config
from libraries.run_context import RunPaths, create_run_paths


def replace_candidates_in_result_file(
    pain_type: str,
    candidates_config: Dict[str, Dict[str, List[str]]],
    run_paths: RunPaths,
) -> None:
    """
    Replace CANDIDATES lists in sorted_results with their logical group names.
    """
    if pain_type not in candidates_config:
        print(f"Error: PAIN_TYPE '{pain_type}' not defined for this data version.")
        return

    input_path = run_paths.output_dir / f"sorted_results_{pain_type}.csv"
    if not input_path.exists():
        print(f"Error: Input file not found at {input_path}")
        return

    df = pd.read_csv(input_path)

    pain_config = candidates_config[pain_type]
    mapping = {str(variables): group_name for group_name, variables in pain_config.items()}

    df["CANDIDATES"] = df["CANDIDATES"].replace(mapping)

    output_path = run_paths.output_dir / f"processed_results_{pain_type}.csv"
    df.to_csv(output_path, index=False)

    print(f"Successfully processed {pain_type} and saved to {output_path}")


def _cli_main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python replaceCandidatesInResultFile.py <PAIN_TYPE> <data_version> [run_name]")
        sys.exit(1)

    pain_type = sys.argv[1]
    data_version = sys.argv[2]  # 'new' or 'old'
    run_name = sys.argv[3] if len(sys.argv) > 3 else None

    candidates_config = get_candidate_config(data_version)
    run_paths = create_run_paths(run_name)

    replace_candidates_in_result_file(pain_type, candidates_config, run_paths)


if __name__ == "__main__":
    _cli_main()
