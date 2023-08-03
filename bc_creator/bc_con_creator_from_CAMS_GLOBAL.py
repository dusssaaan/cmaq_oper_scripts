#!/usr/bin/env /users/p6065/anaconda3/envs/supergeo/bin/python

# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 08:40:47 2022


CREATED CMAQ CONC file by horizontal, vertical and time interpolation 
of IFS CAMS global model
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

date  =  sys.argv[1]
start =  datetime.datetime.strptime(date, '%Y-%m-%d')

cams_file_path=f'/data/users/oko001/CAMS_DATA/download_{date}_mod.grib'
metcro3d_file_path=f'/data/oko/dusan/mcip_kosymoko_2km_87/METCRO3D_PYCIP-{date}.nc' #    f'/data/users/oko001/mcip_out_2021/METCRO3D_{date}.nc'

output_dir = '/data/users/oko001/CAMS_DATA_POST/'
out_file_name = 'CONC_CAMS_POST_87'

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
# dictionary nazov_cams: {nazov_cmaq:konverzny faktor}
#faktory pre aerosoly si pomahame tu (este stale su v kg/kg)
# nazvy https://confluence.ecmwf.int/display/CKB/CAMS%3A+Global+atmospheric+composition+forecast+data+documentation
#https://atmosphere.copernicus.eu/sites/default/files/2020-07/CAMS84_2018SC1_D4.1.1-JJA2019_v1.pdf

dic_prekl={
 'aermr01':{'ACLI':1/4.3},
 'aermr02':{'ACLJ':0.5/4.3,'ACLK':0.5/4.3},  # vsetky seasalt som zobral ako ACL aby som ich vedel rozlisit
 'aermr03':{'ACLK':0},
 'aermr04':{'AOTHRI':1},
 'aermr05':{'AOTHRJ':1},
 'aermr06':{'ACORS':0.4},
 'aermr07':{'APOCI':0.07, 'APOCJ':0.63, 'ACORS':0.3}, # na zaklade cmaq sim a dokum
 'aermr08':{'APOCI':0.07, 'APOCJ':0.63, 'ACORS':0.3},
 'aermr09':{'AECI':0.1,'AECJ':0.9},  # na zaklade cmaq sim
 'aermr10':{'AECI':0.1,'AECJ':0.9},
 'aermr11':{'ASO4I':0.01,'ASO4J':0.69,'ASO4K':0.3},
 'aermr16':{'ANO3I':0.34,'ANO3J':0.66},
 'aermr17':{'ANO3K':1},
 'aermr18':{'ANH4I':0.3,'ANH4J':0.4,'ANH4K':0.3 }, # na zaklade cmaq sim a dokum
 'c2h6':{'ETHA': 28.9644 / 30.1 *1e6 },
 'c3h8':{'PRPA': 28.9644 / 44.1 *1e6 },
 'c5h8':{'ISOP': 28.9644 / 68.1 *1e6 },
 'ch4_c':{'ECH4': 28.9644 / 16 *1e6 },
 'co':{'CO':28.9644 / 28.0101 *1e6 },
 'go3':{'O3':28.9644 / 48 *1e6 },
 'h2o2':{'H2O2': 28.9644 / 34 *1e6 },
 'hcho':{'FORM': 28.9644 / 30 *1e6 },
 'hno3':{'HNO3': 28.9644 / 63 *1e6 },
 'no':{'NO': 28.9644 / 30 *1e6 },
 'no2':{'NO2': 28.9644 / 46 *1e6 },
 'oh':{'OH': 28.9644 / 17 *1e6 },
 'pan':{'PAN': 28.9644 / 121 *1e6 },
 'so2':{'SO2': 28.9644 / 64 *1e6 } }    

CMAQ_NAMES=[]
for x in dic_prekl: CMAQ_NAMES = CMAQ_NAMES + list(dic_prekl[x].keys()) 

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

# vysky v modely CMAQ prvy je takmer 10
#cmaq_v= [10, 3.5156799e+01, 7.4332169e+01, 1.3550476e+02,
#         2.3165237e+02, 3.8405069e+02, 6.2797552e+02, 1.0220774e+03,
#         1.6623434e+03, 2.6965090e+03, 4.3166060e+03, 6.3285967e+03,
#         8.3410596e+03, 1.0303563e+04, 1.2123985e+04, 1.3652878e+04,
#         1.4792681e+04, 1.5404158e+04, 1.5669349e+04]   


