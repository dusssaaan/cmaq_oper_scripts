#!/usr/bin/env /users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 31 12:39:52 2023

@author: oko001
"""
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib import colors
import rioxarray
import cartopy.crs as ccrs
from matplotlib import colors
import datetime
import cartopy.feature as cfeature
import pyproj
import sys
import os
import pytz

#%%
datum    =  datetime.datetime.strptime( '2023-09-10' ,'%Y-%m-%d') #datetime.datetime.strptime(str( sys.argv[1]  ,'%Y-%m-%d')
forecast =  '00' # '12' 
start    =  0 #int(sys.argv[0])  # 0  or 24
end      = start + 24
#%%
time_zone=pytz.timezone( 'EUROPE/Bratislava'  )
shift_time = int(str(time_zone.localize(datum))[-6:-3])
local_datum=datum+datetime.timedelta(hours=shift_time)
#%%
datum_strf = datum.strftime('%Y%m%d')

grid = xr.open_dataset('/data/users/oko001/cmaq_oper_data/static_and_default_files/GRIDCRO2D_2021-01-01.nc')
post = xr.open_dataset(f'/data/users/oko001/cmaq_oper_data/combine/run_{forecast}/COMBINE_ACONC_v533_intel_com_{forecast}_{start}_{end}_{datum_strf}.nc')

#%%

proj4 = '+proj=lcc +lat_1=48.80182499999999 +lat_2=48.80182499999999 +lat_0=48.80182499999999 +lon_0=18.111565 +x_0=0.0 +y_0=0.0 +a=6371229.0 +b=6371229.0 +units=m +no_defs:'

a,c = 0, 0
b,d = None, None

X,Y = pyproj.Proj(proj4)(grid.LON.data[0,0,a:b,c:d], grid.LAT.data[0,0,a:b,c:d], inverse=False)
X,Y = X[0,:],Y[:,0]

lcc = ccrs.LambertConformal(central_longitude=18.111565,
                            central_latitude=48.80182499999999,
                            standard_parallels=(48.80182499999999,48.80182499999999),
                            globe=ccrs.Globe(semimajor_axis=6371229.0, semiminor_axis=6371229.0,ellipse=None))


border=cfeature.BORDERS.with_scale('10m')

xds = xr.Dataset()
#xds['PM25']=(('y','x'), np.sum(emis*0.0036, axis=0 ) )
xds.coords['x'] = (('x'),X)
xds.coords['y'] = (('y'),Y)
xds=xds.rio.set_spatial_dims("x","y",inplace=True)
xds=xds.rio.write_crs(proj4)

#%%

def plotter(timestep, vmin, vmax, pol, pol_name_in_post,pol_name_save, plt_save_path, save_plot = False ):
    
    xds.coords['aux'] = (('y','x'), post[pol_name_in_post][timestep,0,:,:].data )
    
    fig = plt.figure(figsize=(20,9)) # open matplotlib figure
    ax1 = plt.axes(projection = lcc)
    ax1.add_feature(border,  linewidth=1, edgecolor='black')
    
    picture = xds['aux'][:,:].plot(ax=ax1,cmap=plt.cm.jet, add_colorbar=False, vmin=vmin, vmax=vmax)
    cb  = plt.colorbar(picture,label=f'{pol} [$\mu g/m^3$] ', orientation="vertical", shrink=1)
    
    
    ldp = local_datum + datetime.timedelta(hours=timestep+start+1)
    timefrombegin = timestep + start
    plt.title(f"forecast from {forecast}UTC {datum_strf}, to + {timefrombegin} UTC (loc measure time {ldp.hour:02d}:00 {ldp.day:02d}.{ldp.month:02d} )  ")
    if save_plot == True:
        
       if not os.path.exists(plt_save_path):
          os.makedirs(plt_save_path)
       plt.savefig(f'{plt_save_path}/{pol_name_save}_forecast{forecast}UTC{datum_strf}_plus_{timefrombegin:02d}hour', dpi=300, bbox_inches='tight')
    
    plt.show()
    plt.close()



#%%
for time in range(0,24):
    plotter(time, 0, 120, '$O_3$','O3_ug', 'O3', f'/data/oko/cmaq_oper/maps/run_{forecast}/O3/{datum_strf}', save_plot=True)

for time in range(0,24):
    plotter(time, 0, 60, '$PM_{2.5}$','PM25_TOT','PM25',f'/data/oko/cmaq_oper/maps/run_{forecast}/PM25/{datum_strf}', save_plot=True)

for time in range(0,24):
    plotter(time, 0, 60, '$PM_{10}$','PM10','PM10',f'/data/oko/cmaq_oper/maps/run_{forecast}/PM10/{datum_strf}', save_plot=True)

for time in range(0,24):
    plotter(time, 0, 60, '$NO_2$','NO2_ug','NO2',f'/data/oko/cmaq_oper/maps/run_{forecast}/NO2/{datum_strf}', save_plot=True)

print('program finished succesfully')
