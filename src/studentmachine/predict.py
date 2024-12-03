import proteusAI as pai
import pandas as pd
import time
from uncertainty_analysis import UncertaintyAnalyzer

# Start total execution timer
total_start_time = time.time()

# Initialize a list to store timepoints
timepoints = []

# Load the dataset
start_time = time.time()
df = pd.read_csv('data/master_dataset_NLFR_1000.csv')
elapsed = time.time() - start_time
timepoints.append({'Step': 'Load Dataset', 'Time (seconds)': elapsed})
print(f"Dataset loaded in {elapsed:.2f} seconds.")

# Initialize lists for target columns and tasks 
y_cols = []
tasks = []

# Append the target columns and tasks to the lists based on the column names and optimization
start_time = time.time()
for col in df.columns:
    if 'pae' and 'NLFRRVWEL' in col:
        y_cols.append(col)
        tasks.append('min')
    if 'plddt' and 'NLFRRVWEL' in col:
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
x_type = 'blosum62'

# Train models for each target column
for i, y_col in enumerate(y_cols):
    start_time = time.time()
    # Create a library and model for each target column
    lib = pai.Library(source='data/master_dataset_NLFR_1000.csv', names_col='name', seqs_col='binder_seq', y_col=y_col, y_type='num')
    if x_type in ['esm2', 'esm1v']:
        lib.compute(method='esm2')
    libraries[y_col] = lib
    model = pai.Model(library=lib, x=x_type, model_type='rf', k_folds=5)
    models[y_col] = model
    model.train()  # Train the model
    elapsed = time.time() - start_time
    timepoints.append({'Step': f'Train Model for {y_col}', 'Time (seconds)': elapsed})
    print(f"Model for {y_col} trained in {elapsed:.2f} seconds.")

# Perform a search for the first target column to find new mutations and their predicted values
start_time = time.time()
first_y_col = y_cols[0]
first_task = tasks[0]
first_model = models[first_y_col]
search_out = first_model.search(optim_problem=first_task, acq_fn='ucb', explore=1.0)
search_out.to_csv(f'bo_results/blosum_rf_ucb/proteus_blosum_rf_ucb_{first_y_col}_1000_1.csv')
elapsed = time.time() - start_time
timepoints.append({'Step': f'Search for {first_y_col}', 'Time (seconds)': elapsed})
print(f"Search completed and results saved in {elapsed:.2f} seconds.")

# Create a list of predicted proteins (sequences) from the search results
predicted_proteins = [pai.Protein(seq=row.sequence, name=row['name']) for i, row in search_out.iterrows()]

# For each target column (except first_y_col)
for y_col in y_cols[1:]:
    start_time = time.time()
    model = models[y_col]
    val_data, y_val_pred, y_val_sigma, y_val, sorted_acq_score = model.predict(predicted_proteins, acq_fn='ucb')
    search_out[f'predicted_{y_col}'] = y_val_pred
    search_out[f'uncertainty_{y_col}'] = y_val_sigma
    search_out[f'acq_Score_{y_col}'] = sorted_acq_score
    elapsed = time.time() - start_time
    timepoints.append({'Step': f'Predict for {y_col}', 'Time (seconds)': elapsed})
    print(f"Predictions for {y_col} completed in {elapsed:.2f} seconds.")

# Save the combined predictions to a CSV file
final_output_file = 'bo_results/blosum_rf_ucb/proteus_blosum_rf_ucb_1000_1.csv'
search_out.to_csv(final_output_file, index=False)

# Analyze the top 300 rows by uncertainty using UncertaintyAnalyzer
start_time = time.time()
uncertainty_analyzer = UncertaintyAnalyzer(
    input_file=final_output_file,
    output_file='bo_results/blosum_rf_ucb/highest_uncertainty/proteus_sigma_100_blosum_rf_ucb_1000_1.csv',
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

# Save all timepoints to a CSV file
timepoints_df = pd.DataFrame(timepoints)
timepoints_df.to_csv('bo_results/blosum_rf_ucb/execution_time/execution_time_blosum_rf_ucb_1000_1.txt', index=False)
print("Timepoints saved to txt file")
