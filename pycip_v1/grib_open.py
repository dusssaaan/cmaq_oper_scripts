#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 10:05:30 2023

@author: p6001
"""

import pygrib
import numpy as np
import time
import multiprocessing
from functools import partial
import datetime

#%%
get_2D = lambda grib,cut: grib.values[cut[0]: cut[1], cut[2]: cut[3]]

cum_var = ['TURB_ZO', 'TURB_ME', 'HFX', 'LH', 'RGRND'  ] # cumulative fields

def read_vars_pygrib(path,file_name,int_datum,nlay,cut,tprev, tstep):
    
    out = {}
    
    start_time =  time.time() 
     
    if tstep == 0 and tprev == '12' : # in case of tstep 0 read tstep 12 from previous run 
        
       datum     = datetime.datetime.strptime(int_datum.split('_')[0],'%Y-%m-%d') 
       file_name    = f'{file_name}{12:04d}.grb.CMAQ'
       
       if int_datum.split('_')[1] =='00':
          datum_bef = datum - datetime.timedelta(days=1)
          int_datum = f'{datum_bef}'[:-9] + '_12'
       elif int_datum.split('_')[1] =='12':
          int_datum = f'{datum}'[:-9] + '_00'

    elif tstep == 0 and tprev == '00' : # in case of tstep 0 read tstep 12 from previous run 
        
       datum     = datetime.datetime.strptime(int_datum.split('_')[0],'%Y-%m-%d') 
       file_name    = f'{file_name}{24:04d}.grb.CMAQ'
       
       datum_bef = datum - datetime.timedelta(days=1)
       int_datum = f'{datum_bef}'[:-9] + '_00'

    
    else : file_name    = f'{file_name}{tstep:04d}.grb.CMAQ'
    
    path = path + '/' + int_datum + '/' 
    
    grib = pygrib.open( path + '/' + file_name )
    
    
    #neglected vertical layers + 1
    nn = 1 + 1
    
    shape = grib.select(shortName='lai',typeOfLevel='surface')[0].values.shape
    for var in ['T', 'QV','CFRAC_3D','QC','QR', 'QS']:
        out[var] = np.zeros( ( nlay, shape[0] - np.abs(cut[0]) - np.abs(cut[1]) , shape[1] - np.abs(cut[2]) - np.abs(cut[3]) ) )
    out['U'] =  np.zeros( ( nlay, shape[0] - np.abs(cut[0]) - np.abs(cut[1]) , shape[1] - np.abs(cut[2]) - np.abs(cut[3]) +1 ) ) # add +1 as in wrf
    out['V'] =  np.zeros( ( nlay, shape[0] - np.abs(cut[0]) - np.abs(cut[1]) +1, shape[1] - np.abs(cut[2]) - np.abs(cut[3]) ) )    # add +1 as in wrf
        
    for var in (cum_var + ['RAINC', 'RAINNC']):
       out[var] = np.zeros( out['T'][0,:].shape )
    
    for g in grib:
        #print(g.shortName) 
        if g.typeOfLevel == 'surface':
            
            if g.shortName == 'lai'               : out['LAI']     = get_2D(g, cut)
            if g.shortName == 'sp'                : out['PRSFC']   = get_2D(g, cut)
            if g.shortName == 'tcc'               : out['CFRAC']   = get_2D(g, cut)
            if g.shortName == 'hpbl'              : out['PBL']     = get_2D(g, cut)
            if g.shortName == 'sot'               : out['TEMPG']   = get_2D(g, cut)
            if g.shortName == 'sde'               : out['SNOCOV']  = get_2D(g, cut)
            if g.shortName == 'ssw'               : out['SOIM1']   = get_2D(g, cut)/1000/0.01  # /hustota vody /depth in [m]
            if g.shortName == 'sfcrh'             : out['ROUGHT']  = get_2D(g, cut)   
            if g.shortName == 'w_i'               : out['WR']      = get_2D(g, cut)
            if g.shortName == 'veg'               : out['VEG']     = get_2D(g, cut)                
            # cumulative vars
            if g.shortName == 'lswp' or  g.shortName == 'lsf'    : 
               out['RAINC']  += get_2D(g, cut)         
              # print("RAINC", g.shortName, out['RAINC'].max()) 
            if g.shortName == 'cwp'  or  g.shortName == 'csf'    :
               out['RAINNC'] += get_2D(g, cut)
              # print("RAINNC", out['RAINNC'].max())
            if tstep !=0:
                if g.shortName == 'ewss'              : out['TURB_ZO'] = get_2D(g, cut)
                if g.shortName == 'nsss'              : out['TURB_ME'] = get_2D(g, cut)
                if g.shortName == 'sshf'              : out['HFX']     = get_2D(g, cut)
                if g.shortName == 'slhf'              : out['LH']      = get_2D(g, cut)
                if g.shortName == 'ssrd'              : out['RGRND']   = get_2D(g, cut)

            
        if g.typeOfLevel == 'depthBelowLand':
            
            if g.shortName == 'ssw'               : out['SOIM2']  = get_2D(g, cut)/1000 
            if g.shortName == 'sot'               : out['SOIT1']  = get_2D(g, cut) 
        
        if g.typeOfLevel == 'heightAboveGround':
            
            if g.shortName == '10u'               : out['U10']    = get_2D(g, cut)
            if g.shortName == '10v'               : out['V10']    = get_2D(g, cut) 
            if g.shortName == '2sh'               : out['Q2']     = get_2D(g, cut)
            if g.shortName == '2t'                : out['TEMP2']  = get_2D(g, cut)

        if g.typeOfLevel == 'hybrid' and g.level >= 2 :

           if g.shortName == 't'                            : out['T'][g.level-nn,:,:]    = get_2D(g, cut)
          
            
           if g.shortName == 'q'                            : out['QV'][g.level-nn,:,:]        = get_2D(g, cut) 
           if g.shortName == 'cdca'                         : out['CFRAC_3D'][g.level-nn,:,:]  = get_2D(g, cut)
           if g.shortName == 'clwc' or g.shortName == 'ciwc':
              #print(g.shortName)
              out['QC'][g.level-nn,:,:]       += get_2D(g, cut)            
           if g.shortName == 'crwc'                         : out['QR'][g.level-nn,:,:]        = get_2D(g, cut)
           if g.shortName == 'cswc'                         : out['QS'][g.level-nn,:,:]        = get_2D(g, cut) 
           if g.shortName == 'u'             : 
               u_wind = g.values 
               out['U'][g.level-nn,:,:] = ( u_wind[cut[0]: cut[1], cut[2]-1: cut[3]] + u_wind[cut[0] : cut[1], cut[2]: cut[3]+1] )/2
           if g.shortName == 'v'             :              
               v_wind = g.values 
               out['V'][g.level-nn,:,:] = ( v_wind[cut[0]-1: cut[1], cut[2]: cut[3]] + v_wind[cut[0] : cut[1]+1, cut[2]: cut[3]] )/2

    print(f'Inputs for int_time {int_datum} and hour {tstep} from {file_name} are read in {(time.time() - start_time):.1f} sec')

    return out

#%%
def multi_reader(path,file_name,int_datum,nlay,cut,tstart,tend,tprev,nproc = 5):
  
    start_time =  time.time()
    pool = multiprocessing.Pool(processes = nproc)
    
    read_vars_timest = partial( read_vars_pygrib, path, file_name, int_datum, nlay, cut, tprev )
    
    data_hours = pool.map ( read_vars_timest, range( tstart, tend+1  )  )
    print(f'Inputs for hours are read in {(time.time() - start_time):.1f} sec')
    return data_hours


def single_reader(path,file_name,int_datum,nlay,cut,tstart, tend, tprev):
   
    start_time =  time.time()
    
    read_vars_timest = partial( read_vars_pygrib, path, file_name, int_datum, nlay, cut, tprev )
    
    data_hours = [read_vars_timest(x) for x in range( tstart, tend+1  )  ]
    print(f'Inputs for hours are read in {(time.time() - start_time):.1f} sec')
    return data_hours


def process_grib_data(type_proc,path,file_name,int_datum,nlay,cut,tstart,tend, tprev, nproc = 5   ):
    
    start_time = time.time()
    
    if type_proc == 'single':
    
        data_hours = single_reader( path,file_name,int_datum,nlay,cut,tstart,tend, tprev )
       
    if type_proc == 'multi':    
       
        data_hours = multi_reader( path,file_name,int_datum,nlay,cut,tstart,tend,tprev, nproc ) 
    
    
    print('dazd {0:.1f} sec'.format(time.time() - start_time))     
    if tstart == 0 and  tprev == '12' :
    
        datum     = datetime.datetime.strptime(int_datum.split('_')[0],'%Y-%m-%d') 
        file_name    = f'{file_name}{11:04d}.grb.CMAQ'
              
        if int_datum.split('_')[1] =='00':
                 datum_bef = datum - datetime.timedelta(days=1)
                 int_datum = f'{datum_bef}'[:-9] + '_12'
        elif int_datum.split('_')[1] =='12':
                 int_datum = f'{datum}'[:-9] + '_00'
    
                 
    elif tstart == 0 and  tprev == '00' :
    
        datum     = datetime.datetime.strptime(int_datum.split('_')[0],'%Y-%m-%d') 
        file_name    = f'{file_name}{23:04d}.grb.CMAQ'
              
        datum_bef = datum - datetime.timedelta(days=1)
        int_datum = f'{datum_bef}'[:-9] + '_00'

    
    else : file_name    = f'{file_name}{tstart-1:04d}.grb.CMAQ'             
       
    print(f'rain from {int_datum}/{file_name}')         
    gribn = pygrib.open( path + '/' + int_datum + '/' + file_name )
    
    rainc   = gribn.select(shortName='lswp',typeOfLevel='surface')[0].values + gribn.select(shortName='lsf',typeOfLevel='surface')[0].values
    rainnc  = gribn.select(shortName='cwp',typeOfLevel='surface')[0].values  + gribn.select(shortName='csf',typeOfLevel='surface')[0].values
    
    rainc   = rainc[cut[0]: cut[1], cut[2]: cut[3] ]
    rainnc  = rainnc[cut[0]: cut[1], cut[2]: cut[3] ] 
    
    #print('dazdkoniec {0:.1f} sec'.format(time.time() - start_time))     
    out = {}
    for k in data_hours[0].keys():
        if k == 'RAINC':
            out[k] = np.array( [ rainc ]  + [out[k] for out in data_hours])
        elif k == 'RAINNC':
            out[k] = np.array( [ rainnc ] + [out[k] for out in data_hours])
        else:    
           out[k] = np.array([out[k] for out in data_hours])
         
    #print('max', out['RAINC'].max(), out['RAINNC'].max())
       
    #print('ikrok {0:.1f} sec'.format(time.time() - start_time))
    out['SOIT1'] = out['TEMPG'] * 8/10 + out['SOIT1'] * 2/10   # some arbitrary coef to get 1 cm soil temp, aladin 

    for var in cum_var:
        out[var] = np.concatenate( ( (out[var][1,:] - out[var][0,:])[None,:,:]/3600, (out[var][2:,:] - out[var][:-2,:])/7200, ((out[var][-1,:] - out[var][-2,:])[None,:,:]  )/3600  ) )
    #print('i3krok {0:.1f} sec'.format(time.time() - start_time))
    for var in ['T', 'QV','CFRAC_3D','QC','QR', 'QS','U','V']:
        out[var][:,:,:,:] = out[var][:,::-1,:,:]
        

    tau = np.sqrt(out['TURB_ZO'] **2 + out['TURB_ME'] **2)
    #print('1krok {0:.1f} sec'.format(time.time() - start_time))
    rho = out['PRSFC'] /( (287.1 + (461.5 - 287.1 ) * out['Q2'] ) * out['TEMP2'] )
    #print('2krok {0:.1f} sec'.format(time.time() - start_time))
    out['USTAR'] = np.sqrt( tau / rho )

    # from specific to mixing ratio
    out['QV'] = out['QV'] / ( 1 - out['QV'] )
    out['QC'] = out['QC'] / ( 1 - out['QC'] )
    out['QR'] = out['QR'] / ( 1 - out['QR'] )
    out['QS'] = out['QS'] / ( 1 - out['QS'] )
    out['Q2'] = out['Q2'] / ( 1 - out['Q2'] )

    # SNOCOV from 0 to 1
    out['SNOCOV'][out['SNOCOV']<5] /= 5
    out['SNOCOV'][out['SNOCOV']>=5] = 1
    out['HFX'] = -out['HFX']
    out['LH']  = -out['LH']

    out['SOIM1'][out['SOIM1'] > 1] = 1
    out['SOIM2'][out['SOIM2'] > 1] = 1
    
    out['po'] = 101325.
    out['bf']   = np.array([1.00000000e+00, 9.97621515e-01, 9.94968780e-01, 9.91835807e-01,
       9.88252355e-01, 9.84229631e-01, 9.79772520e-01, 9.74882396e-01,
       9.69558284e-01, 9.63797454e-01, 9.57595774e-01, 9.50947933e-01,
       9.43847599e-01, 9.36287534e-01, 9.28259690e-01, 9.19755280e-01,
       9.10764854e-01, 9.01278362e-01, 8.91285220e-01, 8.80774382e-01,
       8.69734411e-01, 8.58153565e-01, 8.46019886e-01, 8.33321311e-01,
       8.20045782e-01, 8.06433191e-01, 7.92696276e-01, 7.78793033e-01,
       7.64688145e-01, 7.50352544e-01, 7.35762948e-01, 7.20901384e-01,
       7.05754685e-01, 6.90313973e-01, 6.74574140e-01, 6.58533301e-01,
       6.42192250e-01, 6.25553909e-01, 6.08622778e-01, 5.91404395e-01,
       5.73904819e-01, 5.56130140e-01, 5.38086046e-01, 5.19777449e-01,
       5.01208204e-01, 4.82380932e-01, 4.63296986e-01, 4.43956570e-01,
       4.24359064e-01, 4.04503556e-01, 3.84389644e-01, 3.64018514e-01,
       3.43394336e-01, 3.22526005e-01, 3.01429226e-01, 2.80128966e-01,
       2.58662234e-01, 2.37081147e-01, 2.15456181e-01, 1.93879449e-01,
       1.72467786e-01, 1.51365292e-01, 1.31273982e-01, 1.12799372e-01,
       9.59450775e-02, 8.06985139e-02, 6.70316250e-02, 5.49018829e-02,
       4.42535121e-02, 3.50188823e-02, 2.71200160e-02, 2.04701548e-02,
       1.49753307e-02, 1.05358929e-02, 7.04794030e-03, 4.40460990e-03,
       2.49715510e-03, 1.21570320e-03, 4.49432000e-04, 8.53058000e-05,
       0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00,
       0.00000000e+00, 0.00000000e+00, 0.00000000e+00])
    
    
    out['af']   = np.array([0.00000000e+00, 0.00000000e+00, 5.16961263e-06, 2.44936985e-05,
       6.39398075e-05, 1.29971665e-04, 2.29593782e-04, 3.70358766e-04,
       5.60365754e-04, 8.08255130e-04, 1.12320122e-03, 1.51490283e-03,
       1.99357157e-03, 2.56991754e-03, 3.25513161e-03, 4.06086365e-03,
       4.99919591e-03, 6.08261064e-03, 7.32395074e-03, 8.73637246e-03,
       1.03332887e-02, 1.21283015e-02, 1.41351220e-02, 1.63674761e-02,
       1.88389944e-02, 2.15123514e-02, 2.43456814e-02, 2.73447691e-02,
       3.05152648e-02, 3.38623320e-02, 3.73903643e-02, 4.11027608e-02,
       4.50017546e-02, 4.90882886e-02, 5.33619368e-02, 5.78208635e-02,
       6.24618204e-02, 6.72801736e-02, 7.22699555e-02, 7.74239342e-02,
       8.27336889e-02, 8.81896822e-02, 9.37813138e-02, 9.94969402e-02,
       1.05323843e-01, 1.11248129e-01, 1.17254528e-01, 1.23326090e-01,
       1.29443725e-01, 1.35585591e-01, 1.41726277e-01, 1.47835779e-01,
       1.53878231e-01, 1.59810381e-01, 1.65579805e-01, 1.71122856e-01,
       1.76362399e-01, 1.81205367e-01, 1.85540267e-01, 1.89234790e-01,
       1.92133776e-01, 1.94057851e-01, 1.94800588e-01, 1.94281376e-01,
       1.92504234e-01, 1.89489896e-01, 1.85275140e-01, 1.79911868e-01,
       1.73465957e-01, 1.66015972e-01, 1.57651776e-01, 1.48473116e-01,
       1.38588223e-01, 1.28112522e-01, 1.17167474e-01, 1.05879663e-01,
       9.43801940e-02, 8.28045860e-02, 7.12934903e-02, 5.99952340e-02,
       4.90758015e-02, 3.87817317e-02, 2.92667659e-02, 2.06241244e-02,
       1.29919687e-02, 6.60935488e-03, 2.14618846e-03])
    
    
    out['etaf'] = out['af'] + out['bf']
    print('All time are read in {0:.1f} sec'.format(time.time() - start_time))
    return out



