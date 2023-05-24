#!/bin/bash

## 1D and 2D (caking) integration using MILKs multigeometry pyFAI tool
milk-integrate.py \
    "calibration_files/CeO2_126.tif" \
    --json "1d.azimint.json" \
    --output "results" \
    --overwrite \
    --poolsize 1 \
    --format "esg" \
    --histogram_plot

milk-integrate.py \
    "calibration_files/CeO2_126.tif" \
    --json "2d.azimint.json" \
    --output "results" \
    --overwrite \
    --poolsize 1 \
    --format "esg1" "esg_detector"\
    --histogram_plot

## Load data into MAUD parameter files
milk-esg-loader.py \
    --interface command \
    --maud-input-par "templates/detector_ang_cal.par" \
    --maud-detectors "det0" \
    --esg-files "results/CeO2_126_det0_2d.esg" \
    --poni-files "calibration_files/det0.poni" \
    --maud-output-par "Detector_ang_cal_2d.par" \
    --maud-run-import

milk-esg-loader.py \
    --interface command \
    --maud-input-par "templates/no_ang_cal.par" \
    --maud-detectors "det0" \
    --esg-files "results/CeO2_126_2d.esg" \
    --maud-output-par "No_ang_cal_2d.par" \
    --maud-run-import
    
milk-esg-loader.py \
    --interface command \
    --maud-input-par "templates/no_ang_cal.par" \
    --maud-detectors "det0" \
    --esg-files "results/CeO2_126.esg" \
    --maud-output-par "No_ang_cal_1d.par" \
    --maud-run-import

## Cleanup a little
rm *.lst 
rm *.log
rm *.err
rm *.ins
