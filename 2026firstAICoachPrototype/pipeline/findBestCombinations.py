import pandas as pd
import json
import sys
from pathlib import Path
from typing import Dict, List
from .gridConfigs import get_candidate_config
from libraries.run_context import RunPaths, SUMMARY_RESULTS_XLSX, create_run_paths


def find_best_combination(
    kneePain: str,
    facePain: str,
    armPain: str,
    candidates_config: Dict[str, Dict[str, List[str]]],
    run_paths: RunPaths,
) -> Path:
    """
    Find the best common hyperparameter combination across three pain types,
    restricted to 'physicalLoad' candidate sets, and write:
      - summaryResults.xlsx
      - best_params_<pain>.json for each pain type.
    """
    file_names = [
        run_paths.output_dir / f"processed_results_{kneePain}.csv",
        run_paths.output_dir / f"processed_results_{facePain}.csv",
        run_paths.output_dir / f"processed_results_{armPain}.csv",
    ]

    merge_keys = [
        "ACUTE_WINDOW",
        "CHRONIC_WINDOW",
        "NB_TOP_FEATURES_TO_KEEP",
        "HIGH_PAIN_QUARTILE_DEFINITION",
        "CANDIDATES",
    ]

    dfs = []
    correspond = {0: "knee", 1: "face", 2: "arm"}

    try:
        for i, fname in enumerate(file_names):
            print(f"Processing {fname}...")
            df = pd.read_csv(fname)

            df_filtered = df[df["CANDIDATES"] == "physicalLoad"].copy()

            if df_filtered.empty:
                print(f"Warning: No 'physicalLoad' candidates found in {fname}")
                return run_paths.output_dir / SUMMARY_RESULTS_XLSX

            df_subset = df_filtered[merge_keys + ["custom_score", "p_val_corr_coeff"]]
            df_subset = df_subset.rename(
                columns={
                    "custom_score": f"score_{correspond[i]}",
                    "p_val_corr_coeff": f"p_val_{correspond[i]}",
                }
            )

            dfs.append(df_subset)

        merged_df = dfs[0]
        for next_df in dfs[1:]:
            merged_df = pd.merge(merged_df, next_df, on=merge_keys, how="inner")

        if merged_df.empty:
            print("No common combinations found across all files.")
            return run_paths.output_dir / SUMMARY_RESULTS_XLSX

        score_columns = [col for col in merged_df.columns if col.startswith("score_")]
        merged_df["mean_custom_score"] = merged_df[score_columns].mean(axis=1)
        merged_df["adjusted_score"] = (
            merged_df["mean_custom_score"] - merged_df[score_columns].std(axis=1)
        )

        best_row = merged_df.loc[merged_df["adjusted_score"].idxmax()]

        print("-" * 40)
        print("OPTIMAL COMBINATION FOUND")
        print("-" * 40)
        for key in merge_keys:
            print(f"{key}: {best_row[key]}")

        print("-" * 40)
        print(f"Mean Custom Score: {best_row['mean_custom_score']:.4f}")
        print("(Mean of scores from all 3 files)")

        output_file = run_paths.output_dir / SUMMARY_RESULTS_XLSX
        print(f"Saving all tested combinations to {output_file}...")

        ranked_df = merged_df.sort_values(by="adjusted_score", ascending=False)
        ranked_df.to_excel(output_file, index=False)
        print("File saved successfully.")

        pain_types = [armPain, facePain, kneePain]

        for p_type in pain_types:
            if p_type not in candidates_config:
                print(f"Warning: pain type '{p_type}' not in candidates_config.")
                continue

            final_params = {
                "ACUTE_WINDOW": int(best_row["ACUTE_WINDOW"]),
                "CHRONIC_WINDOW": int(best_row["CHRONIC_WINDOW"]),
                "ONLY_USE_ACWR": False,
                "INCLUDE_NB_PREVIOUS_DAY_PAIN": 0,
                "SEEK_MOST_IMPORTANT_FEATURES": True,
                "NB_TOP_FEATURES_TO_KEEP": int(best_row["NB_TOP_FEATURES_TO_KEEP"]),
                "HIGH_PAIN_QUARTILE_DEFINITION": float(
                    best_row["HIGH_PAIN_QUARTILE_DEFINITION"]
                ),
                "WARNING_WINDOW": 1,
                "CANDIDATES": candidates_config[p_type][best_row["CANDIDATES"]],
            }

            json_filename = run_paths.output_dir / f"best_params_{p_type}.json"
            with json_filename.open("w") as f:
                json.dump(final_params, f, indent=4)

            print(f"Saved optimized parameters to {json_filename}")

        return output_file

    except FileNotFoundError as e:
        print(f"Error: Could not find file. {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return run_paths.output_dir / SUMMARY_RESULTS_XLSX


def _cli_main() -> None:
    if len(sys.argv) < 5:
        print(
            "Usage: python findBestCombinations.py <kneePain> <facePain> <armPain> <data_version> [run_name]"
        )
        sys.exit(1)

    kneePain = sys.argv[1]
    facePain = sys.argv[2]
    armPain = sys.argv[3]
    data_version = sys.argv[4]
    run_name = sys.argv[5] if len(sys.argv) > 5 else None

    candidates_config = get_candidate_config(data_version)
    run_paths = create_run_paths(run_name)

    find_best_combination(kneePain, facePain, armPain, candidates_config, run_paths)


if __name__ == "__main__":
    _cli_main()
