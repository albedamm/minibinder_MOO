import proteusAI as pai
import pandas as pd

# Load the dataset
df = pd.read_csv('data/blosum_ridge_ucb_pareto_2_dataset.csv')

# Initialize lists for target columns and tasks 
y_cols = []
tasks = []

# Append the target columns and tasks to the lists based on the column names and optimzation
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

# Dictionaries to store libraries and models for each target column
libraries = {}
models = {}

# Define the representation type
x_type = 'blosum62'

for i, y_col in enumerate(y_cols):
    # Create a library and model for each target column
    lib = pai.Library(source='data/blosum_ridge_ucb_pareto_2_dataset.csv', names_col='name', seqs_col='binder_seq', y_col=y_col, y_type='num')
    libraries[y_col] = lib
    model = pai.Model(library=lib, x=x_type, model_type='ridge', k_folds=5)
    models[y_col] = model
    # Train the model 
    model.train()

# Get the first target column, task, and model
first_y_col = y_cols[0]
first_task = tasks[0]
first_model = models[first_y_col]

# Perform a search for the first target column to find new mutations and their predicted values
search_out = first_model.search(optim_problem=first_task, acq_fn='ucb', explore=1.0)
# Save the search results to a CSV file
search_out.to_csv(f'bo_results/proteus_blosum_ridge_ucb_{first_y_col}_pareto_3.csv')  

# Create a list of predicted proteins (sequences) from the search results
predicted_proteins = [pai.Protein(seq=row.sequence, name=row['name']) for i, row in search_out.iterrows()]

# For each target column (except first_y_col)
for y_col in y_cols[1:]:
    model = models[y_col]
    
    # Use the predict function to get predictions, uncertainties, and acquisition scores
    val_data, y_val_pred, y_val_sigma, y_val, sorted_acq_score = model.predict(predicted_proteins, acq_fn='ucb')
    
    # Add predictions, uncertainties, and acquisition scores to the search_out DataFrame
    search_out[f'predicted_{y_col}'] = y_val_pred
    search_out[f'uncertainty_{y_col}'] = y_val_sigma
    search_out[f'acq_Score_{y_col}'] = sorted_acq_score

# Save the combined predictions to a CSV file
search_out.to_csv('bo_results/blosum_ridge_ucb/proteus_blosum_ridge_ucb_pareto_3.csv', index=False)


