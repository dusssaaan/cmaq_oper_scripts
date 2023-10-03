#!/usr/bin/env /users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  4 14:31:58 2023

@author: oko001
"""

import os
import datetime
import time
import subprocess
import sys

datum =  datetime.datetime.strptime( str( sys.argv[1] ),'%Y-%m-%d')
files_download  = 0
num_req_files   = 9


path     = '/data/users/oko001/cmaq_oper_data/cams_files'
exe_EU   = '/users/oko001/cmaq_oper_scripts/bc_creator/cdsapi_CAMS_EUROPE.py'
exe_GLOB = '/users/oko001/cmaq_oper_scripts/bc_creator/cdsapi_CAMS_GLOBAL.py'
ds       = f'{datum}'[:10]

starttime=time.time()
timeout = starttime + 4*3600
print(f'starting downloading data for CAMS data for {ds} ')
while files_download < num_req_files:

    
      # download CAMS GLOBAL  
      if not os.path.isfile(path + f'/download_{ds}_CAMS_GLOBAL_0+96_ozone.grib') :
    
         try: 
           
           print( 'try to download data for CAMS GLOBAL' )
           
           subprocess.run( f'{exe_GLOB}  {ds}', shell=True )
           
           if os.path.isfile(path + f'/download_{ds}_CAMS_GLOBAL_0+96_ozone.grib') :
              files_download += 1 
           else: 
               datum_non = f'{datetime.datetime.now()}'[:16] 
               print(f"CAMS GLOBAL data  not available in {datum_non} ") 
            
         except:
           datum_non = f'{datetime.datetime.now()}'[:16] 
           print(f"CAMS GLOBAL data  not available in {datum_non} ")  
    
      # download CAMS EUROPE
      for tp in [ '00+24', '24+48', '48+72', '72+96' ]:
          for par in ['full','selected']:
              if not os.path.isfile(path + f'/download_{ds}_CAMS_EUROPE_{tp}_{par}.nc') :
              
                try: 
                     
                     print(f'try to download data for {tp} and {par} ')
                     
                     subprocess.run(f'{exe_EU}  {ds} {tp} {par} ' ,shell=True)
                     
                     if os.path.isfile(path + f'/download_{ds}_CAMS_EUROPE_{tp}_{par}.nc') :
                        files_download += 1 
                     else: 
                         datum_non = f'{datetime.datetime.now()}'[:16] 
                         print(f"CAMS EUROPE data for {tp}_{par} not available in {datum_non} ")                     
                 
                except:
                    
                     datum_non = f'{datetime.datetime.now()}'[:16] 
                     print(f"CAMS EUROPE data for {tp}_{par} not available in {datum_non} ") 
      

        
      print(f'koniec prehladavania, pocet stiahnutych suborov {files_download}, cas: {(time.time() - starttime)/60:.1f} min ')
      
      time.sleep(600)
      if time.time() > timeout:
          print('end due to time limit')
          break

print(f'koniec skriptu {files_download}, cas: {(time.time() - starttime)/60:.1f} min ')


