import pandas as pd
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from sklearn.preprocessing import MinMaxScaler
import os

# --- Configuration ---
FILE_NAME = './dataMay2023andLater_2026firstAIPrototype.pkl'

class TimeSeriesVisualizer:
    def __init__(self, root, dataframe):
        self.root = root
        self.root.title("Dynamic Time Series Visualizer")
        self.root.geometry("1200x800")
        
        self.df = dataframe
        self.scaled_df = self.preprocess_data(dataframe)
        
        # Dictionary to store checkbutton states (Variable Name -> BooleanVar)
        self.check_vars = {}
        
        # --- Layout ---
        # Split into two sides: Control Panel (Left) and Plot (Right)
        self.paned_window = ttk.PanedWindow(root, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)
        
        self.control_frame = ttk.Frame(self.paned_window, width=280, padding="10")
        self.plot_frame = ttk.Frame(self.paned_window, padding="10")
        
        self.paned_window.add(self.control_frame, weight=1)
        self.paned_window.add(self.plot_frame, weight=4)
        
        # --- Control Section ---
        
        # 1. Rolling Controls (Mean & Scaler)
        self.create_rolling_controls()
        
        ttk.Separator(self.control_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # 2. Variable Selection List
        ttk.Label(self.control_frame, text="Select Variables:", font=("Arial", 12, "bold")).pack(pady=5)
        
        # Canvas for scrolling
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
        
        # Add Checkboxes
        self.create_checkboxes()
        
        # Select All / Deselect All Buttons
        btn_frame = ttk.Frame(self.control_frame)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side="left", expand=True, padx=2)
        
        # --- Plot Section ---
        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        
        # 1. Create Canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # 2. Add Navigation Toolbar (Zoom, Pan, Save)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        self.toolbar.update()
        
        # Initial Plot
        self.update_plot()

    def preprocess_data(self, df):
        """
        Scales all numeric columns to range [0, 1] globally.
        Used when Rolling Scaler is disabled.
        """
        # Select only numeric columns
        numeric_df = df.select_dtypes(include=['float64', 'int64', 'float32', 'int32'])
        
        if numeric_df.empty:
            return pd.DataFrame()

        # Handle NaNs
        numeric_df = numeric_df.ffill().bfill()
        
        # Scale Data
        scaler = MinMaxScaler()
        scaled_values = scaler.fit_transform(numeric_df)
        
        scaled_df = pd.DataFrame(scaled_values, columns=numeric_df.columns, index=df.index)
        return scaled_df

    def create_rolling_controls(self):
        """Creates the checkboxes and entries for rolling mean and rolling scaler."""
        frame = ttk.LabelFrame(self.control_frame, text="Processing Options", padding=10)
        frame.pack(fill="x", pady=5)
        
        # --- 1. Rolling Mean Control ---
        self.rolling_enabled = tk.BooleanVar(value=False)
        chk_mean = ttk.Checkbutton(
            frame, 
            text="Apply Rolling Mean", 
            variable=self.rolling_enabled, 
            command=self.update_plot
        )
        chk_mean.pack(anchor="w", pady=(0, 5))
        
        mean_window_frame = ttk.Frame(frame)
        mean_window_frame.pack(fill="x")
        
        ttk.Label(mean_window_frame, text="Mean Win:").pack(side="left")
        
        self.rolling_window = tk.StringVar(value="10")
        self.window_entry = ttk.Entry(mean_window_frame, textvariable=self.rolling_window, width=8)
        self.window_entry.pack(side="left", padx=5)
        
        self.window_entry.bind('<Return>', self.update_plot)
        self.window_entry.bind('<FocusOut>', self.update_plot)

        # --- Separator ---
        ttk.Separator(frame, orient='horizontal').pack(fill='x', pady=10)

        # --- 2. Rolling Scaler Control ---
        self.rolling_scaler_enabled = tk.BooleanVar(value=False)
        chk_scaler = ttk.Checkbutton(
            frame, 
            text="Apply Rolling Scaler", 
            variable=self.rolling_scaler_enabled, 
            command=self.update_plot
        )
        chk_scaler.pack(anchor="w", pady=(0, 5))
        
        scaler_window_frame = ttk.Frame(frame)
        scaler_window_frame.pack(fill="x")
        
        ttk.Label(scaler_window_frame, text="Scale Win:").pack(side="left")
        
        self.scaler_window = tk.StringVar(value="30")
        self.scaler_window_entry = ttk.Entry(scaler_window_frame, textvariable=self.scaler_window, width=8)
        self.scaler_window_entry.pack(side="left", padx=5)
        
        self.scaler_window_entry.bind('<Return>', self.update_plot)
        self.scaler_window_entry.bind('<FocusOut>', self.update_plot)

    def create_checkboxes(self):
        columns = sorted(self.scaled_df.columns)
        for col in columns:
            var = tk.BooleanVar(value=False)
            chk = ttk.Checkbutton(self.scrollable_frame, text=col, variable=var, command=self.update_plot)
            chk.pack(anchor="w", pady=2)
            self.check_vars[col] = var

    def clear_all(self):
        for var in self.check_vars.values():
            var.set(False)
        self.update_plot()

    def update_plot(self, event=None):
        self.ax.clear()
        
        # Identify selected variables
        selected_cols = [col for col, var in self.check_vars.items() if var.get()]
        
        if not selected_cols:
            self.ax.text(0.5, 0.5, "Select variables to plot", 
                         transform=self.ax.transAxes, ha="center", va="center")
            self.canvas.draw()
            return

        title_parts = []

        # --- Step 1: Determine Base Data (Global Scaled vs Rolling Scaled) ---
        if self.rolling_scaler_enabled.get():
            # Use RAW data for rolling scaling calculation
            raw_data = self.df[selected_cols].copy()
            scaler_win_val = self.scaler_window.get()
            
            try:
                # Assuming integer window for simplicity
                s_window = int(scaler_win_val)
                
                # Calculate Rolling Min and Max
                roll_min = raw_data.rolling(window=s_window).min()
                roll_max = raw_data.rolling(window=s_window).max()
                
                # Apply MinMax Formula: (x - min) / (max - min)
                denominator = roll_max - roll_min
                # Replace 0s in denominator to avoid div by zero errors
                denominator = denominator.replace(0, 1e-9) 
                
                plot_data = (raw_data - roll_min) / denominator
                title_parts.append(f"Rolling Scaler ({s_window})")
                
            except ValueError:
                 # Fallback if invalid window input
                plot_data = self.scaled_df[selected_cols].copy()
                title_parts.append("Scaler Error")
        else:
            # Use pre-calculated global scaled data
            plot_data = self.scaled_df[selected_cols].copy()
            title_parts.append("Global Scaler")

        # --- Step 2: Apply Rolling Mean (Optional Smoothing) ---
        if self.rolling_enabled.get():
            window_val = self.rolling_window.get()
            try:
                # Try integer (number of rows)
                window_size = int(window_val)
                plot_data = plot_data.rolling(window=window_size).mean()
                title_parts.append(f"Smoothed ({window_size})")
            except ValueError:
                # Try time offset (e.g. '7D')
                try:
                    plot_data = plot_data.rolling(window=window_val).mean()
                    title_parts.append(f"Smoothed ({window_val})")
                except Exception:
                    pass

        # Set Title
        self.ax.set_title(" + ".join(title_parts))

        # Plot
        for col in plot_data.columns:
            self.ax.plot(plot_data.index, plot_data[col], label=col)
        
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Normalized Value (0-1)")
        
        # Smart Legend
        if len(selected_cols) > 10:
             self.ax.legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='x-small')
        else:
             self.ax.legend(loc='best', fontsize='small')
            
        self.fig.autofmt_xdate()
        self.fig.tight_layout()
        self.canvas.draw()

def main():
    # 1. Load Data
    if not os.path.exists(FILE_NAME):
        print(f"Error: File '{FILE_NAME}' not found.")
        return

    try:
        df = pd.read_pickle(FILE_NAME)
        print("Data loaded successfully.")
    except Exception as e:
        print(f"Error loading pickle file: {e}")
        return

    # 2. Fix Index
    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except:
            potential_time = [c for c in df.columns if 'date' in c.lower() or 'time' in c.lower()]
            if potential_time:
                df.set_index(potential_time[0], inplace=True)
                df.index = pd.to_datetime(df.index)
    
    # 3. Launch GUI
    root = tk.Tk()
    app = TimeSeriesVisualizer(root, df)
    root.mainloop()

if __name__ == "__main__":
    main()