import os
import biotite.structure.io.pdbx as pdbx
import biotite.structure.io.pdb as pdb

class CifToPdb:
    def __init__(self, input_folder, output_folder):
        """
        Initialize the converter with input and output folders.

        Args:
            input_folder (str): Path to the folder containing CIF files.
            output_folder (str): Path to save the converted PDB files.
        """
        self.input_folder = input_folder
        self.output_folder = output_folder

        # Ensure the output folder exists
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

    def cif_to_pdb(self, input_cif, output_pdb):
        """
        Convert a CIF file to a PDB file.

        Args:
            input_cif (str): Path to the input CIF file.
            output_pdb (str): Path to save the output PDB file.
        """
        if input_cif.endswith(".cif"):
            cif_file = pdbx.PDBxFile.read(input_cif)
            structure = pdbx.get_structure(cif_file)
            
            # Save the structure as a PDB file
            pdb_file = pdb.PDBFile()
            pdb_file.set_structure(structure)
            pdb_file.write(output_pdb)
            print(f"Converted {input_cif} to {output_pdb}")
        else:
            print(f"Skipped {input_cif} - does not match '.cif' pattern.")

    def convert_all_cifs(self):
        """
        Convert all CIF files ending with '.cif' in the input folder
        to PDB files, saving them in the output folder.
        """
        # Iterate over files in the input folder
        for file_name in os.listdir(self.input_folder):
            if file_name.endswith(".cif"):
                input_cif = os.path.join(self.input_folder, file_name)
                output_pdb = os.path.join(self.output_folder, file_name.replace(".cif", ".pdb"))
                self.cif_to_pdb(input_cif, output_pdb)

# Usage Example:
# if __name__ == "__main__":
#     converter = CifToPdbConverter(input_folder="data/NLFR_target", output_folder="data/NLFR_target/pdb")
#     converter.convert_all_superimposed_cifs()

