#!/bin/bash
set -e

# ---------- User Input ----------
IMT="PGA"
T="1_000" # FOR SA ONLY (will be ignored for other IMT)
NUM_GMFs=10
POIS_FILE="grid.txt"
IMT_MIN=0.001
IMT_MAX=1.0
BUFFER=1

WORK_DIR=$(pwd)
echo "WORK_DIR: $WORK_DIR"

# Load Conda
source [your_path]/conda.sh


# ----------  Run ProbShakemap ----------

echo  "-----------------------"
echo  "Running ProbShakemap..."
echo  "-----------------------"

conda activate probshakemap

if [[ "$IMT" == "SA" ]]; then
    T_FLOAT="${T/_/.}"  # Convert 1_000 -> 1.000
    IMT_STR="SA(${T_FLOAT})"
else
    IMT_STR="$IMT"
fi

echo "Running with IMT: $IMT_STR"

# ---------- Tool ----------

echo "Tool: StationRecords"
python ../../ProbShakemap.py --imt "$IMT_STR" --tool StationRecords --imt_min "$IMT_MIN" --imt_max "$IMT_MAX" --station_file stationlist.json


# ---------- Prob tools ----------

echo "Prob tool: GetStatistics"
python ../../ProbShakemap.py --imt "$IMT_STR" --prob_tool GetStatistics --pois_file "$POIS_FILE" --numGMPEsRealizations "$NUM_GMFs" --imt_min "$IMT_MIN" --imt_max "$IMT_MAX" --vector_npy --buffer "$BUFFER"

echo "Prob tools: GetDistributions"
python ../../ProbShakemap.py --imt "$IMT_STR" --prob_tool GetDistributions --pois_file "$POIS_FILE" --numGMPEsRealizations "$NUM_GMFs" \
    --imt_min "$IMT_MIN" --imt_max "$IMT_MAX" --station_file stationlist.json --buffer "$BUFFER" \
    --pois_subset --n_pois 12 --max_distance 50 --pois_selection_method azimuth_uniform

echo "Prob tool: EnsemblePlot"
python ../../ProbShakemap.py --imt "$IMT_STR" --prob_tool EnsemblePlot --pois_file "$POIS_FILE" --numGMPEsRealizations "$NUM_GMFs" --reuse_pois_subset --buffer "$BUFFER"

conda deactivate
