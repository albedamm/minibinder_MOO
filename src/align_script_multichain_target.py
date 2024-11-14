import os
from pymol import cmd, stored

# Directory containing Structure 1 PDB files
binder_dir = "data/NLFR_partial/partial_pdbs"

# Directory containing Structure 2 PDB files
target_dir = "data/NLFR_target/HLA_A_0201_NLFRRVWEV"

# Directory to save the output combined structures
output_dir = "data/NLFR_moo/blosum_rf_ucb/pareto_2/HLA_B_0801"

def process_structure(binder_path, target_path, output_dir):
    # Extract base names without file extension
    binder_name = os.path.splitext(os.path.basename(binder_path))[0]
    binder_parts = binder_name.split('_')
    target_name = os.path.splitext(os.path.basename(target_path))[0]
    combined_name = f"_{target_name}"
    # For 1. iteration
    #combined_name = f"{binder_parts[0]}_{binder_parts[1]}_{binder_parts[2]}_{target_name}"
    # For 2. iteration
    # combined_name = f"{binder_parts[0]}_{binder_parts[1]}_{binder_parts[2]}_{binder_parts[3]}_{target_name}"
    # For 3. iteration
    # combined_name = f"{binder_parts[0]}_{binder_parts[1]}_{binder_parts[2]}_{binder_parts[3]}_{binder_parts[4]}_{target_name}"
    
    # Reinitialize PyMOL session to clear old data
    cmd.reinitialize()

    # Load both structures
    cmd.load(binder_path, "structure1")
    cmd.load(target_path, "structure2")

    # Remove water molecules and ligands from both structures
    cmd.remove("resn HOH")  # Remove water molecules
    cmd.remove("hetatm")    # Remove heteroatoms (commonly used to represent ligands)

    # Get the last residue number of chain A in structure 1
    last_resi_structure1 = cmd.get_model("structure1 and chain A").atom[-1].resi

    # Calculate offset for continuous residue numbering
    offset = int(last_resi_structure1) + 1

    # Alter chain ID of all residues in structure 2 to 'B'
    cmd.alter("structure2", "chain='B'")
    cmd.sort()

    # Update residue numbers in structure 2
    cmd.alter("structure2", f'resi=str(int(resi)+{offset}-1)')
    cmd.sort()

    # Additional operations to align and clean structures
    cmd.align("structure2", "structure1 and chain B")
    cmd.remove("structure1 and chain B")
    cmd.sort()

    # Create and save the combined structure
    cmd.create(combined_name, "structure1 or structure2")
    output_path = os.path.join(output_dir, f"{combined_name}.pdb")
    cmd.save(output_path, combined_name)

    # Calculate RMSD between original chain B and new chain B in the aligned structure
    #rmsd = cmd.rms_cur("original_chain_B and name CA", f"{combined_name} and chain B and name CA")
    #print(f"RMSD between original chain B and new chain B in the aligned structure: {rmsd}")

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process each combination of PDB files from both directories
for binder_filename in os.listdir(binder_dir):
    if binder_filename.endswith(".pdb"):
        binder_path = os.path.join(binder_dir, binder_filename)
        for target_filename in os.listdir(target_dir):
            if target_filename.endswith(".pdb") or target_filename.endswith(".cif"):
                target_path = os.path.join(target_dir, target_filename)
                process_structure(binder_path, target_path, output_dir)