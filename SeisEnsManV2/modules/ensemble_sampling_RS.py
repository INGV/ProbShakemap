import sys
import time
import numpy as np
from scipy.stats       import norm
from scipy import stats
from random import seed
from random import random
import utm
import random
from ismember          import ismember
from mix_utilities import NormMultiDvec
from scaling_laws  import correct_BS_vertical_position
from scaling_laws  import correct_BS_horizontal_position
from scaling_laws  import correct_PS_horizontal_position
from scaling_laws  import mag_to_w_BS
from scaling_laws  import mag_to_l_BS
from scaling_laws  import mag_to_w_leonardo
from scaling_laws  import mag_to_a_leonardo
import scipy
from numpy.linalg import inv
import emcee
import copy
import math
import pyproj
from math import radians, cos, sin, asin, sqrt
from pyproj import Proj, transform

def compute_ensemble_sampling_RS(**kwargs):

    Config         = kwargs.get('cfg', None)
    ee             = kwargs.get('event_parameters', None)
    args           = kwargs.get('args', None)
    LongTermInfo   = kwargs.get('LongTermInfo', None)
    PSBarInfo      = kwargs.get('PSBarInfo', None)
    lambda_bsps    = kwargs.get('lambda_bsps', None)
    pre_selection  = kwargs.get('pre_selection', None)
    regions        = kwargs.get('regions', None)
    Scenarios_PS   = kwargs.get('Scenarios_PS', None)
    RS_samp_scen   = kwargs.get('RS_samp_scen', None)

    # Choice of the region #
    if (ee['lat']>28.5 and ee['lat']<47.0 and ee['lon']>1.0 and ee['lon']<22.0) or (ee['lat']>32.0 and ee['lat']<42.0 and ee['lon']>-7.0 and ee['lon']<=1.0) or (ee['lat']>30.0 and ee['lat']<41.5 and ee['lon']>=22.0 and ee['lon']<37.5):
        #RS_type='LH'
        RS_type='MC'
        print('Event inside the Mediterranean Area')
    else:
        RS_type='MC'
        print('Event outside the Mediterranean Area')

    discretizations=LongTermInfo['Discretizations']
    TotProbBS_all = 1.0 #np.sum(probability_scenarios['ProbScenBS'])
    TotProbPS_all = 0.0 #np.sum(probability_scenarios['ProbScenPS'])
    short_term = TotProbBS_all
 
    ### Number of scenarios and runs ###
    RS_samp_run=1
    Nsamp=np.ones(RS_samp_run)*int(RS_samp_scen)
    sampled_ensemble = {}

    Nid=0
    ### Loop of Nsamp MC sampling ###
    for N in Nsamp:
        ### Begining of the creation of the Nth sampled ensemble ###
        N=int(N)
        NBS= round(TotProbBS_all*N) ### NBS: number of scenarios sampled from the BS ensemble
        NPS= N-NBS ### NPS: number of scenarios sampled from the PS ensemble
        # NBS and NPS are proportionnal to the probability of PS and BS
        sampled_ensemble[Nid] = dict()
        sampled_ensemble[Nid] = set_if_compute_scenarios(cfg           = Config,
                                                short_term    = short_term)
        
       
        ### Initialization of the dictionnaries ### 
        sampled_ensemble[Nid]['prob_scenarios_bs_fact'] = np.zeros( (NBS,  5) )
        sampled_ensemble[Nid]['prob_scenarios_bs'] = np.zeros( (NBS) )
        sampled_ensemble[Nid]['prob_angles_bs'] = np.zeros( (NBS) )
        sampled_ensemble[Nid]['real_prob_scenarios_bs'] = np.zeros( (NBS) )
        sampled_ensemble[Nid]['par_scenarios_bs'] = np.zeros(  (NBS, 11) )
        sampled_ensemble[Nid]['real_par_scenarios_bs'] = np.zeros(  (NBS, 11) )
        sampled_ensemble[Nid]['prob_scenarios_ps_fact'] = np.zeros( (NPS,  5) )
        sampled_ensemble[Nid]['prob_scenarios_ps'] = np.zeros( (NPS) )
        sampled_ensemble[Nid]['real_prob_scenarios_ps'] = np.zeros( (NPS) )
        sampled_ensemble[Nid]['par_scenarios_ps'] = np.zeros(  (NPS,  7) )
        sampled_ensemble[Nid]['real_par_scenarios_ps'] = np.zeros( (NPS, 7) )
        sampled_ensemble[Nid]['iscenbs']=np.zeros(NBS)
        sampled_ensemble[Nid]['iscenps']=np.zeros(NPS)

        if RS_type == 'MC':
           sampled_ensemble = bs_probability_scenarios_RMCS(cfg              = Config,
                                                            short_term       = short_term,
                                                            pre_selection    = pre_selection,
                                                            regions_files    = regions,
                                                            samp_ens         = sampled_ensemble,
                                                            Discretizations  = LongTermInfo['Discretizations'],
	   			                        		            NBS	      = NBS,
                                                            Nid	      = Nid,
                                                            Num_Samp         = NBS,
                                                            ee               = ee)

        if RS_type == 'LH':
           sampled_ensemble = bs_probability_scenarios_RLHS(cfg              = Config,
                                                            short_term       = short_term,
                                                            pre_selection    = pre_selection,
                                                            regions_files    = regions,
                                                            samp_ens         = sampled_ensemble,
                                                            Discretizations  = LongTermInfo['Discretizations'],
                                                            NBS              = NBS,
                                                            Nid              = Nid,
                                                            Num_Samp         = NBS,
                                                            ee               = ee)



        if(sampled_ensemble[Nid] == False):
            return False

        TotBS=len(sampled_ensemble[Nid]['real_par_scenarios_bs'])
        TotPS=len(sampled_ensemble[Nid]['real_par_scenarios_ps'])
        Tot=TotBS+TotPS
        sampled_ensemble[Nid]['RealProbScenBS'] = np.ones(TotBS)*1./Tot
        sampled_ensemble[Nid]['RealProbScenPS'] = np.ones(TotPS)*1./Tot
        
        ### Re-normalization of all the probabilities ###
        TotProbBS = np.sum(sampled_ensemble[Nid]['RealProbScenBS'])
        TotProbPS = np.sum(sampled_ensemble[Nid]['RealProbScenPS'])
        print("Final probabilities",TotProbBS,TotProbPS)

        try:
            max_idxBS = np.argmax(RealProbScenBS)
        except:
            max_idxBS = -1
        try:
            max_ValBS = ProbScenBS[max_idxBS]
        except:
            max_ValBS = 0
        try:
            max_idxPS = np.argmax(RealProbScenPS)
        except:
            max_idxPS = -1
        try:
            max_ValPS = ProbScenPS[max_idxPS]
        except:
            max_ValPS = 0

            max_ValPS = 0

            max_ValPS = 0

        sampled_ensemble[Nid]['real_best_scenarios'] = {'max_idxBS':max_idxBS, 'max_idxPS':max_idxPS, 'max_ValBS':max_ValBS, 'max_ValPS':max_ValPS}

        Nid=Nid+1

    return sampled_ensemble

