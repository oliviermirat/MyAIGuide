import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from sklearn.preprocessing import MinMaxScaler
import os

# --- Configuration ---
FILE_NAME = 'dataMay2023andLater_2026firstAIPrototype.pkl'

class TimeSeriesVisualizer:
    def __init__(self, root, dataframe):
        self.root = root
        self.root.title("Dynamic Time Series Visualizer")
        self.root.geometry("1200x800")
        
        # Load raw data only. Transformations happen dynamically on selection.
        self.raw_numeric_df = self.prepare_data(dataframe)
        
        # Dictionary to store checkbutton states (Variable Name -> BooleanVar)
        self.check_vars = {}
        
        # --- Layout ---
        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        self.control_frame = ttk.Frame(self.paned_window, width=300, padding="10")
        self.plot_frame = ttk.Frame(self.paned_window, padding="10")
        
        self.paned_window.add(self.control_frame, weight=1)
        self.paned_window.add(self.plot_frame, weight=4)
        
        # --- Control Section ---
        self.create_processing_controls()
        
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill='x', pady=10)
        
        ttk.Label(self.control_frame, text="Select Variables:", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Canvas for scrolling checkboxes
        self.canvas_scroll = tk.Canvas(self.control_frame)
        self.scrollbar = ttk.Scrollbar(self.control_frame, orient="vertical", command=self.canvas_scroll.yview)
        self.scrollable_frame = ttk.Frame(self.canvas_scroll)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas_scroll.configure(scrollregion=self.canvas_scroll.bbox("all"))
        )
        
        self.canvas_scroll.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas_scroll.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas_scroll.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        self.create_checkboxes()
        
        # Clear All Button
        btn_frame = ttk.Frame(self.control_frame)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side="left", expand=True, padx=2)
        
        # --- Plot Section ---
        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        
        # Initial Plot
        self.update_plot()

    def prepare_data(self, df):
        """Cleans and returns raw numeric data."""
        numeric_df = df.select_dtypes(include=['float64', 'int64', 'float32', 'int32'])
        if not numeric_df.empty:
            numeric_df = numeric_df.ffill().bfill()
        return numeric_df

    def create_processing_controls(self):
        """Creates the controls for rolling mean, scaling, and operation order."""
        frame = ttk.LabelFrame(self.control_frame, text="Processing Options", padding=10)
        frame.pack(fill="x", pady=5)
        
        # 1. Rolling Mean Toggle
        self.rolling_enabled = tk.BooleanVar(value=True)
        chk_rolling = ttk.Checkbutton(
            frame, text="Apply Rolling Mean", variable=self.rolling_enabled, command=self.update_plot
        )
        chk_rolling.pack(anchor="w", pady=(0, 5))
        
        # 1a. Rolling Window Size
        window_frame = ttk.Frame(frame)
        window_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(window_frame, text="Window:").pack(side="left")
        self.rolling_window = tk.StringVar(value="35")
        self.window_entry = ttk.Entry(window_frame, textvariable=self.rolling_window, width=8)
        self.window_entry.pack(side="left", padx=5)
        self.window_entry.bind('<Return>', self.update_plot)
        self.window_entry.bind('<FocusOut>', self.update_plot)
        ttk.Label(window_frame, text="(rows)", font=("Arial", 8)).pack(side="left")

        # 2. Scaling Toggle
        self.scale_enabled = tk.BooleanVar(value=True)
        chk_scale = ttk.Checkbutton(
            frame, text="Scale variables (0 to 1)", variable=self.scale_enabled, command=self.update_plot
        )
        chk_scale.pack(anchor="w", pady=(5, 5))
        
        # 3. Order of Operations Dropdown
        ttk.Label(frame, text="Operation Order:", font=("Arial", 9, "italic")).pack(anchor="w")
        self.order_var = tk.StringVar(value="Scale first, then Roll")
        order_combo = ttk.Combobox(
            frame, 
            textvariable=self.order_var, 
            values=["Scale first, then Roll", "Roll first, then Scale"], 
            state="readonly"
        )
        order_combo.pack(fill="x", pady=(0, 5))
        order_combo.bind("<<ComboboxSelected>>", self.update_plot)

    def create_checkboxes(self):
        columns = sorted(self.raw_numeric_df.columns)
        for col in columns:
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(self.scrollable_frame, text=col, variable=var, command=self.update_plot)
            chk.pack(anchor="w", pady=2)
            self.check_vars[col] = var

    def clear_all(self):
        for var in self.check_vars.values():
            var.set(False)
        self.update_plot()

    def _apply_scaling(self, df):
        """Scales columns ignoring NaNs (which can be introduced by rolling means)."""
        scaler = MinMaxScaler()
        scaled_df = df.copy()
        for col in scaled_df.columns:
            valid_data = scaled_df[col].dropna()
            if not valid_data.empty:
                scaled_vals = scaler.fit_transform(valid_data.values.reshape(-1, 1))
                scaled_df.loc[valid_data.index, col] = scaled_vals.flatten()
        return scaled_df

    def _apply_rolling(self, df):
        """Applies a rolling mean based on the entry field."""
        window_val = self.rolling_window.get()
        try:
            window_size = int(window_val)
            return df.rolling(window=window_size).mean()
        except ValueError:
            return df  # Fallback if input is entirely invalid

    def update_plot(self, event=None):
        self.ax.clear()
        
        # Identify selected variables
        selected_cols = [col for col, var in self.check_vars.items() if var.get()]
        
        if not selected_cols:
            self.ax.text(0.5, 0.5, "Select variables to plot", 
                         transform=self.ax.transAxes, ha="center", va="center")
            self.canvas.draw()
            return

        # Start with fresh raw data for selected columns
        plot_data = self.raw_numeric_df[selected_cols].copy()
        
        # Get toggle states
        do_scale = self.scale_enabled.get()
        do_roll = self.rolling_enabled.get()
        order = self.order_var.get()
        
        # Apply Operations dynamically based on selected order
        if order == "Scale first, then Roll":
            if do_scale: plot_data = self._apply_scaling(plot_data)
            if do_roll:  plot_data = self._apply_rolling(plot_data)
        else: # "Roll first, then Scale"
            if do_roll:  plot_data = self._apply_rolling(plot_data)
            if do_scale: plot_data = self._apply_scaling(plot_data)

        # Generate Title String
        title_parts = []
        if do_scale: title_parts.append("Scaled")
        if do_roll:  title_parts.append(f"Rolling (w={self.rolling_window.get()})")
        if not title_parts: title_parts.append("Raw")
        
        self.ax.set_title(f"{' + '.join(title_parts)} Time Series Comparison")

        # Plot data
        for col in plot_data.columns:
            self.ax.plot(plot_data.index, plot_data[col], label=col)
        
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Scaled Value (0-1)" if do_scale else "Original Value")
        
        # Smart Legend
        if len(selected_cols) > 10:
             self.ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='x-small')
        else:
             self.ax.legend(loc='best', fontsize='small')
            
        self.fig.autofmt_xdate()
        self.fig.tight_layout()
        self.canvas.draw()

def main():
    if not os.path.exists(FILE_NAME):
        print(f"Error: File '{FILE_NAME}' not found.")
        return

    try:
        df = pd.read_pickle(FILE_NAME)
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading pickle file: {e}")
        return

    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except:
            potential_time = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()]
            if potential_time:
                df.set_index(potential_time[0], inplace=True)
                df.index = pd.to_datetime(df.index)
    
    root = tk.Tk()
    app = TimeSeriesVisualizer(root, df)
    root.mainloop()

if __name__ == "__main__":
    main()