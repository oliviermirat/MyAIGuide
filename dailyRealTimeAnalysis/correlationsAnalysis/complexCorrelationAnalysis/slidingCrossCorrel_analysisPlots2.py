import pickle
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.signal import argrelextrema
import scipy.stats as stats
import pandas as pd
from numpy.linalg import inv
import xlsxwriter
import seaborn as sns

globalMeasureCalculation = 'max_minus_min'
# globalMeasureCalculation = 'only_max'
# globalMeasureCalculation = 'peak'

useNewOrOldData = 'old'

# Load previously saved cross-correlation data
with open("crosscorrelation_plots_" + useNewOrOldData + "/crosscorrelation_data.pkl", "rb") as f:
    data = pickle.load(f)

# Helper to compute local and global measures
def compute_measures(lags, corrs, integral_half_window=30):
    lags = np.array(lags)
    corrs = np.array(corrs)
    zero_idx = np.where(lags == 0)[0][0] if 0 in lags else np.argmin(np.abs(lags))

    local_max_idx = argrelextrema(corrs, np.greater)[0]
    local_min_idx = argrelextrema(corrs, np.less)[0]

    left_extremum_idx = next((i for i in reversed(range(zero_idx)) if i in local_max_idx or i in local_min_idx), None)
    right_extremum_idx = next((i for i in range(zero_idx, len(lags)) if i in local_max_idx or i in local_min_idx), None)

    local_measure = 0
    if left_extremum_idx is not None and right_extremum_idx is not None:
        left_val = corrs[left_extremum_idx]
        right_val = corrs[right_extremum_idx]
        denom = right_extremum_idx - left_extremum_idx
        if denom != 0:
            if left_val > right_val:
                local_measure = (zero_idx - right_extremum_idx) / denom
            elif left_val < right_val:
                local_measure = (zero_idx - left_extremum_idx) / denom

    neg_integral = np.trapz(corrs[zero_idx - integral_half_window:zero_idx], lags[zero_idx - integral_half_window:zero_idx])
    pos_integral = np.trapz(corrs[zero_idx + 1:zero_idx + 1 + integral_half_window], lags[zero_idx + 1:zero_idx + 1 + integral_half_window])
    
    if globalMeasureCalculation == 'max_minus_min':
        global_measure = pos_integral - neg_integral
    elif globalMeasureCalculation == 'only_max':
        global_measure = pos_integral
    elif globalMeasureCalculation == 'peak':
        positive_mask = lags > 0
        if not np.any(positive_mask):
            global_measure = np.nan
        else:
            global_measure = np.max(corrs[positive_mask])

    return local_measure, global_measure

# Organize results
results_by_pain = {}
for entry in data:
    pain = entry['pain']
    var = entry['var']
    lags = entry['lags']
    corrs = entry['corrs']
    integral = entry.get('integral', 1)

    local, global_ = compute_measures(lags, corrs)

    if pain not in results_by_pain:
        results_by_pain[pain] = []
    results_by_pain[pain].append({
        'var': var,
        'local_measure': local,
        'global_measure': global_,
        'integral': integral
    })

all_pains = sorted(list(results_by_pain.keys()))


##################

startDate = '2016-01-01'
endDate = '2022-03-26'
rolling_window = 7

from scipy.stats import pearsonr
import statsmodels.api as sm

print("🔍 Running partial correlation filtering...")

def compute_partial_corr(x, y, controls):
    """Computes partial correlation between x and y, controlling for controls."""
    if controls.shape[1] == 0:
        return pearsonr(x, y)[0]  # no controls
    
    x_resid = sm.OLS(x, sm.add_constant(controls)).fit().resid
    y_resid = sm.OLS(y, sm.add_constant(controls)).fit().resid
    return pearsonr(x_resid, y_resid)[0]  # residual correlation

filtered_results_by_pain = {}

# Load normalized data used during sliding window phase
with open("crosscorrelation_plots_" + useNewOrOldData + "/crosscorrelation_data.pkl", "rb") as f:
    data_entries = pickle.load(f)