def set_if_compute_scenarios(**kwargs):

    short_term     = kwargs.get('short_term', None)
    Config         = kwargs.get('cfg', None)

    neg_prob       = float(Config.get('Settings','negligible_probability'))
    out = dict()

    # Some inizialization
    out['nr_ps_scenarios'] = 0
    out['nr_bs_scenarios'] = 0

    BScomputedYN   = False
    PScomputedYN   = False
    
    tmpbs      = short_term #(short_term['magnitude_probability'] * short_term['RatioBSonTot']).sum()
    tmpps      = 1.0-short_term #(short_term['magnitude_probability'] * short_term['RatioPSonTot']).sum()

    if(tmpbs > neg_prob):
        BScomputedYN = True
    if(tmpps > neg_prob):
        PScomputedYN = True

    out['BScomputedYN'] = BScomputedYN
    out['PScomputedYN'] = PScomputedYN

    return out

## Function giving random values of rake ##
def roll(massDist):
        randRoll = random.random() # in [0,1]
        sum = 0
        result = 0
        for mass in massDist:
            sum += mass
            if randRoll < sum:
                return result
            result+=90

def find_nearest(array, value):
    arr = np.asarray(array)
    idx = 0
    diff = arr-value
    diff[diff<1e-26]=100.0
    idx=diff.argmin()
    return idx,array[idx]

def utm_to_wgs84(zone, easting, northing):
    # Définir la projection UTM et WGS84
    utm_proj = Proj(proj='utm', zone=zone, ellps='WGS84')
    wgs84_proj = Proj(proj='latlong', datum='WGS84')
    # Convertir les coordonnées UTM en coordonnées WGS84
    lon, lat = transform(utm_proj, wgs84_proj, easting, northing)
    return lon, lat

def wgs84_to_utm(latitude, longitude):
    utm_coords = utm.from_latlon(latitude, longitude)
    zone = utm_coords[2]
    hemisphere = 'N' if latitude >= 0 else 'S'
    return zone, hemisphere

def region_med(latlon,pre_selection,Discretizations,region_files):

    region_info = dict()
    regions_nr = []

    # Inside the original code the strike/dip/rake
    # do not depend of the magnitude and position
    bs2_pos = len(pre_selection['BS2_Position_Selection_inn'])
    d_lonlat=np.zeros((bs2_pos,2))
    d_diff=np.zeros((bs2_pos))
    for val in range(bs2_pos):
            tmp_idx = pre_selection['BS2_Position_Selection_inn'][val]
            d_lonlat[val,:] = Discretizations['BS-2_Position']['Val'][tmp_idx].split()
            d_diff[val] = haversine(latlon[1], latlon[0], d_lonlat[val,0], d_lonlat[val,1])
    ipos_idx = int(np.argmin(d_diff))
    ipos = pre_selection['BS2_Position_Selection_inn'][ipos_idx]
    ireg = Discretizations['BS-2_Position']['Region'][ipos]

    # Faccio il load della regione se non già fatto
    if(ireg not in regions_nr):
        #print("...............................", region_files)
        region_info = load_region_infos(ireg         = ireg,
                                        region_info  = region_info,
                                        region_files = region_files)
        regions_nr.append(ireg)
    RegMeanProb_BS4 = region_info[ireg]['BS4_FocMech_MeanProb_valNorm']

    # Non credo che qui ci saranno errori, nel senso che i npy sono creati a partire dai mat conteneti roba
    if(RegMeanProb_BS4.size == 0):
         print(' --> WARNING: region info %d is empty!!!' % (ireg) )
    ipos_reg = np.where(region_info[ireg]['BS4_FocMech_iPosInRegion'] == ipos+1)[1]
    tmpProbAngles = RegMeanProb_BS4[ipos_reg[0]]

    # Creation of the array of cumulated probability intervals
    int_ens = np.zeros(len(tmpProbAngles))
    prob_cum = 0
    prob_mod=tmpProbAngles/np.sum(tmpProbAngles)
    for iii in range(len(tmpProbAngles)):
        prob_cum=prob_cum+prob_mod[iii]
        int_ens[iii]= prob_cum
    # Random selection of a value inside the cumulative distrib.
    random_value = np.random.random()
    iangle,proba_a = find_nearest(int_ens,random_value)
    proba_angles=tmpProbAngles[iangle]
    str_val,dip_val,rak_val = Discretizations['BS-4_FocalMechanism']['Val'][iangle].split()
    dip_val_rad=math.radians(float(dip_val))

    return str_val,dip_val,rak_val,dip_val_rad,ireg

def region_world(latlon,world_ang,world_prob,world_pos):

    ireg = 0
    # Arrays loaded at the start of the function #
    # ang = all (strike,dip,rake) combinations (128) weighted in each cell (64800) of the world grid #
    # prob = probabilities associated to each combination for each cell (128*66800) #
    # pos = lat lon positions (center and corners = 10) of each cell (10*66800)
    ang=world_ang
    prob=world_prob
    pos=world_pos

    # Identification of the cell corresponding to the scenario position
    sump=np.sum(prob,axis=1)
    for ip in range(len(prob)):
        prob[ip]=prob[ip]/sump[ip]
        if latlon[1]<pos[ip,2] and latlon[1]>pos[ip,6]:
            if latlon[0]<pos[ip,3] and latlon[0]>pos[ip,7]:
               cell=ip
    # Creation of the cumulative distribution #
    ang_prob_cum = np.zeros(len(ang))
    prob_cum = 0
    for iang in range(len(ang)):
        prob_cum = prob_cum+prob[cell,iang]
        ang_prob_cum[iang] = prob_cum
    # Selection of a random value in the distribution #
    random_value = np.random.random()
    idx,proba = find_nearest(ang_prob_cum,random_value)
    str_val=ang[idx,0]
    dip_val=ang[idx,1]
    rak_val=ang[idx,2]
    if rak_val<0:
       rak_val=ang[idx,2]+360 # Convention to be checked #

    dip_val_rad=math.radians(float(dip_val))

    return str_val,dip_val,rak_val,dip_val_rad,ireg

