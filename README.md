# Multi-Objective Optimization of minibinders

# Table of Contents

1. [Multi-Objective Optimization of minibinders](#multi-objective-optimization-of-minibinders)
   - [Overview](#overview)
2. [Technologies Used](#technologies-used)
3. [Project Structure](#project-structure)
4. [How to Run the Pipeline](#how-to-run-the-pipeline)
   - [Initial binder design](#initial-binder-design)
     - [Binder Design Using RFdiffusion](#binder-design-using-rfdiffusion-1)
     - [Partial Diffusion](#partial-diffusion)
   - [Cross-reactivity pipeline](#cross-reactivity-pipeline)
     - [Structural Alignment of Minibinders With New Targets](#structural-alignment-of-minibinders-with-new-targets)
     - [Refold using AF2](#refold-using-af2-2)
   - [Binder optimization](#binder-optimization)
     - [Mutation and prediction of binders using ProteusAI](#mutation-and-prediction-of-binders-using-proteusai-3)
   - [Computing the Pareto front]()



## Overview

This GitHub serves as a personal archive of our work for our bachelorproject, "Design and Optimization of Multitarget Protein-Protein Binders".

## Technologies Used

- [Python](https://github.com/python)
- [ProteusAI](https://github.com/jonfunk21/ProteusAI/)
- [BoTorch](https://github.com/pytorch/botorch)
- [Pandas](https://github.com/pandas-dev/pandas)

## Project Structure

`/src`: Main source code.  
`/data`: Data used in the project.

# How to run the pipeline

## Initial binder design


### Binder design using RFdiffusion [^1]

Initial binders were designed using the `src/gbar/RFdiffusion_submit.sh` script.

#### Defining the Input Target:

- The predicted pMHC complex structure is provided as the input target using the parameter:
    ```
    inference.input_pdb=NLFR_complex.pdb
    ```

#### Constraining miBd Length:

- The designed miBds are constrained to a length between 100 and 150 residues using:
    ```
    contigmap.contigs=[A1-276/0 B1-100/0 C1-9/0 100-150]
    ```

- Breakdown of the contig definition:
    - `A1-276/0`: Represents the HLA class I chain.
    - `B1-100/0`: Represents the Beta-2-microglobulin.
    - `C1-9/0`: Represents the target peptide.
    - `100-150`: Defines the miBd chain length constraint.
    - Chain breaks are indicated using `/0`.

#### Binding Interface Definition

Marking Residues as Hotspots:

- To define the binding interface, the residues of the NLFR peptide are marked as hotspots using:
    ```
    ppi.hotspot_res=[C1,C2,C3,C4,C5,C6,C7,C8,C9]
    ```

- Explanation:
    - `C` refers to the peptide chain.
    - Numbers represent specific residues within the chain.




### Partial diffusion

Partial diffusion was applied to further optimize the most promising miBds from the RFdiffusion campaign. This process introduces diversity to the initial fold of the miBds by partially noising their backbones and then denoising them.

Partial diffusion was done using the `src/gbar/partial_submit.sh` script.

#### Input Requirements:
The input for partial diffusion is the PDB file of the miBd structure in complex with NLFR/HLA-B*08:01, generated using AlphaFold2 (AF2).

#### Configuration Details

- Contig Definition:
    - Use the following configuration for defining the chains:
    ```
    contigmap.contigs=[116-116/0 B117-501]
    ```

    - Breakdown of the contig definition:
        - `116-116/0`: Represents the miBd chain.
        - `B117-501`: Represents the target chain (NLFR/HLA-B*08:01 complex).

#### Noising Steps:

- The amount of noising introduced is controlled by the parameter:
```
diffuser.partial_T=20
```
- In this case, 20 noising steps were applied to refine the miBds.



## Cross-reactivity pipeline


### Structural Alignment of Minibinders With New Targets

- Align off-target structures with the original target using PyMol v3.0.3 to maintain binding site orientation.
    - Script used: `src/local/align_script_multichain_target.py`
    - Script inputs:
        - Minibinder/target complex `.pdb` file.
        - Directory containing `.pdb`files for new targets.


### Refold using AF2 [^2]

- Use AlphaFold2 (AF2) inital guess to refold miBds with off-target pMHCs:
    - Script used: `src/gbar/af2_init.sh`
    - Script inputs:
        - `.pdb` file of new minibinder/target complexes.


## Binder optimization 
### Mutation and prediction of binders using ProteusAI [^3]

Mutations and predictions were made using `src/studentmachine/predict.py`

#### Input Requirements:
The input is a CSV file containing binder name, sequence and ipAE score for different targets

- Defining the input CSV file: 
```
df = pd.read_csv('data/NLFR_master_dataset_1000.csv')
```

#### Configuration Details

- Specify the type of protein representation:
```
x_type = 'esm2'
```
- Other options include `blosum62` and `ohe`.

- Creating a library
```
lib = pai.Library(source='data/NLFR_master_dataset_1000.csv', names_col='name', seqs_col='binder_seq', y_col=y_col, y_type='num')
```
- Define the column containing the name and sequence

- Creating a model from the library:
```
model = pai.Model(library=lib, x=x_type, model_type='ridge', k_folds=5)
```
- `model_type`: Specifies the surrogate model type. Options include `ridge`, `rf`, and `gp`.
- `k_folds`: Defines the number of cross-validation folds for model training.

- Performing a search on the data from the first column of the input file
```
search_out = first_model.search(optim_problem=first_task, acq_fn='ucb', explore=1.0) # explore 1.0 will test all mutations
```
- Options for the acquisition function include `ucb` and `ei` 
- `explore`: Defines the level of exploration, if 1 the mutation will be random

- Performing predictions for the other targets
```
val_data, y_val_pred, y_val_sigma, y_val, sorted_acq_score = model.predict(predicted_proteins, acq_fn='ucb')
```
- Same acquisition function as used in the search step.


### Computing the Pareto front

The Pareto front was computed using `src/studentmachine/pareto_analysis.py`

#### Tools and Functions Used
BoTorch Library:
- The `is_non_dominated` function from `botorch.utils.multi_objective.pareto` was used to identify Pareto-optimal sequences.
- This function determines sequences that are not dominated in at least one optimization objective, yielding the set of Pareto-optimal trade-offs.

#### Input Data
    - The input for this step is a CSV file containing:
        - Binder Details:
        - Binder name
        - Sequence
        - Predicted ipAE scores for all targets (A, B, C, D, E)

#### Objective Definitions
- Two types of objectives were defined:
    - Minimization Objective:
        - Minimize the ipAE score for target A to enhance specificity.
    - Maximization Objectives:
        - Maximize ipAE scores for off-targets B, C, D, and E to reduce cross-reactivity.
```
for i in range(len(old_pAE_cols)):
    # Prepare objectives
    objectives = torch.tensor(df_old[old_pAE_cols].values, dtype=torch.float32)
    
    objectives[:, 0] *= -1
    
    if i != 0:
        objectives[:, i] *= 1

    # Find Pareto optimal points for the current main objective
    pareto_mask = is_non_dominated(objectives)
    pareto_indices_sets.append(set(np.where(pareto_mask.numpy())[0]))
```

- The ipAE scores for target A were negated to adapt to the is_non_dominated function’s default assumption of maximization.
- The ipAE scores for off-targets B, C, D, and E were left unchanged.



## Resources:
[^1]: [RFdiffusion GitHub](https://github.com/RosettaCommons/RFdiffusion)  
[^2]: [AF2 inital guess protocol](https://www.nature.com/articles/s41467-023-38328-5)  
      [Protocol GitHub](https://github.com/nrbennet/dl_binder_design)
[^3]: [ProteusAI GitHub](https://github.com/jonfunk21/ProteusAI)
