#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 10:07:52 2023

@author: p6001
"""
import numpy as np



# parameters for z0 calculations
# usgs summer [cm]
sfz0usgssum = [80.0,  15.0,  10.0,  15.0,  14.0,  20.0,  12.0,   5.0,  
                6.0,  15.0,  50.0,  50.0,  50.0,  50.0,  50.0,   0.01, 
               20.0,  40.0,   1.0,  10.0,  30.0,  15.0,  10.0,   5.0,  
                1.0,  15.0,   1.0,  80.0,  80.0,  80.0,  80.0,  80.0,  80.0 ]
        
# usgs winter [cm]
sfz0usgswin = [80.0,   5.0,   2.0,   5.0,   5.0,  20.0,  10.0,   1.0,  
                1.0,  15.0,  50.0,  50.0,  50.0,  50.0,  20.0,   0.01, 
               20.0,  40.0,   1.0,  10.0,  30.0,  15.0,   5.0,   5.0,  
                1.0,  15.0,   1.0,  80.0,  80.0,  80.0,  80.0,  80.0,  80.0 ]

# modis summer [cm]
sfz0modsum = [50.0,  50.0,  50.0,  50.0,  50.0,   5.0,  6.0,   5.0,
              15.0,  12.0,  30.0,  15.0,  80.0,  14.0,  0.1,   1.0,
              0.01, 30.0,  15.0,  10.0,   0.01, 80.0,  80.0,  80.0,  
              80.0,  80.0,  80.0,  80.0,  80.0,  80.0,  80.0,  80.0,  80.0 ]

# modis winter [cm]
sfz0modwin = [50.0,  50.0,  50.0,  50.0,  20.0,   1.0,   1.0,   1.0,  
              15.0,  50.0,  30.0,   5.0,  80.0,   5.0,   0.1,   1.0,  
              0.01, 10.0,  30.0,  15.0,   0.01, 80.0,  80.0,  80.0,  
              80.0,  80.0,  80.0,  80.0,  80.0,  80.0,  80.0,  80.0,  80.0 ]

def zruf_calc(inp):
    """
    return z0 roughness length based on the LU index scheme
    """

    #it depends what is summer and what winter
    season = 'summer' if inp.datum.timetuple().tm_yday in range(121,304) else 'winter' 
        
    print(f'Season for z0 roughness lenght is determined as {season}' )
    
    if inp.lu_scheme == 'MODIS' :
        
       if season == 'winter':  
          func = lambda x: sfz0modwin[x-1]
       else:
          func = lambda x: sfz0modsum[x-1] 
       
    elif inp.lu_scheme == 'USGS':
       
       if season == 'winter':  
          func = lambda x: sfz0usgswin[x-1]
       else:
          func = lambda x: sfz0usgssum[x-1]     
    
    
    return (lambda x : np.vectorize(func)(x)) (inp.lu[0,:,:])*0.01




def  resist_calc(inp, cro3d):
     """
     Calculates aerodynamic and stomatal resistances required
     to compute dry deposition velocities as in soubrutine resistcalc
     """
     out ={}
    
     vkar      =  0.40 
     pro       =  0.95
     gamah     =  11.60
     betah     =  8.21
     amolmin   =  1.25
     grav      =  9.80622
     ep1       =  0.608
     lv0       =  2.501e6
     dlvdt     =  2370.0
     stdtemp   =  273.15
     cp        =  7.0 * 287 / 2.0
     
     ql1      =  cro3d['QV'][:,0,:]
     cpair    =  cp * (1.0 + 0.84 * ql1)
     
     #################################
     # CALCULATE M-O length     
     #################################
     theta1    = cro3d['TA'][:,0,:] * (100000.0/cro3d['PRES'][:,0,:] )**0.286
     thetav1   = theta1 * (1.0 + ep1 * ql1)
     lv        = lv0 - dlvdt * (inp.TEMPG -  stdtemp)
     wvflx     = inp.LH / lv
     hfx       = -inp.HFX / (cro3d['DENS'][:,0,:]  * cpair)
     tstv      = ( hfx * (1.0 + ep1 * ql1) + (ep1 * theta1 * wvflx)/cro3d['DENS'][:,0,:] ) / inp.USTAR
      
     xmol  = np.where( np.abs(tstv) > 0.000001,   thetav1 * inp.USTAR * inp.USTAR / (vkar * grav * tstv), 1e7 )
     xmol  = np.where( np.abs(xmol) < 1/amolmin,  np.copysign( 1/amolmin , xmol), xmol )
    
     out['MOLI'] = 1/xmol
   
     #################################
     # CALCULATE aerodynamic resistance     
     #################################
    
     z1       = cro3d['ZH'][0,0,:]
     alogz1z0 = np.log(z1/inp.ZRUF)
     z1ol     = z1 / xmol
     zntol    = inp.ZRUF/ xmol
    
       
    
     psih = np.where( ( (z1ol >= 0) & (z1ol <= 1) & (zntol > 1) ),  -betah * z1ol - (1.0 - betah - zntol)  , np.zeros(z1ol.shape))
    
     psih += np.where( ( (z1ol >= 0) & (z1ol <= 1) & (zntol <= 1) ),  -betah * z1ol + betah * zntol  , np.zeros(z1ol.shape))
    
     psih += np.where( ( (z1ol > 1) & (zntol > 1) ),  zntol -z1ol , np.zeros(z1ol.shape))
    
     psih += np.where( ( (z1ol > 1) & (zntol <= 1) ),  1.0 - betah - z1ol + betah * zntol  , np.zeros(z1ol.shape) )
                                                                                                                              
     psih += np.where( z1ol < 0  ,  2.0 * np.log( (1.0 + np.sqrt(1.0 - gamah*z1ol) )/(1.0 + np.sqrt(1.0 - gamah*zntol) ) ),  np.zeros(z1ol.shape)  )
    
         
     xradyn = np.where(inp.USTAR > 0, pro * ( alogz1z0 - psih ) / ( vkar * inp.USTAR ) , -9.0e20  )
     
     out['RADYNI'] = 1 / xradyn


     #################################
     # CALCULATE stomatal resistance     
     #################################
     ftmin      = 0.0000001
     rsmax      = 5000.0
     vp0   = 611.29
     svp2  = 17.67
     svp3  = 29.65
     f3min = 0.25

     
     if inp.lu_scheme == 'MODIS' :
        rstmod = [    175.0,  120.0,  175.0,  200.0,  200.0,  200.0,  200.0,  150.0,   
                      120.0,  100.0,  160.0,   70.0,  150.0,  100.0, 9999.0,  100.0,   
                      9999.0,  175.0,  120.0,  100.0, 9999.0, 9999.0, 9999.0, 9999.0,   
                      9999.0, 9999.0, 9999.0, 9999.0, 9999.0, 9999.0,  150.0,  140.0,  125.0 ]  
        
        f2defmod  = [  0.90,   0.90,   0.90,   0.90,   0.90,   0.50,   0.50,   0.60,  
                       0.60,   0.70,   0.99,   0.93,   0.80,   0.85,   0.99,   0.30,  
                       1.00,   0.50,   0.60,   0.20,   1.00,   0.00,   0.00,   0.00,  
                       0.00,   0.00,   0.00,   0.00,   0.00,   0.00,   0.84,   0.82,   0.80 ]
        
        
        f2     = np.vectorize(lambda x: f2defmod[x-1]) (inp.lu[0,:]) 
        rstmin = np.vectorize(lambda x: rstmod[x-1]  ) (inp.lu[0,:])  
        
     elif inp.lu_scheme == 'USGS':
     
       rstusgs = [   150.0,   70.0,   60.0,   70.0,   80.0,  180.0,  100.0,  200.0,   
                     150.0,  120.0,  200.0,  175.0,  120.0,  175.0,  200.0, 9999.0,   
                     164.0,  200.0,  100.0,  150.0,  200.0,  150.0,  100.0,  300.0,   
                     100.0,  100.0,  100.0, 9999.0, 9999.0, 9999.0,  150.0,  140.0,  125.0 ]

       f2defusgs = [  0.80,   0.85,   0.98,   0.90,   0.80,   0.90,   0.70,   0.50,  
                      0.60,   0.60,   0.90,   0.90,   0.90,   0.90,   0.90,   1.00,  
                      0.99,   0.99,   0.30,   0.40,   0.50,   0.60,   0.20,   0.99,  
                      0.20,   0.20,   0.20,   0.00,   0.00,   0.00,   0.84,   0.82,   0.80 ]


       f2     = np.vectorize(lambda x: f2defusgs[x-1]) (inp.lu[0,:]) 
       rstmin = np.vectorize(lambda x: rstusgs[x-1]  ) (inp.lu[0,:])  
     
     # Effects of radiation.   
     radl   = np.where(rstmin > 130, 30, 100 )
     xlai =  np.where(inp.LANDMASK > 0, inp.LAI, 10000)
     radf = 1.1 * inp.RGRND/ ( radl * xlai )  # NP89 - EQN34
     f1   = (rstmin / rsmax + radf) / (1.0 + radf)

     t1 = cro3d['TA'][:,0,:]
     #Effects of air temperature following Avissar (1985) and Xiu (7/95).
     f4 = np.where( t1 <= 302.15, 1.0 / (1.0 + np.exp(-0.41 * (t1 - 282.05))),  1.0 / (1.0 + np.exp( 0.50 * (t1 - 314.00))) )

     ftot = np.maximum( (xlai * f1 * f2 * f4), ftmin )
     gsfc = ftot / rstmin          
   
     raw = xradyn + 4.503 / inp.USTAR    # 4.503 = (Scw/Pran)^2/3
     ga  = 1.0 / raw
    
     #Compute the saturated mixing ratio at surface temperature (XTEMPG). Saturation vapor pressure [mb] of water.
     es = np.where( ( (inp.SNOCOV > 0) | ( inp.TEMPG <= stdtemp )), vp0 * np.exp(22.514 - 6.15e3/inp.TEMPG), vp0 * np.exp(svp2 * (inp.TEMPG - stdtemp) / (inp.TEMPG - svp3))   )
     qss  = es * 0.622 / (inp.PRSFC - es)
     
     #Compute humidity effect according to RH at leaf surface
     f3 = 0.5 * (gsfc - ga + np.sqrt(ga * ga + ga * gsfc * (4.0 * ql1 / qss - 2.0) + gsfc * gsfc)) / gsfc
     f3 = np.minimum( np.maximum(f3,f3min), 1.0 )
    

     xrstom  = np.where( inp.LANDMASK > 0, 1.0 / (gsfc * f3) , -9.0e20 )

     out['RSTOMI']  = np.where( xrstom > 0, 1/xrstom, 0 )
      
     return out


   









         
