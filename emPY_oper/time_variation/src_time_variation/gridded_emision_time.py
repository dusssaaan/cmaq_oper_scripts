#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 12:55:40 2019

@author: p6001
"""
import time
import os
import numpy as np
import netCDF4
import datetime

coef=(10**6/(8760*3600))
def area_time_arrays(time_zone, input_dir,var_names,dic_time_matrix, dic_time_map,dim,ni,nj,dic_array_nc):
   
   
   
   start_time=time.time() 
    
   dic_species={}         
   for spec in var_names:
       dic_species[spec]=np.zeros([dim,1,ni,nj])
                                                                                                                                                                                                                                                                                                                                                                
   for file in (set(os.listdir(input_dir))-set(['point_sources'])):
        f_split=file.split( "-" )
            
        if f_split[1][:-4] in dic_species.keys():
        
           if int(f_split[0]) in dic_time_map.keys():
            
              au=np.load('{0}/{1}'.format(input_dir,file))
                  
              if dic_time_map[int(f_split[0])] not  in dic_array_nc.keys():
                 au2=np.einsum("kl,i->ikl",au,dic_time_matrix[dic_time_map[int(f_split[0])]])
              else:
                                                   
                 #print(f'time matrix is applied for {int(f_split[0])} and {file}')
                 au2=np.einsum("kl,ikl->ikl",au,dic_array_nc[dic_time_map[int(f_split[0])]])
             
              dic_species[f_split[1][:-4]][:,0,:,:]+=au2
            
           else:
              print('{0}-{1} is not taking to time variation'.format(f_split[0],f_split[1][:-4])) 
   
   list_spec=list(dic_species.keys())
   for _ in list_spec:
       if np.sum(dic_species[_])==0:
          del dic_species[_] 
    
   print('numpy arrays are done in {0:.1f} sec'.format(time.time() - start_time))  
   return dic_species;


#writing to netcdf ############################################################################
def gridded_to_netCDF(output_dir,out_file_name,var_names,dic_species,datum,projection,grid_params,dim,file_datum,forecast,start,end ):
        
       
    if not os.path.exists(output_dir):
       os.makedirs(output_dir)
     
    # if some pollutans has zero emisions do not take it to the outputs    
    var_names_sel= { key: var_names[key] for key in dic_species }
    var_names=var_names_sel
    
    global_params={ 'CDATE':np.int32('{0}{1:03d}'.format(datetime.datetime.today().year,datetime.datetime.today().timetuple().tm_yday)),
                    'P_ALP':projection['lat_1'],
                    'P_BET':projection['lat_2'],
                    'P_GAM':projection['lon_0'],
                    'XCENT':projection['lon_0'],
                    'YCENT':projection['lat_0'],
                    'CTIME':np.int32(63057),
                    'DATE_TIME':np.int32(2),
                    'EXEC_ID':"???????????????? ",
                    'FILEDESC':"gridded emissions",
                    'FTYPE':np.int32(1),
                    'GDTYP':np.int32(2),
                    'HISTORY':"",
                    'IOAPI_VERSION':"Id",
                    'NC_STEP':np.int32(1),
                    'NLAYS':np.int32(1),
                    'NTHIK':np.int32(1),
                    'NVARS':np.int32(len(dic_species.keys())),
                    'SDATE':np.int32('{0}{1:03d}'.format(datum.year,datum.timetuple().tm_yday)),
                    'STIME':np.int32(0),
                    'TSTEP':np.int32(10000),
                    'UPNAM':"OPENEOUT        ",
                    'VAR-LIST':"".join('{0:16s}'.format(f) for f in dic_species.keys()),
                    'VGLVLS':np.array([0., 0],dtype='float32'),
                    'VGTOP':np.float32(0.),
                    'VGTYP':-np.int32(1),
                    'WDATE':np.int32('{0}{1:03d}'.format(datetime.datetime.today().year,datetime.datetime.today().timetuple().tm_yday)),
                    'WTIME':np.int32(63057),
                    'NCOLS':np.int32(grid_params['nj']),
                    'NROWS':np.int32(grid_params['ni']),
                    'XORIG':grid_params['XORIG'],
                    'YORIG':grid_params['YORIG'],
                    'XCELL':grid_params['XCELL'],
                    'YCELL':grid_params['XCELL'],
                    'GDNAM':f"{out_file_name[:16]}"}
   
    
    with netCDF4.Dataset(f'{output_dir}/{out_file_name}-{file_datum.isoformat()[:10]}_{forecast}_for_{start}+{end}.nc',mode='w') as out:
    
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
         