# Build a global DataFrame to compute raw correlations
# Re-use raw_window_df from one of the entries
first_entry = data_entries[0]
raw_data_sample_path = os.path.join("crosscorrelation_plots_" + useNewOrOldData, first_entry['pain'], f"{first_entry['pain']}_{first_entry['start'].date()}_{first_entry['end'].date()}.png")
raw_data_path = raw_data_sample_path.replace('.png', '.pkl')  # assuming it's saved (optional)
# Instead, let's just reload the full raw window data
with open("../data/preprocessed/preprocessedMostImportantDataParticipant1_12_29_2024.txt", "rb") as f:
    full_data = pickle.load(f)

# Filter time
full_data = full_data[(full_data.index >= startDate) & (full_data.index <= endDate)].rolling(rolling_window).mean().dropna()

threshold_r = 0.2
partial_r_threshold = 0.01  # if abs(partial r) < 0.1, discard


for pain, entries in results_by_pain.items():
    filtered = []
    for entry in entries:
        var = entry['var']
        if var not in full_data.columns or pain not in full_data.columns:
            continue

        x = full_data[var]
        y = full_data[pain]

        valid_xy = x.notna() & y.notna()
        if valid_xy.sum() < 5:
            continue  # skip if insufficient data

        x = x[valid_xy]
        y = y[valid_xy]

        # Find other variables highly correlated with var
        control_vars = []
        for other_var in full_data.columns:
            if other_var in (var, pain):
                continue
            x1 = full_data[other_var]
            x2 = full_data[var]
            valid = x1.notna() & x2.notna()
            if valid.sum() < 2:
                continue
            r, _ = pearsonr(x1[valid], x2[valid])
            if abs(r) >= threshold_r:
                control_vars.append(other_var)

        controls = full_data[control_vars].loc[valid_xy].values if control_vars else np.empty((len(x), 0))
        partial_r = compute_partial_corr(x.values, y.values, controls)

        if abs(partial_r) >= partial_r_threshold:
            filtered.append(entry)
        else:
            print(f"🧹 Filtered out {var} (pain={pain}) due to weak partial correlation ({partial_r:.3f})")

    filtered_results_by_pain[pain] = filtered

results_by_pain = filtered_results_by_pain

################


# Compute global y-axis (global_measure) limit
all_global_measures = [r['global_measure'] for plist in results_by_pain.values() for r in plist]

if not all_global_measures:
    print("❌ No variables passed partial correlation filtering. Exiting early.")
    exit()

max_abs_global = max(abs(min(all_global_measures)), abs(max(all_global_measures)))

# Group definitions
if useNewOrOldData == 'new':
    group_definitions = {
        'Driving': ['timeSpentDriving', 'timeSpentRidingCar', 'timeInCar'],
        'ComputerUse': ['numberOfComputerClicksAndKeyStrokes', 'timeOnComputer'],
        'Climbing': ['climbingDenivelation', 'climbingMaxEffortIntensity', 'garminClimbingActiveCalories'],
        'LowerBodyActivity': ['numberOfHeartBeatsBetween70and110_lowerBodyActivity', 'numberOfSteps'],
        'UpperBodyActivity': ['swimAndSurfStrokes', 'numberOfHeartBeatsAbove110_upperBodyActivity'],
        'CardioGeneral': [
            'numberOfHeartBeatsBetween70and110', 'numberOfHeartBeatsBetween70and110_upperBodyActivity',
            'numberOfHeartBeatsAbove110', 'numberOfHeartBeatsAbove110_lowerBodyActivity',
            'garminKneeRelatedActiveCalories', 'computerAndCarTime'
        ],
        'Cycling': [
            'numberOfHeartBeatsBetween70and110_lowerBodyActivity_cycling',
            'numberOfHeartBeatsAbove110_lowerBodyActivity_cycling', 'cyclingCalories'
        ],
        'Suitcase': ['movingBadSuitcase']
    }
else:
    group_definitions = {
        'Walking': ['tracker_mean_distance', 'tracker_mean_denivelation'],
        'ComputerUse': ['whatPulseT_corrected', 'manicTimeDelta_corrected'],
        'Climbing': ['climbingDenivelation', 'climbingMaxEffortIntensity', 'climbingMeanEffortIntensity', 'climbing', 'viaFerrata'],
        'Swimming': ['swimmingKm', 'surfing', 'swimming'],
        'Cycling': ['cycling'],
        'Driving': ['timeDrivingCar', 'scooterRiding']
    }

