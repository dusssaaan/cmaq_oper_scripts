#!/usr/bin/env /users/p6065/anaconda3/envs/cdsapi/bin/python
"""
Function:
cdsapi script for downloading the CAMS GLOBAL data
for the ozone just above 5000 m since below is ozone 
from the CAMS EUROPE

Usage: ./cdsapi_CAMS_GLOBAL.py YYYY-MM-DD

Libraries and modules needed:

libraries: datetime, cdsapi, sys
modules:

Revision History:

04.08.2023 D.Stefanik: creating first version of script
"""
import datetime
import cdsapi
import sys


datum = datetime.datetime.strptime( str( sys.argv[1] ),'%Y-%m-%d')


ds = f'{datum}'[:10]


c = cdsapi.Client()


c.retrieve(
    'cams-global-atmospheric-composition-forecasts',
    {
        'date': f'{ds}/{ds}',
        'type': 'forecast',
        'format': 'grib',
        'variable': 'ozone',
        'model_level': [
            '24', '45', '57',
            '62', '65', '67',
            '72', '77', '82',
            '87', '92', '97',
        ],
        'time': '00:00',
        'leadtime_hour': [
            '0', '12', '15',
            '18', '21', '24',
            '27', '3', '30',
            '33', '36', '39',
            '42', '45', '48',
            '51', '54', '57',
            '6', '60', '63',
            '66', '69', '72',
            '75', '78', '81',
            '84', '87', '9',
            '90', '93', '96',
            '99',
        ],
        'area': [52.3, 10.60, 44.83, 25.5,],
    },     
    f'/data/users/oko001/cmaq_oper_data/cams_files/download_{ds}_CAMS_GLOBAL_0+96_ozone.grib')




