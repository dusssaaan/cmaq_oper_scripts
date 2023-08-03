#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CREATE TIME VARIATION MATRICES

@author: p6001
"""
import datetime
import numpy as np
import time

def time_matrix(time_zone, tv_values, tv_mapping, tv_series, em_cat_file,datum,dim):
    
    start_time = time.time()
  
    shift_time=int(str(time_zone.localize(datum))[-6:-3])
    
    ########################### preparing time_matrix for the tv_mapping  ###############################################################    
          
    dic_time_matrix={}
    for i, tv in tv_mapping.iterrows():
        
        local_datum=datum+datetime.timedelta(hours=shift_time)
        dic_time_matrix[tv['time_profile']]=[]
        
        #print('#######',tv['time_profile'])   
        for t_step in range(0,dim):
            
                       
              coef_m=float(tv_values[((tv_values['tv_id']==tv['mounth_factor'])&(tv_values['period']==local_datum.month))]['tv_factor']) 
              weekday=local_datum.weekday()+1
                                  
              coef_weekday=float(tv_values[((tv_values['tv_id']==tv['day_factor'])&(tv_values['period']== weekday ))]['tv_factor'])
              
              coef_hour=float(tv_values[((tv_values['tv_id']==tv['hour_factor'])&(tv_values['period']== local_datum.hour ))]['tv_factor'])
              
              #print(local_datum.hour)
                                   
              dic_time_matrix[tv['time_profile']].append(coef_m*coef_weekday*coef_hour)
              
              local_datum += datetime.timedelta(hours=1)
              
              
                      
        dic_time_matrix[tv['time_profile']]=np.array(dic_time_matrix[tv['time_profile']])
              
       
    
    #################################### preparing time_matrix from the tv_select ##########################################################
    for category in tv_series['time_profile'].unique():
        #print('3#######',category)
        if category in em_cat_file['time_profile'].unique():
            tv_series_select=tv_series[tv_series['time_profile']==category]
            dic_time_matrix[category]=[]
            
            local_datum=datum # +datetime.timedelta(hours=shift_time)# in tv_series there is assumed to be a utc_time
            
            for t_step in range(0,dim):
                  
                  #print( local_datum.isoformat().replace('T',' ') )
                  if tv_series_select[tv_series_select['time_utc']==local_datum.isoformat().replace('T',' ')].shape[0]==0:
                     print('WARNING: no profile for {0} and date {1} using default coeficient = 1'.format(category,local_datum)) 
                     coef=1
                     
                  else:  
                    
                     coef=float(tv_series_select[tv_series_select['time_utc']==local_datum.isoformat().replace('T',' ')]['tv_factor'])
                  
                  dic_time_matrix[category].append(coef)
                  
                  local_datum += datetime.timedelta(hours=1)
                  
                 
                  
            dic_time_matrix[category]=np.array(dic_time_matrix[category])               



    print('time arrays are prepared in {0:.1f} sec'.format(time.time() - start_time))
    return dic_time_matrix; 
