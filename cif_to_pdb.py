import os
import biotite.structure.io.pdbx as pdbx
import biotite.structure.io.pdb as pdb

def cif_to_pdb(input_cif, output_pdb):
    """
    Convert a CIF file to a PDB file.

    Args:
        input_cif (str): Path to the input CIF file.
        output_pdb (str): Path to save the output PDB file.
    """
    # Ensure the file ends with "superimposed.cif"
    if input_cif.endswith(".cif"):
        # Load the CIF structure
        cif_file = pdbx.PDBxFile.read(input_cif)
        structure = pdbx.get_structure(cif_file)
        
        # Save the structure as a PDB file
        pdb_file = pdb.PDBFile()
        pdb_file.set_structure(structure)
        pdb_file.write(output_pdb)
        print(f"Converted {input_cif} to {output_pdb}")
    else:
        print(f"Skipped {input_cif} - does not match 'superimposed.cif' pattern.")

def convert_all_superimposed_cifs(input_folder, output_folder):
    """
    Convert all CIF files ending with 'superimposed.cif' in a folder to PDB files,
    saving them in a specified output folder.

    Args:
        input_folder (str): Path to the folder containing CIF files.
        output_folder (str): Path to save the converted PDB files.
    """
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Iterate over files in the input folder
    for file_name in os.listdir(input_folder):
        if file_name.endswith(".cif"):
            input_cif = os.path.join(input_folder, file_name)
            output_pdb = os.path.join(output_folder, file_name.replace(".cif", ".pdb"))
            cif_to_pdb(input_cif, output_pdb)

# Run the conversion function on an input folder and specify an output folder
input_folder = "data/NLFR_target"
output_folder = "data/NLFR_target/pdb"
convert_all_superimposed_cifs(input_folder, output_folder)