def adjust_utm_values(lat_val, lon_val, zone_number, stop_id):
    """Adjust UTM values to ensure they fall within valid ranges."""
    # Typical UTM values range for easting is between 100,000 and 900,000
    if lat_val < 100000.0 or lat_val > 900000.0:
        stop_id=0
        if lat_val < 100000.0:
            lat_val = 900000.0 - (100000.0 - lat_val)
            zone_number -= 1
        elif lat_val > 900000.0:
            lat_val = 100000.0 + (lat_val - 900000.0)
            zone_number += 1
    else:
        stop_id=1
    return lat_val, lon_val, zone_number, stop_id

def convert_utm_to_wgs84(utm_zone, easting, northing, northern):
    # Define the UTM CRS based on the zone
    if northern:
       utm_crs = pyproj.CRS(f"EPSG:326{utm_zone}")
    else:
       utm_crs = pyproj.CRS(f"EPSG:327{utm_zone}")
    wgs84_crs = pyproj.CRS("EPSG:4326")
    
    # Create transformer
    transformer = pyproj.Transformer.from_crs(utm_crs, wgs84_crs, always_xy=True)
    
    # Perform the transformation
    lon, lat = transformer.transform(easting, northing)
    
    return lon, lat

def bs_probability_scenarios_RMCS(**kwargs):

    Config          = kwargs.get('cfg', None)
    short_term      = kwargs.get('short_term', None)
    samp_ens        = kwargs.get('samp_ens', None)
    pre_selection   = kwargs.get('pre_selection', None)
    Discretizations = kwargs.get('Discretizations', None)
    region_files    = kwargs.get('regions_files', None)
    NBS	            = kwargs.get('NBS', None)
    Nid             = kwargs.get('Nid', None)
    Num_Samp        = kwargs.get('Num_Samp', None)
    ee              = kwargs.get('ee', None)
    region_info     = dict()
    ee_d=ee

    print('Ensemble MC')

    # Choice of the region #
    if (ee['lat']>28.5 and ee['lat']<47.0 and ee['lon']>1.0 and ee['lon']<22.0) or (ee['lat']>32.0 and ee['lat']<42.0 and ee['lon']>-7.0 and ee['lon']<=1.0) or (ee['lat']>30.0 and ee['lat']<41.5 and ee['lon']>=22.0 and ee['lon']<37.5):
        region='med'
    else:
        region='world'
        ### Load world angles combinations (Selva_Taroni_2021) ###
        file_ang = './IO/world-fm/Angles_Combinations.txt'
        world_ang=np.zeros((128,3))
        with open(file_ang,'r') as f:
            #next(f)
            for (il, line) in enumerate(f):
                world_ang[il,:] = np.array(line.split())

        ### Load world angles probabilities for each cell of the world grid (Selva_Taroni_2021) ###
        file_model = './IO/world-fm/Final_Model.txt'
        world_prob=np.zeros((64800,128))
        world_pos=np.zeros((64800,10))
        with open(file_model,'r') as f:
            #next(f)
            for (il, line) in enumerate(f):
                col = np.array(line.split())
                world_prob[il,:] = col[10::]
                world_pos[il,:] = col[0:10]

    ### Check the existence of BS scenarios ###
    if(samp_ens[Nid]['BScomputedYN'] == False or pre_selection['BS_scenarios'] == False):
        samp_ens[Nid]['nr_bs_scenarios'] = 0
        return samp_ens
    regions_nr = []

    ### Load parameters of the source ###
    Mw=ee['mag']
    sig=ee['MagSigma']
    mu      = ee['PosMean_3d']
    #co      = copy.deepcopy(ee['PosCovMat_3dm'])
    hx             = ee['ee_utm'][0]
    hy             = ee['ee_utm'][1]
    hz             = ee['depth']* (1000.0)
    xyz            = np.array([hx, hy, hz])
    real_val=np.zeros((Num_Samp,11))
    disc_val=np.zeros((Num_Samp,11))

    iscenbs=0
    ### Beginning of the parameter selection for each scenario (Num_samp = number of scenarios) ###
    ### The "disc" values correspond to another scenario selection method not used here ###
    ### but kept because could be usefull in futur testing ###
    for i in range(Num_Samp):
       
       iscenbs=i

       ### Choice of the magnitude ###
       ###############################
       mag_val_disc = 0.0
       mag_val=np.random.normal(loc=Mw, scale=sig)
       mag_min_presel=np.ndarray.min(pre_selection['sel_BS_Mag_val'][:])
       if mag_val<mag_min_presel:
           mag_val_disc=mag_min_presel
       else:
           mag_val_disc=mag_val
       
       ### Compute length and width with respect the magnitude ###
       width = mag_to_w_BS(mag=mag_val, type_scala='M2W')
       length = mag_to_l_BS(mag=mag_val, type_scala='M2L')
       area = width*length

       ### Moment and slip ###
       rig = 30.0e9
       Mo=10**((mag_val+10.7)*(3.0/2.0))*1e-7
       slip=Mo/(area*rig)
             
       ### Choice of the position (lat, lon, depth) ###
       ################################################

       # Correct  Covariance matrix #
       PosCovMat_3d    = np.array([[ee_d['cov_matrix']['XX'], ee_d['cov_matrix']['XY'], ee_d['cov_matrix']['XZ']], \
                                     [ee_d['cov_matrix']['XY'], ee_d['cov_matrix']['YY'], ee_d['cov_matrix']['YZ']], \
                                     [ee_d['cov_matrix']['XZ'], ee_d['cov_matrix']['YZ'], ee_d['cov_matrix']['ZZ']]])
       co = PosCovMat_3d*1000000
       cov = copy.deepcopy(co) #np.zeros((3,3))
       
       cov[0,0] = co[0,0] + (0.5*length)**2
       cov[1,1] = co[1,1] + (0.5*length)**2
       cov[2,2] = co[2,2] + (math.sin(math.pi/4)*0.5*width)**2

       mean=xyz
       
       # Definition of the resolution of the gaussian #
       bounds=np.zeros((3,2))
       ee_d=copy.deepcopy(ee) 
       dip_min=math.radians(float(10.0))
       depmax=500.0*1000.0 # no depth limit
       depmin=1000.0+(width/2.0)*math.sin(dip_min)
       bounds[0,0]=xyz[0]-(2.0*length)
       bounds[0,1]=xyz[0]+(2.0*length)
       bounds[1,0]=xyz[1]-(2.0*length)
       bounds[1,1]=xyz[1]+(2.0*length)
       bounds[2,0]=depmin
       bounds[2,1]=depmax 
       # Creation of the Guassian #
       Nsteps=1000
       x = np.random.multivariate_normal(mean=mean, cov=cov, size=Nsteps)
       prob = np.zeros((len(x)))
       prob = scipy.stats.multivariate_normal.pdf(x,mean=xyz, cov=cov)
       # Search for uncompatible values #
       izero=[]
       for iii in range(len(x)):
           if np.any(x[iii,0] < bounds[0,0]) or np.any(x[iii,0] > bounds[0,1]) or np.any(x[iii,1] < bounds[1,0]) or np.any(x[iii,1] > bounds[1,1]):
              izero=np.append(izero,int(iii))
           if np.any(x[iii,2] < bounds[2,0]) or np.any(x[iii,2] > bounds[2,1]):
              izero=np.append(izero,int(iii))
       # Erase the uncompatible values from the list #
       if len(izero)>0:
          izero=izero.astype(int)
          prob=np.delete(prob,izero)
          x=np.delete(x,izero,axis=0)
       # Creation of the cumulative probability distribution #
       int_ens = np.zeros(len(x))
       prob_mod = np.zeros(len(x))
       prob_cum = 0
       prob_mod=prob[:]/np.sum(prob)
       for iii in range(len(prob)):
           prob_cum=prob_cum+prob_mod[iii]
           int_ens[iii]= prob_cum
       # Random selection of a value inside the cumulative distrib. #
       random_value = np.random.random()
       idx,proba = find_nearest(int_ens,random_value)
       pos_fin=x[idx]
       prob_fin=prob_mod[idx]
       pos_fin=x[0]
       #print('Final position :',pos_fin)
       lon_val=pos_fin[0]
       lat_val=pos_fin[1]
       dep_val=pos_fin[2]

       # Checking depth
       if dep_val > depmax:
          dep_val=depmax
       elif dep_val < depmin:
          dep_val=depmin

       # Searching latlon
       latlon = np.zeros((2))
       utm_zone, hemisphere = wgs84_to_utm(ee['lat'],ee['lon'])
       if hemisphere=='S':
           north=False
       else:
           north=True
                    
       ## Conversion into Lat/Lon degree values
       #stop_id=0
       #while stop_id<1:
       #     lat_val, lon_val, utm_zone, stop_id = adjust_utm_values(lat_val, lon_val, utm_zone, stop_id)
       #
       ##latlon[0], latlon[1] = utm.to_latlon(lat_val,
       ##                           lon_val,
       ##                           utm_zone, northern=north)
       
       latlon[1], latlon[0] = convert_utm_to_wgs84(utm_zone, lon_val,
                                  lat_val,northern=north)

       if region=='med':
           str_val,dip_val,rak_val,dip_val_rad,ireg = region_med(latlon,pre_selection,Discretizations,region_files)
       else:
           str_val,dip_val,rak_val,dip_val_rad,ireg = region_world(latlon,world_ang,world_prob,world_pos)


       ### Choice of the angle for the real sampling ###
       #################################################
       # Strike angle: uniform law #
       low_str=float(str_val)-22.5
       high_str=float(str_val)+22.5
       str_real_val=np.random.uniform(low=low_str, high=high_str)
       if str_real_val>360:
           str_real_val=str_real_val-360.0
       elif str_real_val<0:
           str_real_val=str_real_val+360.0
       # Rake angle: uniform law #
       low_rak=float(rak_val)-45.0
       high_rak=float(rak_val)+45.0
       rak_real_val=np.random.uniform(low=low_rak, high=high_rak)
       ## GMPEs angle convention ###
       if rak_real_val>180:
           rak_real_val=rak_real_val-360.0
       rak_real_val=float(rak_real_val)
       # Dip angle: uniform law #
       if region=='med':
           low_dip=max(10,float(dip_val)-10.0)
           high_dip=min(90,float(dip_val)+10.0)
       else:
           low_dip=max(10,float(dip_val)-11.25)
           high_dip=min(90,float(dip_val)+11.25)

       dip_real_val=np.random.uniform(low=low_dip, high=high_dip)
       dip_real_val_rad=math.radians(float(dip_real_val))

       ### Re-evaluation of the depth: the fault plane should not reach the surface ###
       #width_leo = mag_to_w_leonardo(mag=mag_val,rake=rak_real_val)
       area_leo = mag_to_a_leonardo(mag=mag_val,rake=rak_real_val)
       aratio = 7
       width_leo = 1000.0 * (area_leo / aratio)**0.5
       lim_dep=1000.0+((width_leo/2.0)*math.sin(dip_real_val_rad))
       if dep_val<lim_dep:
          dep_val=lim_dep
       area = length*width

       ### Slip, mag and region ###
       ############################

       # mag_list=np.array(Discretizations['BS-1_Magnitude']['Val'][:])
       # imag = np.argmin(np.abs(mag_list-mag_val_disc)) 
       # Depth of the event #
       # idep = np.argmin(np.abs(Discretizations['BS-3_Depth']['ValVec'][imag][ipos]-(dep_val-(v_hwidth*math.sin(dip_val_rad)/math.sin(math.pi/4)))/1000.0))#/math.sin(math.pi/4)))/1000.0))
       # are_val = Discretizations['BS-5_Area']['ValArea'][ireg, imag, iangle]
       # len_val = Discretizations['BS-5_Area']['ValLen'][ireg, imag, iangle]
       # sli_val = Discretizations['BS-6_Slip']['Val'][ireg, imag, iangle]
      
       ### Real sampled parameters ###
       ###############################
       real_val[i,0]=ireg
       real_val[i,1]=mag_val
       real_val[i,2]=latlon[0]
       real_val[i,3]=latlon[1]
       real_val[i,4]=dep_val/1000.0 
       real_val[i,5]=str_real_val
       real_val[i,6]=dip_real_val
       real_val[i,7]=rak_real_val
       real_val[i,8]=area/(1000.0**2)
       real_val[i,9]=length/1000.0
       real_val[i,10]=slip
       ##############################
       
       ### Real values ###
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,0]=real_val[i,0] #Reg
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,1]=real_val[i,1] #Mag
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,2]=real_val[i,2] #Lon
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,3]=real_val[i,3] #Lat
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,4]=real_val[i,4] #Depth
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,5]=real_val[i,5] #Strike
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,6]=real_val[i,6] #Dip
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,7]=real_val[i,7] #Rake
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,8]=real_val[i,8] #Area 
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,9]=real_val[i,9] #Length
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,10]=real_val[i,10] #Slip

    samp_ens[Nid]['nr_bs_scenarios'] = np.shape(samp_ens[Nid]['prob_scenarios_bs_fact'])[0]
    return samp_ens

