# Description: Script to align target structures with other targets 

import os
from pymol import cmd

# Define directories
binder_dir = "results/fold/494_sample/esm2_rf_ucb/uncertainty_3/HLA_A_0201_NLFRRVWEV"
target_dir = "data/NLFR_target/HLA_A_2402_NYFRRVWEF"
output_dir = "results/fold/494_sample/esm2_rf_ucb/uncertainty_3/HLA_A_2402_NYFRRVWEF"


def process_structure(binder_path, target_path, output_dir):
    # Extract base names without file extensions
    binder_name = os.path.splitext(os.path.basename(binder_path))[0]
    parts = binder_filename.split('_')
    target_name = os.path.splitext(os.path.basename(target_path))[0]

    # Construct combined name based on binder mutations
    if "HLA" in parts:  # Findng the 'HLA' keyword in the file name
        hla_index = parts.index("HLA")
        if hla_index == 3:  # Single mutation case
            combined_name = "_".join(parts[:3])
        elif hla_index == 4:  # Double mutation case
            combined_name = "_".join(parts[:4])
        elif hla_index == 5:  # Triple mutation case
            combined_name = "_".join(parts[:5])
        else:
            raise ValueError("Unexpected filename format for mutations.")
    else:
        raise ValueError("Filename does not contain 'unrelaxed' as expected.")
    # Create name with binder number, mutations and target name
    combined_name = f"{combined_name}_{target_name}"
    #print(f"Processing: {combined_name}")

    # Reinitialize PyMOL session
    cmd.reinitialize()

    # Load structures
    cmd.load(binder_path, "structure1")
    cmd.load(target_path, "structure2")

    # Remove unwanted molecules
    cmd.remove("resn HOH")
    cmd.remove("hetatm")

    # Get last residue number from structure1
    try:
        last_resi_structure1 = cmd.get_model("structure1 and chain A").atom[-1].resi
        offset = int(last_resi_structure1) + 1
    except IndexError:
        print(f"Error: No atoms found in chain A of {binder_path}.")
        return

    # Adjust chain ID and residue numbering for structure2
    cmd.alter("structure2", "chain='B'")
    cmd.alter("structure2", f"resi=str(int(resi)+{offset}-1)")
    cmd.sort()
    
    # Additional operations to align and clean structures
    cmd.align("structure2", "structure1 and chain B")
    cmd.remove("structure1 and chain B")
    cmd.sort()

    # Combine structures
    cmd.create(combined_name, "structure1 or structure2")
    output_path = os.path.join(output_dir, f"{combined_name}.pdb")
    cmd.save(output_path, combined_name)
    #print(f"Saved: {output_path}")


# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Process PDB files
for binder_filename in os.listdir(binder_dir):
    if binder_filename.endswith(".pdb"):
        binder_path = os.path.join(binder_dir, binder_filename)
        for target_filename in os.listdir(target_dir):
            if target_filename.endswith((".pdb", ".cif")):
                target_path = os.path.join(target_dir, target_filename)
                process_structure(binder_path, target_path, output_dir)
