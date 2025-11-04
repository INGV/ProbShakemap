# ProbShakemap

`ProbShakemap` is a Python toolbox that propagates source uncertainty from an ensemble of earthquake scenarios to ground motion predictions at a grid of Points of Interest (POIs). It accounts for model uncertainty by accommodating multiple Ground Motion Models (GMMs) and their inherent variability. The output consists of a set of products aiding the user to explore and visualize the predictive distribution of ground motion at each target point. 
The package includes `SeisEnsMan`, a tool for generating event-compatible source scenario ensembles. Originally designed for Urgent Computing applications, `ProbShakemap` is versatile enough to be adapted for other uses, such as scenario-based seismic hazard assessments.

Dependencies
------------

 * [OpenQuake](https://github.com/gem/oq-engine/blob/master/README.md)
 
Command line usage
------------------
<pre>
usage: ProbShakemap.py [-h] [--imt IMT] [--tool {StationRecords,Save_Output,QueryHDF5}]
                       [--prob_tool {GetStatistics,GetDistributions,EnsemblePlot} [{GetStatistics,GetDistributions,EnsemblePlot} ...]]
                       [--numGMPEsRealizations NUMGMPESREALIZATIONS] [--num_processes NUM_PROCESSES]
                       [--imt_min IMT_MIN] [--imt_max IMT_MAX] [--station_file STATION_FILE]
                       [--scenario SCENARIO] [--pois_file POIS_FILE] [--pois_subset] [--n_pois N_POIS]
                       [--buffer BUFFER] [--max_distance MAX_DISTANCE]
                       [--pois_selection_method {random,azimuth_uniform}] [--reuse_pois_subset]
                       [--vector_npy] [--fileScenariosWeights FILESCENARIOSWEIGHTS]

ProbShakemap Toolbox

optional arguments:
  -h, --help            show this help message and exit

input params:
  --imt IMT             Intensity measure type (IMT). Possible choices: PGA, PGV, SA.
  --tool {StationRecords,Save_Output,QueryHDF5}
                        Tool(s) to use
  --prob_tool {GetStatistics,GetDistributions,EnsemblePlot} [{GetStatistics,GetDistributions,EnsemblePlot} ...]
                        ProbShakemap Tool(s) to use
  --numGMPEsRealizations NUMGMPESREALIZATIONS
                        Total number of GMPEs random samples
  --num_processes NUM_PROCESSES
                        Number of CPU cores for code parallelization
  --imt_min IMT_MIN     Minimum value for the selected IMT (for plot only)
  --imt_max IMT_MAX     Maximum value for the selected IMT (for plot only)
  --station_file STATION_FILE
                        Station file (.json, Shakemap-formatted)
  --scenario SCENARIO   Scenario number
  --pois_file POIS_FILE
                        Filename with latitude and longitude of POIs
  --pois_subset         Extract a subset of POIs
  --n_pois N_POIS       Number of POIs in the subset
  --buffer BUFFER       Buffer to control resolution in prob_tools maps
  --max_distance MAX_DISTANCE
                        Max distance from epicenter of POIs in the subset
  --pois_selection_method {random,azimuth_uniform}
                        Selection method for the POIs of the subset
  --reuse_pois_subset   Reuse the subset of POIs already extracted in POIs.txt
  --vector_npy          Store ground motion distributions at all POIs (vector.npy)
  --fileScenariosWeights FILESCENARIOSWEIGHTS
                        File with scenarios weights
</pre>                        
            
INSTALLATION
------------
To install `ProbShakemap`, clone the `ProbShakemap` repository to your local machine:

```bash
git clone https://github.com/INGV/ProbShakemap.git
```
Then, create and activate the `probshakemap` conda environment:

```bash
conda env create -f probshakemap_environment.yml -n probshakemap
conda activate probshakemap
```

The repository includes example input files (`INPUT_FILES`) and output (`OUTPUT_REPO`) from the Mw 6.5, 2016 October 30, Norcia Earthquake.

`SeisEnsMan` requires a separate virtual environment. To set it up, follow these steps:

```bash
python -m venv SeisEnsMan
```

On macOS and Linux:
```bash
source [path_to]SeisEnsMan/bin/activate
```

On Windows:
```bash
[path_to]SeisEnsMan\Scripts\activate
```
Navigate to the `SeisEnsManV2` folder and use the provided `requirements.txt` to install the necessary libraries:

```bash
python3 -m pip install -r requirements.txt
```


GETTING STARTED
---------------

To get started with `ProbShakemap`, make sure to provide all required input files in the folder `INPUT_FILES`:

1) `input_file.txt`

