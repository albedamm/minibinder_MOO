import pandas as pd
import torch
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import matplotlib
from botorch.utils.multi_objective.pareto import is_non_dominated
import os

# Function to set the font of the plots
def set_plot_font(family='serif', weight='bold', size=12):
    font = {'family': family, 'weight': weight, 'size': size}
    matplotlib.rc('font', **font)

# Set the font for the plot
set_plot_font()

# Load the old dataset
df_old = pd.read_csv('bo_results/blosum_ridge_ucb/proteus_blosum_ridge_ucb_1.csv')

# Filter columns related to pae (all columns containing 'pae' as objectives)
old_pAE_cols = [col for col in df_old.columns if 'pae' in col and 'uncertainty' not in col and 'acq_Score' not in col]

# List to hold indices of Pareto optimal points for each objective
pareto_indices_sets = []

# Identify Pareto optimal points for each column, treating it as the main objective
for i in range(len(old_pAE_cols)):
    # Prepare objectives
    objectives = torch.tensor(df_old[old_pAE_cols].values, dtype=torch.float32)
    
    # Minimize the first column (always), so we negate it
    objectives[:, 0] *= -1
    
    # If the current column is not the first one, negate it to maximize
    if i != 0:
        objectives[:, i] *= -1

    # Find Pareto optimal points for the current main objective
    pareto_mask = is_non_dominated(objectives)
    pareto_indices_sets.append(set(np.where(pareto_mask.numpy())[0]))

# Find common Pareto optimal points across all objectives
common_pareto_indices = set.intersection(*pareto_indices_sets)
pareto_df_old = df_old.iloc[list(common_pareto_indices)]

# Calculate and print the number of new Pareto-optimal binders
num_old_pareto_optimal = len(pareto_df_old)
print(f"Number of new Pareto-optimal binders: {num_old_pareto_optimal}")


# Plotting section (optional, if you want to visualize the results as well)
# Sort Pareto-optimal points to get the top 20 based on the objectives
sorted_pareto_df_old = pareto_df_old.sort_values(by=old_pAE_cols, ascending=[True] + ([False] * (len(old_pAE_cols) - 1)))
top_20_pareto_df_old = sorted_pareto_df_old.head(20)
remaining_pareto_df_old = sorted_pareto_df_old.iloc[20:]

pareto_points_df = sorted_pareto_df_old
pareto_points_df.to_csv('pareto_results/pareto_proteus_blosum_ridge_1.csv', index=False)
print("Saved common Pareto-optimal points to CSV file.")

# Create a custom colormap
colors_list = ['darkseagreen', 'indianred', '#4a8cb5']
cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', colors_list)
norm = mcolors.Normalize(vmin=0, vmax=20)

# Set up side-by-side plot layout
fig, axs = plt.subplots(1, 2, figsize=(22, 10))

# Plot Pareto front for common optimal points
ax = axs[0]
for idx, row in remaining_pareto_df_old[old_pAE_cols].iterrows():
    # Plot background lines with reduced opacity and width
    color = cmap(norm(row.mean()))
    ax.plot(range(len(old_pAE_cols)), row, color=color, alpha=0.1, linewidth=0.5)  # Background lines with reduced opacity and width

for idx, row in top_20_pareto_df_old[old_pAE_cols].iterrows():
    # Plot top 20 lines with higher opacity and thickness
    color = cmap(norm(row.mean()))
    ax.plot(range(len(old_pAE_cols)), row, color=color, alpha=0.9, linewidth=3)  # Top 20 lines with higher opacity and thickness

# Set x-axis labels and ticks
ax.set_xticks(range(len(old_pAE_cols)))
ax.set_xticklabels([col.replace('predicted_pae_interaction_', 'Target ') for col in old_pAE_cols], rotation=15, ha="right", size=12)  # Tilt labels
ax.set_ylabel('pae Score', size=20)
ax.grid(axis='x')
ax.set_ylim(5, 28)  # Set y-axis to start at 6
ax.set_title("Proteus_blosum_ridge_ucb_1 Pareto Front (Top 20 in Bold)", loc="left", size=20)

# Colorbar
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=axs, location='right', shrink=0.6, label='Average pae score')

# Save and show the plot
plt.savefig('pareto_results/plots/pareto_proteus_blosum_ridge_plot_1.pdf', format="pdf")
print("Saved PDF with common Pareto-optimal binders.")
plt.show()