cmaq_v     =      [10, 2.9846039e+01, 5.3152699e+01,
                   8.0168564e+01, 1.1071051e+02, 1.4469603e+02,
                   1.8208015e+02, 2.2283795e+02, 2.6695789e+02,
                   3.1443903e+02, 3.6528854e+02, 4.1952051e+02,
                   4.7715829e+02, 5.3823096e+02, 6.0277057e+02,
                   6.7080890e+02, 7.4238293e+02, 8.1753510e+02,
                   8.9631610e+02, 9.7878326e+02, 1.0650005e+03,
                   1.1550389e+03, 1.2489771e+03, 1.3468984e+03,
                   1.4479572e+03, 1.5504783e+03, 1.6538442e+03,
                   1.7583861e+03, 1.8643947e+03, 1.9721118e+03,
                   2.0817515e+03, 2.1934971e+03, 2.3075032e+03,
                   2.4239102e+03, 2.5428418e+03, 2.6644124e+03,
                   2.7887275e+03, 2.9158906e+03, 3.0460132e+03,
                   3.1792131e+03, 3.3156365e+03, 3.4554470e+03,
                   3.5988396e+03, 3.7460471e+03, 3.8973506e+03,
                   4.0530669e+03, 4.2135840e+03, 4.3793623e+03,
                   4.5509150e+03, 4.7288672e+03, 4.9139360e+03,
                   5.1069404e+03, 5.3088159e+03, 5.5206421e+03,
                   5.7436548e+03, 5.9792710e+03, 6.2291011e+03,
                   6.4950151e+03, 6.7791494e+03, 7.0840234e+03,
                   7.4126055e+03, 7.7637217e+03, 8.1305801e+03,
                   8.5101064e+03, 8.9045713e+03, 9.3167725e+03,
                   9.7498848e+03, 1.0207265e+04, 1.0692325e+04,
                   1.1208158e+04, 1.1757299e+04, 1.2342350e+04,
                   1.2966703e+04, 1.3635037e+04, 1.4353714e+04,
                   1.5131276e+04, 1.5978774e+04, 1.6910443e+04,
                   1.7945283e+04, 1.9108662e+04, 2.0442076e+04,
                   2.2012527e+04, 2.3929221e+04, 2.6393545e+04,
                   2.9821576e+04, 3.5307445e+04][:]



#%%
cams = xr.open_dataset(cams_file_path, engine='cfgrib')
cams = cams.rio.set_spatial_dims("longitude","latitude",inplace=True)
cams = cams.rio.write_crs('epsg:4326')

#nacita levely z CAMSu
levels = sorted([clev[x] for x in  cams.hybrid.data])
# cas podla camsu
tdim   = cams.dims['step']
times  = pd.date_range(start=start, periods=tdim, freq='3H')

domena=domain_2D()
domena.coords["level"]=(('level'), levels )
domena.coords["time"]=(('time'), pd.date_range(start=start, periods=tdim, freq='3H'))

# nulove pomocne pole a pole v domene
dic_var={}
for var in dic_prekl:
    dic_var[var]=np.zeros((tdim,len(levels),domena.y.shape[0],domena.x.shape[0]))
for var in dic_prekl:
    for c_name in dic_prekl[var]:
        domena[c_name] = (('time','level','y','x'), dic_var[var])    

for time in range(0,tdim):
    cams_s=cams.isel({'step':time})
    cams_reproject=cams_s.rio.reproject(dst_crs=domena.rio.crs)
    cams_reproject_match=cams_reproject.rio.reproject_match(domena)

    for var in dic_prekl:
        dic_var[var][time,:,:,:]= cams_reproject_match[var][::-1,:,:]

for var in dic_prekl:
    for c_name in dic_prekl[var]:        
        coef = dic_prekl[var][c_name]
        domena[c_name] = coef * dic_var[var] + domena[c_name]

#%%
# interpolacia vyskove hladiny
dom_interp_vyska=domena.interp(level=cmaq_v)

time_25  = pd.date_range(start=start, periods=25, freq='1H')
dom_interp_time=dom_interp_vyska.interp(time=time_25)

#grid=xr.open_dataset('/data/users/p6001/ala_2021_input/met/METCRO3D_2021-11-02.nc')


