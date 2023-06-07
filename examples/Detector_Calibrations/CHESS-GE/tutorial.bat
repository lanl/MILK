@echo off

: 1D and 2D (caking) integration using MILKs multigeometry pyFAI tool
echo "Doing the integration"
milk-integrate ^
    "calibration_files/CeO2_126.tif" ^
    --json "1d.azimint.json" ^
    --output "results" ^
    --overwrite ^
    --poolsize 1 ^
    --format "esg" ^
    --histogram_plot

milk-integrate ^
    "calibration_files/CeO2_126.tif" ^
    --json "2d.azimint.json" ^
    --output "results" ^
    --overwrite ^
    --poolsize 1 ^
    --format "esg1" "esg_detector" ^
    --histogram_plot

: Load data into MAUD parameter files
echo ""Loading data into MAUD parameter files
milk-esg-loader ^
    --interface command ^
    --maud-input-par "templates/detector_ang_cal.par" ^
    --maud-detectors "det0" ^
    --esg-files "results/CeO2_126_det0_2d.esg" ^
    --poni-files "calibration_files/det0.poni" ^
    --maud-output-par "Detector_ang_cal_2d.par" ^
    --maud-run-import

milk-esg-loader ^
    --interface command ^
    --maud-input-par "templates/no_ang_cal.par" ^
    --maud-detectors "det0" ^
    --esg-files "results/CeO2_126_2d.esg" ^
    --maud-output-par "No_ang_cal_2d.par" ^
    --maud-run-import
    
milk-esg-loader ^
    --interface command ^
    --maud-input-par "templates/no_ang_cal.par" ^
    --maud-detectors "det0" ^
    --esg-files "results/CeO2_126.esg" ^
    --maud-output-par "No_ang_cal_1d.par" ^
    --maud-run-import

echo "starting  MAUD calibration refinements" 
echo "for No_ang_cal_1d.par"
python refine_no_ang_cal.py "No_ang_cal_1d.par"
echo "for No_ang_cal_2d.par"
python refine_no_ang_cal.py "No_ang_cal_2d.par"
echo "for Detector_ang_cal_2d.par"
python refine_detector_ang_cal.py "Detector_ang_cal_2d.par"

: Cleanup a little
echo "Cleaning up"
del *.lst 
del *.log
del *.err
Del *.ins
del results.txt