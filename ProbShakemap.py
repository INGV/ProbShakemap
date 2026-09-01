import tools
import os
import numpy as np
import argparse
import time
import shutil
import logging
from datetime import datetime
import config

start_time = time.time()

def setup_logging(log_dir):
            
    """
    Set up the LOG file
    """
       
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")
    log_file = os.path.join(log_dir, f"setup_{current_time}.log")
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_scenarios_file(scenarios_file):
    if isinstance(scenarios_file, (list, tuple)):
        return scenarios_file[0] if scenarios_file else "not available"
    return scenarios_file

def log_scenario_weights(fileScenariosWeights):
    weights_file = fileScenariosWeights if fileScenariosWeights else "default uniform weights"
    logging.info(f"Scenario Weights File: {weights_file}")

def log_pois_mode(args):
    if args.reuse_pois_subset:
        logging.info("POIs Mode: reuse existing subset")
        logging.info("POIs Source File: OUTPUT/POIs.txt")
        logging.info(f"Original POIs File Argument: {args.pois_file}")
    elif args.pois_subset:
        logging.info("POIs Mode: extract new subset")
        logging.info(f"POIs Source File: {args.pois_file}")
        logging.info("POIs Output File: OUTPUT/POIs.txt")
        logging.info(f"Num POIs in Subset: {args.n_pois}")
        logging.info(f"Max Distance: {args.max_distance} km")
        logging.info(f"POIs Selection Method: {args.pois_selection_method}")
    else:
        logging.info("POIs Mode: full input grid")
        logging.info(f"POIs Source File: {args.pois_file}")

def run_main():

    """
    Run tools.Main()
    """

    # Set the random seed for reproducibility (must be the same as in tools.py)
    config_dict = config.load_config('input_file.txt')
    seed = config_dict['seed']
    np.random.seed(seed)

    ProbCalc = tools.Main(args.imt, args.pois_file,
                        args.numGMPEsRealizations)
    
    prob_output, logging_info = ProbCalc.run_prob_analysis()

    return prob_output, logging_info

