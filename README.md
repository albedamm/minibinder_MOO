# Multi-Objective Optimization of minibinders

# Table of Contents

1. [Multi-Objective Optimization of minibinders](#multi-objective-optimization-of-minibinders)
   - [Overview](#overview)
2. [Technologies Used](#technologies-used)
3. [Project Structure](#project-structure)
   - [Source Code (`/src`)](#source-code-src)
   - [Data (`/data`)](#data-data)
4. [How to Run the Pipeline](#how-to-run-the-pipeline)
   - [Initial Binder Design](#initial-binder-design)
     - [Binder Design Using RFdiffusion](#binder-design-using-rfdiffusion)
       - [Defining the Input Target](#defining-the-input-target)
       - [Constraining miBd Length](#constraining-mibd-length)
     - [Binding Interface Definition](#binding-interface-definition)
   - [Partial Diffusion](#partial-diffusion)


## Overview

This GitHub serves as a personal archive of our work for our bachelorproject, "Design and Optimization of Multitarget Protein-Protein Binders".

## Technologies Used

- [Python](https://github.com/python)
- [ProteusAI](https://github.com/jonfunk21/ProteusAI/)
- [BoTorch](https://github.com/pytorch/botorch)
- [Pandas](https://github.com/pandas-dev/pandas)

## Project Structure

/src: Main source code.  
/data: Data used in the project.

## How to run the pipeline

### Binder design using RFdiffusion [^1]

Defining the Input Target:

- The predicted pMHC complex structure is provided as the input target using the parameter:
    ```
    inference.input_pdb=NLFR_complex.pdb
    ```

Constraining miBd Length:

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

### Binding Interface Definition

Marking Residues as Hotspots:

- To define the binding interface, the residues of the NLFR peptide are marked as hotspots using:
    ```
    ppi.hotspot_res=[C1,C2,C3,C4,C5,C6,C7,C8,C9]
    ```

- Explanation:
    - `C` refers to the peptide chain.
    - Numbers represent specific residues within the chain.


[^1]: [RFdiffusion GitHub](https://github.com/RosettaCommons/RFdiffusion)


### Partial diffusion