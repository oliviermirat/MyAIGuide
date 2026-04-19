import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Union

from libraries.run_context import (
    BEST_HYPERPARAMETERS_SET_RESULTS_SUBDIR,
    HYPERPARAMETERS_GRID_SEARCH_RESULTS_SUBDIR,
)


def _prepare_categorized_data(
    df,
    PAIN_TYPE,
    nbDaysPriors,
    percentTierHigh,
    percentTierLow,
    rolling_func="none",
):
    """
    Helper function to categorize days into 5 groups based on pain levels and history.
    Returns the grouped data and the masks for further processing.
    """
    # 1. PREPARE ROLLING PREDICTIONS
    if rolling_func == 'mean':
        rolling_past_pred = df['predictedProbsWarning'].rolling(window=nbDaysPriors, min_periods=1).mean()
    elif rolling_func == 'ewm':
        rolling_past_pred = df['predictedProbsWarning'].ewm(span=nbDaysPriors, min_periods=1).mean()
    elif rolling_func == "max":
        rolling_past_pred = df["predictedProbsWarning"].rolling(window=nbDaysPriors, min_periods=1).max()
    elif rolling_func == "none":
        rolling_past_pred = df["predictedProbsWarning"]
    else:
        rolling_past_pred = df["predictedProbsWarning"]
    
    # 2. DEFINE THRESHOLDS
    thresh_high = df[PAIN_TYPE].quantile(percentTierHigh)
    thresh_low  = df[PAIN_TYPE].quantile(percentTierLow)
    
    # 3. CREATE MASKS
    # Group 1: High Pain
    g1_mask = (df[PAIN_TYPE] > thresh_high)
    
    # Prepare History for Low Pain Groups
    past_pain_max = df[PAIN_TYPE].rolling(window=nbDaysPriors, min_periods=1).max().shift(1)
    is_low_pain = (df[PAIN_TYPE] <= thresh_low)
    
    # Group 3: Low Pain with CLEAN History
    g3_mask = is_low_pain & (past_pain_max <= thresh_low)
    # Group 4: Low Pain with DIRTY History
    g4_mask = is_low_pain & (past_pain_max > thresh_low)
    # Group 5: All other days
    g5_mask = ~(g1_mask | g3_mask | g4_mask) & df[PAIN_TYPE].notna()
    
    masks = [g1_mask, g3_mask, g4_mask, g5_mask]
    data_groups = [rolling_past_pred[mask].dropna() for mask in masks]
    
    return data_groups, masks


def plot_risk_by_pain_category(
    df,
    PAIN_TYPE,
    SAVE_RISK_BY_CATEGORY_DONT_PLOT,
    nbDaysPriors=5,
    percentTierHigh=0.95,
    percentTierLow=0.90,
    output_dir: Union[str, Path] = HYPERPARAMETERS_GRID_SEARCH_RESULTS_SUBDIR,
    figures_dir: Union[str, Path] = BEST_HYPERPARAMETERS_SET_RESULTS_SUBDIR,
):
    data_groups, masks = _prepare_categorized_data(
        df, PAIN_TYPE, nbDaysPriors, percentTierHigh, percentTierLow
    )
    
    # Statistics and Saving (Group 1 vs Group 3)
    group_high = data_groups[0]
    group_low_clean   = data_groups[1]

    # if len(group_high) > 0 and len(group_low_clean) > 0:
        # t_stat, p_val = stats.ttest_ind(group_high, group_low_clean, equal_var=False)
        
        # if not os.path.exists(BEST_HYPERPARAMETERS_SET_RESULTS_SUBDIR): os.makedirs(...)
        # pval_filename = os.path.join(BEST_HYPERPARAMETERS_SET_RESULTS_SUBDIR, f'p_value_comparison_{PAIN_TYPE}.txt')
        
        # with open(pval_filename, 'w') as f:
            # f.write(f"--- P-Value Comparison ---\nPain Type: {PAIN_TYPE}\nT-statistic: {t_stat}\nP-value: {p_val}\n")
        # print(f"P-value ({p_val:.5e}) saved to: {pval_filename}")

    labels = [
        f"High\n(>{percentTierHigh})",
        f"Low Clean\n(<={percentTierLow})",
        f"Low Dirty\n(<={percentTierLow})",
        "Others",
    ]

    # Plotting
    plt.figure(figsize=(20, 8))
    plt.boxplot(data_groups, labels=labels, patch_artist=True, whis=[0, 100])
    plt.title(f"Normalized Risk Prediction by Pain Context ({PAIN_TYPE})")

    if SAVE_RISK_BY_CATEGORY_DONT_PLOT:
        figures_path = Path(figures_dir)
        figures_path.mkdir(parents=True, exist_ok=True)
        plt.savefig(
            figures_path / f"categories_{PAIN_TYPE}.png",
            dpi=300,
            bbox_inches="tight",
        )
    else:
        plt.show()

def difference_in_means(x, y):
    return np.mean(x) - np.mean(y)

def get_roc_auc(results, PAIN_TYPE, nbDaysPriors=5, percentTierHigh=0.95, percentTierLow=0.90):
    
    data_groups, _ = _prepare_categorized_data(results, PAIN_TYPE, nbDaysPriors, percentTierHigh, percentTierLow)
    
    group_high      = np.array(data_groups[0])
    group_low_clean = np.array(data_groups[1])
    
    n_high = len(group_high)
    n_low = len(group_low_clean)

    if n_high > 0 and n_low > 0:
            
        # ROC-AUC
        # Mann-Whitney U test gives us the U statistic and a non-parametric p-value
        U_stat, p_val_roc = stats.mannwhitneyu(group_high, group_low_clean, alternative='two-sided')
        # ROC-AUC is the U statistic divided by the product of the sample sizes
        roc_auc = U_stat / (n_high * n_low)
        return {
            'top': np.mean(group_high), 'nb_top': n_high, 'std_top': np.std(group_high), 
            'bottom': np.mean(group_low_clean), 'nb_bottom': n_low, 
            'corr_coeff': U_stat, 'p_val_corr_coeff': p_val_roc, 'custom_score': roc_auc
        }
    
    else:
        return {
            'top': np.mean(group_high), 'nb_top': len(group_high), 'std_top': np.std(group_high), 
            'bottom': np.mean(group_low_clean), 'nb_bottom': len(group_low_clean), 
            'corr_coeff': -10000, 'p_val_corr_coeff': -10000, 'custom_score': -10000
        }
 