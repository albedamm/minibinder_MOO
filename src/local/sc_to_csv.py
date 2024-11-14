import csv
import os

def convert_sc_to_csv(input_file, output_file):
    """
    Converts a space-separated .sc file to a comma-separated .csv file.
    
    Args:
        input_file (str): Path to the input .sc file.
        output_file (str): Path to save the output .csv file.
    """
    with open(input_file, 'r') as sc_file:
        with open(output_file, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            
            # Read each line in the .sc file, split by whitespace, and write to .csv
            for line in sc_file:
                row = line.strip().split()  # Split by whitespace
                csv_writer.writerow(row)

def convert_directory_sc_to_csv(directory):
    """
    Converts all .sc files in a directory to .csv files in the same directory.
    
    Args:
        directory (str): Path to the directory containing .sc files.
    """
    for file_name in os.listdir(directory):
        if file_name.endswith('.sc'):
            input_file = os.path.join(directory, file_name)
            output_file = os.path.join(directory, file_name.replace('.sc', '.csv'))
            print(f"Converting {input_file} to {output_file}")
            convert_sc_to_csv(input_file, output_file)

# Example usage
directory = 'data/AF2_init_guess_results'
convert_directory_sc_to_csv(directory)
