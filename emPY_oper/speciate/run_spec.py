#!/usr/bin/env python3

"""

SPECIATION SCRIPT

Function:    
speciate all files from output_to_domain directory 
according speciation file, based on gspro file

Libraries and modules needed:
libraries: pandas, numpy, time, os, sys, importlib
modules: group_point_sources

Revision History:
    
29.01.2019 D. Stefanik: creating first version of script


"""
#####
#set path to case 
case_path='../case_run'


# imported libraries
import numpy as np
import pandas as pd
import os
import time
import sys
import importlib
import src_speciate.group_point_sources as gps
sys.path.append(case_path)
import emPY_config_file
importlib.reload(emPY_config_file)

##############################################################################
# read parameters from emPY_emPY_config_file.py
##############################################################################

grid_params=emPY_config_file.grid_params

projection=emPY_config_file.projection
#set input directory
input_dir=emPY_config_file.speciate_input_dir
# set the output directory
output_dir=emPY_config_file.speciate_output_dir

# set the  spec file
spec=pd.read_csv(emPY_config_file.spec_file,comment='#')


#emission category file
em_cat_file=pd.read_csv(emPY_config_file.em_cat_file)


if 'list_inv_area_spec' in emPY_config_file.__dir__():
    list_inv=emPY_config_file.list_inv_area_spec
else: 
    list_inv=os.listdir(input_dir)
    if os.path.isdir(input_dir+'/point_sources'):
       list_inv.remove('point_sources')

if 'list_inv_point_spec' in emPY_config_file.__dir__():
    list_point=emPY_config_file.list_inv_point_spec
else:
    if os.path.isdir(input_dir+'/point_sources'):
       list_point=os.listdir(input_dir+'/point_sources')
    else: list_point=False
###########################################################################################################
start_time = time.time()


if os.path.exists(output_dir):
   
   print('deleting files in the {0} '.format(output_dir))
   
   os.system('rm -f {0}/*.npy'.format(output_dir))


#creating output directory
if not os.path.exists(output_dir):
   os.makedirs(output_dir)

###############################################################################
#Point sources
################################################################################
if list_point:
    print('#################################')
    print('processing point sources')
    print('#################################')
    
    point_emissions=gps.stack_params_to_netCDF4(gps.group_point_sources(input_dir+'/point_sources',list_point),output_dir,grid_params,projection)
    
    #spec_names in gspro files
    spec_names=spec['spec_name'].unique()
    
    # create new columns in point_emission files
    for sp in spec_names:
        if sp not in point_emissions.columns:
            point_emissions[sp]=0 
    
    
    # for cycle for all categiories in GSPROFILES
    for cat in spec['cat'].unique():
        print(cat)
        
        # dictionary {'new_species_1': 'old_name', 'new_species_2': 'old_name' }
        dic_speciate=dict(zip(spec[spec.cat==cat]['spec_name'], spec[spec.cat==cat]['old_name']))
        # dictionary {'new_species_1': 'koef_1', 'new_species_2': 'koef_2' }
        dic_koef=dict(zip(spec[spec.cat==cat]['spec_name'], spec[spec.cat==cat]['coef1']/spec[spec.cat==cat]['coef2']))
        
        # case cat 0 which just convert names and coef
        if cat == 0:
        
            for sp in dic_speciate:
                if dic_speciate[sp] in point_emissions.columns:   
                    print('Speciate {0} on category {1} with coeficient {2}*{3}'.format(sp,cat,dic_koef[sp],dic_speciate[sp]))
                    
                    point_emissions[sp]=point_emissions[dic_speciate[sp]]*dic_koef[sp]      
        
        else:
            # list of all profiles (cat_internal) in em_cat_file which speciate according cat    
            profiles_speciate_as_cat=list(em_cat_file[em_cat_file.speciation_profile ==cat]['cat_internal'].unique())
            
            for sp in dic_speciate:
                    if dic_speciate[sp] in point_emissions.columns:
                        print('Speciate {0} on categories {1} as {2} with coeficient {3}*{4}'.format(sp,profiles_speciate_as_cat,cat,dic_koef[sp],dic_speciate[sp]))
                        
            
                        point_emissions[sp]=point_emissions.apply(lambda x: x[dic_speciate[sp]]*dic_koef[sp] 
                                        if x['cat_internal'] in profiles_speciate_as_cat and
                                        x[dic_speciate[sp]]==x[dic_speciate[sp]] else x[sp], axis=1)
                        
            
            # mask=point_emissions['cat_internal'].isin(profiles_speciate_as_cat)
        
            # if mask.any():
                
            #     # choose that part of the point_emision file which will be speciate                
            #     apply=point_emissions[mask]
            #     # choose that part of the point_emision file which will not be speciate
            #     not_apply=point_emissions[~mask]
            
            #     for sp in dic_speciate:
            #         if dic_speciate[sp] in point_emissions.columns:
            #             print('Speciate {0} on categories {1} as {2} with coeficient {3}*{4}'.format(sp,profiles_speciate_as_cat,cat,dic_koef[sp],dic_speciate[sp]))
                        
            #             apply[sp]=apply[dic_speciate[sp]]*dic_koef[sp]             
    
            #     # merge apply and not_apply    
            #     point_emissions=pd.concat([apply,not_apply],sort=False).sort_index()
    
    # point emissions to csv
    point_emissions=point_emissions[['cat_internal']+list(spec_names)]           
    point_emissions=point_emissions.replace(np.nan,0)
    point_emissions.to_csv(output_dir+'/point_sources/'+'speciate_points', index=False)    
    ##############################################################################################################################  
