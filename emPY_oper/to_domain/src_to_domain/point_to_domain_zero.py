"""
POINT TO DOMAIN ZERO SCRIPT

Function:    
- point_to_domain: take point emisions to numpy array
- regridding_control: check how many emissions from the source file is
  in the grid and compare the numbers

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

    if not os.path.exists(output_dir):
       os.makedirs(output_dir)
    
    XORIG=grid_params['XORIG']
    YORIG=grid_params['YORIG']
    XCELL=grid_params['XCELL']
    nj=grid_params['nj']
    ni=grid_params['ni']
    
    
    start_time = time.time()
 
    outProj = pyproj.Proj(projection)
   
    x,y =pyproj.transform(inProj,outProj,list(emis_file['x'][:]), list(emis_file['y'][:]))
 
    emis_file['x']=x
    emis_file['y']=y

    emis_file=emis_file[(emis_file['x']>=XORIG)]
    emis_file=emis_file[(emis_file['y']>=YORIG)]
    emis_file=emis_file[(emis_file['x']<=XORIG+(nj-1)*XCELL)]
    emis_file=emis_file[(emis_file['y']<=YORIG+(ni-1)*XCELL)]
    
    if mask_out != False:
      mask=gpd.read_file(mask_out)
      mask=mask.to_crs(projection)
      emis_file['Point'] = list(zip(emis_file.x, emis_file.y))
      
      emis_file['Point'] = emis_file['Point'].apply(shapely.geometry.Point)    
      emis_file=gpd.GeoDataFrame(emis_file, geometry='Point')
      emis_file=emis_file[emis_file['Point'].within(mask['geometry'].iloc[0])!=True]
       
      print("Data are masked by {}".format(mask_out))
       
    dic_out={}   
    for sn in emis_file['cat_internal'].unique():
        for de in def_emis.values():
            de='{0}_{1}'.format(de,sn)
            dic_out[de]=np.zeros([ni,nj])
  
    for sn in emis_file['cat_internal'].unique():
        
        print('Processing cat: {}'.format(sn))
        emis_que=emis_file[(emis_file['cat_internal']==sn)]
     
        for index, em in emis_que.iterrows():
         
            j=int((em['x']-XORIG)/XCELL)
            i=int((em['y']-YORIG)/XCELL)
              
            for de in def_emis.values():    
                dic_out['{0}_{1}'.format(de,sn)][i,j]+=em[de]
      
        print("cat {0} is regrided in {1:.3f} seconds ---".format(sn,time.time() - start_time))
        
    for sn in emis_file['cat_internal'].unique():
        for de in def_emis.values():
            np.save('{0}/{1}-{2}-{3}'.format(output_dir,sn,de,name),  dic_out['{0}_{1}'.format(de,sn)])

      
    
    
    print("Data for {0} are regrided in {1:.3f} seconds".format(name,time.time() - start_time))




def regridding_control(emis_file, output_dir, name, def_emis,projection, inProj, grid_params):
    
    
    XORIG=grid_params['XORIG']
    YORIG=grid_params['YORIG']
    XCELL=grid_params['XCELL']
    nj=grid_params['nj']
    ni=grid_params['ni']
    

    emis_file=emis_file[(emis_file['x']>=XORIG)]
    emis_file=emis_file[(emis_file['y']>=YORIG)]
    emis_file=emis_file[(emis_file['x']<=XORIG+(nj-1)*XCELL)]
    emis_file=emis_file[(emis_file['y']<=YORIG+(ni-1)*XCELL)]
    
    dic_con={}
    for sn in emis_file['cat_internal'].unique():
        for de in def_emis.values():
            de='{0}_{1}'.format(de,sn)
            dic_con[de]=0
            
    
    for sn in emis_file['cat_internal'].unique():
        for de in def_emis.values():
            sk2=emis_file[(emis_file['cat_internal']==sn)]
            dic_con['{0}_{1}'.format(de,sn)]+=np.sum(sk2[de])
    
    print('################# CHECKING regriding of {0} inventory'.format(name))
             
    for sn in emis_file['cat_internal'].unique():
        for de in def_emis.values():   
            if '{0}_{1}'.format(de,sn) in dic_con.keys():
            
                sk=np.load('{0}/{1}-{2}-{3}.npy'.format(output_dir,sn,de,name)) 
               
                a=np.sum(sk)
                
                b=np.sum(dic_con['{0}_{1}'.format(de,sn)])
                
                per=0
                if b > 0:
                   per=np.round((a-b)/b*100,1) 
                
                print('cat {0}, pollutant {1}, diference {2:.2f} in percent {3}'.format(sn,de, a-b, per))
                print('value in grid {0:.3f}'.format(a))
                print('value in source file {0:.3f}'.format(b))    
    
    
