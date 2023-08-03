#!/usr/bin/env /users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 08:20:10 2023

@author: p6001
"""
import numpy as np
import netCDF4
import datetime
import sys

datum    = datetime.datetime.strptime( str( sys.argv[1] ),'%Y-%m-%d')
forecast = str(sys.argv[2])  #'00' or '12'
start    = int(sys.argv[3])  # 0  or 24
end      = start + 24


fh = [0.38, 0.36, 0.36, 0.36, 0.37, 0.5 , 1.19, 1.53, 1.57, 1.56, 1.35,
       1.16, 1.07, 1.06, 1.  , 0.98, 0.99, 1.12, 1.41, 1.52, 1.39, 1.35,
       1.  , 0.42]

# hdd mean from 2021
hdd_mean = np.load('/data/users/oko001/cmaq_oper_data/static_and_default_files/hdd_mean_2021.npy') 

# mean temperature 
td = netCDF4.Dataset(f'/data/users/oko001/cmaq_oper_data/mcip_files/METCRO2D_PYCIP-{datum.isoformat()[:10]}_{forecast}_for_{start}+{end}.nc')
Td = np.array( td['TEMP2'][:,0,:,:].mean(axis = 0) )


if forecast    ==  '12':
    
    fh = fh[12:] + fh[:13]

elif forecast  ==  '00':

    fh = fh + [0.38]  
   
def calc_res_heat_em_fac(Td, fh, hdd_mean):
    
    hdd = 286.15 -Td
    hdd[ hdd < 0 ] = 0
 
    return np.einsum('i,jk -> ijk', fh, hdd[:,:]/hdd_mean[:,:] )

em_fac =  calc_res_heat_em_fac(Td, fh, hdd_mean)   

np.save(f'/data/users/oko001/cmaq_oper_data/emis_files/emfac_resheat/emfac_{datum.isoformat()[:10]}_{forecast}_for_{start}+{end}',em_fac)
    
    
"""    
# create hdd_mean for normalization
# it was run for the first time before operation time
import pandas as pd
#mean_temp
mean_temp  = np.array(netCDF4.Dataset('/data/users/oko001/cmaq_oper_data/static_and_default_files/mean_daily_T_ala2km_2021.nc')['TEMP2'])
#hourly_prof
fh     = pd.read_csv('/data/users/oko001/cmaq_oper_data/static_and_default_files/hourly_factors_res_heating_TNO.csv',sep=',')
fh = fh['fh'].to_numpy()


hdd = np.zeros( [ mean_temp.shape[0]*24, mean_temp.shape[1], mean_temp.shape[2] ] )


Tb = 13 +273.15
for i in range(365):
    hdd[i*24:(i+1)*24,:,:] = Tb - mean_temp[i,:,:]

hdd[ hdd < 0 ] = 0 # using 0 instead standart 1

    
hdd_mean = hdd.mean( axis =0 )

fd       = np.zeros( hdd.shape )

fuel = 'uni'
f = {'gas':0.223,'solid':0.093,'oil':0.189,'uni':0}

for i in range(365):
   fd[i*24:(i+1)*24,:,:] = ( hdd[i*24:(i+1)*24,:,:] + f[fuel]*hdd_mean )/( ( 1 + f[fuel] )*hdd_mean ) # is normalized to 365


for i in range(365):
    fd[i*24:(i+1)*24,:,:] = fh[:,None,None] * fd[i*24:(i+1)*24,:,:] # is normalized to 24*365

np.save('/data/users/p6001/hdd_mean_2021',hdd_mean)
        
"""    
    
    
