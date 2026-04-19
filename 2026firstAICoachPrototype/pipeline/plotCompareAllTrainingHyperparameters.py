import pandas as pd
import sys
from libraries.run_context import RunPaths, create_run_paths


def plot_compare_all_training_hyperparameters(
    knee_pain: str,
    face_pain: str,
    arm_pain: str,
    run_paths: RunPaths,
) -> None:
    """
    Load processed results for all pain types and print per-hyperparameter custom_score stats.
    """
    files = [
        run_paths.output_dir / f"processed_results_{arm_pain}.csv",
        run_paths.output_dir / f"processed_results_{face_pain}.csv",
        run_paths.output_dir / f"processed_results_{knee_pain}.csv",
    ]

    data_frames = []
    for file in files:
        try:
            df = pd.read_csv(file)
            data_frames.append(df)
            print(f"Successfully loaded {file}")
        except FileNotFoundError:
            print(f"Error: Could not find {file}")
            return

    df_all = pd.concat(data_frames, ignore_index=True)

    columns_to_plot = [
        "ACUTE_WINDOW",
        "CHRONIC_WINDOW",
        "NB_TOP_FEATURES_TO_KEEP",
        "HIGH_PAIN_QUARTILE_DEFINITION",
        "CANDIDATES",
    ]

    for col in columns_to_plot:
        unique_vals = sorted(df_all[col].unique())

        print(f"\n--- Statistics for {col} ---")
        print(f"{'Value':<40} | {'Mean':<10} | {'Median':<10}")
        print("-" * 66)

        for val in unique_vals:
            subset = df_all[df_all[col] == val]["custom_score"]
            mean_val = subset.mean()
            median_val = subset.median()
            print(f"{str(val):<40} | {mean_val:.4f}     | {median_val:.4f}")

    print("\n--- Identifying Best Hyperparameters ---")

    for col in columns_to_plot:
        medians = df_all.groupby(col)["custom_score"].median()
        best_val = medians.idxmax()
        best_score = medians.max()
        print(f"Best {col}: {best_val} (Median Score: {best_score:.4f})")


def _cli_main() -> None:
    knee_pain = sys.argv[1]
    face_pain = sys.argv[2]
    arm_pain = sys.argv[3]
    run_name = sys.argv[4] if len(sys.argv) > 4 else None
    run_paths = create_run_paths(run_name)
    plot_compare_all_training_hyperparameters(knee_pain, face_pain, arm_pain, run_paths)


if __name__ == "__main__":
    _cli_main()
