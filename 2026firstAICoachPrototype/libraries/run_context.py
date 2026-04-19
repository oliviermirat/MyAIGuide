from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class RunPaths:
    """
    Simple container for run-specific directories.

    ``output_dir`` is results/<run>/hyperparametersGridSearchResults (CSVs, JSON, summaryResults.xlsx).
    ``figures_dir`` is results/<run>/bestHyperparametersSetResults (plots, traffic-light xlsx).
    """
    base_dir: Path
    output_dir: Path
    figures_dir: Path


RESULTS_ROOT = Path("results")

# Subdirectory names under results/<run_name>/
HYPERPARAMETERS_GRID_SEARCH_RESULTS_SUBDIR = "hyperparametersGridSearchResults"
BEST_HYPERPARAMETERS_SET_RESULTS_SUBDIR = "bestHyperparametersSetResults"

# Hyperparameter grid summary (ranked combinations + test metrics) in output_dir
SUMMARY_RESULTS_XLSX = "summaryResults.xlsx"


def create_run_paths(run_name: Optional[str] = None) -> RunPaths:
    """
    Create (if needed) and return the run-specific directories.

    All run outputs live under results/<run_name>/ (e.g. results/baseline/).
    If run_name is None or empty, uses results/default.
    """
    subdir = run_name if run_name else "default"
    base = RESULTS_ROOT / subdir

    output_dir = base / HYPERPARAMETERS_GRID_SEARCH_RESULTS_SUBDIR
    figures_dir = base / BEST_HYPERPARAMETERS_SET_RESULTS_SUBDIR

    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    return RunPaths(base_dir=base, output_dir=output_dir, figures_dir=figures_dir)

