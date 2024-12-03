import os
from pymol import cmd, stored

# Directory containing Structure 1 PDB files
binder_dir = "data/NLFR_moo/blosum_rf_ucb/pareto_2/new_pareto_blosum_rf_ucb_2_pdb"

# Directory containing Structure 2 PDB files
target_dir = "data/NLFR_bind_494/binder_pdbs"

# Directory to save the output combined structures
output_dir = "data/NLFR_moo/blosum_rf_ucb/pareto_2/HLA_B_0801_NLFRRVWEL"

def process_structure(binder_path, target_path, output_dir):
    # Extract full binder name with mutation info without file extension
    binder_name = os.path.splitext(os.path.basename(binder_path))[0]
    
    # Reinitialize PyMOL session to clear old data
    cmd.reinitialize()

    # Load both structures
    cmd.load(binder_path, "structure2")
    cmd.load(target_path, "structure1")

    # Remove water molecules and ligands from both structures
    cmd.remove("resn HOH")  # Remove water molecules
    cmd.remove("hetatm")    # Remove heteroatoms (commonly used to represent ligands)

    # Get the last residue number of chain A in structure 1
    last_resi_structure1 = cmd.get_model("structure1 and chain A").atom[-1].resi

    # Calculate offset for continuous residue numbering
    offset = int(last_resi_structure1) + 1

    # Alter chain ID of all residues in structure 2 to 'B'
    cmd.alter("structure2", "chain='A'")
    cmd.sort()

    # Update residue numbers in structure 2
    cmd.alter("structure1", f'resi=str(int(resi)+{offset}-1)')
    cmd.sort()

    # Additional operations to align and clean structures
    cmd.align("structure2", "structure1 and chain A")
    cmd.remove("structure1 and chain A")
    cmd.sort()


    # Create and save the combined structure with mutation info in the filename
    cmd.create(binder_name, "structure1 or structure2")
    output_path = os.path.join(output_dir, f"{binder_name}.pdb")
    cmd.save(output_path, binder_name)

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process each binder file and its corresponding complex file
for binder_filename in os.listdir(binder_dir):
    if binder_filename.endswith(".pdb"):
        binder_path = os.path.join(binder_dir, binder_filename)
        
        # Extract the base identifier (e.g., binder_[number])
        binder_id = binder_filename.split('_')[0] + "_" + binder_filename.split('_')[1]
        target_filename = f"{binder_id}.pdb"
        target_path = os.path.join(target_dir, target_filename)
        
        # Check if the corresponding complex file exists
        if os.path.exists(target_path):
            process_structure(binder_path, target_path, output_dir)
