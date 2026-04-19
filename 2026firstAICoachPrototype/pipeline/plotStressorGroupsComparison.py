import pandas as pd
import sys
from libraries.run_context import RunPaths, create_run_paths


def plot_stressor_groups_comparison(pain_type: str, run_paths: RunPaths) -> None:
    """
    Print custom-score quartiles grouped by candidate set (from sorted_results CSV).
    """
    csv_path = run_paths.output_dir / f"sorted_results_{pain_type}.csv"
    df = pd.read_csv(csv_path)

    summary_stats = df.groupby("CANDIDATES")["custom_score"].describe(
        percentiles=[0.25, 0.5, 0.75]
    )
    print(summary_stats[["25%", "50%", "75%"]])


def _cli_main() -> None:
    pain_type = sys.argv[1]
    run_name = sys.argv[2] if len(sys.argv) > 2 else None
    run_paths = create_run_paths(run_name)
    plot_stressor_groups_comparison(pain_type, run_paths)


if __name__ == "__main__":
    _cli_main()
