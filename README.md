# Switchable Exchange Bias Resulting From Correlated Domain Structures in Orthogonally Coupled Antiferromagnet/Ferromagnet van der Waals Heterostructures

**Kumar, A.**, Hameed, S., Denneulin, T., Balan, A. P., Vas, J., Leutner, K., Gao, L., Gomonay, O., Sinova, J., Dunin-Borkowski, R. E., & Kläui, M.  
*Small* **21**, e06284 (2025). DOI: [10.1002/smll.202506284](https://doi.org/10.1002/smll.202506284)

---

## Overview

This repository contains the experimental data and analysis code supporting the above publication. We study exchange bias (EB) in Fe₃GeTe₂ (FGT) / CrSBr van der Waals heterostructures using Anomalous Hall Effect (AHE) transport measurements. The code quantifies the exchange bias field H_EB and coercive width W as a function of temperature and field-cooling protocol, and characterises domain structures in the heterostructure through Raman, SQUID, and AFM measurements.

---

## Repository structure

```
EB-in FGT-CrSBr/
├── data/                           # Raw measurement files
│   ├── T vs EB/                    # AHE hysteresis loops vs temperature
│   ├── Minor loops/                # Minor loop measurements
│   ├── Training effect/            # Training effect measurements
│   ├── Raman/                      # Raman spectra (.txt)
│   ├── SQUID_Bulk_CrSBr/          # SQUID magnetometry data
│   ├── AFM/                        # AFM topography files
│   └── Theoretical calculations by Helen/  # Calculated magnetization profiles
├── results/                        # Intermediate CSV outputs (read by notebooks)
├── notebooks/                      # Jupyter notebooks — one per analysis topic
│   ├── EB at 10 K.ipynb            # EB hysteresis at 10 K (sample 1)
│   ├── EB at 10 K sample 3.ipynb  # EB hysteresis at 10 K (sample 3)
│   ├── EB_vs_T_PF2500mT.ipynb     # EB vs T, positive field cooling (+2.5 T)
│   ├── EB_vs_T_PFM2500mT.ipynb    # EB vs T, negative field cooling (−2.5 T)
│   ├── HEB_and_W_vs_T.ipynb       # Summary: H_EB and W vs temperature
│   ├── Minor_loops_wPF.ipynb      # Minor loops with prior field
│   ├── Training_effect_PF2500mT.ipynb  # Training effect
│   ├── Raman_FGT_CrSBr.ipynb     # Raman characterisation
│   ├── SQUID_Bulk_MvsH.ipynb     # SQUID bulk magnetometry (CrSBr)
│   ├── AFM line cuts.ipynb        # AFM topography line profiles
│   ├── Theory_CrSBr hysteresis calculation.ipynb
│   ├── Theory_CrSBr_magnetization profile along c.ipynb
│   └── Theory_M_FM_and_AFM_along_Z.ipynb
├── scripts/                        # Installable Python package
│   ├── data_loader.py              # AHE_hysteresis class (HDF5 + .txt reader)
│   ├── ahe_collection.py          # AHE_Collection batch loader
│   └── utils/
│       └── notebook_setup.py      # setup_notebook(), Okabe-Ito palette
├── pyproject.toml
├── requirements.txt
├── LICENSE                         # MIT (code)
└── LICENSE-DATA                    # CC BY 4.0 (data/)
```

---

## Installation

Clone the repository and install the `scripts` package in editable mode:

```bash
git clone https://github.com/sadityakr/EB-in-FGT_CrSBr-vdW-heterostructure.git
cd "EB-in FGT-CrSBr"
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
pip install -e .
```

---

## Usage

Open the notebooks in the order that matches the analysis you want to reproduce:

| Notebook | What it produces |
|---|---|
| `EB at 10 K.ipynb` | Hysteresis loops and H_EB at 10 K |
| `EB_vs_T_PF2500mT.ipynb` | H_EB and W vs T (positive FC); saves CSV to `results/` |
| `EB_vs_T_PFM2500mT.ipynb` | H_EB and W vs T (negative FC); saves CSV to `results/` |
| `HEB_and_W_vs_T.ipynb` | Summary figures (reads the two CSVs above) |
| `Minor_loops_wPF.ipynb` | Minor loop analysis |
| `Training_effect_PF2500mT.ipynb` | Training effect |
| `Raman_FGT_CrSBr.ipynb` | Raman spectra of FGT and CrSBr |
| `SQUID_Bulk_MvsH.ipynb` | M vs H for bulk CrSBr (all axes) |
| `AFM line cuts.ipynb` | AFM topography line cuts |
| `Theory_*.ipynb` | Theoretical magnetization profiles |

**Note:** `HEB_and_W_vs_T.ipynb` depends on outputs from the two `EB_vs_T_*.ipynb` notebooks. Run those first if you want to regenerate the CSVs.

---

## Data formats

| Directory | Format | Reader |
|---|---|---|
| `data/T vs EB/` | HDF5 (`.hdf5`) and tab-delimited `.txt` | `AHE_hysteresis` in `scripts/data_loader.py` |
| `data/Minor loops/` | HDF5 / `.txt` | `AHE_hysteresis` |
| `data/Training effect/` | HDF5 / `.txt` | `AHE_hysteresis` |
| `data/Raman/` | Tab-delimited `.txt` (wavenumber, intensity) | `pandas.read_csv` |
| `data/SQUID_Bulk_CrSBr/` | Tab-delimited `.txt` (field, magnetization) | `pandas.read_csv` |
| `data/AFM/` | Line-cut `.txt` files | `pandas.read_csv` |
| `results/*.csv` | Columns: `T`, `HEB`, `W`, `C1`, `C2` | `pandas.read_csv` |

The `AHE_hysteresis` class auto-detects HDF5 vs text format and returns field (mT) and Hall voltage (µV) arrays with correct polarity.

---

## Citation

If you use this code or data, please cite:

```bibtex
@article{kumar2025switchable,
  author  = {Kumar, Aditya and Hameed, Sadeed and Denneulin, Thibaud and
             Balan, Aravind Puthirath and Vas, Joseph and Leutner, Kilian and
             Gao, Lei and Gomonay, Olena and Sinova, Jairo and
             Dunin-Borkowski, Rafal E. and Kl{\"{a}}ui, Mathias},
  title   = {Switchable Exchange Bias Resulting From Correlated Domain Structures
             in Orthogonally Coupled Antiferromagnet/Ferromagnet van der Waals
             Heterostructures},
  journal = {Small},
  volume  = {21},
  number  = {42},
  pages   = {e06284},
  year    = {2025},
  doi     = {10.1002/smll.202506284},
  url     = {https://doi.org/10.1002/smll.202506284},
  issn    = {1613-6810},
}
```

---

## License

| Component | License |
|---|---|
| Code (`notebooks/`, `scripts/`, `*.py`, `*.toml`) | [MIT License](LICENSE) |
| Data (`data/`) | [CC BY 4.0](LICENSE-DATA) |

**Data reuse requires attribution.** Any work that uses the data in `data/` must cite the paper:

> Kumar, A. et al., "Switchable Exchange Bias Resulting From Correlated Domain Structures in Orthogonally Coupled Antiferromagnet/Ferromagnet van der Waals Heterostructures", *Small* **21**, e06284 (2025). DOI: [10.1002/smll.202506284](https://doi.org/10.1002/smll.202506284)
