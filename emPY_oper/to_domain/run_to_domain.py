#!/usr/bin/env python3
"""
Function:    
regridding the year emission inventory files to the grid, 
files should be defined in inventory_input file acording rules

Libraries and modules needed:
libraries: pandas, numpy, time, geopandas, shapely, pyproj, importlib
modules:
src.area_to_domain - read shape files and csv with area sources and gridding them
src.line_to_domain - read shape files for line sources gridding them
src.point_to_domain_zero - read shape files and csv with point sources and gridding them, 
                                just as the area sources 
    

Revision History:

16.09.2019 D. Stefanik: remove calculate pollutants, new key in inventory input "new_pollutants"     
31.10.2019 D.Stefanik: major revision of the script    
28.01.2019 D.Stefanik: creating first version of script
"""
#####
#set path to case 
case_path='../case_run'

#####Import libraries and modules
#import python libraries
import pandas as pd
import geopandas as gpd
import shapely
import pyproj
import numpy as np
import time 
import os
import sys
import importlib

#import config file
sys.path.append(case_path)
import emPY_config_file
importlib.reload(emPY_config_file)
#import libraries
import src_to_domain.area_to_domain as area_to_domain 
import src_to_domain.point_to_domain_zero as point_to_domain_zero
import src_to_domain.point_to_domain as point_to_domain
import src_to_domain.convert_to_empy_names as convert_to_empy_names

#### read parameters from config file
# set projection
projection=emPY_config_file.projection
# set grid params
grid_params=emPY_config_file.grid_params
#read internal processor names
#emis_proc_names=emPY_config_file.emis_proc_names
# read inventory input
dic_inv=emPY_config_file.dic_inv
# read case names wnich needed
list_inv=emPY_config_file.list_inv
#define output directory
output_directory=emPY_config_file.to_domain_output_directory
#set True if you want to have regriding control check in output
check_regrid=emPY_config_file.check_regrid
#set mask out file for the area sources
if 'mask_area' in emPY_config_file.__dir__(): mask_area=emPY_config_file.mask_area
#set shape file for masking out the point sources
if 'mask_point' in emPY_config_file.__dir__(): mask_point=emPY_config_file.mask_point

###############################################################################
print('The regriding will be done for {}'.format(list(list_inv)), flush=True)

start_time_of_whole_program = time.time()

#testing if input files in dictionaries exist

for name in list_inv:
     
    au=dic_inv[name]
    
    if 'input_file' in au.keys():
        if not os.path.isfile(au['input_file']):
           print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
           print('Input File {} does not exist'.format(au['input_file'])) 
        
    if 'shape_file' in au.keys():    
        if not os.path.isfile(au['shape_file']):
          print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
          print('Input File {} does not exist'.format(au['shape_file']))    
 

        
for name in list_inv:    
      
    print('####################################################################')
    print('Regrriding the {} inventory'.format(name))
   
    output_dir='{0}/{1}'.format(output_directory,name)
    
    if os.path.exists(output_dir):
       
       print('deleting files in the {0}/{1} inventory'.format(output_directory,name))
       
       os.system('rm -f {0}/{1}/*.npy'.format(output_directory,name))
       

    au=dic_inv[name]
    
    
    if 'new_pollutants' in au.keys():
        new={ x.split('=')[0].strip(): x.split('=')[0].strip() for x in au['new_pollutants'].split(',') }
        au['def_emis']={**au['def_emis'],**new}
        
    def_emis=au['def_emis']
    #area sources  
    if au['source_type'] == 'A' or au['source_type'] == 'L':
        
        if au['source_type'] == 'L': au['type']='shape'            
    
        if au['type']== 'csv+shape':
           
           emis_file=pd.read_csv(au['input_file'],sep=au['sep'], encoding=au['encoding'])
           emis_file=convert_to_empy_names.csv_to_processor_names(emis_file,au)
           emis_file['IJ']=emis_file['source_id']
           
           shape_file=gpd.read_file(au['shape_file'], encoding='utf-8')
           shape_file['IJ']=shape_file[au['shape_id']]
        
        elif au['type']== 'csv':
                       
            
           emis_file=pd.read_csv(au['input_file'],sep=au['sep'], encoding=au['encoding'])
                      
           min_x=np.min(emis_file[au['x']])
           min_y=np.min(emis_file[au['y']])
                      
           emis_file=convert_to_empy_names.csv_to_processor_names(emis_file,au)
           emis_file['IJ']=10000+(emis_file['x']-min_x)/au['grid_dx']*10000+(emis_file['y']-min_y)/au['grid_dy']           
           emis_file['IJ']=emis_file['IJ'].apply(int)   
                     
           shape_file=gpd.GeoDataFrame()
           shape_file['IJ']=emis_file['IJ']
           shape_file['geometry'] = list(zip(emis_file['x']-au['grid_dx']/2.0, emis_file['y']-au['grid_dy']/2.0,emis_file['x']+au['grid_dx']/2.0,emis_file['y']+au['grid_dy']/2.0))
           shape_file=shape_file.drop_duplicates()      
           shape_file['geometry'] = shape_file['geometry'].apply(lambda x: shapely.geometry.box(*x,ccw=True) )
           shape_file.crs = "+init=epsg:{0}".format(au['EPSG'])

        elif au['type']== 'shape':
           
           shape_file=gpd.read_file(au['shape_file'], encoding='utf-8')
           shape_file['IJ']=shape_file.index
           
           emis_file=shape_file                 
           emis_file=convert_to_empy_names.csv_to_processor_names(emis_file,au)          
        
        if 'mask_out' in au.keys(): mask_out=mask_area      
        else: mask_out=False 
              
        area_to_domain.area_to_grid(emis_file, shape_file, output_dir, name, def_emis, projection, grid_params,au['source_type'],mask_out)
        
        if check_regrid==True:
           area_to_domain.regridding_control(emis_file, shape_file, output_dir, name, def_emis, projection, grid_params)

########################################################################################################         
#point sources
#          
########################################################################################################          
    if au['source_type'] == 'P':
    
        if au['type']== 'csv':
           emis_file=pd.read_csv(au['input_file'],sep=au['sep'], encoding=au['encoding'])
           
           inProj = pyproj.Proj('init=epsg:{0}'.format(au['EPSG']))
              
        if au['type']== 'shape':
            
           emis_file=gpd.read_file(au['shape_file'], encoding='utf-8') 
            
           inProj = pyproj.Proj(emis_file.crs)
           emis_file['x']=emis_file['geometry'].x
           emis_file['y']=emis_file['geometry'].y
               
        emis_file=convert_to_empy_names.csv_to_processor_names(emis_file,au) 
        
        if 'mask_out' in au.keys(): mask_out=mask_point
        else: mask_out=False 
        
        if au['def_heights']== False:
           emis_file=convert_to_empy_names.apply_stack_parameters(emis_file,emPY_config_file.parameters)  
          
        if au['def_heights']=='zero':
           point_to_domain_zero.point_to_domain(emis_file,output_dir, name, def_emis, projection, inProj, grid_params, mask_out)
        
           if check_regrid==True:
              point_to_domain_zero.regridding_control(emis_file, output_dir, name, def_emis, projection, inProj, grid_params)
        
        if au['def_heights'] != 'zero':
           nove=point_to_domain.point_to_domain(emis_file,output_dir, name, def_emis, projection, inProj, grid_params, mask_out)

                                          
print('###############################################################################')
print('Program run sucessfully!')        
print('All data are in domain {0:.3f}'.format(time.time() - start_time_of_whole_program))
















