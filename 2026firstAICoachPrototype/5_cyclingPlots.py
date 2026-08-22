import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def create_combined_publication_plot():
    # 1. Load the data
    file_path = "dataMay2023andLater_2026firstAIPrototype_truncated.pkl"
    d = pd.read_pickle(file_path)

    # 2. Apply 60-day rolling filter (mean) to the variables
    # min_periods=1 ensures we get a rolling average for the first 59 days as well
    pain_rolling = d['kneePain'].rolling(window=60, min_periods=1).mean()
    cal_rolling = d['cyclingCalories'].rolling(window=60, min_periods=1).mean()
    bpm_rolling = d['numberOfHeartBeatsAbove110_lowerBodyActivity_cycling'].rolling(window=60, min_periods=1).mean()
    
    # Create the X-axis (day number starting from 0)
    day_numbers = np.arange(len(d))

    # 3. Configure publication-ready aesthetics
    plt.rcParams.update({
        'font.size': 12,
        'font.family': 'sans-serif',
        'axes.linewidth': 1.2,
        'figure.figsize': (12, 7),
        'figure.dpi': 300
    })

    # 4. Create the main figure and first axis
    fig, ax1 = plt.subplots()

    # Create two additional y-axes that share the same x-axis
    ax2 = ax1.twinx()
    ax3 = ax1.twinx()

    # Offset the right spine of ax3 so it doesn't overlap with ax2
    ax3.spines['right'].set_position(('outward', 70))
    
    # Make sure we don't draw overlapping grid lines
    ax1.grid(True, linestyle='--', alpha=0.5)

    # 5. Plot Variable 1: Knee pain (RED) on the primary y-axis (left)
    color1 = 'red'
    line1, = ax1.plot(day_numbers, pain_rolling, color=color1, linewidth=2, label='Knee pain')
    ax1.set_xlabel('Day Number', fontweight='bold')
    ax1.set_ylabel('Knee pain', color=color1, fontweight='bold')
    ax1.tick_params(axis='y', colors=color1)

    # 6. Plot Variable 2: Cycling calories on the secondary y-axis (first right)
    color2 = '#1f77b4' # Matplotlib default blue
    line2, = ax2.plot(day_numbers, cal_rolling, color=color2, linewidth=2, label='Cycling calories')
    ax2.set_ylabel('Cycling calories', color=color2, fontweight='bold')
    ax2.tick_params(axis='y', colors=color2)

    # 7. Plot Variable 3: Heart Beats on the tertiary y-axis (second right, offset)
    color3 = '#2ca02c' # Matplotlib default green
    line3, = ax3.plot(day_numbers, bpm_rolling, color=color3, linewidth=2, label='Cycling related cumulative bpm > 110')
    ax3.set_ylabel('Cycling related cumulative bpm > 110', color=color3, fontweight='bold')
    ax3.tick_params(axis='y', colors=color3)

    # 8. Consolidate the legend (Moved to top right)
    lines = [line1, line2, line3]
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper right', framealpha=0.9)

    # Adjust layout so the extra offset y-axis doesn't get clipped
    fig.tight_layout()

    # 9. Save outputs
    png_filename = "results/combinedAnalysis/cycling_pain_analysis.png"
    pdf_filename = "results/combinedAnalysis/cycling_pain_analysis.pdf"
    
    # Ensure the target directory exists before saving
    os.makedirs(os.path.dirname(png_filename), exist_ok=True)
    
    plt.savefig(png_filename, bbox_inches='tight')
    plt.savefig(pdf_filename, format='pdf', bbox_inches='tight')
    
    print(f"Successfully saved combined plots as '{png_filename}' and '{pdf_filename}'.")

    # Display the plot 
    plt.show()

if __name__ == "__main__":
    create_combined_publication_plot()