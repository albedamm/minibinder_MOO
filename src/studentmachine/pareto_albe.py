import pandas as pd
import torch
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib
from botorch.utils.multi_objective.pareto import is_non_dominated
import os

class ParetoAnalyzer:
    def __init__(self, input_file, output_dir, pareto_output_file, top_n=20):
        """
        Initialize the Pareto Analyzer with the input file, output directory, and number of top Pareto points to highlight.

        Args:
            input_file (str): Path to the input CSV file.
            output_dir (str): Path to save output files (CSV and plots).
            pareto_output_file (str): Name of the output CSV file to save Pareto-optimal points.
            top_n (int): Number of top Pareto points to highlight in the plot.
        """
        self.input_file = input_file
        self.output_dir = output_dir
        self.pareto_output_file = pareto_output_file  # Add this line to set pareto_output_file as an attribute
        self.top_n = top_n
        self.df = None
        self.pae_cols = []
        self.pareto_df = None

        # Ensure output directories exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, 'plots'), exist_ok=True)

    def load_data(self):
        """Load the dataset and identify pae-related columns."""
        self.df = pd.read_csv(self.input_file)
        self.pae_cols = [col for col in self.df.columns if 'pae' in col and 'uncertainty' not in col and 'acq_Score' not in col]
        print(f"Data loaded from {self.input_file}. Identified pae columns: {self.pae_cols}")

    def find_common_pareto_optimal_points(self):
        """Identify common Pareto-optimal points across all pae-related objectives."""
        pareto_indices_sets = []
        objectives = torch.tensor(self.df[self.pae_cols].values, dtype=torch.float32)

        for i in range(len(self.pae_cols)):
            # Negate the first column for minimization
            objectives_copy = objectives.clone()
            objectives_copy[:, 0] *= -1
            if i != 0:
                objectives_copy[:, i] *= -1
            pareto_mask = is_non_dominated(objectives_copy)
            pareto_indices_sets.append(set(np.where(pareto_mask.numpy())[0]))

        common_pareto_indices = set.intersection(*pareto_indices_sets)
        self.pareto_df = self.df.iloc[list(common_pareto_indices)]
        print(f"Number of new Pareto-optimal binders: {len(self.pareto_df)}")

    def save_pareto_results(self):
        """Save the Pareto-optimal points to a CSV file."""
        output_file = os.path.join(self.output_dir, self.pareto_output_file)
        self.pareto_df.to_csv(output_file, index=False)
        print(f"Saved common Pareto-optimal points to {output_file}")

    def run_analysis(self):
        """Run the full analysis: load data, find Pareto-optimal points, save results."""
        self.load_data()
        self.find_common_pareto_optimal_points()
        self.save_pareto_results()
        
        # Use ParetoPlotter to create the plot
        plotter = ParetoPlotter(self.pareto_df, self.pae_cols, self.output_dir, 'test_pareto_plot.png', self.top_n)
        plotter.plot_pareto_front()


class ParetoPlotter:
    def __init__(self, pareto_df, pae_cols, output_dir, plot_file, top_n=20, title="Pareto Front Plot"):
        """
        Initialize the Pareto Plotter with data and plot configuration.

        Args:
            pareto_df (DataFrame): DataFrame containing Pareto-optimal points.
            pae_cols (list): List of columns for pae objectives.
            output_dir (str): Path to save the plot image.
            plot_file (str): Filename for the plot output.
            top_n (int): Number of top Pareto points to highlight in the plot.
            title (str): Title for the plot.
        """
        self.pareto_df = pareto_df
        self.pae_cols = pae_cols
        self.output_dir = output_dir
        self.plot_file = plot_file
        self.top_n = top_n
        self.title = title

        # Set the plot font
        self.set_plot_font()

    @staticmethod
    def set_plot_font(family='serif', weight='bold', size=12):
        font = {'family': family, 'weight': weight, 'size': size}
        matplotlib.rc('font', **font)

    def plot_pareto_front(self):
        """Plot the Pareto front, highlighting the top N points."""
        sorted_pareto_df = self.pareto_df.sort_values(by=self.pae_cols, ascending=[True] + ([False] * (len(self.pae_cols) - 1)))
        top_pareto_df = sorted_pareto_df.head(self.top_n)
        remaining_pareto_df = sorted_pareto_df.iloc[self.top_n:]

        # Define colormap
        colors_list = ['darkseagreen', 'indianred', '#4a8cb5']
        cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', colors_list)
        norm = mcolors.Normalize(vmin=0, vmax=20)

        fig, ax = plt.subplots(figsize=(22, 10))
        
        for idx, row in remaining_pareto_df[self.pae_cols].iterrows():
            color = cmap(norm(row.mean()))
            ax.plot(range(len(self.pae_cols)), row, color=color, alpha=0.1, linewidth=0.5)
        
        for idx, row in top_pareto_df[self.pae_cols].iterrows():
            color = cmap(norm(row.mean()))
            ax.plot(range(len(self.pae_cols)), row, color=color, alpha=0.9, linewidth=3)

        ax.set_xticks(range(len(self.pae_cols)))
        ax.set_xticklabels([col.replace('predicted_pae_interaction_', 'Target ') for col in self.pae_cols], rotation=15, ha="right", size=12)
        ax.set_ylabel('Predicted IpAE Score', size=20)
        ax.grid(axis='x')
        ax.set_ylim(5, 28)
        ax.set_title(self.title, loc="left", size=20)

        sm = cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        plt.colorbar(sm, ax=ax, location='right', shrink=0.6, label='Average pae score')

        plot_path = os.path.join(self.output_dir, self.plot_file)
        plt.savefig(plot_path, format="png")
        print(f"Saved plot to {plot_path}")
        plt.show()
