# In Silico Genome Mining and Structural Characterization of Putative Entomopathogenic Toxins Against *Tecia solanivora*

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/)

## Overview
This repository contains the custom Python scripts and reproducible data-processing pipeline supporting the manuscript:

> **Forero Torres, D. F. (2026).** *In Silico Genome Mining and Structural Characterization of Novel Putative Entomopathogenic Toxins from Enterobacter ludwigii, Rahnella variigena, and Serratia quinivorans for the Biocontrol of Tecia solanivora.* Submitted to *Current Microbiology* (Springer Nature).

The workflow screens uncharacterized hypothetical proteomes ($N = 721$) from three enterobacterial reference genomes (*Enterobacter ludwigii* `GCF_001750725.1`, *Rahnella variigena* `GCF_003610915.1`, and *Serratia quinivorans* `GCA_900638135.1`) to identify non-canonical pore-forming toxins and chitin-degrading virulence factors.

---

## Repository Structure

```text
tecia-solanivora-toxin-mining/
├── 01_filtrar_proteinas_hipoteticas.py    # Extracts hypothetical/uncharacterized ORFs from RefSeq FASTA files
├── 02_filtrar_secuencias.py               # Standardizes FASTA headers (>WP_...) for NGPhylogeny alignment
├── 03_organizar_datos_tabla2.py           # Generates formatted Table S2 (Hypothetical Protein Pool, N = 721)
├── 04_organizar_datos_articulos_tabla1.py # Parses Scopus CSV export into Table S1 (Systematic Literature Matrix)
├── 05_organizar_dominios_proteinas.py     # Consolidates NCBI Batch CD-Search outputs & COG classes (Table S3)
├── 06_organizar_dominos_toxinas.py        # Curates UniProtKB/Swiss-Prot reference toxins for phylogeny (Table S4)
├── environment.yml                        # Conda environment specification
└── README.md                              # Documentation and execution instructions
