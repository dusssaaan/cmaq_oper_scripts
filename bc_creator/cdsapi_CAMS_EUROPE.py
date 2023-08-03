#!/usr/bin/env /users/p6065/anaconda3/envs/cdsapi/bin/python
"""
Function:
cdsapi script for downloading the CAMS EUROPE data

Usage: ./cdsapi_CAMS_EUROPE.py f_range [00+23 or 24+47] f_levels [full or selected]

Libraries and modules needed:

libraries: datetime, cdsapi, sys
modules:

Revision History:

06.07.2023 D.Stefanik: creating first version of script
"""
import datetime
import cdsapi
import sys

datum = datetime.datetime.now()

f_range  =  str( sys.argv[1] )#'00+23' or '24+47'
f_levels =  str( sys.argv[2] )# full or selected
       
ds=f'{datum}'[:10]
print(f'{ds}')


log_path='/work/users/oko001/cmaq_oper_logs/bc_creator_logs'

datum = datetime.date.today() - datetime.timedelta(days=1)
YYYYMMDD = f"{datum}".replace('-','') #date in format YYYYMMDD

sys.stdout = open(f'{log_path}/LOG_{ds}_{f_range}_{f_levels}.txt','w')

print(f'{ds} CMAMS EUROPE forecast downloaded from 0:00 UTC and range  {f_range} for {f_levels} set of levels.')

# two range of the forecasts
if f_range == '00+23':
   hours = ['0', '1', '2',
            '3', '4', '5',
            '6', '7', '6',
            '7', '8', '9',
            '10', '11','12',
            '13', '14', '15',
            '16', '17', '18',
            '19', '20', '21',
            '22', '23',]
elif f_range == '24+47':
    hours = ['24', '25', '26', 
             '27', '28', '29', 
             '30', '31', '32', 
             '33', '34', '35', 
             '36', '37', '38', 
             '39', '40', '41', 
             '42', '43', '44', 
             '45', '46', '47',]

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
        'area': [52.12, 10.60, 44.83, 25.25,],
    },
    f'/data/users/oko001/cmaq_oper_data/bcon_files/download_{ds}_CAMS_EUROPE_{f_range}_{f_levels}.nc')
