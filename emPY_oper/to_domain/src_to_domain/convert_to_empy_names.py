"""
Function:    

This script contains two functions    
csv_to_processor_names     
apply_stack_parameters

Libraries and modules needed:
libraries: numpy    

Revision History:

16.09.2019 D. Stefanik: creating first version of script      
"""
import numpy as np
import sys

def csv_to_processor_names(emis_file, dic_inv):
    """
    input:  emis_file: dataframe of emission inventory, 
            dic_inv: item of dictionary from inventory input
    output: emis_file with proper names of pollutants, other parameters and 
            units in tons per year        
    """
      
    if 'filter' in dic_inv.keys():
        for filters in dic_inv['filter']:
        
            emis_file=emis_file.query(filters)
        
            print('filter {} was applied'.format(filters))
    
    
    # rename pollutant names according the def_emiss names         
    emis_file=emis_file.rename(columns=dic_inv['def_emis'])
    
    if 'new_pollutants' in dic_inv.keys():
        for equation in dic_inv['new_pollutants'].split(','):

            emis_file=emis_file.eval(equation)

            print('Equation {} was applied'.format(equation))



    # rename other columns in emis file
    convert_col=['x', 'y', 'ID','height', 'diameter', 'temperature', 'velocity', 
                     'cat_internal','source_id']
    emis_file=emis_file.rename(columns={dic_inv[i]:i for i in list(set(convert_col) & set(dic_inv.keys())) })
   
    # identify cat_internal numbers in dataframe 
    if 'emission_inventory' not in dic_inv.keys():
        emis_file['cat_internal']=dic_inv['one_cat']  
    else:
        emis_file=emis_file.replace({'cat_internal':dic_inv['emission_inventory']})
        emis_file['cat_internal']=emis_file['cat_internal'].apply(int)
    
    # apply on pollutants unit conversion
    pollutants=list(dic_inv['def_emis'].values())    
    print('')
        
    if dic_inv['units']=='kg/year':
       emis_file[pollutants]=emis_file[pollutants]/1000.0
       print('{} is in kg/year and its transformed to t/year'.format(pollutants))
    elif dic_inv['units']=='g/year':
       emis_file[pollutants]=emis_file[pollutants]/1000000.0
       print('{} is in g/year and its transformed to t/year'.format(pollutants))
    elif dic_inv['units']=='mg/year':
       emis_file[pollutants]=emis_file[pollutants]/1000000000.0
       print('{} is in mg/year and its transformed to t/year'.format(pollutants))
    elif dic_inv['units']=='kilot/year':
       emis_file[pollutants]=1000*emis_file[pollutants]
       print('{} is in kilot/year and its transformed to t/year'.format(pollutants))
    elif dic_inv['units']=='tonne/year':
       print('{} is in t/year'.format(pollutants))
    else:
       print('Error, unknown unit format {0} is in {1} '.format(pollutants,dic_inv['units']))
       sys.exit()
    print('')      
    
             
    emis_file=emis_file.replace(np.nan,0)  
    return emis_file;
 
    
def apply_stack_parameters(emis_file,parameters):
    """
    inputs emis_file, 
           parameters - defined in config file 
    outputs emis_file - with custom parameters defined in config file
    
    """
    emis_file['height']=0
    emis_file['temperature']=0
    emis_file['velocity']=0
    emis_file['diameter']=0
  
    for index, row in emis_file.iterrows():        
                
        cat=row['cat_internal']
                      
        param=parameters[cat]
        poll=param[0]
        
        keys=np.sort(list(param[1].keys()))
       
        for key in keys:
            if row[poll] >= key:
               height=param[1][key]['height'] 
               temperature=param[1][key]['temperature']-273.15 
               velocity=param[1][key]['velocity']
               diameter=param[1][key]['diameter'] 
         
               
        emis_file.loc[index,'height']=height 
        emis_file.loc[index,'temperature']=temperature
        emis_file.loc[index,'velocity']=velocity
        emis_file.loc[index,'diameter']=diameter     
              
           
   
    return emis_file;


 





