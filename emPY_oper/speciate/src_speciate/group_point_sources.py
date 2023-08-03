"""
GROUP POINT SOURCES

Functions:    
- group_point_sources: append all point sources csv to one file
-stack_params_to_netCDF4: write netcdf file with stack params 

Libraries and modules needed: 
libraries: pandas, netCDF4, numpy, pyproj, datetime, os
modules:

Revision History:
    
30.01.2019 D. Stefanik: creating first version of script

@author: p6001
"""
import pandas as pd
import numpy as np
import netCDF4
import pyproj
import datetime
import os

def group_point_sources(points_path, list_point):
    
    df=pd.DataFrame()
    
    for file in list_point:
        print('!!!!!!!!!!!!!!',file)                
        data_file=pd.read_csv('{0}/{1}'.format(points_path,file))
            
        df=df.append(data_file, sort=False)
        
    df=df.reset_index()
    
    df['ROW']=df.index
    
    del df['index']    
        
    return df;    

    
        

def stack_params_to_netCDF4(df_stack,output_dir,grid_params,projection):
    
    output_dir=output_dir + '/point_sources' # save file in special subdirectory for point sources
    if not os.path.exists(output_dir):
       os.makedirs(output_dir)
    
    
    
    var_names = {'ISTACK': ['none', 'ISTACK', 'Stack group number'],
                 'LATITUDE': ['degrees', 'LATITUDE', 'Latitude'],
                 'LONGITUDE': ['degrees', 'LONGITUDE', 'Longitude'],
                 'STKDM': ['m', 'STKDM', 'Inside stack diameter'],
                 'STKHT': ['m', 'STKHT', 'Stack height above ground surface'],
                 'STKTK': ['degrees K', 'STKTK', 'Stack exit temperature'],
                 'STKVE': ['m/s', 'STKVE', 'Stack exit velocity'],
                 'STKFLW': ['m**3/s', 'STKFLW', 'Stack exit flow rate'],
                 'STKCNT': ['none', 'STKCNT', 'Number of stacks in group'],
                 'ROW': ['none', 'ROW', 'Grid row number'],
                 'COL': ['none', 'COL', 'Grid column number'],
                 'XLOCA': ['', 'XLOCA', 'Projection x coordinate'],
                 'YLOCA': ['', 'YLOCA', 'Projection y coordinate'],
                 'IFIP': ['none', 'IFIP', 'FIPS CODE'],
                 'LMAJOR': ['none', 'LMAJOR', '1= MAJOR SOURCE in domain, 0=otherwise'],
                 'LPING': ['none', 'LPING', '1=PING SOURCE in domain, 0=otherwise']}
    
    
    
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
                    'SDATE':np.int32(2016001),
                    'STIME':np.int32(0),
                    'TSTEP':np.int32(10000),
                    'UPNAM':"OPENEOUT        ",
                    'VAR-LIST':"".join('{0:16s}'.format(f) for f in var_names.keys()),
                    'VGLVLS':np.array([0.0, 0.0],dtype='float32'),
                    'VGTOP':np.float32( -9.e+36),
                    'VGTYP':np.int32(-9999),
                    'WDATE':np.int32('{0}{1:03d}'.format(datetime.datetime.today().year,datetime.datetime.today().timetuple().tm_yday)),
                    'WTIME':np.int32(63057),
                    'NCOLS':np.int32(1),
                    'NROWS':np.int32(df_stack.shape[0]),
                    'XORIG':grid_params['XORIG'],
                    'YORIG':grid_params['YORIG'],
                    'XCELL':grid_params['XCELL'],
                    'YCELL':grid_params['XCELL'],
                    'GDNAM':"Stacks_nov_grid "}
 
                      
    
    with netCDF4.Dataset('{0}/STACK_PARAM.nc'.format(output_dir),mode='w') as out:
        
         # create globals
         for global_par in global_params:
                         
            out.setncattr(global_par, global_params[global_par])

         # create dimensions
        
         out.createDimension('TSTEP', size=1)
         out.createDimension('DATE-TIME', size=global_params['DATE_TIME'])
         out.createDimension('LAY', size=global_params['NLAYS'])
         out.createDimension('VAR', size=global_params['NVARS'])
         out.createDimension('COL', size=global_params['NCOLS'])
         out.createDimension('ROW', size=global_params['NROWS'])
         
         # create TFLAGS
         out.createVariable('TFLAG', np.int32, ('TSTEP', 'VAR', 'DATE-TIME'),fill_value=None)
         out.variables['TFLAG'].setncatts({'units': "<YYYYDDD,HHMMSS>", 'long_name': "TFLAG", 'var_desc': "Timestep-valid flags:  (1) YYYYDDD or (2) HHMMSS"})     
         
         tflag=np.zeros([1,global_params['NVARS']],dtype=int)

         out.variables['TFLAG'][:,:,1]=tflag
         out.variables['TFLAG'][:16,:,0]=2016001
              
         
         # create variables
         for name in var_names:
             
             out.createVariable(name, np.float32, ('TSTEP', 'LAY', 'ROW', 'COL'),fill_value=None)
             out.variables[name].setncatts({'units': var_names[name][0], 'long_name': var_names[name][1], 'var_desc': var_names[name][2]})     
             out.variables[name][0,0,:,0]=np.array(df_stack[name][:])
             
    
            
    df_stack.drop(list(var_names.keys()), axis=1, inplace=True)
    
    
    
    return df_stack;
    
    
