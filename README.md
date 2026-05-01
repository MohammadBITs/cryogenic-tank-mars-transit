# Cryogenic Propellant Storage — Earth-Mars Transit Thermal Analysis

## Overview
This project develops a parametric thermal model for liquid hydrogen (LH₂) 
storage aboard a spacecraft during a 240-day Earth-Mars transit. The model 
evaluates passive multi-layer insulation (MLI), active cryocooler cooling, 
and their combined effect on total system mass under a time-varying solar 
environment.

## Key Results
- Optimal design: 11 MLI layers with 110W active cooling
- Total system mass at optimum: 350 kg
- Passive-only boil-off over 240 days: 5,241 kg
- Active cooling boil-off: 583 kg — a saving of 4,658 kg of LH₂
- Zero boil-off achieved from day 111 onwards
- Constant-temperature assumptions underestimate boil-off by 2x compared 
  to the time-varying model

## Repository Contents
- `cryogenic_tank_mars_analysis.py` — complete parametric thermal model
- `figures/` — all 9 trade study graphs
- `report.pdf` — full technical report

## Dependencies
- Python 3.x
- numpy
- matplotlib

## How to Run
cryogenic_tank_mars_analysis.py
All 9 figures will be generated and saved automatically.

## Report
The full technical report is available in this repository and on Zenodo:
[DOI link — to be added after Zenodo upload]

## Author
Mohammad Shah
BITS Pilani
April 2026
