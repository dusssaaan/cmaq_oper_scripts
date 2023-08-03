#!/usr/bin/env /users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 14:47:06 2023

@author: p6001
"""
import grib_open
import numpy as np
import time
import metcalc 
import to_nc 
import importlib
importlib.reload(metcalc)
importlib.reload(grib_open)
importlib.reload(to_nc)
import sys

import datetime
import netCDF4

wrf_file = netCDF4.Dataset('/data/users/oko001/alacon/outputs/2021-01-02_24h.nc') # need to be replaced

class Inputs:
      def __init__(self, datum, method, path, file_name, int_step, start_hour, end_hour, start_time, tprev):
          
          self.projection={'proj': 'lcc',
           'lat_1': 48.80182647705078,
           'lat_2': 48.80182647705078,
           'lat_0': 48.80182647705078,
           'lon_0': 18.11156463623047,
           'x_0': 0,
           'y_0': 0,
           'a': 6370000.0,
           'b': 6370000.0,
           'units': 'm',
           'no_defs': True}
          
          self.xorig = -494999.4375
          self.yorig = -367000.4375
          self.xcell = 2000.0
           
          self.out_dir = '/data/users/oko001/cmaq_oper_data/mcip_files'   
          
          self.datum  = datum
          self.stdate = np.int32('{0}{1:03d}'.format(self.datum.year,self.datum.timetuple().tm_yday))
          self.stime  = np.int32(0)
          self.tstep  = np.int32(10000)
          self.int_datum = f'{datum}'[:-9] + f'_{int_step}'
          self.cut = [2,-2,2,-2]     #cut in the order [cut[0]:cut[1],cut[2]:cut[3]]
   
          
          #self.xorig += self.cutc * self.xcell 
          #self.yorig += self.cuta * self.xcell
          
          if method == 'ala_oper':
              self.giwrf = 1 / 9.81
              self.rdwrf = 287
              self.rvwrf = 461.6

              self.lu_scheme = 'USGS'
             
              self.nlays = 86  # (path,self.datum,self.lays, self.cut, start_time)
              
              self.ala_file = grib_open.process_grib_data('multi', path, file_name, self.int_datum, self.nlays, self.cut, start_hour, end_hour, tprev)
              self.pt = 0
              self.po = self.ala_file['po']              
              
              # inputs 1D vertical params
              self.etaf         = self.ala_file['etaf']                   # required by CRO3D
              self.bf           = self.ala_file['bf']                     # required by CRO3D                  
              
             
              
              
              # inputs 2D
              self.PRSFC        = self.ala_file['PRSFC']                  # required by CRO3D, CRO2D      
              self.TEMP2        = self.ala_file['TEMP2']                  # required by CRO3D, CRO2D                      
              self.USTAR        = self.ala_file['USTAR']                  # required by CRO2D           
              self.PBL          = self.ala_file['PBL']                    # required by CRO2D         
              self.HFX          = self.ala_file['HFX']                    # required by CRO2D   
              self.LH           = self.ala_file['LH']                     # required by CRO2D  
              self.RGRND        = self.ala_file['RGRND']                  # required by CRO2D  
              self.TEMPG        = self.ala_file['TEMPG']                  # required by CRO2D  
              self.Q2           = self.ala_file['Q2']                     # required by CRO2D  
              self.SNOCOV       = self.ala_file['SNOCOV']                 # required by CRO2D  
              self.SOIM1        = self.ala_file['SOIM1']                  # required by CRO2D  
              self.SOIM2        = self.ala_file['SOIM2']                  # required by CRO2D  
              self.SOIT1        = self.ala_file['SOIT1']
              self.WR           = self.ala_file['WR']                     # required by CRO2D
              self.CFRAC        = self.ala_file['CFRAC'] 
              self.U10          = self.ala_file['U10']                    # required by CRO2
              self.V10          = self.ala_file['V10']                    # required by CRO2D
              self.RAINC        = self.ala_file['RAINC']                  # required by CRO2D
              self.RAINNC       = self.ala_file['RAINNC']                 # required by CRO2D

              
               # inputs 2D static                               
              self.mapfac_m      = np.array(wrf_file['MAPFAC_M'][0,:,:])       # required by CRO3D
              self.SLTYP         = np.array(wrf_file['ISLTYP'])                # required by CRO2D   
              self.VEG           = np.array(wrf_file['VEGFRA'])                # required by CRO2D
              self.SEAICE        = np.zeros(self.U10.shape)                    # required by CRO2D
              self.LU_INDEX      = np.array(wrf_file['LU_INDEX'])  
              self.LANDMASK      = np.array(wrf_file['LANDMASK'])
              self.LAI           = np.array(wrf_file['LAI'])                   # required by CRO2D   
             
              
              self.SLTYP         = np.concatenate( (self.SLTYP, self.SLTYP[-1,:][None,:,:]), axis=0)
              self.VEG           = np.concatenate( (self.VEG, self.VEG[-1,:][None,:,:]), axis=0)
              self.LU_INDEX      = np.concatenate( (self.LU_INDEX, self.LU_INDEX[-1,:][None,:,:]), axis=0)
              self.LANDMASK      = np.concatenate( (self.LANDMASK, self.LANDMASK[-1,:][None,:,:]), axis=0)
              self.LAI           = np.concatenate( (self.LAI, self.LAI[-1,:][None,:,:]), axis=0)  
             
              
              # inputs 3D
              self.T            = self.ala_file['T']                      # required by CRO3D                  
              self.QV           = self.ala_file['QV']                     # required by CRO3D       
              self.CFRAC_3D     = self.ala_file['CFRAC_3D']               # required by CRO3D, CRO2D
              self.QC           = self.ala_file['QC']                     # required by CRO3D
              self.QR           = self.ala_file['QR']                     # required by CRO3D
              self.QI           = np.zeros(self.ala_file['T'].shape)      # required by CRO3D
              self.QS           = self.ala_file['QS']                     # required by CRO3D
              self.QG           = np.zeros(self.ala_file['T'].shape)      # required by CRO3D    
              self.U            = self.ala_file['U']                      # required by DOT3D
              self.V            = self.ala_file['V']                      # required by DOT3D


#%%
start_time = time.time()


datum = datetime.datetime.combine( datetime.date.today(), datetime.datetime.min.time() )
method = 'ala_oper'
path = '/data/nwp/ala2e/grib/sh20/'
file_name = 'ALA2ESH20+'
int_step =  str(sys.argv[1])
start_hour, end_hour =  int(sys.argv[2]), int(sys.argv[3])
tprev = '12' # 12  means that +12 hour from the previous run (-12 h) is taking as the 0;  
             # 00  means that +24 hour from the previus  run (-24 h) is taking as the 0; 

inp = Inputs(datum, method, path, file_name, int_step, start_hour, end_hour, start_time, tprev)


out_metcro3d = metcalc.metcro3D_var(inp, method)
print('METCRO3D outputs are prepared in {0:.1f} sec'.format(time.time() - start_time))
out_metcro2d = metcalc.metcro2D_var(inp, method, out_metcro3d)
print('METCRO2D outputs are prepared in {0:.1f} sec'.format(time.time() - start_time))
out_metdot3d = metcalc.metdot3D_var(inp, method, out_metcro3d)
print('METDOT2D outputs are prepared in {0:.1f} sec'.format(time.time() - start_time))

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
# interpolation to 33 vertical layers
# comment out if no interpolation is needed 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  

levels = [0,1,2,3,4,6,8,11,14,17,21,24] +[27,30,33,36,39,43,46,50] + [55, 58, 61, 63, 65, 67, 69, 71, 72,73, 75,76,77]
zh, zf, zhnew, zfnew = metcalc.interp_z( levels, out_metcro3d )

out_metcro3d = metcalc.interp_levels( out_metcro3d, zhnew, zh, zfnew, zf, levels, 'CRO')
print('CRO outputs are interpolated in {0:.1f} sec'.format(time.time() - start_time))

out_metdot3d = metcalc.interp_levels( out_metdot3d, zhnew, zh, zfnew, zf, levels, 'DOT')
print('DOT outputs are interpolated in {0:.1f} sec'.format(time.time() - start_time))    

inp.etaf = inp.etaf[levels] 

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
# save to netcdf 
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
inp.int_step = int_step
inp.start_hour, inp.end_hour = start_hour, end_hour

to_nc.metcro3D_to_nectdf(inp,out_metcro3d)
print('METCRO3D outputs are written in {0:.1f} sec'.format(time.time() - start_time))
to_nc.metcro2D_to_nectdf(inp,out_metcro2d)
print('METCRO2D outputs are written in {0:.1f} sec'.format(time.time() - start_time))
to_nc.metdot3D_to_nectdf(inp,out_metdot3d)
print('METDOT3D outputs are written in {0:.1f} sec'.format(time.time() - start_time))
to_nc.metbdy3D_to_nectdf(inp,out_metcro3d)
print('METBDY3D outputs are written in {0:.1f} sec'.format(time.time() - start_time))


""" 
import netCDF4
a1= netCDF4.Dataset('/data/oko/dusan/mcip_kosymoko_2km_2022_33/METDOT3D_PYCIP-2023-07-06.nc')
a2= netCDF4.Dataset('/data/oko/dusan/mcip_kosymoko_2km_2022_sk/METDOT3D_PYCIP-2023-07-06.nc')

for var in a1.variables:
    
    m=np.max( np.abs( a1[var][:] - a2[var][:] ) )
    mper = np.max( np.abs( a1[var][:] - a2[var][:] )/a2[var][:] )
    print( var, m, mper )
"""