This file (do not rename) contains the necessary inputs for `OpenQuake`, including:

> * TectonicRegionType: as defined in OpenQuake tectonic regionalisation.
> * Magnitude_Scaling_Relationship: as required from openquake.hazardlib.scalerel.
> * Rupture_aratio: rupture aspect ratio as required from openquake.hazardlib.geo.surface.PlanarSurface.from_hypocenter
> * ID_Event: Event ID, pointing to the corresponding event folder in the `events` directory.
> * Vs30file: GMT .grd Vs30 file; if not provided, set it to None. Default Vs30 value (760 m/s) will be used instead.
> * CorrelationModel: as required from openquake.hazardlib.correlation.
> * CrosscorrModel: as required from openquake.hazardlib.cross_orrelation.
> * vs30_clustering: `True` value means that Vs30 values are expected to show clustering (as required from openquake.hazardlib.correlation).
> * truncation_level: number of standard deviations for truncation of the cross-correlation model distribution (as required from openquake.hazardlib.cross_correlation). Note that the truncation feature is lost if you use correlation (see OpenQuake documentation). This parameter is only accounted for when 'NoCrossCorrelation' is selected by the user.
> * seed: Random seed to ensure reproducibility in sampling from the GMMs.

2) `POIs file` 

A file with two space-separated columns: LAT and LON of the POIs.

3) `ENSEMBLE`

This folder must contain the ensemble of source scenarios for the current event. Scenarios can be loaded by the user or automatically generated by `SeisEnsMan`.
  
4)  `events` 

This folder should contain a subfolder named with the current event ID, which needs to include:
- `event.xml`: contains event magnitude and time, allowing `SeisEnsMan` to download the event's QUAKEML file and generate an ensemble of compatible earthquake source scenarios. 
- `gmpes.conf`: configuration file for GMMs and their relative weights, which the user must input under `gmpe_sets`. GMMs available in OpenQuake are listed under `gmpe_modules` and can be updated by the user.

5) `vs30` (Optional) 

Place the Vs30 .grd file here. An example file, `global_italy_vs30_clobber.grd` (Michelini et al., 2020), is available at this [link](https://drive.google.com/file/d/1nMzPRH4-tmoGh3_8fBY7Jdk7FfllRIx6/view?usp=sharing).

7) `stationlist.json` (Optional) 

This file should contain ground shaking records from a set of stations and be placed in the event's subfolder. The file should be formatted like USGS `Shakemap` files (see the example in `INPUT_FILES/events/8863681`).

HOW TO RUN
----------

**Generate the scenarios ensemble with `SeisEnsMan`**

First, create a subfolder under `events` named with the event ID. In this folder, populate the `event.xml` file with the event's magnitude and time. This information will be used by `SeisEnsMan` to download the event's QUAKEML file, which is required to generate the ensemble of event-compatible scenarios.

Next, activate the `SeisEnsMan` environment and navigate to the `SeisEnsManV2` directory. Run the following command, adjusting the `--nb_scen` parameter to specify the number of scenarios in the ensemble. The `--angles` parameter is optional, and includes the strike, dip, and rake of the inverted fault model in the plot:

```bash
./line_call.sh
```

Once the scenarios are generated, `SeisEnsMan` will: 1) copy the ensemble of scenarios to the `INPUT_FILES/ENSEMBLE` folder, making them ready for `ProbShakemap`; 2) move any previous files to the `BACKUP` folder; 3) copy the `event_stat.json` and `parameters_histo_map_99999999.pdf` files to the event subfolder. 

Before running `ProbShakemap`, make sure to deactivate the `SeisEnsMan` environment:

```bash
deactivate
```

**Run ProbShakemap**

Activate `probshakemap` conda environment:

```bash
conda activate probshakemap
```

