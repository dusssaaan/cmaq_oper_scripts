#!/usr/bin/env /users/p6065/anaconda3/envs/supergeo/bin/python
"""
TIME VARIATION SCRIPT

Function:    
reading numpy arrays after speciation, preparing time matrices from time maping and time series files,
applying the time matrices to the numpy arrays,
saving the emissions to netcdf files

now you need read old netcdf file in which the fields will be saving 

Libraries and moduls needed:
libraries: pandas, numpy, netCDF4, time, pytz, datetime, os, netCDF4

Revision History:
    
28.01.2019 D. Stefanik: creating first version of script

"""
#set path to case 
case_path='/users/oko001/cmaq_oper_scripts/emPY_oper/case_run'

# import proper libraries
import pandas as pd
import time
import os
import datetime
import src_time_variation.time_matrix as tm
import src_time_variation.gridded_emision_time as gt
import src_time_variation.point_emision_time as pt
import sys
import importlib
sys.path.append(case_path)
import emPY_config_file
importlib.reload(emPY_config_file)
import pytz
import numpy as np


datum    = datetime.datetime.strptime( str( sys.argv[1] ),'%Y-%m-%d')
forecast = str(sys.argv[2])  #'00' or '12'
start    = int(sys.argv[3])  # 0  or 24
end      = start + 24
  

dic_array={9020:f'/data/users/oko001/cmaq_oper_data/emis_files/emfac_resheat/emfac_{datum.isoformat()[:10]}_{forecast}_for_{start}+{end}.npy' }

#read configuration file 
input_dir=emPY_config_file.time_variate_input_dir
output_dir=emPY_config_file.time_variate_output_dir
out_file_name=emPY_config_file.out_file_name
T_ZONE=emPY_config_file.T_ZONE
tv_mapping=pd.read_csv(emPY_config_file.tv_mapping)
tv_values=pd.read_csv(emPY_config_file.tv_values) 
tv_series=pd.read_csv(emPY_config_file.tv_series)

em_cat_file=pd.read_csv(emPY_config_file.em_cat_file)
# datum_start=datetime.datetime.strptime(emPY_config_file.datum_start, '%Y-%m-%d')
# datum_end=datetime.datetime.strptime(emPY_config_file.datum_end, '%Y-%m-%d')
var_names=emPY_config_file.var_names
# parameters of grid
ni = emPY_config_file.grid_params['ni']
nj = emPY_config_file.grid_params['nj']
projection=emPY_config_file.projection
grid_params=emPY_config_file.grid_params


#########################################################################################################
# proper sript, nothing to set up
#########################################################################################################
start_time = time.time()

#species_write to netcdf file
cmaq_sp=list(pd.read_csv(emPY_config_file.spec_file, comment='#')['spec_name'].unique())

for _ in cmaq_sp: 
      if _ not in var_names: 
          sys.exit(f'!!!! Error: {_} not in var names and will not be in output')
          
var_names_sel= { key: var_names[key] for key in cmaq_sp }


time_zone=pytz.timezone(T_ZONE)

if not os.path.exists(output_dir):
   os.makedirs(output_dir)


dic_array_nc={}
for cat in dic_array:

        dic_array_nc[cat]= np.load(dic_array[cat])



dic_time_map=dict(zip(em_cat_file['cat_internal'], em_cat_file['time_profile']))
if os.path.isdir(input_dir+'/point_sources'): points=pd.read_csv(input_dir+'/point_sources/speciate_points')



if forecast == '00' and start == 0:
   
   datum_map = datum

elif forecast == '00' and start == 24:    
   
   datum_map = datum + datetime.timedelta(days=1)

elif forecast == '12' and start == 0:    
   
   datum_map = datum + datetime.timedelta(hours=12)

elif forecast == '12' and start == 24:    
   
   datum_map = datum + datetime.timedelta(hours=36)

    
    
dim=25
dic_time_matrix=tm.time_matrix(time_zone, tv_values, tv_mapping, tv_series, em_cat_file, datum_map, dim)

#%%
print("####################### Processing area sources ############################################")

dic_species=gt.area_time_arrays(time_zone, input_dir,var_names,dic_time_matrix, dic_time_map,dim,ni,nj,dic_array_nc)
gt.gridded_to_netCDF(output_dir,out_file_name,var_names_sel,dic_species,datum_map,projection,grid_params,dim, datum, forecast,start,end)

if os.path.isdir(input_dir+'/point_sources'):
   print("####################### Processing point sources ############################################")

   dic_species=pt.point_time_arrays(dic_time_map,em_cat_file,points,dim,dic_time_matrix,var_names)
   pt.point_to_netCDF(output_dir,out_file_name +'_STACK',var_names_sel,dic_species,datum_map,projection,grid_params,dim, datum, forecast,start,end)
else:
   print('no point sources detected') 


print('Program run succesfully:-) in {0:.1f} sec'.format(time.time() - start_time))  