def bs_probability_scenarios_RLHS(**kwargs):

    Config          = kwargs.get('cfg', None)
    short_term      = kwargs.get('short_term', None)
    samp_ens        = kwargs.get('samp_ens', None)
    pre_selection   = kwargs.get('pre_selection', None)
    Discretizations = kwargs.get('Discretizations', None)
    region_files    = kwargs.get('regions_files', None)
    NBS	            = kwargs.get('NBS', None)
    Nid             = kwargs.get('Nid', None)
    Num_Samp        = kwargs.get('Num_Samp', None)
    ee              = kwargs.get('ee', None)
    region_info     = dict()
    ee_d=ee

    print('Ensemble LH')

    if(samp_ens[Nid]['BScomputedYN'] == False or pre_selection['BS_scenarios'] == False):
        samp_ens[Nid]['nr_bs_scenarios'] = 0
        return samp_ens

    regions_nr = []

    # Parameters and arrays
    Mw=ee['mag']
    sig=ee['MagSigma']
    mu      = ee['PosMean_3d']
    #co      = copy.deepcopy(ee['PosCovMat_3dm'])
    hx             = ee['ee_utm'][0]
    hy             = ee['ee_utm'][1]
    hz             = ee['depth']* (1000.0)
    xyz            = np.array([hx, hy, hz])

    # Arrays of the scenarios parameters #
    real_val=np.zeros((Num_Samp,11))
    disc_val=np.zeros((Num_Samp,11))
    iscenbs=0
    
    ### Calculation of the combined grid of parameters and its associated PDF ###    

    # Resolution for the magitude, position
    mag_res = 0.1 #default=0.05
    dep_res = 30 #default=2000 (every 2km)
    pos_res = 50

    ### Magnitude PDF ###
    #####################
    mag_val_disc = 0.0
    magmax = Mw + 2.0*sig
    magmin = Mw - 2.0*sig
    mag_val_grid = np.arange(magmin,magmax,mag_res)
    mag_prob_pdf = scipy.stats.norm.pdf(mag_val_grid,loc=Mw, scale=sig)
    mag_prob_cum = scipy.stats.norm.cdf(mag_val_grid,loc=Mw, scale=sig)
    mag_prob_pdf_norm = mag_prob_pdf/np.sum(mag_prob_pdf)
    width = mag_to_w_BS(mag=Mw, type_scala='M2W')
    length = mag_to_l_BS(mag=Mw, type_scala='M2L')
    area = length*width

    PosCovMat_3d    = np.array([[ee_d['cov_matrix']['XX'], ee_d['cov_matrix']['XY'], ee_d['cov_matrix']['XZ']], \
                                  [ee_d['cov_matrix']['XY'], ee_d['cov_matrix']['YY'], ee_d['cov_matrix']['YZ']], \
                                  [ee_d['cov_matrix']['XZ'], ee_d['cov_matrix']['YZ'], ee_d['cov_matrix']['ZZ']]])
    co = PosCovMat_3d*1000000
    cov = copy.deepcopy(co) #np.zeros((3,3))
    cov[0,0] = co[0,0] + (0.5*length)**2
    cov[1,1] = co[1,1] + (0.5*length)**2
    cov[2,2] = co[2,2] + (math.sin(math.pi/4)*0.5*width)**2
    mean=xyz

    # Resolution of the position
    #pos_res=int(np.log(Mw)*math.sqrt((cov[0,0]+cov[1,1]))*pos_res_div)

    ### Position PDF ###
    ####################
    xarrmin = xyz[0] - (4.)*math.sqrt(cov[0,0])
    xarrmax = xyz[0] + (4.)*math.sqrt(cov[0,0])
    pos_res_x=(xarrmax-xarrmin)/pos_res
    #xarr = np.arange(xarrmin,xarrmax,pos_res_x)
    xarr = np.linspace(xarrmin,xarrmax,pos_res)
    yarrmin = xyz[1] - (4.)*math.sqrt(cov[1,1])
    yarrmax = xyz[1] + (4.)*math.sqrt(cov[1,1])
    pos_res_y=(yarrmax-yarrmin)/pos_res
    #yarr = np.arange(yarrmin,yarrmax,pos_res_y)
    yarr = np.linspace(yarrmin,yarrmax,pos_res)
    dip_min=math.radians(float(10.0))
    zarrmin = 1000+(width/2.0)*math.sin(dip_min)
    zarrmax = xyz[2] + (4.)*math.sqrt(cov[2,2]) #10000 #co[2,2]
    pos_res_z=(zarrmax-zarrmin)/dep_res
    #zarr = np.arange(zarrmin,zarrmax,dep_res_z)
    zarr = np.linspace(zarrmin,zarrmax,dep_res)
    X, Y, Z = np.meshgrid(xarr,yarr,zarr)
    xyz_list = np.vstack(np.hstack(np.stack((X,Y,Z),axis=-1)))
    xyz_ind=np.arange(0,len(xyz_list),1)
    xyz_prob_pdf = scipy.stats.multivariate_normal.pdf(xyz_list,mean=mean, cov=cov)
    xyz_prob_pdf_norm = xyz_prob_pdf/np.sum(xyz_prob_pdf)

    ### Angles PDF ###
    ##################
    # Inside the original code the strike/dip/rake
    # do not depend of the magnitude and position
    lon_val=hx ## event position
    lat_val=hy ## event position

    ## Searching latlon
    latlon = np.zeros((2))
    utm_zone, hemisphere = wgs84_to_utm(ee['lat'],ee['lon'])
    if hemisphere=='S':
        north=False
    else:
        north=True
        
    latlon[1], latlon[0] = convert_utm_to_wgs84(utm_zone, lon_val,
                               lat_val,northern=north)

    lat_val=latlon[0]
    lon_val=latlon[1]
    bs2_pos = len(pre_selection['BS2_Position_Selection_inn'])
    d_lonlat=np.zeros((bs2_pos,2))
    d_diff=np.zeros((bs2_pos))
    for val in range(bs2_pos):
            tmp_idx = pre_selection['BS2_Position_Selection_inn'][val]
            d_lonlat[val,:] = Discretizations['BS-2_Position']['Val'][tmp_idx].split()
            d_diff[val] = haversine(lon_val, lat_val, d_lonlat[val,0], d_lonlat[val,1])
    ipos_idx = int(np.argmin(d_diff))
    ipos = pre_selection['BS2_Position_Selection_inn'][ipos_idx]
    ireg = Discretizations['BS-2_Position']['Region'][ipos]       
    # Faccio il load della regione se non già fatto
    if(ireg not in regions_nr):
        #print("...............................", region_files)
        region_info = load_region_infos(ireg         = ireg,
                                        region_info  = region_info,
                                        region_files = region_files)
        regions_nr.append(ireg)
    RegMeanProb_BS4 = region_info[ireg]['BS4_FocMech_MeanProb_valNorm']

    # Non credo che qui ci saranno errori, nel senso che i npy sono creati a partire dai mat conteneti roba
    if(RegMeanProb_BS4.size == 0):
         print(' --> WARNING: region info %d is empty!!!' % (ireg) )
    ipos_reg = np.where(region_info[ireg]['BS4_FocMech_iPosInRegion'] == ipos+1)[1]
    ang_prob_pdf = RegMeanProb_BS4[ipos_reg[0]]
    ang_list = Discretizations['BS-4_FocalMechanism']['Val']
    ang_ind=np.arange(0,len(ang_list),1)
    ang_prob_pdf_norm = ang_prob_pdf/np.sum(ang_prob_pdf)
    
    ### Combination of the three PDF functions ###
    ##############################################

    print('Length of arrays : ','Lon: ',len(xarr),' Lat: ',len(yarr),' Depth: ',len(zarr),' Ang: ',len(ang_ind),' Mag: ',len(mag_val_grid))

    M, P, A = np.meshgrid(mag_val_grid,xyz_ind,ang_ind)
    mxyza_list = np.vstack(np.hstack(np.stack((M,P,A),axis=-1)))
    PX, PY, PZ = np.meshgrid(mag_prob_pdf_norm,xyz_prob_pdf_norm,ang_prob_pdf_norm)
    mxyza_prob = np.vstack(np.hstack(np.stack((PX,PY,PZ),axis=-1)))
    mxyza_prob_prod = np.prod(mxyza_prob, axis=1)
    
    print('5d Meshgrid created')

    ### Creation of the array of cumulated probability intervals associated to the initial ensemble ###
    mxyza_prob_cum = np.zeros(len(mxyza_prob_prod))
    prob_cum = 0
    for i in range(len(mxyza_prob_prod)):
        prob_cum=prob_cum+mxyza_prob_prod[i]
        mxyza_prob_cum[i]= prob_cum
    
    sampler = scipy.stats.qmc.LatinHypercube(d=1)
    random_value = sampler.random(n=Num_Samp)
    para_scen_lhs = np.zeros((Num_Samp,8))
    itmp = 0
    
    for i in random_value:
        ### Each value is associated to a scenario that can be retrieved from the cumulative probability function
        idx,proba = find_nearest(mxyza_prob_cum,i)
        #print('find nearest done',itmp)
        para_scen_lhs[itmp,0] = mxyza_list[idx,0] #mag
        XYZ_idx = int(mxyza_list[idx,1])
        ANG_idx = int(mxyza_list[idx,2])
        para_scen_lhs[itmp,1] = xyz_list[XYZ_idx,0] #lat
        para_scen_lhs[itmp,2] = xyz_list[XYZ_idx,1] #lon
        para_scen_lhs[itmp,3] = xyz_list[XYZ_idx,2] #dep
        Sv,Dv,Rv = Discretizations['BS-4_FocalMechanism']['Val'][ANG_idx].split() 
        para_scen_lhs[itmp,4] = float(Sv)
        para_scen_lhs[itmp,5] = float(Dv)
        para_scen_lhs[itmp,6] = float(Rv)
        para_scen_lhs[itmp,7] = ANG_idx
        itmp=itmp+1

    ### Beginning of the parameter selection for each scenario ###
    ##############################################################
    for i in range(Num_Samp):

       print(i)
       iscenbs=i


       ### Choice of the magnitude ###
       ###############################
       mag_val_disc = 0.0
       mag_val_min=para_scen_lhs[i,0]-(0.5*mag_res)
       mag_val_max=para_scen_lhs[i,0]+(0.5*mag_res)
       mag_val=np.random.uniform(low=mag_val_min, high=mag_val_max)
       mag_min_presel=np.ndarray.min(pre_selection['sel_BS_Mag_val'][:])
       if mag_val<mag_min_presel:
           mag_val_disc=mag_min_presel
       else:
           mag_val_disc=mag_val

       ### Compute length and width with respect the magnitude ###
       width = mag_to_w_BS(mag=mag_val, type_scala='M2W')
       length = mag_to_l_BS(mag=mag_val, type_scala='M2L')
       area = width*length

       ### Moment and slip ###
       rig = 30.0e9
       ### Moment ###
       Mo=10**((mag_val+10.7)*(3.0/2.0))*1e-7
       slip=Mo/(area*rig)

       dip_min=math.radians(float(10.0))
       depmax=500.0*1000.0
       depmin=1000.0+((width/2.0)*math.sin(dip_min))
       lon_val=para_scen_lhs[i,1]
       lon_val_min=para_scen_lhs[i,1]-(0.5*pos_res_x)
       lon_val_max=para_scen_lhs[i,1]+(0.5*pos_res_x)
       lon_val=np.random.uniform(low=lon_val_min, high=lon_val_max)
       lat_val_min=para_scen_lhs[i,2]-(0.5*pos_res_y)
       lat_val_max=para_scen_lhs[i,2]+(0.5*pos_res_y)
       lat_val=np.random.uniform(low=lat_val_min, high=lat_val_max)
       dep_val_min=para_scen_lhs[i,3]-(0.5*pos_res_z)
       dep_val_max=para_scen_lhs[i,3]+(0.5*pos_res_z)
       dep_val=np.random.uniform(low=dep_val_min, high=dep_val_max)
       if dep_val > depmax:
          dep_val=depmax
       elif dep_val < depmin:
          dep_val=depmin
       
       # Searching latlon
       latlon = np.zeros((2))
       utm_zone, hemisphere = wgs84_to_utm(ee['lat'],ee['lon'])
       if hemisphere=='S':
           north=False
       else:
           north=True
           
       latlon[1], latlon[0] = convert_utm_to_wgs84(utm_zone, lon_val,
                                  lat_val,northern=north)
 
       ### Choice of the angles ###
       ############################

       # Inside the original code the strike/dip/rake
       # do not depend of the magnitude and position
       lat_val=latlon[0]
       lon_val=latlon[1]
       bs2_pos = len(pre_selection['BS2_Position_Selection_inn'])
       d_lonlat=np.zeros((bs2_pos,2))
       d_diff=np.zeros((bs2_pos))
       for val in range(bs2_pos):
               tmp_idx = pre_selection['BS2_Position_Selection_inn'][val]
               d_lonlat[val,:] = Discretizations['BS-2_Position']['Val'][tmp_idx].split()
               d_diff[val] = haversine(lon_val, lat_val, d_lonlat[val,0], d_lonlat[val,1])
       ipos_idx = int(np.argmin(d_diff))
       d_lon_val = d_lonlat[ipos_idx,0]
       d_lat_val = d_lonlat[ipos_idx,1]
       ipos = pre_selection['BS2_Position_Selection_inn'][ipos_idx]
       ireg = Discretizations['BS-2_Position']['Region'][ipos]
       # Faccio il load della regione se non già fatto
       if(ireg not in regions_nr):
           #print("...............................", region_files)
           region_info = load_region_infos(ireg         = ireg,
                                           region_info  = region_info,
                                           region_files = region_files)
           regions_nr.append(ireg)
       RegMeanProb_BS4 = region_info[ireg]['BS4_FocMech_MeanProb_valNorm']
       # Non credo che qui ci saranno errori, nel senso che i npy sono creati a partire dai mat conteneti roba
       if(RegMeanProb_BS4.size == 0):
            print(' --> WARNING: region info %d is empty!!!' % (ireg) )
       ipos_reg = np.where(region_info[ireg]['BS4_FocMech_iPosInRegion'] == ipos+1)[1]
       tmpProbAngles = RegMeanProb_BS4[ipos_reg[0]]
       # Creation of the array of cumulated probability intervals
       int_ens = np.zeros(len(tmpProbAngles))
       prob_cum = 0
       prob_mod=tmpProbAngles/np.sum(tmpProbAngles)
       for iii in range(len(tmpProbAngles)):
           prob_cum=prob_cum+prob_mod[iii]
           int_ens[iii]= prob_cum
       # Random selection of a value inside the cumulative distrib.
       random_value = np.random.random()
       iangle,proba_a = find_nearest(int_ens,random_value)
       str_val,dip_val,rak_val = Discretizations['BS-4_FocalMechanism']['Val'][iangle].split()
       dip_val_rad=math.radians(float(dip_val))

       #Multigaussiana
       #str_val=para_scen_lhs[i,4]
       #dip_val=para_scen_lhs[i,5]
       #rak_val=para_scen_lhs[i,6]

       ### Choice of the angle for the real sampling ###
       #################################################
       # Strike angle: uniform law #
       low_str=float(str_val)-22.5
       high_str=float(str_val)+22.5
       str_real_val=np.random.uniform(low=low_str, high=high_str)
       if str_real_val>360:
           str_real_val=str_real_val-360.0
       elif str_real_val<0:
           str_real_val=str_real_val+360.0
       # Rake angle: uniform law #
       low_rak=float(rak_val)-45.0
       high_rak=float(rak_val)+45.0
       rak_real_val=np.random.uniform(low=low_rak, high=high_rak)
       if rak_real_val>360:
           rak_real_val=rak_real_val-360.0
       elif rak_real_val<0:
           rak_real_val=rak_real_val+360.0
       ## GMPEs angle convention ###
       if rak_real_val>180:
           rak_real_val=rak_real_val-360.0
       # Dip angle: uniform law #
       low_dip=max(10,float(dip_val)-10.0)
       high_dip=min(90,float(dip_val)+10.0)

       dip_real_val=np.random.uniform(low=low_dip, high=high_dip)
       dip_real_val_rad=math.radians(float(dip_real_val))

       ### Re-evaluation of the depth: the fault plane should not reach the surface ###
       #width_leo = mag_to_w_leonardo(mag=mag_val,rake=rak_real_val)
       area_leo = mag_to_a_leonardo(mag=mag_val,rake=rak_real_val)
       aratio = 7
       width_leo = 1000.0 * (area_leo / aratio)**0.5
       lim_dep=1000.0+((width_leo/2.0)*math.sin(dip_real_val_rad))
       if dep_val<lim_dep:
          dep_val=lim_dep


       ### Slip, mag and region ###
       ############################

       #mag_list=np.array(Discretizations['BS-1_Magnitude']['Val'][:])
       #imag = np.argmin(np.abs(mag_list-mag_val_disc))
       ## Depth of the event
       #idep = np.argmin(np.abs(Discretizations['BS-3_Depth']['ValVec'][imag][ipos]-(dep_val-((area/length/2.0)*math.sin(dip_val_rad)/math.sin(math.pi/4)))/1000.0))#/math.sin(math.pi/4)))/1000.0))
       #are_val = Discretizations['BS-5_Area']['ValArea'][ireg, imag, iangle]
       #len_val = Discretizations['BS-5_Area']['ValLen'][ireg, imag, iangle]
       #sli_val = Discretizations['BS-6_Slip']['Val'][ireg, imag, iangle]

       ### Real sampled parameters ###
       ###############################
       real_val[i,0]=ireg
       real_val[i,1]=mag_val
       real_val[i,2]=lat_val
       real_val[i,3]=lon_val
       real_val[i,4]=dep_val/1000.0 
       real_val[i,5]=str_real_val
       real_val[i,6]=dip_real_val
       real_val[i,7]=rak_real_val
       real_val[i,8]=area/(1000.0**2)
       real_val[i,9]=length/1000.0
       real_val[i,10]=slip
       
       ###############################
       ##### Identification of the corresponding discretized parameters ###
       ####################################################################
       #temp_val=np.zeros((10))
       #temp_val[0]=ireg
       #temp_val[1]=Discretizations['BS-1_Magnitude']['Val'][imag] #pre_selection['sel_BS_Mag_val'][imag] #Discretizations['BS-1_Magnitude']['Val'][imag]
       #temp_val[2]= d_lat_val #d_latlon[ipos_idx,0]
       #temp_val[3]= d_lon_val #d_latlon[ipos_idx,1]
       #temp_val[4]=Discretizations['BS-3_Depth']['ValVec'][imag][ipos][idep]
       #temp_val[5]=str_val
       #temp_val[6]=dip_val
       #temp_val[7]=rak_val
       
       
       ### Real values ###
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,0]=real_val[i,0] #Reg
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,1]=real_val[i,1] #Mag
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,2]=real_val[i,2] #Lon
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,3]=real_val[i,3] #Lat
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,4]=real_val[i,4] #Depth
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,5]=real_val[i,5] #Strike
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,6]=real_val[i,6] #Dip
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,7]=real_val[i,7] #Rake
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,8]=real_val[i,8] #Area 
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,9]=real_val[i,9] #Length
       samp_ens[Nid]['real_par_scenarios_bs'][iscenbs,10]=real_val[i,10] #Slip

    samp_ens[Nid]['nr_bs_scenarios'] = np.shape(samp_ens[Nid]['prob_scenarios_bs_fact'])[0]
    return samp_ens