Use any of the `ProbShakemap` utilities to explore and visualize the predictive distribution of ground motion at POIs.
`ProbShakemap` comes with three utility tools - `StationRecords`, `Save_Output`, `QueryHDF5` - and three 'prob tools' - `GetStatistics`, `GetDistributions`, `EnsemblePlot`. 

**TOOL: StationRecords**

Plot data from station file `stationlist.json`, if provided. 

```bash
python ProbShakemap.py --imt PGA --tool StationRecords --imt_min 0.01 --imt_max 1 --station_file stationlist.json
```
OUTPUT

`Data_stationfile_{imt}.pdf`: Plot data from .json station file for the selected IMT (PGA in the example).

<p align="center">
    <img src="https://github.com/INGV/ProbShakemap/blob/main/OUTPUT_REPO/Data_stationfile_PGA.png" alt="Data_stationfile_PGA" width="60%" height="60%">
</p>


**TOOL: Save_Output**

Run the probabilistic analysis and save the output to a .HDF5 file (can be large!) with the following hierarchical structure.

scenario --> POI --> GMPEs realizations

```bash
python ProbShakemap.py --imt PGA --tool Save_Output --num_processes 8 --pois_file grid.txt --numGMPEsRealizations 10
```

OUTPUT

`SIZE_{num_scenarios}_ENSEMBLE_{IMT}.hdf5`


**TOOL: QueryHDF5**

Navigate and query the .HDF5 file.

```bash
python ProbShakemap.py --tool QueryHDF5 --imt PGA --scenario 10 --pois_file grid.txt
```

OUTPUT

`GMF_info.txt`: Print the ground motion fields for the selected scenario at the POIs listed in `grid.txt`.

Preview of an example output file:
<pre>
GMF realizations at Site_LAT:43.2846_LON:12.7778 for Scenario_10: [0.17520797, 0.21844997, 0.093965515, 0.27266037, 0.079073295, 0.09725358, 0.08347481, 0.06693749, 0.005907976, 0.060873847]
GMF realizations at Site_LAT:43.1846_LON:12.8778 for Scenario_10: [0.100996606, 0.35003924, 0.24363522, 0.19941418, 0.15757227, 0.1009447, 0.19146584, 0.06460667, 0.03146108, 0.097111605]
GMF realizations at Site_LAT:43.0846_LON:13.4778 for Scenario_10: [0.18333985, 0.11954803, 0.2914887, 0.050770156, 0.07628956, 0.17871241, 0.10297835, 0.15162756, 0.020328628, 0.04087482]
</pre>

***************************************

**PROB_TOOLS**

**TOOL: GetStatistics**

Calculate, save and plot the statistics of the ground motion predictive distributions at all POIs.

```bash
python ProbShakemap.py --imt PGA --prob_tool GetStatistics --num_processes 8 --pois_file grid.txt --numGMPEsRealizations 10 --imt_min 0.001 --imt_max 1
```

OUTPUT

* npy files with the statistics (saved in the `npyFiles` folder)
* map view of the statistics in `vector_stat.npy` (saved in the `STATISTICS` folder)

Output saved in the `npyFiles` folder:
* `vector_stat.npy`: dictionary of statistics computed for the ground motion distributions at all POIs: 'Mean', 'Median','Percentile 10','Percentile 20','Percentile 80','Percentile 90','Percentile 5','Percentile 95','Percentile 2.5','Percentile 97.5';
* (OPTIONAL, with command `--vector_npy`) `vector.npy`: a 2D array that stores the ground-motion distributions at all POIs. The array has dimensions (`num_pois`, `num_GMPEsRealizations` * `num_scenarios`), where `num_GMPEsRealizations` represents the number of realizations per scenario, and `num_scenarios` is the total number of scenarios in the ensemble. 

<p align="center">
    <img src="https://github.com/INGV/ProbShakemap/blob/main/OUTPUT_REPO/STATISTICS/summary_stats.png" alt="SummaryStats" width="90%" height="90%">
</p>

**TOOL: GetDistributions**

Plot the cumulative distribution of the predicted ground-motion values and main statistics at a specific POI together with the ground-motion value recorded at the closest station (or at a POI coincident with the station, if available).

Note: requires `stationlist.json` file. 

