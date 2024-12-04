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
df_old = pd.read_csv('bo_results/test.csv')
# Filter columns related to pae (all columns containing 'pae' as objectives)
old_pAE_cols = [col for col in df_old.columns if 'y_predicted' in col or 'pae' in col and 'uncertainty' not in col and 'acq_Score' not in col]

# List to hold indices of Pareto optimal points for each objective
pareto_indices_sets = []

# Identify Pareto optimal points for each column, treating it as the main objective
for i in range(len(old_pAE_cols)):
    # Prepare objectives
    objectives = torch.tensor(df_old[old_pAE_cols].values, dtype=torch.float32)
    
    objectives[:, 0] *= -1
    
    if i != 0:
        objectives[:, i] *= 1

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
# If too many pareto points
sorted_pareto_df_old = sorted_pareto_df_old.head(100)
top_20_pareto_df_old = sorted_pareto_df_old.head(10)
remaining_pareto_df_old = sorted_pareto_df_old.iloc[20:]

pareto_points_df = sorted_pareto_df_old
pareto_points_df.to_csv('pareto_results/test.csv', index=False)
print("Saved common Pareto-optimal points to CSV file.")

# Print the names of binders within the constraints
if 'name' in sorted_pareto_df_old.columns:
    print("Top 100 Pareto-optimal binders:")
    print(sorted_pareto_df_old['name'].tolist())
else:
    print("Column 'name' not found in the dataset.")

# Create a custom colormap
colors_list = ['darkseagreen', 'indianred', '#4a8cb5']
cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', colors_list)
norm = mcolors.Normalize(vmin=0, vmax=20)

# Plot Pareto front for all optimal points in a single plot
fig, ax = plt.subplots(figsize=(16, 10))

# Plot remaining Pareto-optimal points with reduced opacity and width
for idx, row in remaining_pareto_df_old[old_pAE_cols].iterrows():
    color = cmap(norm(row.mean()))
    ax.plot(range(len(old_pAE_cols)), row, color=color, alpha=0.1, linewidth=0.5)

# Plot top 20 Pareto-optimal points with higher opacity and thickness
for idx, row in top_20_pareto_df_old[old_pAE_cols].iterrows():
    color = cmap(norm(row.mean()))
    ax.plot(range(len(old_pAE_cols)), row, color=color, alpha=0.9, linewidth=3)

# Set x-axis labels and ticks
ax.set_xticks(range(len(old_pAE_cols)))

# Predicted y values
ax.set_xticklabels([col.replace('predicted_pae_interaction_', 'Target ') for col in old_pAE_cols], rotation=15, ha="right", size=12)

# True y values
# ax.set_xticklabels([col.replace('pae_interaction_', 'Target ') for col in old_pAE_cols], rotation=15, ha="right", size=12)

ax.set_ylabel('IpAE Score', size=20)
ax.grid(axis='x')
ax.set_ylim(0, 30)  # Adjust y-axis range as needed

# Predicted y values
ax.set_title("Proteus_pareto_blosum62_ridge_ucb_test Predicted IpAE Pareto Front (Top 20 in Bold)", loc="left", size=20)

# True y values# 
# ax.set_title("True_pareto_blosum62_rf_ei_494_2 True IpAE Pareto Front (Top 20 in Bold)", loc="left", size=20)

# Add colorbar
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, location='right', shrink=0.6, label='Average IpAE score')

# Save and show the plot
# Predicted y values
plt.savefig('pareto_results/plots/pareto_proteus_esm2_ridge_ucb_test.png', format="png")

# True y values
# plt.savefig('pareto_results/plots/true_pareto_proteus_blosum62_rf_ei_494_plot_2.png', format="png")

print("Saved plot with common Pareto-optimal binders.")
plt.show()
