# EECT-EEI-Calculation
"Python and Google Earth Engine scripts for calculating the Ecological Entropy Index (EEI)."
# EECT-EEI Calculation
This repository contains scripts for calculating the Ecological Entropy Index (EEI) as part of the Entropy-Ecological Cycles Theory (EECT).

## Files
- `eei_calculation.py`: Python script for Sobol sensitivity analysis, SHAP, and EEI computation.
- `eei_dashboard.js`: Google Earth Engine script for real-time EEI monitoring dashboard.

## Requirements
- Python: pandas, numpy, scipy, SALib, xgboost, shap
- Google Earth Engine: ee, geemap

## Usage
1. Run `eei_calculation.py` to compute EEI and generate Figures 5 and 6.
2. Run `eei_dashboard.js` in Google Earth Engine to create the dashboard (Figure 4).
