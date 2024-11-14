import pandas as pd
import os

class UncertaintyAnalyzer:
    def __init__(self, input_file, output_file, top_n=300):
        """
        Initialize the analyzer with input and output file paths and the number of top rows to select.

        Args:
            input_file (str): Path to the input CSV file.
            output_file (str): Path to save the output CSV file.
            top_n (int): Number of top rows to select based on total uncertainty.
        """
        self.input_file = input_file
        self.output_file = output_file
        self.top_n = top_n
        self.df = None

    def load_data(self):
        """Load the dataset from the specified CSV file."""
        self.df = pd.read_csv(self.input_file)
        print(f"Data loaded from {self.input_file}")

    def calculate_total_uncertainty(self):
        """Calculate the sum of all uncertainty columns and add it as a new column."""
        if self.df is not None:
            self.df['total_uncertainty'] = self.df.filter(regex='uncertainty').sum(axis=1)
            print("Total uncertainty calculated and added as a column.")
        else:
            print("Data has not been loaded. Please call load_data() first.")

    def get_top_n_by_uncertainty(self):
        """Sort the data by total uncertainty and select the top N rows."""
        if 'total_uncertainty' in self.df.columns:
            df_sorted = self.df.sort_values(by='total_uncertainty', ascending=False)
            top_binders = df_sorted.head(self.top_n)
            print(f"Top {self.top_n} rows by uncertainty selected.")
            return top_binders
        else:
            print("Total uncertainty column not found. Please call calculate_total_uncertainty() first.")
            return None

    def save_top_binders(self):
        """Save the top N rows with the highest uncertainty to the specified output file."""
        top_binders = self.get_top_n_by_uncertainty()
        if top_binders is not None:
            # Ensure the output directory exists
            os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
            top_binders.to_csv(self.output_file, index=False)
            print(f"The top {self.top_n} binders have been saved to {self.output_file}.")

# Usage Example:
# if __name__ == "__main__":
#     analyzer = UncertaintyAnalyzer(
#         input_file='bo_results/blosum_ridge_ucb/proteus_blosum_ridge_ucb_pareto_3.csv',
#         output_file='bo_results/blosum_ridge_ucb/highest_uncertainty/high_300_sigma_proteus_blosum_ridge_ucb_3.csv'
#     )
#     analyzer.load_data()
#     analyzer.calculate_total_uncertainty()
#     analyzer.save_top_binders()
