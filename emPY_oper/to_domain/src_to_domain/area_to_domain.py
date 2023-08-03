"""
AREA TO DOMAIN SCRIPT

Function:    
- area_to_grid: prepare emisions from csv and shape file to numpy array
- regridding_control: check how many emissions from the source file is
  in the grid and compare the numbers

Libraries and modules needed: 
libraries: numpy, shapely, time, os
modules:

Revision History:
    
30.01.2019 D. Stefanik: creating first version of script
"""


import numpy as np
import shapely
import time
import os



def area_to_grid(emis_file, shape_file, output_dir, name, def_emis, projection, grid_params,source_type,mask_out):

    if not os.path.exists(output_dir):
       os.makedirs(output_dir)
    
    XORIG=grid_params['XORIG']
    YORIG=grid_params['YORIG']
    XCELL=grid_params['XCELL']
    nj=grid_params['nj']
    ni=grid_params['ni']
    
    
    start_time = time.time()
    
    
    shape_file=shape_file.to_crs(projection)
    polyg=shapely.geometry.box(XORIG,YORIG,XORIG+(nj-1)*XCELL,YORIG+(ni-1)*XCELL,ccw=True)
    shape_file=shape_file[shape_file['geometry'].intersects(polyg) == True]
           
    
    emis_file=emis_file[emis_file['IJ'].isin(list(shape_file['IJ'].unique()))]
    
      
    dic_out={}   
    for sn in emis_file['cat_internal'].unique():
        for de in def_emis.values():
            de='{0}_{1}'.format(de,sn)
            dic_out[de]=np.zeros([ni,nj])
     
    for sn in emis_file['cat_internal'].unique():
        
        print('Processing cat: {}'.format(sn))
             
        emis_que=emis_file[(emis_file['cat_internal']==sn)]
        
             
        for index, em in emis_que.iterrows():
                
                
            ij=int(em['IJ'])
                    
            sec=shape_file[shape_file['IJ']==ij]
                   
            pol2=sec['geometry'][sec.index[0]]
            
            a=pol2.bounds
            
            if not pol2.is_valid:
               pol2=pol2.buffer(0)
               print('Be carefull, polygon {} was bad definned, buffer(0) was used to repair it'.format(index))
            
            jmin=int((a[0]-XORIG)/(XCELL))
            jmax=int((a[2]-XORIG)/(XCELL))
            
            imin=int((a[1]-YORIG)/(XCELL))
            imax=int((a[3]-YORIG)/(XCELL))
             
            if jmin < 0: jmin=0
            if imin < 0: imin=0
            if jmax > nj-1: jmax=nj-1 
            if imax > ni-1: imax=ni-1   
            
                      
            for i in range(imin,imax+1):
                for j in range(jmin,jmax+1):
                    x=j*XCELL+XORIG
                    y=i*XCELL+YORIG
                    
                    pol=shapely.geometry.box(x,y,x+XCELL,y+XCELL,ccw=True)
                    
                    if source_type == 'A': coef=pol2.intersection(pol).area/pol2.area
                    else: coef=pol2.intersection(pol).length/pol2.length  
                    
                    for de in def_emis.values():
                        dic_out['{0}_{1}'.format(de,sn)][i,j]+=coef*em[de]
      
        print("cat {0} is regrided in {1:.3f} seconds ---".format(sn,time.time() - start_time))  
        
    if mask_out != False:
       mask=np.load(mask_out)
       
       for sn in emis_file['cat_internal'].unique():
           for de in def_emis.values():    
               dic_out['{0}_{1}'.format(de,sn)]=dic_out['{0}_{1}'.format(de,sn)]*mask
    
       print("Data are masked by {}".format(mask_out))   
        
    for sn in emis_file['cat_internal'].unique():    
        for de in def_emis.values():
            if np.mean(dic_out[f'{de}_{sn}'])!=0:
               np.save(f'{output_dir}/{sn}-{de}-{name}', dic_out[f'{de}_{sn}'])  
            
        
        
    print("Data for {0} are regrided in {1:.3f} seconds".format(name,time.time() - start_time))
    

    
    
    
def regridding_control(emis_file, shape_file, output_dir, name, def_emis, projection, grid_params):
    
    XORIG=grid_params['XORIG']
    YORIG=grid_params['YORIG']
    XCELL=grid_params['XCELL']
    nj=grid_params['nj']
    ni=grid_params['ni']
        
    dic_con={}
    
    shape_file=shape_file.to_crs(projection)
    polyg=shapely.geometry.box(XORIG,YORIG,XORIG+(nj-1)*XCELL,YORIG+(ni-1)*XCELL,ccw=True)
    shape_file=shape_file[shape_file['geometry'].intersects(polyg) == True]

    
    emis_file=emis_file[emis_file['IJ'].isin(list(shape_file['IJ'].unique()))]
 
    
    for sn in emis_file['cat_internal'].unique():
        for de in def_emis.values():
            dic_con['{0}_{1}'.format(de,sn)]=0
    
    for sn in emis_file['cat_internal'].unique():
        for de in def_emis.values():
                   
            sk2=emis_file[(emis_file['cat_internal']==sn)]       
            dic_con['{0}_{1}'.format(de,sn)]+=np.sum(sk2[de])
    
    print('################# CHECKING regriding of {0} inventory'.format(name))
             
    for sn in emis_file['cat_internal'].unique():
        for de in def_emis.values():   
            
            if f'{de}_{sn}' in dic_con.keys():
            
                b=np.sum(dic_con[f'{de}_{sn}'])     
                
                if b !=0:
                
                    a=np.sum(np.load(f'{output_dir}/{sn}-{de}-{name}.npy')) 
                    per=np.round((a-b)/b*100,1) 
                
                else:     
                    a=0
                    per=0
                               
                print('cat {0}, pollutant {1}, diference {2:.2f} in percent {3}'.format(sn,de, a-b, per))
                print('value in grid {0:.3f}'.format(a))
                print('value in source file {0:.3f}'.format(b))
            
            
                   
        
            
        
               
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