# Plot results by group
for pain, results in results_by_pain.items():
    for group_name, group_vars in group_definitions.items():
        grouped = [r for r in results if r['var'] in group_vars]
        if not grouped:
            continue

        colors = plt.colormaps['tab10'](np.linspace(0, 1, len(group_vars)))
        var_color_map = {v: colors[i] for i, v in enumerate(group_vars)}

        plt.figure(figsize=(10, 6))
        for var_name in group_vars:
            points = [r for r in grouped if r['var'] == var_name]
            if not points:
                continue

            x_vals = [r['local_measure'] for r in points]
            y_vals = [r['global_measure'] for r in points]
            integrals = [r['integral'] for r in points]

            min_i, max_i = min(integrals), max(integrals)
            range_i = max_i - min_i if max_i > min_i else 1
            sizes = [10 + (val - min_i) / range_i * (100 - 10) for val in integrals]

            plt.scatter(x_vals, y_vals, s=sizes, label=var_name, color=var_color_map[var_name], alpha=0.7)

        plt.title(f"2D Summary: {pain} - {group_name}")
        plt.xlabel("Local Measure")
        plt.xlim(-1, 1)
        plt.ylabel("Global Measure")
        plt.grid(True)
        if False:
            ymin, ymax = plt.ylim()
            max_abs_y = max(abs(ymin), abs(ymax))
            plt.ylim(-max_abs_y, max_abs_y)
        else:
            plt.ylim(-max_abs_global, max_abs_global)
        plt.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), borderaxespad=0.)
        plt.tight_layout()
        folder = f"crosscorrelation_plots_" + useNewOrOldData + f"/{pain}_Grouped2DPlots"
        os.makedirs(folder, exist_ok=True)
        plt.savefig(os.path.join(folder, f"summary_{pain}_{group_name}.png"), bbox_inches='tight')
        plt.close()

print("✅ Analysis complete and scaled plots saved (per-variable scaling).")


def hotelling_t2_test(data, mu_0=None):
    data = np.asarray(data)
    n, p = data.shape
    if mu_0 is None:
        mu_0 = np.zeros(p)
    mu_0 = np.asarray(mu_0)

    sample_mean = np.mean(data, axis=0)
    cov_matrix = np.cov(data, rowvar=False)
    inv_cov = inv(cov_matrix)

    diff = sample_mean - mu_0
    T_squared = n * diff @ inv_cov @ diff.T
    F_stat = (n - p) * T_squared / (p * (n - 1))
    p_value = 1 - stats.f.cdf(F_stat, p, n - p)

    return T_squared, F_stat, p_value


def caculateStatistics(pain, var, x_vals, y_vals, integrals):
    # Convert to numpy arrays
    x_vals = np.array(x_vals)
    y_vals = np.array(y_vals)
    integrals = np.array(integrals)

    # Remove invalid entries
    valid_mask = np.isfinite(x_vals) & np.isfinite(y_vals) & np.isfinite(integrals)
    x_vals = x_vals[valid_mask]
    y_vals = y_vals[valid_mask]
    integrals = integrals[valid_mask]

    # Skip if no valid data remains
    if len(x_vals) == 0:
        return

    # Weighted standard deviation
    def weighted_std(values, weights, mean_val):
        return np.sqrt(np.average((values - mean_val)**2, weights=weights))
    
    if False:
        mean_x = np.average(x_vals, weights=integrals)
        std_x = weighted_std(np.array(x_vals), np.array(integrals), mean_x)
    else:
        # Circular mean of x_vals
        angles = np.pi * x_vals  # scale [-1, 1] to [-π, π]
        sin_sum = np.average(np.sin(angles), weights=integrals)
        cos_sum = np.average(np.cos(angles), weights=integrals)

        # Mean angle and convert back to [-1, 1]
        mean_angle = np.arctan2(sin_sum, cos_sum)
        mean_x = mean_angle / np.pi

        # Mean resultant length R
        R = np.sqrt(sin_sum**2 + cos_sum**2)

        # Circular standard deviation (in radians), normalized back to [-1, 1] scale
        if R > 0:  # avoid log(0)
            circ_std = np.sqrt(-2 * np.log(R)) / np.pi
        else:
            circ_std = np.nan  # or assign large value to indicate full dispersion

        std_x = circ_std
    
    mean_y = np.average(y_vals, weights=integrals)
    std_y = weighted_std(np.array(y_vals), np.array(integrals), mean_y)

    # Mahalanobis distance from (0, 0)
    mahalanobis_dist = np.sqrt((mean_x / std_x) ** 2 + (mean_y / std_y) ** 2)
    p_value_mahalanobis = 1 - stats.chi2.cdf(mahalanobis_dist**2, df=2)
    
    if True:
        points = np.vstack((x_vals, y_vals)).T
        if points.shape[0] < 2 or points.shape[1] < 2:
            print("cannot calculate hotelling_t2_test for", pain, "and", var)
            p_value_hotelling_t2 = 1
        else:
            T_squared, F_stat, p_value_hotelling_t2 = hotelling_t2_test(points)

    # Instead of printing, store the results
    statistics_records.append({
        'Group': group_name,
        'Pain': pain,
        'Variable': var,
        'Weighted Mean X': mean_x,
        'Weighted Mean Y': mean_y,
        'Weighted Std X': std_x,
        'Weighted Std Y': std_y,
        'Mahalanobis Distance': mahalanobis_dist,
        'p_value_mahalanobis': p_value_mahalanobis,
        'p_value_hotelling_t2': p_value_hotelling_t2
    })


