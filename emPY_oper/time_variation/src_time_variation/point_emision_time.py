#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 10:51:06 2019

@author: p6001
"""
import pandas as pd
import numpy as np
import time
import copy
import os
import datetime
import netCDF4
import pyproj

coef=(10**6/(8760*3600))

def point_time_arrays(dic_time_map, em_cat_file,points,dim,dic_time_matrix,var_names):
    
    start_time=time.time() 

    print(f"Point sources contain these internal categories {points['cat_internal'].unique()}")     
    list_time_categories_used= [dic_time_map[x] for x in points['cat_internal'].unique() ]
    print(f"These are speciated as following time profiles { list_time_categories_used}")
                   
    dic_time={}
    for i in range(0,dim):
        dic_time[i]=copy.deepcopy(points)
    
        for cat in list_time_categories_used:
            
            profile_time_as_cat=list(em_cat_file[em_cat_file.time_profile ==cat]['cat_internal'].unique())
                                  
            dic_time[i].loc[(dic_time[i].cat_internal.isin(profile_time_as_cat))]*= dic_time_matrix[cat][i]
    
    dic_species={}
     
    var_names_sel= (set(points.columns) & set(var_names.keys()))
    for sp in var_names_sel:
        dic_species[sp]=np.zeros([dim,1,points.shape[0],1])
        for i in range(0,dim):
            dic_species[sp][i,0,:,0]=dic_time[i][sp]
    
    for _ in var_names_sel:
       if np.sum(dic_species[_])==0:
          del dic_species[_]     
    
    print('numpy arrays are done in {0:.1f} sec'.format(time.time() - start_time))  
    return dic_species;    

def point_to_netCDF(output_dir,out_file_name,var_names,dic_species,datum,projection,grid_params,dim,file_datum,forecast,start,end):
        
       
    if not os.path.exists(output_dir):
       os.makedirs(output_dir)
    

     
    var_names_sel= { key: var_names[key] for key in dic_species }
    var_names=var_names_sel

    
    
    global_params={ 'CDATE':np.int32('{0}{1:03d}'.format(datetime.datetime.today().year,datetime.datetime.today().timetuple().tm_yday)),
                    'P_ALP':projection['lat_1'],
                    'P_BET':projection['lat_2'],
                    'P_GAM':projection['lon_0'],
                    'XCENT':projection['lon_0'],
                    'YCENT':projection['lat_0'],
                    'PROJ4':pyproj.Proj(projection).definition_string(),
                    'CTIME':np.int32(63057),
                    'DATE_TIME':np.int32(2),
                    'EXEC_ID':"???????????????? ",
                    'FILEDESC':"Point source stack groups",
                    'FTYPE':np.int32(1),
                    'GDTYP':np.int32(2),
                    'HISTORY':"",
                    'IOAPI_VERSION':"Id",
                    'NC_STEP':np.int32(1),
                    'NLAYS':np.int32(1),
                    'NTHIK':np.int32(1),
                    'NVARS':np.int32(len(var_names.keys())),
                    'SDATE':np.int32('{0}{1:03d}'.format(datum.year,datum.timetuple().tm_yday)),
                    'STIME':np.int32(0),
                    'TSTEP':np.int32(10000),
                    'UPNAM':"OPENEOUT        ",
                    'VAR-LIST':"".join('{0:16s}'.format(f) for f in var_names.keys()),
                    'VGLVLS':np.array([0., 0.],dtype='float32'),
                    'VGTOP':np.float32( -9.e+36),
                    'VGTYP':np.int32(-9999),
                    'WDATE':np.int32('{0}{1:03d}'.format(datetime.datetime.today().year,datetime.datetime.today().timetuple().tm_yday)),
                    'WTIME':np.int32(63057),
                    'NCOLS':np.int32(1),
                    'NROWS':np.int32(dic_species[list(dic_species.keys())[0]].shape[2]),
                    'XORIG':grid_params['XORIG'],
                    'YORIG':grid_params['YORIG'],
                    'XCELL':grid_params['XCELL'],
                    'YCELL':grid_params['XCELL'],
                    'GDNAM':"OPENEOU2        "}
   
    
    with netCDF4.Dataset(f'{output_dir}/{out_file_name}-{file_datum.isoformat()[:10]}_{forecast}_for_{start}+{end}.nc'  ,mode='w') as out:
    
         # create globals
         for global_par in global_params:
                         
            out.setncattr(global_par, global_params[global_par])

         # create dimensions
        
         out.createDimension('TSTEP', None)
         out.createDimension('DATE-TIME', size=global_params['DATE_TIME'])
         out.createDimension('LAY', size=global_params['NLAYS'])
         out.createDimension('VAR', size=global_params['NVARS'])
         out.createDimension('COL', size=global_params['NCOLS'])
         out.createDimension('ROW', size=global_params['NROWS'])
         
         # create TFLAGS
         out.createVariable('TFLAG', np.int32, ('TSTEP', 'VAR', 'DATE-TIME'),fill_value=None)
         out.variables['TFLAG'][:,:,1]= np.array( [[  int( 10000 * ( datum + datetime.timedelta( hours=i ) ).hour )  for i in range(0,dim) ] for var in range(0, global_params['NVARS']) ] ).transpose()
         out.variables['TFLAG'][:,:,0]= np.array( [[  int(f'{datum.year}{(datum + datetime.timedelta(hours=x)).timetuple().tm_yday:03d}') for x in range( 0, dim ) ] for var in range(0, global_params['NVARS']) ] ).transpose()
         out.variables['TFLAG'].setncatts({'units': '<YYYYDDD,HHMMSS>', 'long_name':'TFLAG           ' , 'var_desc':'Timestep-valid flags:  (1) YYYYDDD or (2) HHMMSS                                '  })
   
         # create variables
         for name in var_names:
             
             out.createVariable(name, np.float32, ('TSTEP', 'LAY', 'ROW', 'COL'),fill_value=None)
             out.variables[name].setncatts({'units': var_names[name][0], 'long_name': var_names[name][1], 'var_desc': var_names[name][2]})     
             out.variables[name][:,:,:,:]=dic_species[name]*coef 









