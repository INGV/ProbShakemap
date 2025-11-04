#!/bin/bash
set -e

# ---------- User Input ----------
IMT="PGA"
T="1_000" # FOR SA ONLY (will be ignored for other IMT)
N_SCENS=1000
NUM_GMFs=10
PROC=8
POIS_FILE="grid.txt"
IMT_MIN=0.001
IMT_MAX=1.0
BUFFER=1

HOME_DIR=$(pwd)
echo "HOME_DIR: $HOME_DIR"

# Load Conda
source [your_path]/conda.sh


# ---------- Step 1: Run SeisEnsMan  ----------

# Comment lines 26-41 if the ensemble already exists

echo  "-----------------------------"
echo  "Step 1: Running SeisEnsMan..."
echo  "-----------------------------"
source [your_path]/SeisEnsMan/bin/activate   
cd ./SeisEnsManV2 || exit

mainFolder=$(pwd)
python write_json_file.py
python run_ens.py --cfg $mainFolder/input/main.config --event $mainFolder/input/event_stat.json --nb_scen "$N_SCENS" 
    
cd "$HOME_DIR" || exit

# OPTIONAL: --angles Strike Dip Rake 
# Example for Norcia event: --angles 151 47 -89

deactivate   


# ---------- Step 2: Run ProbShakemap ----------

echo  "------------------------------"
echo  "Step 2: Running ProbShakemap..."
echo  "------------------------------"

conda activate probshakemap

if [[ "$IMT" == "SA" ]]; then
    T_FLOAT="${T/_/.}"  # Convert 1_000 -> 1.000
    IMT_STR="SA(${T_FLOAT})"
else
    IMT_STR="$IMT"
fi

echo "Running with IMT: $IMT_STR"

# ######## Tools ########

# TOOL: 'StationRecords'
echo "Tool: StationRecords"
python ProbShakemap.py --imt "$IMT_STR" --tool StationRecords --imt_min "$IMT_MIN" --imt_max "$IMT_MAX" --station_file stationlist.json
# 
# # TOOL: 'Save_Output'
echo "Tool: Save_Output"
python ProbShakemap.py --imt "$IMT_STR" --tool Save_Output --num_processes  "$PROC" --pois_file "$POIS_FILE" --numGMPEsRealizations "$NUM_GMFs"
# 
# # TOOL: 'QueryHDF5'
echo "Tool: QueryHDF5"
python ProbShakemap.py --imt "$IMT_STR" --tool QueryHDF5 --scenario 50 --pois_file "$POIS_FILE"
# 
# 
# # ######## Prob_tools ########
# 
# # TOOL: 'GetStatistics'
echo "Tool: GetStatistics"
python ProbShakemap.py --imt "$IMT_STR" --prob_tool GetStatistics --num_processes "$PROC" --pois_file "$POIS_FILE" --numGMPEsRealizations "$NUM_GMFs" --imt_min "$IMT_MIN" --imt_max "$IMT_MAX" --vector_npy --buffer "$BUFFER"
# 
# # TOOL: 'GetDistributions'
echo "Tool: GetDistributions"
python ProbShakemap.py --imt "$IMT_STR" --prob_tool GetDistributions --num_processes "$PROC" --pois_file "$POIS_FILE" --numGMPEsRealizations "$NUM_GMFs" --imt_min "$IMT_MIN" --imt_max "$IMT_MAX" --station_file stationlist.json --reuse_pois_subset --buffer "$BUFFER"

# TOOL: 'EnsemblePlot'
echo "Tool: EnsemblePlot"
python ProbShakemap.py --imt "$IMT_STR" --prob_tool EnsemblePlot --num_processes "$PROC" --pois_file "$POIS_FILE" --numGMPEsRealizations "$NUM_GMFs" --reuse_pois_subset --buffer "$BUFFER"

# TOOL: ' GetDistributions & EnsemblePlot'
# Merge if applying to the same subset of POIs
# echo "Tool: GetDistributions & EnsemblePlot"
# python ProbShakemap.py --imt "$IMT_STR" --prob_tool GetDistributions EnsemblePlot --num_processes "$PROC" --pois_file "$POIS_FILE" --imt_min "$IMT_MIN" --imt_max "$IMT_MAX" --station_file stationlist.json --numGMPEsRealizations "$NUM_GMFs" --reuse_pois_subset --buffer "$BUFFER"
# 

conda deactivate