else:
    print('#################################')
    print('no point sources detected')
    print('#################################')
#########################################################################################################
# area sources
#########################################################################################################
if len(list_inv)>0:

    print('#################################')
    print('processing area sources')
    print('#################################')
    #define which pollutants will mapping to themselves
    spec_from_all_categories=list(spec[spec.cat==0]['old_name'].unique())
    
    # create mapper {cat_internal-old_poll_name': {cat_internal-old_poll_name: koef} }
    mapper={}
    for name in list_inv:
        for file in os.listdir(f'{input_dir}/{name}'):
               
            cat_poll_old=file.split( "-" )
            s=f'{cat_poll_old[0]}-{cat_poll_old[1]}'
            cat=em_cat_file[em_cat_file['cat_internal']== int(cat_poll_old[0])] 
        
            if cat_poll_old[1] not in spec_from_all_categories:          
                
                if cat.shape[0]==0: 
                   print(f'{s} is not taking to the speciate inputs, category {cat_poll_old[0]} is not defined in em_cat_file')
                elif cat.shape[0] > 1 :
                   print(f'!!!!Error and warning cat id {cat_poll_old[0]} is more than one time in em_cat_file') 
                   sys.exit()
                elif cat.shape[0]==1:
                   cat=int(cat['speciation_profile']) 
                                                
                   select_spec=spec[(spec.cat==cat) & (spec.old_name==cat_poll_old[1])]
                   
                   if select_spec.shape[0]==0:
                      
                      print(f'{s} is not taking in the speciate inputs') 
                      
                   else: 
                       mapper[s]={} 
                       mapper[s]=dict(zip(select_spec['spec_name'].apply(lambda x: cat_poll_old[0]+'-'+x), select_spec['coef1']/select_spec['coef2']))
            else:  
                   mapper[s]={} 
                   mapper[s]=dict(zip(spec[spec.old_name==cat_poll_old[1]]['spec_name'].apply(lambda x: cat_poll_old[0]+'-'+x), spec[spec.old_name==cat_poll_old[1]]['coef1']/spec[spec.old_name==cat_poll_old[1]]['coef2']))
    
    
    # making set of unique defined cat_internal-pollutant_new_name strings
    cat_pol_new_unique=set([item for sublist in list(map(lambda x: list(mapper[x].keys()), mapper)) for item in sublist])
    
    #making empty arrays with size ni, nj in dictionary with keys unique_cat_em
    dic_pol={}
    for _ in cat_pol_new_unique:
        dic_pol[_]=np.zeros([grid_params['ni'],grid_params['nj']])
    
    check_list=[]
    # making speciation#########################    
    for name in list_inv:
        for file in os.listdir(f'{input_dir}/{name}'):          
            s=f"{file.split( '-' )[0]}-{file.split( '-' )[1]}"
            if s in mapper:
                auxilary_array=np.load(f'{input_dir}/{name}/{file}')
                for i in mapper[s]:
                    
                    dic_pol[i]+= auxilary_array*mapper[s][i]
                    
                    #print(i.split('-')+'-' + '0' if len(mapper[s])==1 else '1'  + '-'+ file)
                    check_list.append(i.split('-')[1]+'|' + ('0' if len(mapper[s])==1 else '1')  + '|'+ file +'|'+str(mapper[s][i]) )
                    
    # save arrays        
    for _ in dic_pol: np.save(f'{output_dir}/{_}', dic_pol[_]) 

else:
    print('#################################')
    print('no area sources detected')
    print('#################################')

    
print('##################### Program run sucessfuly ########################################')
print("Data are speciated in %s seconds ---" % (time.time() - start_time))



############################Checking area emisions ###################################################################
if len(list_inv)>0:

    for poll in spec['spec_name'].unique():
        
        print('###########################################################')
        print(poll)
        print('###')
        print('mapping themselves:')      
        for keys in check_list:
            if keys.startswith('{}|0'.format(poll)):
               print(keys.split('|')[2]+f"' with koef {float(keys.split('|')[3]):.3f}")
        print('###')       
        print('speciating from files:')
        for keys in check_list:
            if keys.startswith('{}|1'.format(poll)):
               print(keys.split('|')[2]+f"' with koef {float(keys.split('|')[3]):.10f}")          
     
    
    
    print("Speciation is checked in %s seconds ---" % (time.time() - start_time))       
    