if __name__ == '__main__':
    # Define command-line arguments
    parser = argparse.ArgumentParser(description='ProbShakemap Toolbox')
    input_params = parser.add_argument_group('input params')
    input_params.add_argument('--imt', help='Intensity measure type (IMT). Possible choices: PGA, PGV, SA.')
    input_params.add_argument('--tool', choices=['StationRecords', 'Save_Output', 'QueryHDF5'], help='Tool(s) to use')
    input_params.add_argument('--prob_tool', choices=['GetStatistics', 'GetDistributions', 'EnsemblePlot'], nargs='+', help='ProbShakemap Tool(s) to use')
    input_params.add_argument('--numGMPEsRealizations', type=int, help='Total number of GMPEs random samples')
    input_params.add_argument('--imt_min', type=float, help='Minimum value for the selected IMT (for plot only)')
    input_params.add_argument('--imt_max', type=float, help='Maximum value for the selected IMT (for plot only)')
    input_params.add_argument('--station_file', help='Station file (.json, Shakemap-formatted)')
    input_params.add_argument('--scenario', type=float, help='Scenario number')
    input_params.add_argument('--pois_file', help='Filename with latitude and longitude of POIs')
    input_params.add_argument('--pois_subset', action='store_true', default=False, help='Extract a new subset of POIs and save it in OUTPUT/POIs.txt')
    input_params.add_argument('--n_pois', type=int, default=10, help='Number of POIs in the subset')
    input_params.add_argument('--max_distance', type=int, default=200, help='Max distance from epicenter of POIs in the subset')
    input_params.add_argument('--pois_selection_method', choices=['random', 'azimuth_uniform'], help='Selection method for the POIs of the subset')
    input_params.add_argument('--reuse_pois_subset', action='store_true', default=False, help='Reuse the subset of POIs already saved in OUTPUT/POIs.txt')
    input_params.add_argument('--buffer', type=float, default=0.5, help='Buffer to control resolution in prob_tools maps')
    input_params.add_argument('--vector_npy', action='store_true', default=False, help='Store ground motion distributions at all POIs (vector.npy)')
    input_params.add_argument('--fileScenariosWeights', default="", help='File with scenarios weights')

    # Parse command-line arguments
    args = parser.parse_args()

    # Set up log file
    outfile_dir = os.path.join(os.getcwd(), "OUTPUT/LOGS/")
    if not os.path.exists(outfile_dir):
                os.makedirs(outfile_dir)
    setup_logging(outfile_dir)

    ###########################
    ##### STATION RECORDS #####
    ###########################

    if args.tool == 'StationRecords':

        if args.imt_max is None:
            raise TypeError("Missing required argument 'imt_max'")
        if args.imt_min is None:
            raise TypeError("Missing required argument 'imt_min'")
        if args.station_file is None:
            raise TypeError("Station .json file from shakemap not available")

        logging.info(f"Tool: {args.tool}")
        logging.info(f"Intensity Measure: {args.imt}")
        logging.info(f"Min {args.imt}: {args.imt_min}")
        logging.info(f"Max {args.imt}: {args.imt_max}")
        logging.info(f"Station file: {args.station_file}")

        StationRecords = tools.StationRecords(args.imt, args.imt_min, args.imt_max, 
                                                args.station_file)
        StationRecords.plot()


    #################################
    ##### WRITE OUTPUT FILE #########
    #################################

    elif args.tool == 'Save_Output':

        if args.imt is None:
            raise TypeError("Missing required argument 'imt'")
        if args.pois_file is None:
                        raise TypeError("Missing required argument 'pois_file'")
        if args.numGMPEsRealizations is None:
            raise TypeError("Missing required argument 'numGMPEsRealizations'")
            
        logging.info(f"Tool: {args.tool}") 
        logging.info(f"Intensity Measure: {args.imt}")
        logging.info(f"POIs File: {args.pois_file}") 
        logging.info(f"Num GMPEsRealizations: {args.numGMPEsRealizations}")   
        
        prob_output, _ = run_main()

        SiteGmf = prob_output["SiteGmf"]
        keys_scen = prob_output["keys_scen"]
        keys_sites = prob_output["keys_sites"]

        Save_Output = tools.Write(args.imt, keys_scen, SiteGmf, keys_sites)
        Save_Output.write_output()


    #################################
    ##### QUERY OUTPUT FILE #########
    #################################

    elif args.tool == 'QueryHDF5':

        outfile_dir = os.path.join(os.getcwd(), "OUTPUT/HDF5_FILES/")
        outputfile = [name for name in os.listdir(outfile_dir) if name != ".DS_Store"][0]
        if not outputfile:
            print("WARNING: No output file found --> run 'Save_Output' first!")
        else:
            if args.scenario is None:
                raise TypeError("Missing required argument 'scenario'")

        logging.info(f"Tool: {args.tool}")
        logging.info(f"Intensity Measure: {args.imt}")
        logging.info(f"POIs File: {args.pois_file}")
        log_pois_mode(args)
        if args.pois_subset:
            logging.info(f"Scenario: {args.scenario}")


        QueryHDF5 = tools.QueryHDF5(args.scenario, args.pois_file,
                                    args.pois_subset, args.n_pois, args.max_distance, 
                                    args.pois_selection_method)
        QueryHDF5.print_info()


    ###############################
    ###### PROBSHAKEMAP TOOLS #####
    ###############################

    if args.prob_tool:

        run_main_flag = True  # Flag variable to track if Main() has been executed
        pois_subset_flag = True  # True: use --pois_file or extract a new subset; False: reuse OUTPUT/POIs.txt

        if args.reuse_pois_subset:
            pois_subset_flag = False # Reuse the subset of POIs already saved in OUTPUT/POIs.txt
        
        for tool in args.prob_tool:
                
            if tool == 'GetStatistics':
                
                if args.imt_max is None:
                    raise TypeError("Missing required argument 'imt_max'")
                if args.imt_min is None:
                    raise TypeError("Missing required argument 'imt_min'")
                if args.pois_subset and not args.pois_selection_method:
                    raise TypeError("Missing required argument 'pois_selection_method'")
                if args.pois_selection_method == 'azimuth_uniform':
                    if args.n_pois % 4 > 0:
                        raise TypeError("Select a number of POIs divisible by 4")
                    
                logging.info(f"Prob Tool: {tool}")  
                logging.info(f"Intensity Measure: {args.imt}")
                logging.info(f"Min {args.imt}: {args.imt_min}")
                logging.info(f"Max {args.imt}: {args.imt_max}") 
                logging.info(f"POIs File: {args.pois_file}")
                logging.info(f"Num GMPEsRealizations: {args.numGMPEsRealizations}")  
                log_scenario_weights(args.fileScenariosWeights)
                log_pois_mode(args)

                if run_main_flag:

                    if args.imt is None:
                        raise TypeError("Missing required argument 'imt'")
                    if args.pois_file is None:
                        raise TypeError("Missing required argument 'pois_file'")
                    if args.numGMPEsRealizations is None:
                        raise TypeError("Missing required argument 'numGMPEsRealizations'")

                    prob_output, logging_info = run_main()
                    scenarios_file = logging_info["Scenarios_File"]
                    EnsembleSize = logging_info["Ensemble_Size"]
                    logging.info(f"Scenarios Ensemble File: {format_scenarios_file(scenarios_file)}") 
                    logging.info(f"Ensemble Size: {EnsembleSize}") 
                    SiteGmf = prob_output["SiteGmf"]

                    run_main_flag = False    

                GetStatistics = tools.GetStatistics(SiteGmf, args.numGMPEsRealizations, args.imt, 
                                                    args.imt_min, args.imt_max, args.fileScenariosWeights, 
                                                    args.pois_file, args.pois_subset, args.n_pois, args.max_distance, 
                                                    args.pois_selection_method, pois_subset_flag, args.vector_npy, args.buffer)
                GetStatistics.save_statistics()
                GetStatistics.plot_statistics()

                if args.pois_subset:
                    pois_subset_flag = False


            elif tool == 'GetDistributions':

                if args.imt_max is None:
                    raise TypeError("Missing required argument 'imt_max'")
                if args.imt_min is None:
                    raise TypeError("Missing required argument 'imt_min'")
                if args.station_file is None:
                    raise TypeError("Station .json file from shakemap not available")
                if args.pois_subset and not args.pois_selection_method:
                    raise TypeError("Missing required argument 'pois_selection_method'")
                if args.pois_selection_method == 'azimuth_uniform':
                    if args.n_pois % 4 > 0:
                        raise TypeError("Select a number of POIs divisible by 4")
                    
                logging.info(f"Prob Tool: {tool}")  
                logging.info(f"Intensity Measure: {args.imt}")
                logging.info(f"Min {args.imt}: {args.imt_min}")
                logging.info(f"Max {args.imt}: {args.imt_max}") 
                logging.info(f"POIs File: {args.pois_file}")
                logging.info(f"Num GMPEsRealizations: {args.numGMPEsRealizations}")  
                logging.info(f"Station file: {args.station_file}")
                log_scenario_weights(args.fileScenariosWeights)
                log_pois_mode(args)

                if run_main_flag:

                    if args.imt is None:
                        raise TypeError("Missing required argument 'imt'")
                    if args.pois_file is None:
                        raise TypeError("Missing required argument 'pois_file'")
                    if args.numGMPEsRealizations is None:
                        raise TypeError("Missing required argument 'numGMPEsRealizations'")
                        
                    prob_output, logging_info = run_main()
                    scenarios_file = logging_info["Scenarios_File"]
                    EnsembleSize = logging_info["Ensemble_Size"]
                    logging.info(f"Scenarios Ensemble File: {format_scenarios_file(scenarios_file)}") 
                    logging.info(f"Ensemble Size: {EnsembleSize}") 
                    SiteGmf = prob_output["SiteGmf"]

                    run_main_flag = False    

                GetDistributions = tools.GetDistributions(SiteGmf, args.numGMPEsRealizations, args.imt, args.station_file, 
                                                            args.imt_min, args.imt_max, args.fileScenariosWeights, 
                                                            args.pois_file, args.pois_subset, args.n_pois, args.max_distance, 
                                                            args.pois_selection_method, pois_subset_flag, args.buffer)
                GetDistributions.plot_distributions() 
                if args.pois_subset:
                    pois_subset_flag = False


            elif tool == 'EnsemblePlot':

                if args.pois_subset and not args.pois_selection_method:
                    raise TypeError("Missing required argument 'pois_selection_method'")    
                if args.pois_selection_method == 'azimuth_uniform':
                    if args.n_pois % 4 > 0:
                        raise TypeError("Select a number of POIs divisible by 4")
                    
                logging.info(f"Prob Tool: {tool}")  
                logging.info(f"Intensity Measure: {args.imt}")
                logging.info(f"POIs File: {args.pois_file}")
                logging.info(f"Num GMPEsRealizations: {args.numGMPEsRealizations}")  
                log_scenario_weights(args.fileScenariosWeights)
                log_pois_mode(args)

                if run_main_flag:

                    if args.pois_file is None:
                        raise TypeError("Missing required argument 'pois_file'")
                    if args.imt is None:
                        raise TypeError("Missing required argument 'imt'")
                    if args.numGMPEsRealizations is None:
                        raise TypeError("Missing required argument 'numGMPEsRealizations'")
                        
                    prob_output, logging_info = run_main()
                    scenarios_file = logging_info["Scenarios_File"]
                    EnsembleSize = logging_info["Ensemble_Size"]
                    logging.info(f"Scenarios Ensemble File: {format_scenarios_file(scenarios_file)}") 
                    logging.info(f"Ensemble Size: {EnsembleSize}") 
                    SiteGmf = prob_output["SiteGmf"]
                    run_main_flag = False    

                EnsemblePlot = tools.EnsemblePlot(SiteGmf, args.imt, args.numGMPEsRealizations, args.fileScenariosWeights, args.pois_file,
                                                    args.pois_subset, args.n_pois, args.max_distance, args.pois_selection_method, pois_subset_flag, args.buffer)
                EnsemblePlot.plot()
                if args.pois_subset:
                    pois_subset_flag = False

            else:

                print('No tool specified')

    print("********* DONE! *******")
    print("--- %s seconds ---" % (time.time() - start_time))



           
