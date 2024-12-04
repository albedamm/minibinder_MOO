import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import torch
from botorch.utils.multi_objective import is_non_dominated
from botorch.utils.multi_objective.hypervolume import Hypervolume
import matplotlib

# Hardcoded paths for input CSV and output files
CSV_PATH = 'data/pareto_scatter_dataset.csv'
PARETO_CHART_PATH = 'results/pareto_plots/pareto_chart_new_2.png'
LINE_GRAPH_PATH = 'results/pareto_plots/line_graph_new_2.png'

def find_pareto_front(data):
    # Dynamically find the columns that match the target patterns
    target_a_col = [col for col in data.columns if "pae_interaction_HLA_B_0801_NLFRRVWEL" in col][0]
    target_b_col = [col for col in data.columns if "pae_interaction_HLA_B_0801_NLSRRVWEL" in col][0]

    # Print column names for debugging
    print("Objective columns:", target_a_col, target_b_col)

    # Prepare objectives tensor
    objectives = torch.tensor(np.column_stack((-data[target_a_col].values, 
                                               data[target_b_col].values)), dtype=torch.float)

    # Debug: Print objectives
    print("Objective values (after negation for the first objective):")
    print(objectives)

    # Find Pareto optimal points
    pareto_mask = is_non_dominated(objectives)

    # Debug: Print Pareto mask and summary
    print("Pareto mask:", pareto_mask)
    print("Number of Pareto points:", pareto_mask.sum().item())
    print("Number of non-Pareto points:", (~pareto_mask).sum().item())

    return pareto_mask.cpu().numpy()  # Convert back to a NumPy array if needed


def calculate_hypervolume(data):
    # Dynamically find the columns for hypervolume calculation
    target_a_col = [col for col in data.columns if "pae_interaction_HLA_B_0801_NLFRRVWEL" in col][0]
    target_b_col = [col for col in data.columns if "pae_interaction_HLA_B_0801_NLSRRVWEL" in col][0]
    
    data = data[[target_b_col, target_a_col]]
    # Find the Pareto front
    pareto_mask = find_pareto_front(data)
    # Extract the Pareto front points
    pareto_points = torch.tensor(data[pareto_mask].to_numpy(), dtype=torch.float)
    # Invert the second objective as Hypervolume is maximized
    pareto_points[:, 1] = -pareto_points[:, 1]
    
    ref_point = torch.tensor((3.00, -28.00))

    hv = Hypervolume(ref_point=ref_point)
    volume = hv.compute(pareto_points)
    return volume

def accumulate_data_by_iteration(data):
    accumulated_data = []
    for iteration in sorted(data['iteration'].unique()):
        # Accumulate data up to the current iteration
        data_up_to_iteration = data[data['iteration'] <= iteration]
        accumulated_data.append(data_up_to_iteration)
    
    return accumulated_data

def set_plot_font(family='serif', weight='bold', size=12):
    font = {'family' : 'serif',
            'weight' : 'bold',
            'size'   : 12
           }
    # Apply font properties
    matplotlib.rc('font', **font)

def plot_pareto_chart(data, save_img_path):

    set_plot_font()

    pareto_mask = find_pareto_front(data)

    pareto_c = 'red' 
    non_pareto_c = 'darkblue'
    fill_c='#0099CC'
    init_iter_c = 'gold'
    
    plt.figure(figsize=(10, 6))

    # Non-pareto points
    non_pareto = data[data['iteration'] != 0]
    plt.scatter(non_pareto['pae_interaction_HLA_B_0801_NLSRRVWEL'], 
                non_pareto['pae_interaction_HLA_B_0801_NLFRRVWEL'], 
                color=non_pareto_c, 
                label='Non-Pareto Points',
                s=10)

    # Extract and plot Pareto front points
    pareto_points = data[pareto_mask]
    plt.scatter(pareto_points['pae_interaction_HLA_B_0801_NLSRRVWEL'], 
                pareto_points['pae_interaction_HLA_B_0801_NLFRRVWEL'], 
                color=pareto_c, 
                edgecolors="black",
                s=50, 
                linewidths=0.5, 
                label='Pareto Front Points')
    
    # Iteration 0 points
    pareto_points_0 = data[pareto_mask & (data['iteration'] == 0)]
    non_pareto_0 = data[data['iteration'] == 0]

    # Iteration 0 non-Pareto points
    plt.scatter(non_pareto_0['pae_interaction_HLA_B_0801_NLSRRVWEL'], 
                non_pareto_0['pae_interaction_HLA_B_0801_NLFRRVWEL'], 
                color=init_iter_c, 
                edgecolors="black",
                s=10, 
                label='Iter 0 Non-Pareto Points')

    # Iteration 0 Pareto points
    plt.scatter(pareto_points_0['pae_interaction_HLA_B_0801_NLSRRVWEL'], 
                pareto_points_0['pae_interaction_HLA_B_0801_NLFRRVWEL'], 
                color=init_iter_c, 
                edgecolors="black",
                s=50, 
                label='Iter 0 Pareto Points')

    # Reference point
    ref_point = (3.00,28.00)
    plt.scatter(ref_point[0], ref_point[1], color='black', label='Reference Point', s=10)
    # Shade hypervolume for Pareto front points
    for i in range(len(pareto_points)):
        plt.fill_between([pareto_points.iloc[i]['pae_interaction_HLA_B_0801_NLSRRVWEL'], ref_point[0]],
                         [pareto_points.iloc[i]['pae_interaction_HLA_B_0801_NLFRRVWEL'], pareto_points.iloc[i]['pae_interaction_HLA_B_0801_NLFRRVWEL']],
                         ref_point[1], color=fill_c, alpha=0.3, zorder=0)

    # Axes and labels
    plt.title('Sequence evaluations: {}'.format(len(data)))
    plt.xlabel('IpAE Target 2', fontsize=12 )
    plt.ylabel('IpAE Target 1', fontsize=12)

    plt.xlim(ref_point[0]-0.25, max(data['pae_interaction_HLA_B_0801_NLSRRVWEL'])+5)
    plt.ylim(0, ref_point[1]+0.5)

    # Show the plot
    plt.savefig(save_img_path)

def plot_line_graph(data, save_img_path):
    set_plot_font()
    accumulated_data = accumulate_data_by_iteration(data)
    
    hypervolumes = []
    for data_up_to_iteration in accumulated_data:
        # Calculate hypervolume for each accumulated data set
        hv = calculate_hypervolume(data_up_to_iteration)
        hypervolumes.append(hv)
    
    # List of the number of sequences up to each iteration
    queried_sequences = [data.shape[0] for data in accumulated_data]
    plt.figure(figsize=(10, 6))
    plt.step(queried_sequences, hypervolumes, where="post", color = 'darkblue')
    plt.axvline(x=queried_sequences[0], color='black', linestyle='--', label='Iteration 0')
    plt.xlabel('Number of Generated Sequences')
    plt.ylabel('Hypervolume')
    plt.savefig(save_img_path)

    
def main():
    # Load the data from the specified CSV path
    data = pd.read_csv(CSV_PATH, delimiter=',')
    print("Column names in the CSV file:", data.columns)  # Debugging step to check columns
    print(data.head())  # Inspect the first few rows to verify proper parsing

    # Optional: Add a default 'iteration' column if missing
    if 'iteration' not in data.columns:
        data['iteration'] = 0
    
    # Generate and save plots
    plot_pareto_chart(data, PARETO_CHART_PATH)
    plot_line_graph(data, LINE_GRAPH_PATH)

if __name__ == "__main__":
    main()