# === ADDITIONAL PLOTS: One figure per group, with three subplots (one per pain type) ===
print("📊 Generating additional group-wise 3-paneled plots...")

output_dir = "crosscorrelation_plots_" + useNewOrOldData + "/Grouped2Dplots"
os.makedirs(output_dir, exist_ok=True)
statistics_records = []

for group_name, group_vars in group_definitions.items():
    fig, axes = plt.subplots(1, 3, figsize=(18, 5), sharex=True, sharey=True)
    all_x, all_y = [], []
    legend_handles = {}
    
    for i, pain in enumerate(all_pains):
        ax = axes[i]
        points = [r for r in results_by_pain[pain] if r['var'] in group_vars]
        if not points:
            ax.set_title(f"{pain} (no data)")
            ax.axis('off')
            continue

        for var in group_vars:
            var_points = [r for r in points if r['var'] == var]
            if not var_points:
                continue

            x_vals = [r['local_measure'] for r in var_points]
            y_vals = [r['global_measure'] for r in var_points]
            integrals = [r['integral'] for r in var_points]
            
            caculateStatistics(pain, var, x_vals, y_vals, integrals)

            all_x.extend(x_vals)
            all_y.extend(y_vals)

            min_i, max_i = min(integrals), max(integrals)
            range_i = max_i - min_i if max_i > min_i else 1
            sizes = [10 + (val - min_i) / range_i * (100 - 10) for val in integrals]

            # Plot and store handle only once per variable
            if var not in legend_handles:
                sc = ax.scatter(x_vals, y_vals, s=sizes, alpha=0.7, label=var)
                legend_handles[var] = sc
            else:
                ax.scatter(x_vals, y_vals, s=sizes, alpha=0.7)

        ax.set_title(f"{pain}")
        ax.set_xlabel("Local Measure")
        ax.grid(True)

    # Set shared symmetric axis limits
    if all_x and all_y:
        max_abs_x = max(abs(min(all_x)), abs(max(all_x)))
        max_abs_y = max(abs(min(all_y)), abs(max(all_y)))
        for ax in axes:
            ax.set_xlim(-max_abs_x, max_abs_x)
            if False:
                ax.set_ylim(-max_abs_y, max_abs_y)
            else:
                ax.set_ylim(-max_abs_global, max_abs_global)

    axes[0].set_ylabel("Global Measure")
    fig.suptitle(f"Grouped 2D Summary for Group: {group_name}", fontsize=16)

    # Show deduplicated legend on the right
    fig.legend(legend_handles.values(), legend_handles.keys(),
               loc='center left', bbox_to_anchor=(1.02, 0.5), borderaxespad=0.)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig(os.path.join(output_dir, f"grouped_summary_{group_name}.png"), bbox_inches='tight')
    plt.close(fig)

print("✅ Group-wise summary plots with 3 subplots each have been saved (axes centered, clean legend).")

# Save statistics to Excel
df_stats = pd.DataFrame(statistics_records)
df_stats = df_stats.sort_values(by=['Pain', 'p_value_hotelling_t2'])
excel_path = os.path.join(output_dir, "groupwise_statistics.xlsx")
df_stats.to_excel(excel_path, index=False)
print(f"📄 Statistics saved to Excel at: {excel_path}")