def ps_probability_scenarios(**kwargs):

    Config             = kwargs.get('cfg', None)
    short_term         = kwargs.get('short_term', None)
    prob_scenes        = kwargs.get('prob_scenes', None)
    samp_ens           = kwargs.get('samp_ens', None)
    pre_selection      = kwargs.get('pre_selection', None)
    Model_Weights      = kwargs.get('Model_Weights', None)
    regions            = kwargs.get('regions', None)
    PSBarInfo          = kwargs.get('PSBarInfo', None)
    region_ps          = kwargs.get('region_ps', None)
    Scenarios_PS       = kwargs.get('Scenarios_PS', None)
    ps1_magnitude      = kwargs.get('ps1_magnitude', None)
    lambda_bsps        = kwargs.get('lambda_bsps', None)
    NPS                = kwargs.get('NPS', None)
    Nid                = kwargs.get('Nid', None)
    Num_Samp           = kwargs.get('Num_Samp', None)
    ee                 = kwargs.get('ee', None)
    region_info        = dict()

    samp_ens[Nid]['PScomputedYN'] == False
    
    if(samp_ens[Nid]['PScomputedYN'] == False):# or short_term['PS_computed_YN'] == False):

        #print("--------uuuuuuuuuuuu------------>>", samp_ens[Nid]['PScomputedYN'], short_term['PS_computed_YN'])

        #fbfix 2021-11-26
        samp_ens[Nid]['PScomputedYN']    = False
        #short_term['PS_computed_YN']   = False
        #
        samp_ens[Nid]['nr_ps_scenarios'] = 0

        return samp_ens

    ##### Initiation of the array #####
    Mw=ee['mag']
    sig=ee['MagSigma']
    mag=[]
    num_mag_ps=Num_Samp
    magvaltmp=np.sort(np.random.normal(loc=Mw, scale=sig, size=num_mag_ps))
    magval=magvaltmp
    discr=np.unique(prob_scenes['par_scenarios_ps'][:,1])
    for i in range(len(magvaltmp)):
       #closestmag=min(Discretizations['PS-1_Magnitude']['Val'], key=lambda x:abs(x-magvaltmp[i]))
       closestmag=min(discr, key=lambda x:abs(x-magvaltmp[i]))
       magval[i]=closestmag
    magvalu,magvali = np.unique(magval,return_counts=True)

    #### Correction of the probability ###
    a     = magvalu[0:-1]
    b     = magvalu[1:]
    c     = np.add(a, b) * 0.5
    lower = np.insert(c, 0, -np.inf)
    upper = np.insert(c, c.size, np.inf)
    lower_probility  = norm.cdf(lower, ee['mag_percentiles']['p50'], ee['MagSigma'])
    upper_probility  = norm.cdf(upper, ee['mag_percentiles']['p50'], ee['MagSigma'])
    corr_mag=np.subtract(upper_probility, lower_probility)
    #corr_rake=np.array(weights)

    ### Identification of all the scenario in the initial ensemble that have the corresponding mag and rake values
    random_value = np.random.random(NPS)
    iscenps=0
    vec                      = np.array([100000000])#,100,1,0.0100,1.0000e-04,1.0000e-06])
    arra                     = prob_scenes['par_scenarios_ps']
    par_matrix               = np.transpose(arra[:,1])
    convolved_par_ps         = par_matrix
    for k in range(len(samp_ens[Nid]['iscenps'])):
       scene_matrix             = np.transpose(magval[k])
       convolved_sce_ps         = magval[k] #np.array(vec.dot(scene_matrix)).astype(int)
       [Iloc,nr_scenarios]      = ismember(convolved_par_ps,convolved_sce_ps)
       idx_true_scenarios       = np.where(Iloc)[0]
       if len(idx_true_scenarios):
          int_ens_tmp = np.zeros((len(idx_true_scenarios)))
          prob_cum=0
          icon=0
          tot_prob_cum=np.sum(prob_scenes['ProbScenPS'][idx_true_scenarios])
          for icum in idx_true_scenarios:
             prob_cum=prob_cum+prob_scenes['ProbScenPS'][icum]/tot_prob_cum
             int_ens_tmp[icon]= prob_cum
             icon=icon+1
          int_ens=int_ens_tmp
          random_value = np.random.random()
          idx_tmp,proba=find_nearest(int_ens,random_value)
          idx=idx_true_scenarios[idx_tmp]
       else:
          print('Issue!')
          print(magval[k])
          idx=1

       ### The final probability needs to be corrected from the biased choice of the parameters
       ### The corrections follow the same laws used to select the parameters 
       ### (gaussian for the mag and specific distribution for the rake)
       idx_mag=np.where(abs(magvalu-magval[k])<0.0001)[0]
       #idx_rake=np.where(abs(rakevalu-mag_rake[k,1])<0.0001)[0]
       corr_mag_k=corr_mag[idx_mag]
       #corr_rake_k=corr_rake[idx_rake]
       corr_vec=[corr_mag_k,1.0,1.0,1.0,1.0]

       ### The final probability corresponds to :
       ### - tot_prob_cum/np.sum(prob_scenes['ProbScenBS'] : thei probability associated to the set of selected scenario
       ### - 1/(len(idx_true_scenarios)) : the uniform value of probability from the monte-carlo sampling
       ### (The Monte Carlo sampling has a weight on the results by the dupplicated scenarios that are counted later in the ensemble)
       ### - divided by the correction of the corr_mag and corr_rake
       samp_ens[Nid]['iscenps'][iscenps]=idx
       samp_ens[Nid]['prob_scenarios_ps'][iscenps]=tot_prob_cum/(np.sum(prob_scenes['ProbScenPS'])*len(idx_true_scenarios)*corr_mag_k) #prob_scenes['ProbScenPS'][idx]/(corr_mag_k*corr_rake_k)
       for j in range(5):
           samp_ens[Nid]['prob_scenarios_ps_fact'][iscenps,j]=np.sum(prob_scenes['prob_scenarios_ps_fact'][idx_true_scenarios,j])/(np.sum(prob_scenes['prob_scenarios_ps_fact'][:,j]*len(idx_true_scenarios)*corr_vec[j]))#prob_scenes['prob_scenarios_ps_fact'][idx,j]/(corr_vec[j])
       for j in range(7):
           samp_ens[Nid]['par_scenarios_ps'][iscenps,j]=prob_scenes['par_scenarios_ps'][idx,j]
       iscenps=iscenps+1

    samp_ens[Nid]['nr_ps_scenarios'] = np.shape(samp_ens[Nid]['prob_scenarios_ps_fact'])[0]

    return samp_ens


def load_region_infos(**kwargs):

    ireg        = kwargs.get('ireg', None)
    files       = kwargs.get('region_files', None)
    region_info = kwargs.get('region_info', None)

    info = np.load(files['ModelsProb_Region_files'][ireg-1], allow_pickle=True).item()

    region_info[ireg] = info

    return region_info

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km
