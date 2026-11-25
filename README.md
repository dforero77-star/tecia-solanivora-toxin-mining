# In Silico Genome Mining and Structural Characterization of Putative Entomopathogenic Toxins Against *Tecia solanivora*

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

## Overview
This repository contains the reproducible bioinformatics pipeline, Python scripts, and processed datasets supporting the manuscript:

> **Forero Torres, D. F. (2026).** *In Silico Genome Mining and Structural Characterization of Novel Putative Entomopathogenic Toxins from Enterobacter ludwigii, Rahnella variigena, and Serratia quinivorans for the Biocontrol of Tecia solanivora.* Submitted to *Current Microbiology* (Springer Nature).

The workflow screens uncharacterized hypothetical proteomes ($N = 721$ ORFs) from three enterobacterial reference genomes (*Enterobacter ludwigii* `GCF_001750725.1`, *Rahnella variigena* `GCF_003610915.1`, and *Serratia quinivorans* `GCA_900638135.1`) to identify non-canonical pore-forming toxins and chitin-degrading virulence factors.

---

## Repository Structure

```text
tecia-solanivora-toxin-mining/
├── 01_clean_fasta_headers.py        # Extracts hypothetical ORFs and standardizes FASTA headers for NGPhylogeny
├── 02_filter_cdsearch_evalue.py     # Filters NCBI Batch CD-Search hits (E-value < 1e-5) and assigns COG classes
├── 03_plot_cog_distribution.py      # Generates publication-ready 300 DPI multi-panel SVG figures (Arial font)
├── environment.yml                  # Conda environment specification for full reproducibility
└── README.md                        # Pipeline documentation and usage instructions