# Significant results
# === Save significant results (p < 0.05) to a new Excel ===

significance_threshold = 0.05
significant_records = []

def collect_significant(stats_list):
    for record in stats_list:
        if (record['p_value_hotelling_t2'] <= significance_threshold) or (record['p_value_mahalanobis'] <= significance_threshold):
            significant_records.append({
                'Group': record['Group'],
                'Pain': record['Pain'],
                'Variable': record['Variable'],
                'Weighted Mean X': record['Weighted Mean X'],
                'Weighted Mean Y': record['Weighted Mean Y'],
                'Weighted Std X': record['Weighted Std X'],
                'Weighted Std Y': record['Weighted Std Y'],
                'Mahalanobis Distance': record['Mahalanobis Distance'],
                'p_value_hotelling_t2': record['p_value_hotelling_t2'],
                'p_value_mahalanobis': record['p_value_mahalanobis']
            })

collect_significant(statistics_records)
    
# Remove NaN or inf Mahalanobis distances
df_significant = pd.DataFrame(significant_records)
df_significant = df_significant.replace([np.inf, -np.inf], np.nan)
df_significant = df_significant.dropna(subset=['Mahalanobis Distance'])

# Sort the DataFrame
df_significant = df_significant.sort_values(by=['Pain', 'p_value_hotelling_t2'])
df_significant = df_significant.reset_index(drop=True)

# Create Excel file with formatting
signif_excel_path = os.path.join(output_dir, "significant_results_p_lt_0.05.xlsx")
with pd.ExcelWriter(signif_excel_path, engine='xlsxwriter') as writer:
    df_significant.to_excel(writer, index=False, sheet_name='Significant')

    workbook  = writer.book
    worksheet = writer.sheets['Significant']

    bold_format = workbook.add_format({'bold': True})

    # Find the column indices for convenience
    col_variable = df_significant.columns.get_loc('Variable')
    col_mean_x = df_significant.columns.get_loc('Weighted Mean X')
    col_mean_y = df_significant.columns.get_loc('Weighted Mean Y')

    # Apply bold formatting conditionally
    
    for row_idx, row in df_significant.iterrows():
        mean_x = row['Weighted Mean X']
        mean_y = row['Weighted Mean Y']
        if ((mean_x >= 0.2) or (mean_x <= -0.8)) and (mean_y > 0):
            worksheet.write(row_idx + 1, col_variable, row['Variable'], bold_format)

print(f"✅ Cleaned, sorted, and formatted significant results saved to: {signif_excel_path}")


### Final plot

# Load the Excel file
df = df_significant

# Set plot style
sns.set(style="whitegrid")

# Create a figure with 3 subplots, one for each type of pain
pain_types = df['Pain'].unique()
num_pains = len(pain_types)
fig, axes = plt.subplots(1, num_pains, figsize=(18, 6), sharex=False, sharey=True)

# Assign colors to each group
groups = df['Group'].unique()
palette = sns.color_palette("hsv", len(groups))
group_color_map = dict(zip(groups, palette))

# Determine symmetric y-axis limits
y_min = df['Weighted Mean Y'].min()
y_max = df['Weighted Mean Y'].max()
y_abs_max = max(abs(y_min), abs(y_max))

# Plot each pain type
for ax, pain in zip(axes, pain_types):
    subset = df[df['Pain'] == pain]
    for _, row in subset.iterrows():
        x = row['Weighted Mean X']
        y = row['Weighted Mean Y']
        label = row['Variable']
        color = group_color_map[row['Group']]
        ax.scatter(x, y, color=color, label=row['Group'], s=50)
        ax.text(x + 0.01, y + 0.01, label, fontsize=8)

    ax.set_title(f'{pain}')
    ax.set_xlabel('Weighted Mean X')
    ax.set_ylabel('Weighted Mean Y')
    ax.set_ylim(-y_abs_max, y_abs_max)
    ax.set_xlim(-1, 1)
    
    # Create legend without duplicates
    handles, labels = ax.get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), fontsize='small', loc='best')

plt.tight_layout()
output_path = os.path.join(output_dir, "pain_type_subplots_symmetric_y.png")
plt.savefig(output_path)
plt.close()
