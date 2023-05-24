#!/bin/bash

## 1D and 2D (caking) integration using MILKs multigeometry pyFAI tool
echo "Doing the integration"
milk-integrate.py \
    "calibration_files/ge1.tif" "calibration_files/ge2.tif" "calibration_files/ge3.tif" "calibration_files/ge4.tif" \
    --json "1d.azimint.json" \
    --output "results" \
    --overwrite \
    --poolsize 1 \
    --format "esg" \
    --histogram_plot

milk-integrate.py \
    "calibration_files/ge1.tif" "calibration_files/ge2.tif" "calibration_files/ge3.tif" "calibration_files/ge4.tif" \
    --json "2d.azimint.json" \
    --output "results" \
    --overwrite \
    --poolsize 1 \
    --format "esg1" "esg_detector"\
    --histogram_plot

# ## Load data into MAUD parameter files
# echo ""Loading data into MAUD parameter files
milk-esg-loader.py \
    --interface command \
    --maud-input-par "templates/detector_ang_cal.par" \
    --maud-detectors "det0" "det1" "det2" "det3" \
    --esg-files "results/ge1_det0_2d.esg" "results/ge1_det1_2d.esg" "results/ge1_det2_2d.esg" "results/ge1_det3_2d.esg"\
    --poni-files "calibration_files/ge1.poni" "calibration_files/ge2.poni" "calibration_files/ge3.poni" "calibration_files/ge4.poni" \
    --maud-output-par "Detector_ang_cal_2d.par" \
    --maud-run-import

milk-esg-loader.py \
    --interface command \
    --maud-input-par "templates/no_ang_cal.par" \
    --maud-detectors "det0" \
    --esg-files "results/ge1_2d.esg" \
    --maud-output-par "No_ang_cal_2d.par" \
    --maud-run-import
    
milk-esg-loader.py \
    --interface command \
    --maud-input-par "templates/no_ang_cal.par" \
    --maud-detectors "det0" \
    --esg-files "results/ge1.esg" \
    --maud-output-par "No_ang_cal_1d.par" \
    --maud-run-import

echo "starting  MAUD calibration refinements" 
echo "for No_ang_cal_1d.par"
python refine_no_ang_cal.py "No_ang_cal_1d.par"
echo "for No_ang_cal_2d.par"
python refine_no_ang_cal.py "No_ang_cal_2d.par"
echo "for Detector_ang_cal_2d.par"
python refine_detector_ang_cal.py "Detector_ang_cal_2d.par"

## Cleanup a little
echo "Cleaning up"
rm *.lst 
rm *.log
rm *.err
rm *.ins
rm results.txt