# Repository structure

## Raw Data

The [data/raw](data/raw) folder stores data derived and aggregated from manifest files located in [manifest/expression_data/](manifest/expression_data/) and [manifest/clinical_data/](manifest/clinical_data/) folders.

### To update manifest files, execute this notebook:
- [1.0_generate_manifest_files.ipynb](1.0_generate_manifest_files.ipynb)

### To generate raw data files for each TCGA project, run notebooks below:
- [2.0_download_expression_data.ipynb](2.0_download_expression_data.ipynb)
- [3.0_download_clinical.ipynb](3.0_download_survival_data.ipynb)


### File Descriptions

1) **TCGA-{project}.csv**: This is a gene expression matrix with rows representing sample IDs. Each row may represent a tumor, normal, or control sample, as discerned from the sample ID (refere to this [link](https://docs.gdc.cancer.gov/Encyclopedia/pages/TCGA_Barcode/) for more info). Tumor types are indicated by codes 01 - 09, normal types by codes 10 - 19, and control samples by codes 20 - 29. The columns represent gene expression values (TPMs), limited to protein-coding genes (modify [this notebook](2.0_download_expression_data.ipynb) if needed).

2) **TCGA-{project}-survival.csv**: This file contains overall survival data. It consists of three columns; Sample ID, Overall Survival Time, and Event Indicator (where 1 signifies a death event). This file may contain more samples than the gene expression matrix, due to some samples in the GDC database lacking expression data. These files will need to be synchronized by IDs during the preprocessing of raw data.