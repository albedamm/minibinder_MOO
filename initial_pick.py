import pandas as pd

# Load the dataset
df = pd.read_csv('bo_results/blosum_ridge_ucb/proteus_blosum_ridge_ucb_pareto_3.csv')

# Calculate the sum of all uncertainty columns
df['total_uncertainty'] = df.filter(regex='uncertainty').sum(axis=1)

# Sort the dataframe by 'total_uncertainty' in descending order
df_sorted = df.sort_values(by='total_uncertainty', ascending=False)

# Select the top 500 rows with the highest total uncertainty
top_300_binders = df_sorted.head(300)

# Save the result to a new CSV file
top_300_binders.to_csv('bo_results/blosum_ridge_ucb/highest_uncertainty/high_300_sigma_proteus_blosum_ridge_ucb_3.csv', index=False)

print("The top 300 binders with the highest uncertainty have been saved to a new CSV file.")