#for var in dom_interp_vyska.variables.keys():
#    print(var, np.count_nonzero(np.isnan(dom_interp_time[var].data)) )

#%%
#premena jednotiek pre pm na mug/m3 
metcro3d=xr.open_dataset(metcro3d_file_path)

koef_aero = metcro3d['PRES'].data/(287.058*metcro3d['TA'].data)*10**9 

for var in dom_interp_time.variables:
    if var.startswith('A'):
       dom_interp_time[var] *= koef_aero 


#%%
def gridded_to_netCDF(output_dir,out_file_name,xr_dataset,datum,projection,grid_params):


    if not os.path.exists(output_dir):
       os.makedirs(output_dir)


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
                    'NLAYS':np.int32(86),
                    'NTHIK':np.int32(1),
                    'NVARS':np.int32(len(xr_dataset.keys())),
                    'SDATE':np.int32('{0}{1:03d}'.format(datum.year,datum.timetuple().tm_yday)),
                    'STIME':np.int32(0),
                    'TSTEP':np.int32(10000),
                    'UPNAM':"OPENEOUT        ",
                    'VAR-LIST':"".join('{0:16s}'.format(f) for f in xr_dataset.keys()),
                    'VGLVLS':np.array([1.,0.99762151, 0.99497395, 0.9918603,0.98831629, 0.9843596, 0.98000211, 0.97525276, 0.97011865, 0.96460571, 0.95871898, 0.95246284, 0.94584117, 0.93885745, 0.93151482, 0.92381614, 0.91576405, 0.90736097, 0.89860917, 0.88951075, 0.8800677, 0.87028187, 0.86015501, 0.84968879, 0.83888478, 0.82794554, 0.81704196, 0.8061378, 0.79520341, 0.78421488, 0.77315331, 0.76200415, 0.75075644, 0.73940226, 0.72793608, 0.71635416, 0.70465407, 0.69283408, 0.68089273, 0.66882833, 0.65663851, 0.64431982, 0.63186736, 0.61927439, 0.60653205, 0.59362906, 0.58055151, 0.56728266, 0.55380279, 0.54008915, 0.52611592, 0.51185429, 0.49727257, 0.48233639, 0.46700903, 0.45125182, 0.43502463, 0.41828651, 0.40099645, 0.38311424, 0.36460156, 0.34542314, 0.32607457, 0.30708075, 0.28844931, 0.27018841, 0.25230677, 0.23481375, 0.21771947, 0.20103485, 0.18477179, 0.16894327, 0.15356355, 0.13864841, 0.12421541, 0.11028427, 0.09687735, 0.08402029, 0.07174292, 0.06008054, 0.0490758, 0.03878173, 0.02926677, 0.02062412, 0.01299197, 0.00660936, 0.00214619],dtype='float32')[:], 
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

    with netCDF4.Dataset('{0}/{1}-{2}.nc'.format(output_dir,out_file_name,datum.isoformat()[:-9]),mode='w') as out:

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
         out.variables['TFLAG'].setncatts({'units': "<YYYYDDD,HHMMSS>", 'long_name': "FLAG", 'var_desc': "Timestep-valid flags:  (1) YYYYDDD or (2) HHMMSS"})


         tflag=np.zeros([25,global_params['NVARS']],dtype=int)

         for i in range(1,24):
             tflag[i,:]=int(i*10000)

         out.variables['TFLAG'][:,:,1]=tflag
         out.variables['TFLAG'][:24,:,0]=int('{0}{1:03d}'.format(datum.year,datum.timetuple().tm_yday))
         datum_next=datum+datetime.timedelta(days=1)
         out.variables['TFLAG'][24,:,0]=int('{0}{1:03d}'.format(datum_next.year,datum_next.timetuple().tm_yday))

         # create variables
         for name in xr_dataset:

             out.createVariable(name, np.float32, ('TSTEP', 'LAY', 'ROW', 'COL'),fill_value=None)

             if name.startswith('A'): units = "ug m-3          "
             else: units = "ppmV            "

             out.variables[name].setncatts({'units': units, 'long_name': "".join(f'{name:16s}'), 'var_desc': "".join(f' Average Concentrations of {name:53s}')})


             out.variables[name][:,:,:,:]=xr_dataset[name].data





gridded_to_netCDF(output_dir,out_file_name,dom_interp_time,start,projection,grid_params)
print(start)






















































