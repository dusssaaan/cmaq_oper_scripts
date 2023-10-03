#!/usr/bin/env /users/p6065/anaconda3/envs/supergeo/bin/python

# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 08:40:47 2022

CREATED CMAQ CONC file by horizontal, vertical and time interpolation 
of CAMS EUROPE and IFS CAMS global model
@author: Dusan Stefanik
"""

import netCDF4
import xarray as xr
import pandas as pd
import rioxarray
import datetime
import numpy as np
import os
import sys
import pygrib

datum    =  datetime.datetime.strptime( str( sys.argv[1] ) ,'%Y-%m-%d') #datetime.datetime.strptime( '2023-08-29' ,'%Y-%m-%d')
forecast =  str(sys.argv[2])  #'00' pre behy '12' to treba este prerobit
start    =  int(sys.argv[3])  # 0  or 24
end      = start + 24



cams_data_path  = '/data/users/oko001/cmaq_oper_data/cams_files'

datumiso = datum.isoformat()[:10]     
ystrd = datum - datetime.timedelta(days=1)
ystrdiso = ystrd.isoformat()[:10]   
real_date = datum + datetime.timedelta(hours= ( int(forecast) + start) )   

output_dir = '/data/users/oko001/cmaq_oper_data/bcon_files'
out_file_name = f'CONC_CAMS_POST_33_{datumiso}_{forecast}_{start}_{end}'

#%%
# domain config

projection={'proj': 'lcc',
 'lat_1': 48.8018264770508,
 'lat_2': 48.8018264770508,
 'lat_0': 48.8018264770508,
 'lon_0': 18.1115646362305,
 'x_0': 0,
 'y_0': 0,
 'a': 6370000.0,
 'b': 6370000.0,
 'units': 'm',
 'no_defs': True}

grid_params={'XCELL': 2000,
 'XORIG': -495000,
 'YORIG': -367000,
 'ni': 367,
 'nj': 495 }

def domain_2D():
    x = np.array([grid_params['XORIG'] + (i+1/2) *grid_params['XCELL'] for i in range(grid_params['nj'])])
    y = np.array([grid_params['YORIG'] + (i+1/2) *grid_params['XCELL'] for i in range(grid_params['ni'])])

    domena=xr.Dataset()
    domena.coords['x']=(('x'), x)
    domena.coords['y']=(('y'), y)
    domena=domena.rio.set_spatial_dims("x","y",inplace=True)
    domena=domena.rio.write_crs(projection)

    return domena


#%%
#
#levely
#
#priemerne vysky v modeli CAMS
clev={ 1:  80301.65 ,  2:  74584.91 ,  3:  71918.79 ,   4:  69365.77 ,  5:  66906.53 , 
       6:  64537.43 ,  7:  62254.39 ,  8:  60053.46 ,   9:  57930.78 , 10:  55882.68 , 
      11:  53905.62 , 12:  51996.21 , 13:  50159.36 ,  14:  48413.94 , 15:  46756.98 , 
      16:  45199.69 , 17:  43738.55 , 18:  42364.93 ,  19:  41071.20 , 20:  39850.56 ,
      21:  38696.94 , 22:  37604.95 , 23:  36569.72 ,  24:  35586.89 , 25:  34652.52 , 
      26:  33763.05 , 27:  32915.27 , 28:  32106.57 ,  29:  31330.96 , 30:  30584.71 , 
      31:  29866.09 , 32:  29173.50 , 33:  28505.47 ,  34:  27860.64 , 35:  27237.73 ,  
      36:  26635.56 , 37:  26053.04 , 38:  25489.15 ,  39:  24942.93 , 40:  24413.50 ,  
      41:  23900.02 , 42:  23401.71 , 43:  22917.85 ,  44:  22447.75 , 45:  21990.82 , 
      46:  21546.62 , 47:  21114.77 , 48:  20694.90 ,  49:  20286.66 , 50:  19889.88 , 
      51:  19503.09 , 52:  19125.61 , 53:  18756.34 ,  54:  18394.25 , 55:  18038.35 , 
      56:  17687.77 , 57:  17341.62 , 58:  16999.08 ,  59:  16659.55 , 60:  16322.83 , 
      61:  15988.88 , 62:  15657.70 , 63:  15329.24 ,  64:  15003.50 , 65:  14680.44 , 
      66:  14360.05 , 67:  14042.30 , 68:  13727.18 ,  69:  13414.65 , 70:  13104.70 , 
      71:  12797.30 , 72:  12492.44 , 73:  12190.10 ,  74:  11890.24 , 75:  11592.86 , 
      76:  11297.93 , 77:  11005.69 , 78:  10714.22 ,  79:  10422.64 , 80:  10130.98 , 
      81:  9839.26 ,  82:  9547.49 ,  83:  9255.70 ,   84:  8963.90 ,  85:  8672.11 , 
      86:  8380.36 ,  87:  8088.67 ,  88:  7797.04 ,   89:  7505.51 ,  90:  7214.09 , 
      91:  6922.80 ,  92:  6631.66 ,  93:  6340.68 ,   94:  6049.89 ,  95:  5759.30 , 
      96:  5469.30 ,  97:  5180.98 ,  98:  4896.02 ,   99:  4615.92 , 100:  4341.73 , 
      101:  4074.41 ,102:  3814.82 , 103:  3563.69 ,  104:  3321.67 , 105:  3089.25 ,
      106:  2866.83 ,107:  2654.69 , 108:  2452.99 ,  109:  2261.80 , 110:  2081.09 ,
      111:  1910.76 ,112:  1750.63 , 113:  1600.44 ,  114:  1459.91 , 115:  1328.70 ,
      116:  1206.44 ,117:  1092.73 , 118:  987.15 ,   119:  889.29 ,  120:  798.72 , 
      121:  715.02 , 122:  637.76 ,  123:  566.54 ,   124:  500.95 ,  125:  440.61 , 
      126:  385.16 , 127:  334.24 ,  128:  287.52 ,   129:  244.69 ,  130:  205.44 , 
      131:  169.51 , 132:  136.62 ,  133:  106.54 ,   134:  79.04 ,   135:  53.92 , 
      136:  30.96 ,  137:  10.00 }

## 33 hladin v modeli CMAQ
cmaq_v = [1.03431873e+01, 3.22395515e+01, 5.73812675e+01, 8.64999161e+01,
       1.19390694e+02, 1.76945770e+02, 2.64464478e+02, 3.96199158e+02,
       5.81286255e+02, 7.99420227e+02, 1.10077393e+03, 1.44336487e+03,
       1.76797412e+03, 2.10723364e+03, 2.46420605e+03, 2.84373950e+03,
       3.24950146e+03, 3.76479028e+03, 4.32325635e+03, 4.95827100e+03,
       5.92912256e+03, 6.96558496e+03, 7.96538086e+03, 8.92610059e+03,
       9.76969141e+03, 1.06733916e+04, 1.16603721e+04, 1.27667295e+04,
       1.36801143e+04, 1.43545225e+04, 1.54878545e+04, 1.67187676e+04,
       1.76611270e+04]

#%%

def transform_eu( file_name, dic_prekl, metcro3d, datum ):
    
    tdim = 25
    cams_data = xr.open_dataset(cams_data_path + '/' + file_name)
    cams_data = cams_data.rio.set_spatial_dims("longitude","latitude",inplace=True)
    cams_data = cams_data.rio.write_crs('epsg:4326')
    levels    = list( cams_data.level.data ) + [6000] +[40000]
    times  = pd.date_range(start=datum, periods=tdim, freq='1H')
    domena=domain_2D()
    domena.coords["level"]=(('level'), levels )
    domena.coords["time"]=(('time'),times)    
    
    dic_var={}
    for var in dic_prekl:
        dic_var[dic_prekl[var][0]]=np.zeros((tdim,len(levels),domena.y.shape[0],domena.x.shape[0]))

    # horizontal reprojection
    for time in range(0,tdim):
        cams_s=cams_data.isel({'time':time})
        cams_s=cams_s.rio.reproject(dst_crs=domena.rio.crs)
        cams_s=cams_s.rio.reproject_match(domena)

        for var in dic_prekl:
            dic_var[dic_prekl[var][0]][time,:-2,:,:]= cams_s[var][:,:,:]

    for var in dic_prekl:
       
        domena[ dic_prekl[var][0] ] = (('time','level','y','x'),  dic_var[ dic_prekl[var][0] ])   
  
    dom_interp_vyska=domena.interp(level=cmaq_v)
    
    temp = metcro3d['TA'].data
    pres = metcro3d['PRES'].data
    for var in dic_prekl: 
        #8.314*T*ug/(p*M) page 16, SEINFELD AND PANDIS: ATMOSPHERIC CHEMISTRY AND PHYSICS
        pol = dic_prekl[var][0]
        mmas = dic_prekl[var][1]
        if mmas != 1:
            dom_interp_vyska[ pol ] = 8.314 * temp * dom_interp_vyska[ pol ] /(pres * mmas )
      
    return dom_interp_vyska

# just used for ozone
def transform_global( file_name, lead_hour,datum ):    
   
    levels_glob  =  [24, 45, 57, 62, 65, 67, 72, 77, 82, 87, 92, 97]
    
    index = {0:0, 12:4,24:8,36:12,48:16,60:20,72:24 }
    leadtime_hours = [0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39,
                      42, 45, 48, 51, 54, 57, 60, 63, 66, 69, 72, 75, 78, 
                      81, 84, 87, 90, 93, 96, 99][index[lead_hour]:index[lead_hour] + 9 ]

    grib = pygrib.open(cams_data_path + '/' + file_name )
    val, lats, lons = grib.message(1).data()
    gl_data = np.zeros( (len(leadtime_hours), len(levels_glob), lats.shape[0], lons.shape[1]) )
    # este raz nacitam aby mi prva sprava nezmizla
    grib = pygrib.open(cams_data_path + '/' + file_name )
    for mes in grib:
        if mes.forecastTime in leadtime_hours:
            gl_data[ leadtime_hours.index(mes.forecastTime), levels_glob.index(mes.level),: ] = mes.data()[0]
   
    cams_data=xr.Dataset()
    cams_data.coords['longitude'] = ( ('longitude'), lons[0,:] )
    cams_data.coords['latitude']  = ( ('latitude'),  lats[:,0] )
    levels = [clev[x] for x in levels_glob][::-1]
    cams_data.coords['level']  = ( ('level'), levels )
    #cams_data.coords['time']  = ( ('time'), leadtime_hours )
    cams_data = cams_data.rio.set_spatial_dims("longitude","latitude",inplace=True)
    cams_data = cams_data.rio.write_crs('epsg:4326')
    #nazvy https://confluence.ecmwf.int/display/CKB/CAMS%3A+Global+atmospheric+composition+forecast+data+documentation
    #https://atmosphere.copernicus.eu/sites/default/files/2020-07/CAMS84_2018SC1_D4.1.1-JJA2019_v1.pdf

    cams_data['O3'] = (('time','level','latitude','longitude'), gl_data[:,::-1,:,:] * 28.9644 / 48 *1e6 )   

    times  = pd.date_range(start=datum, periods=len(leadtime_hours), freq='3H')
    domena=domain_2D()
    domena.coords["level"]=(('level'), levels )
    domena.coords["time"]=(('time'),times)

    dic_var={}

    dic_var['O3']=np.zeros((times.shape[0],len(levels),domena.y.shape[0],domena.x.shape[0]))

    # horizontal reprojection
    for time in range(0,times.shape[0]):
        cams_s=cams_data.isel({'time':time})
        cams_s=cams_s.rio.reproject(dst_crs=domena.rio.crs)
        cams_s=cams_s.rio.reproject_match(domena)

        dic_var['O3'][time,:,:,:]= cams_s['O3'][:,:,:]

    domena[ 'O3' ] = (('time','level','y','x'), dic_var['O3'])
    dom_interp_vyska=domena.interp(level=cmaq_v)
    
    
    time_25  = pd.date_range(start=datum, periods=25, freq='1H')
    dom_interp_time=dom_interp_vyska.interp(time=time_25) 
    
    return dom_interp_time

#%%%


dic_prekl_sel = {
   'no_conc' : ('NO' , 30.01  ),
   'no2_conc': ('NO2', 46.0055  ),
   'nh3_conc': ('NH3', 17  ),
   'so2_conc': ('SO2', 64  )}

dic_prekl_full = {
   'co_conc' :  ('CO',  28.0101  ),
   'o3_conc':   ('O3',  48 ),
   'pm10_conc': ('PM10', 1 ),
   'pm2p5_conc': ('PM25', 1 )}


    

if   forecast == '00': ss, ee = start+24, end+24
elif forecast == '12': ss, ee = start+12, end+12

lead_hour = ss    

file_name_sel = f'download_{ystrdiso}_CAMS_EUROPE_{ss}+{ee}_selected.nc'
file_name_full = f'download_{ystrdiso}_CAMS_EUROPE_{ss}+{ee}_full.nc'
metcro3d_file_path=f'/data/users/oko001/cmaq_oper_data/mcip_files/METCRO3D_PYCIP-{datumiso}_{forecast}_for_{start}+{end}.nc'
metcro3d = xr.open_dataset(metcro3d_file_path)

file_name_glob = f'/download_{ystrdiso}_CAMS_GLOBAL_0+96_ozone.grib'


print('Process CAMS EU data')
eu_sel = transform_eu( file_name_sel, dic_prekl_sel,metcro3d, real_date )
eu_full = transform_eu( file_name_full, dic_prekl_full,metcro3d, real_date )
print('Process CAMS GLOBAL data')
glob_o3 = transform_global( file_name_glob, lead_hour, real_date )


eu_sel['O3']     = eu_full['O3']
eu_sel['O3'][:,20:,:,:]     = glob_o3['O3'][:,20:,:,:]
eu_sel['CO']     = eu_full['CO']
eu_sel['ACORS']  = eu_full['PM10']-eu_full['PM25']
eu_sel['AOTHRI'] = eu_full['PM25'] * 0.1
eu_sel['AOTHRJ'] = eu_full['PM25'] * 0.9
#%%
def gridded_to_netCDF(output_dir,out_file_name,xr_dataset,datum,projection,grid_params,metcro3d):

    global_params={ 'CDATE':np.int32('{0}{1:03d}'.format(datetime.datetime.today().year,datetime.datetime.today().timetuple().tm_yday)),
                    'P_ALP':projection['lat_1'],
                    'P_BET':projection['lat_2'],
                    'P_GAM':projection['lon_0'],
                    'XCENT':projection['lon_0'],
                    'YCENT':projection['lat_0'],
                    'CTIME':np.int32(63057),
                    'DATE_TIME':np.int32(2),
                    'EXEC_ID':"???????????????? ",
                    'FILEDESC':"gridded emissions",
                    'FTYPE':np.int32(1),
                    'GDTYP':np.int32(2),
                    'HISTORY':"",
                    'IOAPI_VERSION':"Id",
                    'NC_STEP':np.int32(1),
                    'NLAYS':np.int32(metcro3d.attrs['NLAYS']),
                    'NTHIK':np.int32(1),
                    'NVARS':np.int32(len(xr_dataset.keys())),
                    'SDATE': np.int32( f'{datum.year}{datum.timetuple().tm_yday:03d}' ),
                    'STIME':np.int32( datum.hour *10000 ),
                    'TSTEP':np.int32(10000),
                    'UPNAM':"OPENEOUT        ",
                    'VAR-LIST':"".join('{0:16s}'.format(f) for f in xr_dataset.keys()),
                    'VGLVLS':np.array(metcro3d.attrs['VGLVLS']),
                    'VGTOP':np.float32(0.00000),
                    'VGTYP':-np.int32(7),
                    'WDATE':np.int32('{0}{1:03d}'.format(datetime.datetime.today().year,datetime.datetime.today().timetuple().tm_yday)),
                    'WTIME':np.int32(63057),
                    'NCOLS':np.int32(grid_params['nj']),
                    'NROWS':np.int32(grid_params['ni']),
                    'XORIG':grid_params['XORIG']+0.0,
                    'YORIG':grid_params['YORIG']+0.0,
                    'XCELL':grid_params['XCELL']+0.0,
                    'YCELL':grid_params['XCELL']+0.0,
                    'GDNAM':"ala2km"}

    with netCDF4.Dataset('{0}/{1}.nc'.format(output_dir,out_file_name),mode='w') as out:

         # create globals
         for global_par in global_params:

            out.setncattr(global_par, global_params[global_par])

         # create dimensions

         out.createDimension('TSTEP', None)
         out.createDimension('DATE-TIME', size=global_params['DATE_TIME'])
         out.createDimension('LAY', size=global_params['NLAYS'])
         out.createDimension('VAR', size=global_params['NVARS'])
         out.createDimension('COL', size=global_params['NCOLS'])
         out.createDimension('ROW', size=global_params['NROWS'])

         # create TFLAGS
         out.createVariable('TFLAG', np.int32, ('TSTEP', 'VAR', 'DATE-TIME'),fill_value=None)
         out.variables['TFLAG'].setncatts({'units': "<YYYYDDD,HHMMSS>", 'long_name': "TFLAG", 'var_desc': "Timestep-valid flags:  (1) YYYYDDD or (2) HHMMSS"})

         out.variables['TFLAG'][:,:,:]= metcro3d['TFLAG'].data[:,:global_params['NVARS'],:]
         
         # create variables
         for name in xr_dataset:

             out.createVariable(name, np.float32, ('TSTEP', 'LAY', 'ROW', 'COL'),fill_value=None)

             if name.startswith('A'): units = "ug m-3          "
             else: units = "ppmV            "

             out.variables[name].setncatts({'units': units, 'long_name': "".join(f'{name:16s}'), 'var_desc': "".join(f' Average Concentrations of {name:53s}')})


             out.variables[name][:,:,:,:]=xr_dataset[name].data




print('Saving data')
gridded_to_netCDF(output_dir,out_file_name,eu_sel,real_date,projection,grid_params,metcro3d)
print('Program finished succesfully')


































