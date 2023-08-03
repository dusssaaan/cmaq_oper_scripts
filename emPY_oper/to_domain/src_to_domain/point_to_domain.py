"""
POINT TO DOMAIN SCRIPT

Function:    
- point_to_domain: take point emisions to the csv with proper names and domain projection

Libraries and modules needed: 
libraries: pandas, geopandas, numpy, shapely, time, os
modules:

Revision History:
    
30.01.2019 D. Stefanik: creating first version of script
"""

import geopandas as gpd
import shapely
import numpy as np
import pyproj
import time
import os



def point_to_domain(emis_file,output_dir, name, def_emis, projection, inProj, grid_params, mask_out=False):
    
    # start time of script for quality control
    start_time = time.time()
    
    # create output directory
    output_dir=output_dir.replace(name,'')+'/point_sources' # save file in special subdirectory for point sources
    if not os.path.exists(output_dir):
       os.makedirs(output_dir)
       
    # read parameters of domain
    XORIG=grid_params['XORIG']
    YORIG=grid_params['YORIG']
    XCELL=grid_params['XCELL']
    nj=grid_params['nj']
    ni=grid_params['ni']
    
    # read projection of domain      
    outProj = pyproj.Proj(projection)
    
    # transform coordinates of stack from intial projection to domain projection 
    x,y =pyproj.transform(inProj,outProj,list(emis_file['x'][:]), list(emis_file['y'][:]))
    
    # rewrite coordinates in emis file to cordinates in domain projection
    emis_file['x']=x
    emis_file['y']=y
    
    # discard of all stacks which do not have coordinates in domain

    emis_file=emis_file[(emis_file['x']>=XORIG)]
    emis_file=emis_file[(emis_file['y']>=YORIG)]
    emis_file=emis_file[(emis_file['x']<=XORIG+(nj-1)*XCELL)]
    emis_file=emis_file[(emis_file['y']<=YORIG+(ni-1)*XCELL)]

    
    #############################################################################
    # if option mask out is true it discards all stacks in region defined by mask
    #############################################################################
    if mask_out != False:
      
      # read mask and transform it to the projection of the domain 
      mask=gpd.read_file(mask_out)
      mask=mask.to_crs(projection)
      
      # make geodata frame from emis file with geometry of point of stacks 
      emis_file['Point'] = list(zip(emis_file.x, emis_file.y))
      emis_file['Point'] = emis_file['Point'].apply(shapely.geometry.Point)    
      emis_file=gpd.GeoDataFrame(emis_file, geometry='Point')
      
      # discart all stacks within mask geometry     
      emis_file=emis_file[emis_file['Point'].within(mask['geometry'].iloc[0])!=True]
      print("Data are masked by {}".format(mask_out))
    ##########################################################################################################
    
    stackparam_name=['cat_internal','ISTACK', 'LATITUDE', 'LONGITUDE', 'STKDM', 'STKHT', 'STKTK', 'STKVE', 'STKFLW', 'STKCNT',
                     'ROW', 'COL', 'XLOCA', 'YLOCA', 'IFIP', 'LMAJOR', 'LPING']
    
    emis_file=emis_file.rename(columns={'ID':'ISTACK','height':'STKHT',
                                       'diameter':'STKDM', 'temperature':'STKTK',
                                       'velocity':'STKVE'})
    
    emis_file['LONGITUDE'], emis_file['LATITUDE'] = outProj(list(emis_file['x'][:]), list(emis_file['y'][:]),inverse='True') 
    
    emis_file=emis_file.rename(columns={'x':'XLOCA','y':'YLOCA'})
    emis_file['STKTK']=emis_file['STKTK']+273.15
    emis_file['STKFLW']=emis_file['STKVE']*np.pi*emis_file['STKDM']**2/4.0
    emis_file['STKCNT']=1
    emis_file['ROW']=0 
    emis_file['COL']=1 
    # what is this? 
    emis_file['IFIP']=emis_file['ISTACK']
    # all stack are given in lmajor option now, lping are included in poit_to_grid case
    emis_file['LMAJOR']=1
    emis_file['LPING']=0
      
    emis_file=emis_file[stackparam_name+list(def_emis.values())]      
          
    emis_file.to_csv('{0}/{1}'.format(output_dir,name),index=False)
    
    print("Point data  {0} are in proper csv format in {1:.3f} seconds".format(name,time.time() - start_time))
