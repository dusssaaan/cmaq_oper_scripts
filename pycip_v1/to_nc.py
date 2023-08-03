#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 08:18:48 2023

@author: p6001
"""
import numpy as np
import netCDF4
import datetime


metcro3D_params = {
   'TFLAG'    :  {'long_name': 'TFLAG           ', 'units': '<YYYYDDD,HHMMSS>', 'var_desc': 'Timestep-valid flags:  (1) YYYYDDD or (2) HHMMSS                                '},
   'JACOBF'   :  {'long_name': 'JACOBF          ', 'units': 'm               ', 'var_desc': 'Jacobian at layer face scaled by MSFX2                                          '},
   'JACOBM'   :  {'long_name': 'JACOBM          ', 'units': 'm               ', 'var_desc': 'Jacobian at layer middle scaled by MSFX2                                        '},
   'DENSA_J'  :  {'long_name': 'DENSA_J         ', 'units': 'kg m-2          ', 'var_desc': 'J-weighted air density (dry) scaled by MSFX2                                    '},
   'TA'       :  {'long_name': 'TA              ', 'units': 'K               ', 'var_desc': 'air temperature                                                                 '},
   'QV'       :  {'long_name': 'QV              ', 'units': 'kg kg-1         ', 'var_desc': 'water vapor mixing ratio                                                        '},
   'PRES'     :  {'long_name': 'PRES            ', 'units': 'Pa              ', 'var_desc': 'pressure                                                                        '},
   'DENS'     :  {'long_name': 'DENS            ', 'units': 'kg m-3          ', 'var_desc': 'density of air (dry)                                                            '},
   'ZH'       :  {'long_name': 'ZH              ', 'units': 'm               ', 'var_desc': 'mid-layer height above ground                                                   '},
   'ZF'       :  {'long_name': 'ZF              ', 'units': 'm               ', 'var_desc': 'full-layer height above ground                                                  '},
   'CFRAC_3D' :  {'long_name': 'CFRAC_3D        ', 'units': '1               ', 'var_desc': '3D resolved cloud fraction                                                      '},
   'QC'       :  {'long_name': 'QC              ', 'units': 'kg kg-1         ', 'var_desc': 'cloud water mixing ratio                                                        '},
   'QR'       :  {'long_name': 'QR              ', 'units': 'kg kg-1         ', 'var_desc': 'rain water mixing ratio                                                         '},
   'QI'       :  {'long_name': 'QI              ', 'units': 'kg kg-1         ', 'var_desc': 'ice mixing ratio                                                                '},
   'QS'       :  {'long_name': 'QS              ', 'units': 'kg kg-1         ', 'var_desc': 'snow mixing ratio                                                               '},
   'QG'       :  {'long_name': 'QG              ', 'units': 'kg kg-1         ', 'var_desc': 'graupel mixing ratio                                                            '},
    }

metcro2D_params = {
   'PRSFC'    :  {'long_name': 'PRSFC           ', 'units': 'Pa              ', 'var_desc': 'surface pressure                                                                '},
   'USTAR'    :  {'long_name': 'USTAR           ', 'units': 'm s-1           ', 'var_desc': 'cell averaged friction velocity                                                 '},
   'PBL'      :  {'long_name': 'PBL             ', 'units': 'm               ', 'var_desc': 'PBL height                                                                      '},
   'ZRUF'     :  {'long_name': 'ZRUF            ', 'units': 'm               ', 'var_desc': 'surface roughness length                                                        '},
   'HFX'      :  {'long_name': 'HFX             ', 'units': 'W m-2           ', 'var_desc': 'sensible heat flux                                                              '},
   'LH'       :  {'long_name': 'LH              ', 'units': 'W m-2           ', 'var_desc': 'latent heat flux                                                                '},
   'RADYNI'   :  {'long_name': 'RADYNI          ', 'units': 'm s-1           ', 'var_desc': 'inverse of aerodynamic resistance                                               '},
   'RSTOMI'   :  {'long_name': 'RSTOMI          ', 'units': 'm s-1           ', 'var_desc': 'inverse of stomatic resistance                                                  '},
   'TEMPG'    :  {'long_name': 'TEMPG           ', 'units': 'K               ', 'var_desc': 'skin temperature at ground                                                      '},
   'TEMP2'    :  {'long_name': 'TEMP2           ', 'units': 'K               ', 'var_desc': 'temperature at 2 m                                                              '},
   'Q2'       :  {'long_name': 'Q2              ', 'units': 'kg kg-1         ', 'var_desc': 'mixing ratio at 2 m                                                             '},
   'WSPD10'   :  {'long_name': 'WSPD10          ', 'units': 'm s-1           ', 'var_desc': 'wind speed at 10 m                                                              '},
   'RGRND'    :  {'long_name': 'RGRND           ', 'units': 'W m-2           ', 'var_desc': 'solar radiation reaching ground                                                 '},
   'RN'       :  {'long_name': 'RN              ', 'units': 'cm              ', 'var_desc': 'nonconvective precipitation in interval                                         '},
   'RC'       :  {'long_name': 'RC              ', 'units': 'cm              ', 'var_desc': 'convective precipitation in interval                                            '},
   'CFRAC'    :  {'long_name': 'CFRAC           ', 'units': '1               ', 'var_desc': 'total cloud fraction                                                            '},
   'SNOCOV'   :  {'long_name': 'SNOCOV          ', 'units': '1               ', 'var_desc': 'snow cover                                                                      '},
   'VEG'      :  {'long_name': 'VEG             ', 'units': '1               ', 'var_desc': 'vegetation coverage                                                             '},
   'LAI'      :  {'long_name': 'LAI             ', 'units': 'm2 m-2          ', 'var_desc': 'leaf-area index                                                                 '},
   'SEAICE'   :  {'long_name': 'SEAICE          ', 'units': '1               ', 'var_desc': 'sea ice                                                                         '},
   'WR'       :  {'long_name': 'WR              ', 'units': 'm               ', 'var_desc': 'canopy moisture content                                                         '},
   'SOIM1'    :  {'long_name': 'SOIM1           ', 'units': 'm3 m-3          ', 'var_desc': 'volumetric soil moisture in top cm                                              '},
   'SOIM2'    :  {'long_name': 'SOIM2           ', 'units': 'm3 m-3          ', 'var_desc': 'volumetric soil moisture in top m                                               '},
   'SOIT1'    :  {'long_name': 'SOIT1           ', 'units': 'K               ', 'var_desc': 'soil temperature in top cm                                                      '},
   'SLTYP'    :  {'long_name': 'SLTYP           ', 'units': '1               ', 'var_desc': 'soil texture type by USDA category                                              '}, 
   'MOLI'     :  {'long_name': 'MOLI            ', 'units': 'm-1             ', 'var_desc': 'inverse of Monin-Obukhov length                                                 '}
   }

metdot3D_params = {
   'UHAT_JD'  :  {'long_name': 'UHAT_JD         ', 'units': 'kg m-1 s-1      ', 'var_desc': '(contravariant_U*Jacobian*Density) at square pt                                 '},
   'VHAT_JD'  :  {'long_name': 'VHAT_JD         ', 'units': 'kg m-1 s-1      ', 'var_desc': '(contravariant_V*Jacobian*Density) at triangle pt                               '},
   'UWIND'    :  {'long_name': 'UWIND           ', 'units': 'm s-1           ', 'var_desc': 'U-comp. of true wind at dot point                                               '},
   'VWIND'    :  {'long_name': 'VWIND           ', 'units': 'm s-1           ', 'var_desc': 'V-comp. of true wind at dot point                                               '}, 
   'UWINDC'   :  {'long_name': 'UWINDC          ', 'units': 'm s-1           ', 'var_desc': 'U-comp. of true wind at W-E faces                                               '}, 
   'VWINDC'   :  {'long_name': 'VWINDC          ', 'units': 'm s-1           ', 'var_desc': 'V-comp. of true wind at S-N faces                                               '} 
   }             

def tflag(out,inp,global_params):
      # create TFLAGS
      out.createVariable('TFLAG', np.int32, ('TSTEP', 'VAR', 'DATE-TIME'),fill_value=None)
      
           
      start, end = int( inp.int_step ) + inp.start_hour, int(  inp.int_step ) + inp.end_hour + 1
      
      out.variables['TFLAG'][:,:,1]= np.array( [[  int( 10000 * ( inp.datum + datetime.timedelta( hours=i ) ).hour )  for i in range(start, end) ] for var in range(0, global_params['NVARS']) ] ).transpose()
      out.variables['TFLAG'][:,:,0]= np.array( [[  int(f'{inp.datum.year}{(inp.datum + datetime.timedelta(hours=x)).timetuple().tm_yday:03d}') for x in range( start, end ) ] for var in range(0, global_params['NVARS']) ] ).transpose()
      out.variables['TFLAG'].setncatts({'units': '<YYYYDDD,HHMMSS>', 'long_name':'TFLAG           ' , 'var_desc':'Timestep-valid flags:  (1) YYYYDDD or (2) HHMMSS                                '  })

def glob_def(inp):  
    
    datum_write = inp.datum + datetime.timedelta( hours = ( int( inp.int_step ) + inp.start_hour ) )
       
    global_params={ 
         'IOAPI_VERSION': 'ioapi-3.2',
         'EXEC_ID': 'mcip',                                                                            
         'FTYPE': np.int32(1),
         'CDATE': np.int32(2022229),
         'CTIME': np.int32(115207),
         'WDATE': np.int32(2022229),
         'WTIME': np.int32(115207),
         'SDATE': np.int32( f'{datum_write.year}{datum_write.timetuple().tm_yday:03d}' ),
         'STIME': np.int32( datum_write.hour *10000 ),
         'TSTEP': inp.tstep,
         'NTHIK': np.int32(1),
         'GDTYP': np.int32(2),
         'P_ALP': inp.projection['lat_1'],
         'P_BET': inp.projection['lat_2'],
         'P_GAM': inp.projection['lon_0'],
         'XCENT': inp.projection['lon_0'],
         'YCENT': inp.projection['lat_0'],
         'XORIG': inp.xorig,
         'YORIG': inp.yorig,
         'XCELL': inp.xcell,
         'YCELL': inp.xcell,
         'VGTYP': -np.int32(9999),
         'VGTOP': np.float32(inp.pt),
      'FILEDESC': 'US EPA COMMUNITY MULTISCALE AIR QUALITY MODEL                                   METEOROLOGY-CHEMISTRY INTERFACE PROCESSOR                                                                                                                       MCIP V5.3.3  FROZEN 06/30/2021                                                                                                                                                                                                                  INPUT METEOROLOGY DATA FROM WRF ARW V4.3.1                                      INPUT RUN INITIALIZED:  2021-01-01-00:00:00.0000                                                                                                                CUMULUS PARAMETERIZATION:  Tiedtke                                                                                                                              SHALLOW CONVECTION:  No shallow convection                                                                                                                      MICROPHYSICS:  Thompson                                                                                                                                         LONGWAVE RADIATION:  RRTMg                                                                                                                                      SHORTWAVE RADIATION:  RRTMg                                                                                                                                     PBL SCHEME:  Mellor-Yamada-Janjic (Eta) TKE                                                                                                                     SURFACE LAYER SCHEME:  Monin-Obukhov (Janjic Eta)                                                                                                               LAND-SURFACE SCHEME:  NOAH Land-Surface Model                                                                                                                   URBAN MODEL:  No urban physics                                                                                                                                  LAND USE CLASSIFICATION:  MODIFIED_IGBP_MODIS                                                                                                                   3D ANALYSIS NUDGING:  OFF                                                          WIND COEFF:  not applicable                                                     TEMP COEFF:  not applicable                                                     MOIS COEFF:  not applicable                                                     GEOP COEFF:  not applicable                                                                                                                                  SFC ANALYSIS NUDGING:  OFF                                                         WIND COEFF:  not applicable                                                     TEMP COEFF:  not applicable                                                     MOIS COEFF:  not applicable                                                                                                                                  OBS NUDGING:  OFF                                                                  WIND COEFF:  not applicable                                                     TEMP COEFF:  not applicable                                                     MOIS COEFF:  not applicable                                                                                                                                  EARTH RADIUS ASSUMED IN MCIP:  6370000.000 m                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    '} 
    return  global_params

def write_netCDF(inp, outfile_name, global_params, out_vars, var_params):
   with netCDF4.Dataset(f'{inp.out_dir}/{outfile_name}', mode='w') as out:

      # create globals
      for global_par in global_params:

         out.setncattr(global_par, global_params[global_par])

      # create dimensions

      out.createDimension('TSTEP', None)
      out.createDimension('DATE-TIME', size=np.int32(2))
      out.createDimension('LAY', size=global_params['NLAYS'])
      out.createDimension('VAR', size=global_params['NVARS'])
      
      if global_params['HISTORY'].endswith( ('METCRO3D file','METCRO2D file','METDOT3D file' ) ):
         out.createDimension('COL', size=global_params['NCOLS'])
         out.createDimension('ROW', size=global_params['NROWS'])
      elif global_params['HISTORY'].endswith( ('METBDY3D file') ):
         out.createDimension('PERIM', size=int(2*global_params['NCOLS']+2*global_params['NROWS']+4))
        
      tflag(out,inp,global_params)
      
      if global_params['HISTORY'].endswith( ('METCRO3D file','METCRO2D file','METDOT3D file' ) ):       
          for name in out_vars:
                        
             out.createVariable(name, np.float32, ('TSTEP', 'LAY', 'ROW', 'COL'),fill_value=None)
             out.variables[name].setncatts({'units': var_params[name]['units'], 'long_name': var_params[name]['long_name'], 'var_desc': var_params[name]['var_desc'] })
             
      elif global_params['HISTORY'].endswith( ('METBDY3D file') ):
           for name in out_vars:  
               
               out.createVariable(name, np.float32, ('TSTEP', 'LAY', 'PERIM'),fill_value=None)
               out.variables[name].setncatts({'units': var_params[name]['units'], 'long_name': var_params[name]['long_name'], 'var_desc': var_params[name]['var_desc'] })
               
                
             
      if   global_params['HISTORY'].endswith('METCRO3D file'):
           for name in out_vars: out.variables[name][:,:,:,:]=out_vars[name][:,:,1:-1,1:-1]
      elif global_params['HISTORY'].endswith('METCRO2D file'):
           for name in out_vars: out.variables[name][:,0,:,:]=out_vars[name][:,1:-1,1:-1] 
      elif global_params['HISTORY'].endswith('METDOT3D file'): 
           for name in out_vars: out.variables[name][:,:,:,:]=out_vars[name] 
      elif global_params['HISTORY'].endswith('METBDY3D file'):
           ncols, nrows = global_params['NCOLS'], global_params['NROWS']
           for name in out_vars: 
               out.variables[name][:,:,               0 : ncols+1 ]           = out_vars[name][:,:,0,1:]
               out.variables[name][:,:,         ncols+1 : ncols+nrows+2 ]     = out_vars[name][:,:,1:,-1]
               out.variables[name][:,:,   ncols+nrows+2 : 2*ncols+nrows+3 ]  =  out_vars[name][:,:,-1,:-1]
               out.variables[name][:,:, 2*ncols+nrows+3 : 2*ncols+2*nrows+4 ] = out_vars[name][:,:,:-1,0]
          
def metcro3D_to_nectdf( inp,out_metcro3d ):
   
   shapes = out_metcro3d['TA'].shape 
   
   global_params = glob_def(inp)
   
   global_params['NCOLS']    = np.int32(shapes[3]-2)
   global_params['NROWS']    = np.int32(shapes[2]-2)
   global_params['NLAYS']    = np.int32(shapes[1])
   global_params['NVARS']    = np.int32(len(out_metcro3d))
   global_params['VAR-LIST'] = "".join(f'{x:16s}' for x in out_metcro3d.keys())
   global_params['VGLVLS']   = inp.etaf
   global_params['GDNAM']    = 'wrf2km_1_CROSS  ' 
   global_params['UPNAM']    = 'OUTCM3IO        '
   global_params['HISTORY'] = 'US EPA COMMUNITY MULTISCALE AIR QUALITY MODEL METCRO3D file'
     
   write_netCDF(inp, 'METCRO3D_PYCIP-'+f'{inp.datum}'[:-9] + f'_{inp.int_step}_for_{inp.start_hour}+{inp.end_hour}.nc', global_params, out_metcro3d, metcro3D_params)

def metcro2D_to_nectdf( inp,out_metcro2d ):
   
   shapes = out_metcro2d['TEMP2'].shape 
   
   global_params = glob_def(inp)
   
   global_params['NCOLS']    = np.int32(shapes[2]-2)
   global_params['NROWS']    = np.int32(shapes[1]-2)
   global_params['NLAYS']    = np.int32(1)
   global_params['NVARS']    = np.int32(len(out_metcro2d))
   global_params['VAR-LIST'] = "".join(f'{x:16s}' for x in out_metcro2d.keys())
   global_params['VGLVLS']   = inp.etaf[:2]
   global_params['GDNAM']    = 'wrf2km_1_CROSS  ' 
   global_params['UPNAM']    = 'OUTCM3IO        '
   global_params['HISTORY'] = 'US EPA COMMUNITY MULTISCALE AIR QUALITY MODEL METCRO2D file'
     
   write_netCDF(inp, 'METCRO2D_PYCIP-'+f'{inp.datum}'[:-9] + f'_{inp.int_step}_for_{inp.start_hour}+{inp.end_hour}.nc', global_params, out_metcro2d, metcro2D_params)

def metdot3D_to_nectdf( inp,out_metdot3d ):
   
   shapes = out_metdot3d['UWIND'].shape 
   
   global_params = glob_def(inp)
   
   global_params['XORIG']    -= global_params['XCELL']/2
   global_params['YORIG']    -= global_params['YCELL']/2
   global_params['NCOLS']    = np.int32(shapes[3])
   global_params['NROWS']    = np.int32(shapes[2])
   global_params['NLAYS']    = np.int32(shapes[1])
   global_params['NVARS']    = np.int32(len(out_metdot3d))
   global_params['VAR-LIST'] = "".join(f'{x:16s}' for x in out_metdot3d.keys())
   global_params['VGLVLS']   = inp.etaf
   global_params['GDNAM']    = 'wrf2km_1_DOT  ' 
   global_params['UPNAM']    = 'OUTCM3IO        '
   global_params['HISTORY'] = 'US EPA COMMUNITY MULTISCALE AIR QUALITY MODEL METDOT3D file'
     
   write_netCDF(inp, 'METDOT3D_PYCIP-'+f'{inp.datum}'[:-9] + f'_{inp.int_step}_for_{inp.start_hour}+{inp.end_hour}.nc', global_params, out_metdot3d, metdot3D_params)


def metbdy3D_to_nectdf( inp,out_metcro3d ):
   
   shapes = out_metcro3d['TA'].shape 
   
   global_params = glob_def(inp)
   
   global_params['FTYPE']    = np.int32(2)
   global_params['NCOLS']    = np.int32(shapes[3]-2)
   global_params['NROWS']    = np.int32(shapes[2]-2)
   global_params['NLAYS']    = np.int32(shapes[1])
   global_params['NVARS']    = np.int32(len(out_metcro3d))
   global_params['VAR-LIST'] = "".join(f'{x:16s}' for x in out_metcro3d.keys())
   global_params['VGLVLS']   = inp.etaf
   global_params['GDNAM']    = 'wrf2km_1_CROSS  ' 
   global_params['UPNAM']    = 'OUTCM3IO        '
   global_params['HISTORY'] = 'US EPA COMMUNITY MULTISCALE AIR QUALITY MODEL METBDY3D file'
     
   write_netCDF(inp, 'METBDY3D_PYCIP-'+f'{inp.datum}'[:-9] + f'_{inp.int_step}_for_{inp.start_hour}+{inp.end_hour}.nc', global_params, out_metcro3d, metcro3D_params)
   
   
   
   
