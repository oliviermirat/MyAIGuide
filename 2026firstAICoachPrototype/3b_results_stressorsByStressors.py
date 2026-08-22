import pandas as pd
import numpy as np
from scipy.stats import pearsonr
from pathlib import Path
import os

for region in ["face", "knee", "arm"]:

    VARIABLE_OF_INTEREST  = "score_" + region         # validation set
    VARIABLE_OF_INTEREST2 = "test_roc_auc_" + region  # test set

    from libraries.run_context import (
        HYPERPARAMETERS_GRID_SEARCH_RESULTS_SUBDIR,
        SUMMARY_RESULTS_XLSX,
    )

    SCRIPT_ROOT = Path(__file__).resolve().parent
    RESULTS_ROOT = SCRIPT_ROOT / "results"
    COMBINED_DIR = RESULTS_ROOT / "combinedAnalysis"

    TABLE1_COLUMNS = [
        "numberOfSteps",
        "manicTimeRealTime",
        "timeSpentDriving",
        "numberOfHeartBeatsAbove110_lowerBodyActivity_cycling",
        "timeSpentRidingCar",
        "phoneTime",
        "numberOfComputerClicksAndKeyStrokes",
        "surfCumBpmAbove110",
        "numberOfHeartBeatsAbove110_upperBodyActivity",
        "climbingMaxEffortIntensity",
        "score",
        "rhr",
        "generalMood",
    ]

    EXPERIMENT_FOLDER_ORDER = (
        "numberOfSteps",
        "manicTimeRealTime",
        "timeSpentDriving",
        "numberOfHeartBeatsAbove110_lowerBodyActivity_cycling",
        "timeSpentRidingCar",
        "phoneTime",
        "numberOfComputerClicksAndKeyStrokes",
        "surfCumBpmAbove110",
        "numberOfHeartBeatsAbove110_upperBodyActivity",
        "climbingMaxEffortIntensity",
        "score",
        "rhr",
        "generalMood",
    )

    TABLE1_ROWS = [
        "maximum mean ROC-AUC that could have been reached for another set of hyperparameters",
        "80th percentile of mean ROC-AUC that could have been reached for another set of hyperparameters",
        "50th percentile of mean ROC-AUC that could have been reached for another set of hyperparameters",
        "Pearson r — mean_custom_score (validation) vs mean_test_roc_auc (test), all grid rows",
        "Pearson r — mean_custom_score (validation) vs mean_test_roc_auc (test), only 0.8 threshold",
    ]

    def _summary_path(exp_folder: str) -> Path:
        return (
            RESULTS_ROOT
            / exp_folder
            / HYPERPARAMETERS_GRID_SEARCH_RESULTS_SUBDIR
            / SUMMARY_RESULTS_XLSX
        )

    def load_summary(exp_folder: str) -> pd.DataFrame:
        p = _summary_path(exp_folder)
        if not p.is_file():
            raise FileNotFoundError(f"Missing summary results: {p}")
        df = pd.read_excel(p)
        if df.empty:
            raise ValueError(f"Empty summary file: {p}")
        return df

    def _pearson_r_p(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
        """Pearson r and two-tailed p-value; drop pairwise NaNs. Need n >= 2 pairs."""
        x = np.asarray(x, dtype=float)
        y = np.asarray(y, dtype=float)
        mask = ~(np.isnan(x) | np.isnan(y))
        if mask.sum() < 2:
            return float("nan"), float("nan")
        r, p = pearsonr(x[mask], y[mask])
        return float(r), float(p)

    def validation_vs_test_correlations(df: pd.DataFrame) -> dict[str, float]:
        """
        Across all hyperparameter rows in summaryResults: correlate validation summaries
        with mean_test_roc_auc (test).
        """
        y = df["mean_test_roc_auc"].values.astype(float)
        mc = df["mean_custom_score"].values.astype(float)
        adj = df["adjusted_score"].values.astype(float)
        r_mc, p_mc = _pearson_r_p(mc, y)
        r_adj, p_adj = _pearson_r_p(adj, y)
        return {
            "r_mean_custom": r_mc,
            "p_mean_custom": p_mc,
            "r_adjusted": r_adj,
            "p_adjusted": p_adj,
        }

    def _mean_auc_distribution(df: pd.DataFrame) -> np.ndarray:
        s  = df[VARIABLE_OF_INTEREST].dropna().astype(float)
        s2 = df[VARIABLE_OF_INTEREST2].dropna().astype(float)
        s = pd.concat([s, s2], axis=0, ignore_index=True)
        if s.empty:
            return np.array([])
        return s.values


    def _grid_stats(df: pd.DataFrame) -> dict:
        v = _mean_auc_distribution(df)
        if len(v) == 0:
            return dict(
                max=np.nan,
                p50=np.nan,
                p80=np.nan,
                p90=np.nan,
            )
        return dict(
            max=float(np.nanmax(v)),
            p50=float(np.nanpercentile(v, 50)),
            p80=float(np.nanpercentile(v, 80)),
            p90=float(np.nanpercentile(v, 90)),
        )


    def build_table1(
        data_by_exp: dict[str, pd.DataFrame]
    ) -> pd.DataFrame:
        
        col_keys = list(EXPERIMENT_FOLDER_ORDER)
        table = pd.DataFrame(index=TABLE1_ROWS, columns=TABLE1_COLUMNS, dtype=object)
        for col_name, exp in zip(TABLE1_COLUMNS, col_keys):
            df = data_by_exp[exp]
            # df_q08 = data_by_exp_q08[exp]
            gs = _grid_stats(df)
            cor_all = validation_vs_test_correlations(df)
            # cor_q08 = validation_vs_test_correlations(df_q08)
            table.loc[TABLE1_ROWS[0], col_name] = gs["max"]
            table.loc[TABLE1_ROWS[1], col_name] = gs["p80"]
            table.loc[TABLE1_ROWS[2], col_name] = gs["p50"]
            table.loc[TABLE1_ROWS[3], col_name] = cor_all["r_mean_custom"]
            # table.loc[TABLE1_ROWS[4], col_name] = cor_q08["r_mean_custom"]
        
        return table


    def main() -> None:
        os.chdir(SCRIPT_ROOT)
        COMBINED_DIR.mkdir(parents=True, exist_ok=True)

        numberOfSteps_df = load_summary("numberOfSteps")
        manicTimeRealTime_df = load_summary("manicTimeRealTime")
        timeSpentDriving_df = load_summary("timeSpentDriving")
        numberOfHeartBeatsAbove110_lowerBodyActivity_cycling_df = load_summary("numberOfHeartBeatsAbove110_lowerBodyActivity_cycling")
        timeSpentRidingCar_df = load_summary("timeSpentRidingCar")
        phoneTime_df = load_summary("phoneTime")
        numberOfComputerClicksAndKeyStrokes_df = load_summary("numberOfComputerClicksAndKeyStrokes")
        surfCumBpmAbove110_df = load_summary("surfCumBpmAbove110")
        numberOfHeartBeatsAbove110_upperBodyActivity_df = load_summary("numberOfHeartBeatsAbove110_upperBodyActivity")
        climbingMaxEffortIntensity_df = load_summary("climbingMaxEffortIntensity")
        score_df = load_summary("score")
        rhr_df = load_summary("rhr")
        generalMood_df = load_summary("generalMood")

        data_by_exp = {
            "numberOfSteps": numberOfSteps_df,
            "manicTimeRealTime": manicTimeRealTime_df,
            "timeSpentDriving": timeSpentDriving_df,
            "numberOfHeartBeatsAbove110_lowerBodyActivity_cycling": numberOfHeartBeatsAbove110_lowerBodyActivity_cycling_df,
            "timeSpentRidingCar": timeSpentRidingCar_df,
            "phoneTime": phoneTime_df,
            "numberOfComputerClicksAndKeyStrokes": numberOfComputerClicksAndKeyStrokes_df,
            "surfCumBpmAbove110": surfCumBpmAbove110_df,
            "numberOfHeartBeatsAbove110_upperBodyActivity": numberOfHeartBeatsAbove110_upperBodyActivity_df,
            "climbingMaxEffortIntensity": climbingMaxEffortIntensity_df,
            "score": score_df,
            "rhr": rhr_df,
            "generalMood": generalMood_df,
        }
        # data_by_exp_q08 = {
            # exp: _filter_high_pain_quartile_08(data_by_exp[exp], _summary_path(exp))
            # for exp in EXPERIMENT_FOLDER_ORDER
        # }
        # save_figure2(data_by_exp, data_by_exp_q08, COMBINED_DIR)

        table1_df = build_table1(data_by_exp) #, data_by_exp_q08)
        table1_df = table1_df.apply(pd.to_numeric, errors="coerce").round(2)
        table1_df = table1_df[table1_df.iloc[1].sort_values(ascending=False).index]
        table1_path = COMBINED_DIR / "table5.xlsx"
        with pd.ExcelWriter(table1_path, engine="openpyxl") as writer:
            table1_df.to_excel(writer, sheet_name="Table1", index=True)
        print(f"Wrote {table1_path} (sheet: Table1; values rounded to 2 decimals)")
        
        t2 = table1_df.T
        t3 = t2['80th percentile of mean ROC-AUC that could have been reached for another set of hyperparameters']
        
        renaming_dict = {'numberOfHeartBeatsAbove110_lowerBodyActivity_cycling': 'Cycling related cumulative bpm > 110',
                        'numberOfHeartBeatsAbove110_upperBodyActivity': 'Upper-body cumulative bpm > 110',
                        'surfCumBpmAbove110': 'Surf cumulative bpm > 110',
                        'climbingMaxEffortIntensity': 'Rock climbing maximum route grade',
                        'phoneTime': 'Time spent using a mobile phone',
                        'rhr': 'Heart rate variability',
                        'timeSpentDriving': 'Time spent driving a car',
                        'numberOfSteps': 'Number of steps taken',
                        'numberOfComputerClicksAndKeyStrokes': 'Number of keyboard and mouse clicks',
                        'score': 'Sleep score',
                        'timeSpentRidingCar': 'Time spent riding a vehicule',
                        'manicTimeRealTime': 'Time spent on computer',
                        'generalMood': 'General mood',
                        }
        
        t3 = t3.rename(index=renaming_dict)
        table_combined_path = COMBINED_DIR / f"table_{region}.xlsx"
        with pd.ExcelWriter(table_combined_path, engine="openpyxl") as writer:
            t3.to_excel(writer, sheet_name="Table1", index=True)

    if __name__ == "__main__":
        main()
