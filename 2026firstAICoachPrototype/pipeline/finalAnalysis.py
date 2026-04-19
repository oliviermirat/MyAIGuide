import pandas as pd
from scipy import stats
from pathlib import Path
import sys


def analyze_scores(file_path: Path) -> str:
    """
    Reads summaryResults.xlsx (hyperparameter grid summary) and calculates statistics for
    score_knee, score_face, and score_arm. Returns a text summary.
    """
    if not file_path.exists():
        msg = f"Error: The file '{file_path}' was not found."
        print(msg)
        return msg

    try:
        df = pd.read_excel(file_path)
        print(f"Successfully loaded '{file_path}'.\n")
    except Exception as e:
        msg = f"Error loading file: {e}"
        print(msg)
        return msg

    lines = []

    columns_to_analyze = ["score_knee", "score_face", "score_arm"]

    for col in columns_to_analyze:
        if col not in df.columns:
            warning = f"Warning: Column '{col}' not found in the Excel file. Skipping."
            print(warning)
            lines.append(warning)
            continue

        data = df[col].dropna()

        if len(data) == 0:
            msg = f"Column '{col}' has no valid data."
            print(msg)
            lines.append(msg)
            continue

        count_positive = (data > 0).sum()
        total_count = len(data)
        percentage = (count_positive / total_count) * 100

        t_stat, p_two_sided = stats.ttest_1samp(data, 0)

        if t_stat > 0:
            p_one_sided = p_two_sided / 2
        else:
            p_one_sided = 1 - (p_two_sided / 2)

        header = f"Analysis for: {col}"
        body = [
            f"  - Percentage of lines > 0: {percentage:.1f}% ({count_positive} out of {total_count})",
            f"  - Mean score:              {data.mean():.4f}",
            f"  - P-value (superior to 0): {p_one_sided:.4e}",
            f"For {col[6:]} pain, {percentage:.1f}% hyperparameters combinations "
            f"({count_positive} out of {total_count}) had a 'high pain' group mean "
            f"larger than the 'low clean pain' group mean, ",
        ]

        if p_one_sided < 0.05:
            interp = "    -> Result: Statistically significantly superior to 0 (p < 0.05)"
        else:
            interp = "    -> Result: Not statistically significant"

        print(header)
        lines.append(header)
        for line in body:
            print(line)
            lines.append(line)
        print(interp)
        lines.append(interp)
        print("-" * 50)
        lines.append("-" * 50)

    column_pairs = {
        "p_val_knee": "score_knee",
        "p_val_face": "score_face",
        "p_val_arm": "score_arm",
    }

    pval_columns = ["p_val_knee", "p_val_face", "p_val_arm"]

    for col in pval_columns:
        col2 = column_pairs.get(col)

        if col not in df.columns or col2 not in df.columns:
            warning = f"Warning: Columns '{col}' or '{col2}' not found. Skipping."
            print(warning)
            lines.append(warning)
            continue

        clean_df = df[[col, col2]].dropna()
        clean_df = clean_df[clean_df[col2] > 0]

        if len(clean_df) == 0:
            msg = f"Column pair '{col}' & '{col2}' has no valid data."
            print(msg)
            lines.append(msg)
            continue

        matches = (clean_df[col] <= 0.05) & (clean_df[col2] > 0)

        count_positive = matches.sum()
        total_count = len(clean_df)

        percentage = (count_positive / total_count) * 100

        header = f"Analysis for: {col}"
        line1 = (
            f"  - Percentage of lines <= 0.05: {percentage:.1f}% "
            f"({count_positive} out of {total_count})"
        )
        line2 = (
            f"{col[6:]}: and that difference was significant for {percentage:.1f}% of "
            f"those hyperparameters combinations ({count_positive} out of {total_count})."
        )

        print(header)
        print(line1)
        print(line2)
        lines.extend([header, line1, line2])

    return "\n".join(lines)


def _cli_main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python finalAnalysis.py <path_to_summaryResults.xlsx>")
        sys.exit(1)

    ranked_path = Path(sys.argv[1])
    summary = analyze_scores(ranked_path)
    print("\nSummary:\n")
    print(summary)


if __name__ == "__main__":
    _cli_main()
