#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 15:04:00 2023

@author: p6001
"""
import numpy as np
import cro2D_func
import time


inter_time = time.time()

def metcro3D_var(inp, method):
    
    out = {}
    
    inp.MU     = inp.PRSFC - inp.pt
    
    inp.etah   = ( inp.etaf[1:] + inp.etaf[:-1] ) / 2
    
    inp.bh  = ( inp.bf[1:] + inp.bf[:-1] ) / 2
    
         
    inp.presf = (inp.etaf - inp.bf )*(inp.po - inp.pt)+inp.pt+np.einsum('i,jkl->jkli', inp.bf, inp.MU)
    inp.presf = np.einsum('iklj->ijkl', inp.presf)

    inp.muh   = np.einsum('ijkl, j -> ijkl', inp.presf[:,1:,:] - inp.presf[:,:-1,:], 1/( inp.etaf[1:] - inp.etaf[:-1] ) )
           
    out['PRES'] = (inp.etah - inp.bh) * (inp.po - inp.pt) + inp.pt + np.einsum('i,jkl->jkli', inp.bh, inp.MU)  
    out['PRES'] = np.einsum('iklj->ijkl', out['PRES'])
    
    inp.muf  =  np.einsum('ijkl, j -> ijkl', (out['PRES'][:,1:,:] - out['PRES'][:,:-1,:]), 1 / ( inp.etah[1:] - inp.etah[:-1] ) )
    inp.muf  =  np.concatenate( (inp.MU[:,None,:,:], inp.muf, np.full( inp.MU.shape, inp.po -inp.pt)[:,None,:,:] ), axis=1 )   
    
    if method == 'wrf':
       out['TA'] = (inp.POT_TEMP + 300)* ( out['PRES']/100000 ) ** (2/7)
    elif method == 'ala_oper':
       out['TA'] = inp.T
    elif method == 'ala_KOS':
       out['TA'] = (inp.T)* ( out['PRES']/100000 ) ** (2/7)
       
    inp.mapfac_m2i = 1/ inp.mapfac_m **2

    out['DENSA_J'] = inp.giwrf * inp.muh *inp.mapfac_m2i
  
    out['DENS'] = out['PRES'] / (inp.rdwrf * out['TA'] * (1.0 + inp.rvwrf* inp.QV/inp.rdwrf) )

    out['JACOBM'] = out['DENSA_J'] / out['DENS'] 

    # for JACOBF
    inp.qf = np.concatenate( ( (inp.QV[:,1:,:]+inp.QV[:,:-1,:])/2, inp.QV[:,-1,:,:][:,None,:,:] ), axis=1 )
    inp.tf = np.concatenate( ( (out['TA'][:,1:,:]+out['TA'][:,:-1,:])/2, out['TA'][:,-1,:,:][:,None,:,:] ), axis=1 )
    
    
    densf  = inp.presf[:,1:,:] / (inp.rdwrf * inp.tf * (1.0 + inp.rvwrf* inp.qf/inp.rdwrf) ) 
    densf0 = inp.presf[:,0,:]  / (inp.rdwrf * inp.TEMP2 * (1.0 + inp.rvwrf* inp.QV[:,0,:]/inp.rdwrf) ) 
    inp.densf = np.concatenate( (densf0[:,None,:,:], densf ), axis=1)
    
    out['JACOBF'] = inp.giwrf * np.einsum('ijkl,kl -> ijkl', inp.muf / inp.densf, inp.mapfac_m2i  )[:,1:,:]
    
    out['ZH'] = np.zeros(out['JACOBM'].shape)
    #co by to teoreticky mohlo byt zhv[:,0,:]= 1/2 * giwrf * (xpresf[:,0,:,:] - xpresf[:,1,:,:] ) * ( 0.5/xdensaf0 + 0.5/xdensam[:,0,:])
    out['ZH'][:,0,:] = 1/4 * inp.giwrf * ( (inp.etaf[0]-inp.etaf[1])*inp.muf[:,0,:]/inp.densf[:,0,:] +  (inp.presf[:,0,:,:] - inp.presf[:,1,:,:] )/out['DENS'][:,0,:] )
    out['ZH'][:,1:,:] =  inp.giwrf * (out['PRES'][:,:-1,:,:] - out['PRES'][:,1:,:,:] )/inp.densf[:,1:-1,:,:]
    out['ZH'] = np.cumsum(out['ZH'], axis=1 )
   
    out['ZF'] = inp.giwrf *  (inp.presf[:,:-1,:,:] - inp.presf[:,1:,:,:])/out['DENS']  
    out['ZF'] = np.cumsum( out['ZF'], axis=1 )
    
    # variables not changed by processor doprogramuj  REAL,               PARAMETER     :: epsilonq   = 1.0e-30
    #REAL,               PARAMETER     :: epsilonqv  = 1.0e-14
    
    out['QV']               = inp.QV
    out['QV'][out['QV'] < 1e-14 ] = 1e-14
    
    out['CFRAC_3D']     = inp.CFRAC_3D
    out['QC']           = inp.QC
    out['QR']           = inp.QR
    out['QI']           = inp.QI
    out['QS']           = inp.QS
    out['QG']           = inp.QG
    
    for par in ['QC','QR','QI', 'QS', 'QG'] :
         out[par][ out[par] < 1e-30 ] = 0 
    
    return out


def metcro2D_var(inp, method, cro3D):
    
    out = {}  
    
    out['WSPD10'] = np.sqrt(inp.U10**2 + inp.V10**2 )    

    inp.lu    = inp.LU_INDEX.astype(int)
    
    inp.ZRUF  = cro2D_func.zruf_calc(inp)
    resist    = cro2D_func.resist_calc(inp,cro3D)
    out['ZRUF'] = np.einsum('jk,i -> ijk', inp.ZRUF, np.ones(out['WSPD10'].shape[0]) ) #porovnat niekedy s tym co dava aladin
 
    
    if method == 'ala_oper':
        out['CFRAC'] =inp.CFRAC     
    else:
        # Calculate CFRAC from 3D cloud fraction (my algorithm) 
        thic         = np.concatenate( (cro3D['ZF'][:,0,:][:,None,:,:], (cro3D['ZF'][:,1:,:] - cro3D['ZF'][:,:-1,:]) ),axis=1 )
       
        kmin = ( inp.CFRAC_3D !=0 ).argmax(axis=1) 
        kmax =   inp.CFRAC_3D.shape[1] - (inp.CFRAC_3D[:,::-1,:,:] !=0 ).argmax(axis=1)
       
    
        clfrac = [[[ ( inp.CFRAC_3D[t,kmin[t,i,j]:kmax[t,i,j],i,j] * thic[t,kmin[t,i,j]:kmax[t,i,j],i,j] ).sum()/(thic[t,kmin[t,i,j]:kmax[t,i,j],i,j]).sum() for j in range(0,thic.shape[3])] for i in range(0,thic.shape[2])] for t  in range(0,thic.shape[0]) ]
        out['CFRAC'] = np.array(clfrac)
 
    
    if method == 'wrf':
        x_rc         =  np.zeros(out['WSPD10'].shape)
        x_rc[0,:]    =  inp.RAINC[0,:] - inp.raincb
        x_rc[1:,:]   =  inp.RAINC[1:,:] - inp.RAINC[:-1,:]           
        out['RC']    =   x_rc  / 10
        out['RC']    =  np.where(out['RC'] < 1e-8,0, out['RC'])
        
        x_rnc         =  np.zeros(out['WSPD10'].shape)
        x_rnc[0,:]    =  inp.RAINNC[0,:]  - inp.rainncb
        x_rnc[1:,:]   =  inp.RAINNC[1:,:] - inp.RAINNC[:-1,:]           
        out['RN']     =  x_rnc  / 10
        out['RN']     =  np.where(out['RN'] < 1e-8,  0 , out['RN'])
    
    elif method == 'ala_KOS' or 'ala_oper': 
        x_rc         =  np.zeros(out['WSPD10'].shape)
        x_rc[0,:]    =  inp.RAINC[1,:] - inp.RAINC[0,:]
        x_rc[1,:]    =  inp.RAINC[2,:]
        x_rc[2:,:]   =  inp.RAINC[3:,:] - inp.RAINC[2:-1,:] 
        out['RC']    =   x_rc  / 10
        out['RC']    =  np.where(out['RC'] < 1e-8,0, out['RC'])
        
        x_rnc         =  np.zeros(out['WSPD10'].shape)
        x_rnc[0,:]    =  inp.RAINNC[1,:]  - inp.RAINNC[0,:]
        x_rnc[1,:]    =  inp.RAINNC[2,:]
        x_rnc[2:,:]   =  inp.RAINNC[3:,:] - inp.RAINNC[2:-1,:]           
        out['RN']     =  x_rnc  / 10
        out['RN']     =  np.where(out['RN'] < 1e-8,  0 , out['RN'])
    
    out['PRSFC']    = inp.PRSFC                  
    out['TEMP2']    = inp.TEMP2    
    out['USTAR']    = inp.USTAR        
    out['PBL']      = inp.PBL          
    out['HFX']      = inp.HFX          
    out['LH']       = inp.LH           
    out['RGRND']    = inp.RGRND    
    out['TEMPG']    = inp.TEMPG
    out['Q2']       = inp.Q2 
    out['LAI']      = inp.LAI            
    out['SNOCOV']   = inp.SNOCOV 
    out['SEAICE']   = inp.SEAICE 
    out['SOIM1']    = inp.SOIM1     
    out['SOIM2']    = inp.SOIM2  
    out['SOIT1']    = inp.SOIT1
    out['SLTYP']    = inp.SLTYP      
    out['WR']       = inp.WR * 0.001
    out['VEG']      = inp.VEG * 0.01
    out['MOLI']     = resist['MOLI']
    out['RADYNI']   = resist['RADYNI']
    out['RSTOMI']   = resist['RSTOMI']

    return out


def metdot3D_var(inp,method,cro3D):
    
    out = {}
    
    out['UWIND']   = 1/2*(inp.U[:,:,:-1,:] + inp.U[:,:,1:,:])[:,:,:,1:-1]
    out['VWIND']   = 1/2*(inp.V[:,:,:,:-1] + inp.V[:,:,:,1:])[:,:,1:-1,:]
    
    out['UWINDC']   = inp.U[:,:,1:,1:-1]
    out['VWINDC']   = inp.V[:,:,1:-1,1:]
    
    jdenm          = cro3D['DENSA_J'] * inp.mapfac_m
    out['UHAT_JD'] = 1/2* ( (jdenm[:,:,1:,:-1] + jdenm[:,:,1:,1:])*inp.U[:,:,1:,1:-1] ) 
   
    out['VHAT_JD'] = 1/2* ( (jdenm[:,:,:-1,1:] + jdenm[:,:,1:,1:])*inp.V[:,:,1:-1,1:] )
    
    return out


def interp_z( levels, cro3D):
    
    zh, zf          = cro3D['ZH'], cro3D['ZF']
    
    zfnew           = zf[:,levels,:,:]
    zhnew           = np.zeros( zfnew.shape )
    zhnew[:,1:,:,:] = (zfnew[:,1:,:,:] + zfnew[:,:-1,:,:])/2 
    zhnew[:,0,:,:]  = zh[:,0,:,:]
    
    return zh, zf, zhnew, zfnew
   
    

def interp_levels( dic_array_3D, zhnew, zh, zfnew, zf, levels, type_file):
    
    print('starting interpolation')
    
    conv    =  {0:1} | dict( zip( levels[1:], (np.array(levels)[1:]-np.array(levels)[:-1]) ) ) # dic {level_orig_number: number of old interpolated levels}
    order   =  { hl : index for index,hl in enumerate(levels) } # dic {level_orig_number: new level number}
    i, j, k, l = zhnew.shape
    
    dic_3D = {}
    for par in dic_array_3D:
        print(par)        
        if type_file   == 'CRO': dic_3D[par] = np.zeros( ( i ,j, k, l ) )
        elif type_file == 'DOT': dic_3D[par] = np.zeros( ( i, j, k-1, l-1 ) )
       

        input_array =  dic_array_3D[par]
        
        
        if par == 'CFRAC_3D':
           for lev in order: 
               dic_3D[par][:,order[lev],:] = np.max( input_array[:,lev-(conv[lev]-1) : lev+1 , :]  , axis=1 ) # calculate maximum in joined vertical cells
        
        elif par == 'ZH':
             dic_3D[par] = zhnew
             
        elif par == 'ZF':    
             dic_3D[par] = zfnew

        else:
        
            for converted_cells in [1,2,3,4,5]: #number of interpolated vertical cells
            
                levels_sel = np.array( [x for x in conv if conv[x] == converted_cells ] )
                ord_sel    = [ order[x] for x in levels_sel]
                
                
                if par in ['QV','QC', 'QR', 'QI', 'QS', 'QG']:
                   
                    if converted_cells in [2,3,4,5]: #weight average in subset cells 
                    
                        dic_3D[par][:,ord_sel,:,:] = sum ( input_array[:,levels_sel -i,:,:] * zf[:,levels_sel-i,:,:] for i in range(0, converted_cells) ) /sum ( zf[:,levels_sel-i,:,:] for i in range(0, converted_cells) )
                     
                    else: 
                        dic_3D[par][:,ord_sel,:,:] = input_array[:,levels_sel,:,:]
                        
                else:
                
                
                    if converted_cells in [1,3,5]:
                                     
                       dic_3D[par][:,ord_sel,:] = input_array[:,levels_sel - converted_cells // 2,:] # for 1 take the original level value, for 3,5 take the middle  
                    
                    elif converted_cells in [2,4]:  # interpolation is taking
                       
                       a, b =  converted_cells // 2 -1,  converted_cells // 2
                        
                       lenght =  zh[:,levels_sel-a,:,:]     -  zh[:,(levels_sel-b),:,:]
                       l1     =  zh[:,levels_sel-a,:,:]     -  zhnew[:,ord_sel,:,:]
                       l2     = -zh[:,(levels_sel-b),:,:]   +  zhnew[:,ord_sel,:,:]   
                       
                       if type_file == 'DOT': # for DOT the wieghting parameters need to be reshaped, simple shape is using
                          lenght = lenght[:,:,1:,1:]
                          l1     = l1[:,:,1:,1:]
                          l2     = l2[:,:,1:,1:]
                       
                          # lenght = np.concatenate( (lenght[:,:,:,0][:,:,:, None], lenght), axis=3   )    
                          # lenght = np.concatenate( (lenght[:,:,0,:][:,:, None,:], lenght), axis=2   )
                               
                          # l1 = np.concatenate( (l1[:,:,:,0][:,:,:, None], l1), axis=3   )    
                          # l1 = np.concatenate( (l1[:,:,0,:][:,:, None,:], l1), axis=2   )
                            
                          # l2 = np.concatenate( (l2[:,:,:,0][:,:,:, None], l2), axis=3   )    
                          # l2 = np.concatenate( (l2[:,:,0,:][:,:, None,:], l2), axis=2   )                   
                       
                       
                       dic_3D[par][:,ord_sel,:,:]      = ( input_array[:,levels_sel - a,:,:] * l1 + input_array[:,levels_sel-b,:,:] * l2  ) / lenght
                     
                        
             
                
    return dic_3D

'''
def q_weighter( dic_array_3D, zhnew, zf, levels, type_file):
     
    conv    =  {0:1} | dict( zip( levels[1:], (np.array(levels)[1:]-np.array(levels)[:-1]) ) )
    order   =  { hl : index for index,hl in enumerate(levels) }
    i, j, k, l = zhnew.shape
   
    
    dic_3D = {}
    for par in dic_array_3D:
        
        input_array =  np.array(nc3Dfile[par])
        if type_file   == 'CRO': dic_3D[par] = np.zeros( ( i ,j, k, l ) )
        elif type_file == 'BDY': dic_3D[par] = np.zeros( ( i, j, (k+l)*2 + 4 ) )
             
        print(par)
        
        if par == 'CFRAC_3D':
           for lev in order: 
               dic_3D[par][:,order[lev],:] = np.max( input_array[:,lev-(conv[lev]-1) : lev+1 , :]  , axis=1 )
        
        else:
            for converted_cells in [1,2,3,4,5]:
            
                levels_sel = np.array( [x for x in conv if conv[x] == converted_cells ] )
                ord_sel    = [ order[x] for x in levels_sel]
                 
                if type_file == 'CRO':
                   dic_3D[par][:,ord_sel,:,:] = sum ( input_array[:,levels_sel -i,:,:] * zf[:,levels_sel-i,:,:] for i in range(0, converted_cells) ) /sum ( zf[:,levels_sel-i,:,:] for i in range(0, converted_cells) )
             
                elif type_file == 'BDY':

                   dic_3D[par][:,ord_sel,:] = sum ( input_array[:,levels_sel -i,:] * zf[:,levels_sel-i,None] for i in range(0, converted_cells) ) /sum ( zf[:,levels_sel-i,None] for i in range(0, converted_cells) )
                                        
               
    return dic_3D
'''







def interp_metcro3d(levels, cro3D,  zhnew, zfnew):
    
    
    dic_intp = {key: cro3D[key] for key in ['PRES', 'TA', 'DENSA_J', 'DENS', 'JACOBM', 'JACOBF']}
    
    dic_out = interp_levels( dic_intp, zhnew, cro3D['ZH'], zfnew, levels, 'CRO' )

    dic_out['ZH'] = zhnew
    dic_out['ZF'] = zfnew
    
    return dic_out
    
     










