#!/usr/bin/env /users/p6065/anaconda3/envs/cdsapi/bin/python
"""
Function:
cdsapi script for downloading the CAMS EUROPE data

Usage:
./cdsapi_CAMS_EUROPE.py YYYY-MM-DD f_range ['00+24', '24+48', '48+72', '72+96'] f_levels [full, selected]

Libraries and modules needed:

libraries: datetime, cdsapi, sys
modules:   none

Revision History:

06.07.2023 D.Stefanik: creating first version of script
"""
import datetime
import cdsapi
import sys


datum    = datetime.datetime.strptime( str( sys.argv[1] ),'%Y-%m-%d')
f_range  =  str( sys.argv[2] )#'00+24' or '24+48'
f_levels =  str( sys.argv[3] )# full or selected
       
ds = f'{datum}'[:10]



#log_path='/work/users/oko001/cmaq_oper_logs/bc_creator_logs'
#sys.stdout = open(f'{log_path}/LOG_{ds}_{f_range}_{f_levels}.txt','w')
#print(f'{ds} CMAMS EUROPE forecast downloaded from 0:00 UTC and range  {f_range} for {f_levels} set of levels.')

# two range of the forecasts
if f_range == '00+24':
     hours = [ f'{x}' for x in range(0,25) ] 
elif f_range == '24+48':
     hours = [ f'{x}' for x in range(24,49) ]
elif f_range == '48+72':
     hours = [ f'{x}' for x in range(48,73) ]
elif f_range == '72+96':
     hours = [ f'{x}' for x in range(72,96) ]


# for PM,O3 and CO full available levels are downloaded, while for NH3, NOx and SO2 just 6 levels
if f_levels == 'full':

   variables = ['carbon_monoxide', 'ozone','particulate_matter_10um', 'particulate_matter_2.5um',]
   
   levels = ['0','50', '100', '250', '500', '750', '1000', '2000', '3000', '5000',]

elif f_levels == 'selected':

   variables = ['ammonia', 'nitrogen_dioxide', 'nitrogen_monoxide','sulphur_dioxide',]
   
   levels = ['0','50', '100', '250', '500', '1000',]

c = cdsapi.Client()

c.retrieve(
    'cams-europe-air-quality-forecasts',
    {
        'model': 'ensemble',
        'date': f'{ds}/{ds}',
        'format': 'netcdf',
        'type': 'forecast',
        'time': '00:00',
        'variable': variables,
        'level': levels,
        'leadtime_hour': hours,
        'area': [52.30, 10.60, 44.83, 25.5,],
    },
    f'/data/users/oko001/cmaq_oper_data/cams_files/download_{ds}_CAMS_EUROPE_{f_range}_{f_levels}.nc')
