import proteusAI as pai
import pandas as pd
import time

# Start total execution timer
total_start_time = time.time()

# Load the dataset
start_time = time.time()
df = pd.read_csv('data/blosum_ridge_ucb_pareto_2_dataset.csv')
print(f"Dataset loaded in {time.time() - start_time:.2f} seconds.")

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
print(f"Target columns and tasks identified in {time.time() - start_time:.2f} seconds.")

# Dictionaries to store libraries and models for each target column
libraries = {}
models = {}

# Define the representation type
x_type = 'blosum62'

# Train models for each target column
for i, y_col in enumerate(y_cols):
    # Create a library and model for each target column
    start_time = time.time()
    lib = pai.Library(source='data/blosum_ridge_ucb_pareto_2_dataset.csv', names_col='name', seqs_col='binder_seq', y_col=y_col, y_type='num')
    libraries[y_col] = lib
    model = pai.Model(library=lib, x=x_type, model_type='ridge', k_folds=5)
    models[y_col] = model
    # Train the model 
    model.train()
    print(f"Model for {y_col} trained in {time.time() - start_time:.2f} seconds.")

# Get the first target column, task, and model
first_y_col = y_cols[0]
first_task = tasks[0]
first_model = models[first_y_col]

# Perform a search for the first target column to find new mutations and their predicted values
start_time = time.time()
search_out = first_model.search(optim_problem=first_task, acq_fn='ucb', explore=1.0)
search_out.to_csv(f'bo_results/proteus_blosum_ridge_ucb_{first_y_col}_pareto_3.csv')
print(f"Search completed and results saved in {time.time() - start_time:.2f} seconds.")

# Create a list of predicted proteins (sequences) from the search results
predicted_proteins = [pai.Protein(seq=row.sequence, name=row['name']) for i, row in search_out.iterrows()]

# For each target column (except first_y_col)
for y_col in y_cols[1:]:
    start_time = time.time()
    model = models[y_col]
    
    # Use the predict function to get predictions, uncertainties, and acquisition scores
    val_data, y_val_pred, y_val_sigma, y_val, sorted_acq_score = model.predict(predicted_proteins, acq_fn='ucb')
    
    # Add predictions, uncertainties, and acquisition scores to the search_out DataFrame
    search_out[f'predicted_{y_col}'] = y_val_pred
    search_out[f'uncertainty_{y_col}'] = y_val_sigma
    search_out[f'acq_Score_{y_col}'] = sorted_acq_score
    print(f"Predictions for {y_col} completed in {time.time() - start_time:.2f} seconds.")

# Save the combined predictions to a CSV file
start_time = time.time()
search_out.to_csv('bo_results/blosum_ridge_ucb/proteus_blosum_ridge_ucb_pareto_3.csv', index=False)
print(f"All predictions saved to CSV in {time.time() - start_time:.2f} seconds.")

# End of total execution
print(f"Total execution time: {time.time() - total_start_time:.2f} seconds.")
