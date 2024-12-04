import proteusAI as pai
import pandas as pd
import time
from uncertainty_analysis import UncertaintyAnalyzer
import os

# Start total execution timer
total_start_time = time.time()

# Initialize a list to store timepoints
timepoints = []

# Load the dataset
start_time = time.time()
df = pd.read_csv('data/25_NLFR_esm2_ridge_ucb_1.csv')
elapsed = time.time() - start_time
timepoints.append({'Step': 'Load Dataset', 'Time (seconds)': elapsed})
print(f"Dataset loaded in {elapsed:.2f} seconds.")

# Initialize lists for target columns and tasks 
y_cols = []
tasks = []

# Append the target columns and tasks to the lists based on the column names and optimization
start_time = time.time()
for col in df.columns:
    if 'pae' in col and 'NLFRRVWEL' in col:
        y_cols.append(col)
        tasks.append('min')
    if 'plddt' in col and 'NLFRRVWEL' in col:
        y_cols.append(col)
        tasks.append('max')
    if 'pae' in col and 'NLFRRVWEL' not in col:
        y_cols.append(col)
        tasks.append('max')
    if 'plddt' in col and 'NLFRRVWEL' not in col:
        y_cols.append(col)
        tasks.append('min')
elapsed = time.time() - start_time
timepoints.append({'Step': 'Identify Target Columns and Tasks', 'Time (seconds)': elapsed})
print(f"Target columns and tasks identified in {elapsed:.2f} seconds.")

# Dictionaries to store libraries and models for each target column
libraries = {}
models = {}

# Define the representation type
x_type = 'esm2'

# Train models for each target column
for i, y_col in enumerate(y_cols):
    start_time = time.time()
    # Create a library and model for each target column
    lib = pai.Library(source='data/25_NLFR_esm2_ridge_ucb_1.csv', names_col='name', seqs_col='binder_seq', y_col=y_col, y_type='num')
    if x_type in ['esm2', 'esm1v']:
        lib.compute(method='esm2')
    libraries[y_col] = lib
    model = pai.Model(library=lib, x=x_type, model_type='ridge', k_folds=5)
    models[y_col] = model
    model.train()  # Train the model
    elapsed = time.time() - start_time
    timepoints.append({'Step': f'Train Model for each target', 'Time (seconds)': elapsed})
    print(f"Model trained in {elapsed:.2f} seconds.")

start_time = time.time()
# Get the first target column, task, and model
first_y_col = y_cols[0]
first_task = tasks[0]
first_model = models[first_y_col]

# Perform a search for the first target column to find new mutations and their predicted values
search_out = first_model.search(optim_problem=first_task, acq_fn='ucb', explore=1.0) # explore 1.0 will test all mutations

# Save the search results to a CSV file
search_out.to_csv(f'bo_results/proteus_esm2_ridge_ucb_{first_y_col}_25_1.csv')


elapsed = time.time() - start_time
timepoints.append({'Step': f'Search for {first_y_col}', 'Time (seconds)': elapsed})
print(f"Search completed and results saved in {elapsed:.2f} seconds.")

# Create a list of predicted proteins (sequences) from the search results
predicted_proteins = [pai.Protein(seq=row.sequence, name=row['name']) for i, row in search_out.iterrows()]


start_time = time.time()
# For each target column (except first_y_col)
for y_col in y_cols[1:]:
    model = models[y_col]

    # Use the predict function to get predictions, uncertainties, and acquisition scores
    val_data, y_val_pred, y_val_sigma, y_val, sorted_acq_score = model.predict(predicted_proteins, acq_fn='ucb')

    # Add predictions, uncertainties, and acquisition scores to the search_out DataFrame
    search_out[f'predicted_{y_col}'] = y_val_pred
    search_out[f'uncertainty_{y_col}'] = y_val_sigma
    search_out[f'acq_Score_{y_col}'] = sorted_acq_score

elapsed = time.time() - start_time
timepoints.append({'Step': f'Predict for all targets', 'Time (seconds)': elapsed})
print(f"Predictions for all targets completed in {elapsed:.2f} seconds.")


# Ensure the output directory exists
output_dir = f'bo_results/esm2_ridge_ucb/'
os.makedirs(output_dir, exist_ok=True)

# Save the combined predictions to a CSV file
search_out.to_csv('bo_results/esm2_ridge_ucb/proteus_esm2_ridge_ucb_25_1.csv')

# Analyze the top 300 rows by uncertainty using UncertaintyAnalyzer
start_time = time.time()

# Ensure the output directory for highest uncertainty exists
highest_uncertainty_dir = os.path.join(output_dir, "highest_uncertainty/")
os.makedirs(highest_uncertainty_dir, exist_ok=True)

# Save highest uncertainty results
uncertainty_analyzer = UncertaintyAnalyzer(
    input_file='bo_results/esm2_ridge_ucb/proteus_esm2_ridge_ucb_25_1.csv',
    output_file='bo_results/esm2_ridge_ucb/highest_uncertainty/proteus_sigma_100_esm2_ridge_ucb_25_1.csv',
    top_n=100
)
uncertainty_analyzer.load_data()
uncertainty_analyzer.calculate_total_uncertainty()
uncertainty_analyzer.save_top_binders()
elapsed = time.time() - start_time
timepoints.append({'Step': 'Uncertainty Analysis', 'Time (seconds)': elapsed})
print(f"Uncertainty analysis completed in {elapsed:.2f} seconds.")

# End of total execution
total_elapsed = time.time() - total_start_time
timepoints.append({'Step': 'Total Execution Time', 'Time (seconds)': total_elapsed})
print(f"Total execution time: {total_elapsed:.2f} seconds.")


# Save all timepoints to a df
timepoints_df = pd.DataFrame(timepoints)

# Ensure the output directory for execution time exists
execution_time_dir = os.path.join(output_dir, "execution_time/")
os.makedirs(execution_time_dir, exist_ok=True)

# Save execution time
timepoints_df.to_csv('bo_results/esm2_ridge_ucb/execution_time/execution_time_esm2_ridge_ucb_25_1.csv')
print("Timepoints saved to csv file")