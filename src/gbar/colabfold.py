
import subprocess
import os
import glob

def run_colabfold(input_fasta, output_dir):
    try:
        # Write all the necessary commands to a bash script
        bash_script = f"""
        #!/bin/bash
        source /dtu/projects/RFdiffusion/setup.sh
        module load colabfold
        colabfold_batch {input_fasta} {output_dir}
        """

        # Save it to a temporary file
        with open("run_colabfold.sh", "w") as file:
            file.write(bash_script)

        # Make the script executable
        subprocess.run("chmod +x run_colabfold.sh", shell=True, check=True)

        try:
            result = subprocess.run("./run_colabfold.sh", shell=True, check=True, capture_output=True, text=True)
            print(result.stdout)  # To print the standard output
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            print(f"Standard output: {e.stdout}")
            print(f"Standard error: {e.stderr}")  # This will show you the actual error
    except subprocess.CalledProcessError as e:
        print(f"Error executing commands: {e}")

def create_folder(directory_path):
    # Check if the folder exists; if not, create it
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"Folder created: {directory_path}")
    else:
        print(f"Folder already exists: {directory_path}")

def process_fastas(input_fasta_dir, output_base_dir):
    # Get all the FASTA files in the input directory
    fasta_files = glob.glob(os.path.join(input_fasta_dir, "*.fasta"))
    
    if not fasta_files:
        print(f"No FASTA files found in {input_fasta_dir}")
        return

    # Iterate through each FASTA file and create an output folder for it
    for fasta_file in fasta_files:
        # Extract the base name of the FASTA file (without the path and extension)
        fasta_basename = os.path.basename(fasta_file).replace(".fasta", "")

        # Create a corresponding output folder for this FASTA file
        output_dir = os.path.join(output_base_dir, fasta_basename)
        create_folder(output_dir)

        # Run the colabfold for this specific FASTA file
        run_colabfold(fasta_file, output_dir)


# Example usage
if __name__ == "__main__":
    # Set input FASTA directory and output base directory
    input_fasta_dir = "path/to/input/fasta"
    output_base_dir = "path/to/output/directory"

    # Create base output folder if it doesn't exist
    create_folder(output_base_dir)

    # Process each FASTA file and create an output folder for each
    process_fastas(input_fasta_dir, output_base_dir)