```bash
python ProbShakemap.py --imt PGA --prob_tool GetDistributions --num_processes 8 --pois_file grid.txt --numGMPEsRealizations 10 --imt_min 0.001 --imt_max 10 --station_file stationlist.json
```

OUTPUT

* `POIs_Map.pdf`: Spatial map of the POIs
* `Distr_POI-{POI_idx}.pdf`: Plot of Datum-Ensemble comparison at a given POI

<p align="center">
    <img src="https://github.com/INGV/ProbShakemap/blob/main/OUTPUT_REPO/POIs_subset.png" alt="DatumEnsemble" width="25%" height="25%">
</p>

<p align="center">
    <img src="https://github.com/INGV/ProbShakemap/blob/main/OUTPUT_REPO/DISTRIBUTIONS/summary_stats.png" alt="DatumEnsemble" width="90%" height="90%">
</p>


**TOOL: EnsemblePlot**

Plot and summarize the key statistical features of the distribution of predicted ground-motion values at the POIs.

```bash
python ProbShakemap.py --imt PGA --prob_tool EnsemblePlot --num_processes 8 --pois_file grid.txt --numGMPEsRealizations 10
```

OUTPUT

* `POIs_Map.pdf`: Spatial map of the POIs
* `Ensemble_Spread_Plot_{imt}.pdf`: Boxplot

<p align="center">
    <img src="https://github.com/INGV/ProbShakemap/blob/main/OUTPUT_REPO/Ensemble_Plot.png" alt="DatumEnsemble" width="50%" height="50%">
</p>

**POIs SUBSET OPTION**

When using the tools `QueryHDF5`, `GetStatistics`, `GetDistributions` and `EnsemblePlot`, you can require to extract a subset of POIs within a maximum distance from the event epicenter following one of the following spatial distributions: <ins>random</ins> and <ins>azimuthally uniform</ins>. This changes the command line to:

```bash
python ProbShakemap.py [...] --pois_subset --n_pois 12 --max_distance 50 --pois_selection_method azimuth_uniform
```
If <ins>azimuthally uniform</ins> is selected, POIs are chosen within a ring in the range `max_distance +- max_distance/10`.

**MULTIPLE TOOLS AT THE SAME TIME**

`ProbShakemap` can handle multiple tools at the same time. Be aware that, in this case, the same settings will apply (ie,`--imt_min`, `--imt_max`, `--pois_subset` etc.).

```bash
python ProbShakemap.py --imt PGA --prob_tool GetDistributions EnsemblePlot --num_processes 8 --pois_file grid.txt --numGMPEsRealizations 10 --imt_min 0.001 --imt_max 10 --station_file stationlist.json --pois_subset --n_pois 12 --max_distance 50 --pois_selection_method azimuth_uniform
```

**HPC**

`ProbShakemap` uses the Python `multiprocessing` library to perform computations on chunks of scenarios distributed across multiple processes.

WORKFLOW
--------
`run_code.sh` automates both the generation of the ensemble of scenarios and the propagation of source uncertainty to the set of POIs. It also provides an overview of the commands that can be used to launch the `ProbShakemap` tools.

Contact
--------

If you need support write to [angela.stallone@ingv.it](mailto:angela.stallone@ingv.it).


Contributions & Acknowledgements
--------------------------------

Jacopo Selva coded the `GetStatistics` tool; Louise Cordrie authored the `SeisEnsMan` tool and tested `ProbShakemap` on the INGV-Bologna ADA cluster.
I thank Valentino Lauciani for testing and developing the INGV Shakemap Docker and Licia Faenza for testing ProbShakemap. I also thank Michele Proietto (@https://github.com/miproietto) for assisting us in building the Docker image on the HPC cluster using Singularity.

Citation
--------

If you use `ProbShakemap` in your research, please cite using the following citation:

```bash
@article{stallone2025probshakemap,
  title={ProbShakemap: A Python toolbox propagating source uncertainty to ground motion prediction for urgent computing applications},
  author={Stallone, Angela and Selva, Jacopo and Cordrie, Louise and Faenza, Licia and Michelini, Alberto and Lauciani, Valentino},
  journal={Computers \& Geosciences},
  volume={195},
  pages={105748},
  year={2025},
  publisher={Elsevier}
}
```

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10654186.svg)](https://doi.org/10.5281/zenodo.10654186)

