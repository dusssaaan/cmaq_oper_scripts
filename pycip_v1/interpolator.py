#!/usr/bin/env /users/p6065/anaconda3/envs/supergeo/bin/python
# -*- coding: utf-8 -*-
"""
Created on Thu May 25 06:55:46 2023

@author: p6001
"""
#import xarray as xr
#import matplotlib.pyplot as plt
import numpy as np
import netCDF4
import datetime
#%%
def interp_levels( parameters, nc3Dfile, zhnew, zh, levels, type_file):
    
    print('starting interpolation')
    
    conv    =  {0:1} | dict( zip( levels[1:], (np.array(levels)[1:]-np.array(levels)[:-1]) ) )
    order   =  { hl : index for index,hl in enumerate(levels) }
    i, j, k, l = zhnew.shape
    
    dic_3D = {}
    for par in parameters:
        print(par)        
        if type_file   == 'CRO': dic_3D[par] = np.zeros( ( i ,j, k, l ) )
        elif type_file == 'DOT': dic_3D[par] = np.zeros( ( i, j, k+1, l+1 ) )
        elif type_file == 'BDY': dic_3D[par] = np.zeros( ( i, j, (k+l)*2 + 4 ) )

        input_array =  np.array(nc3Dfile[par])
        for converted_cells in [1,2,3,4,5]:
        
            levels_sel = np.array( [x for x in conv if conv[x] == converted_cells ] )
            ord_sel    = [ order[x] for x in levels_sel]
            
            if converted_cells in [1,3,5]:
                             
               dic_3D[par][:,ord_sel,:] = input_array[:,levels_sel - converted_cells // 2,:]
            
            elif converted_cells in [2,4]:  
               
               a, b =  converted_cells // 2 -1,  converted_cells // 2
                
               lenght =  zh[:,levels_sel-a,:,:]     -  zh[:,(levels_sel-b),:,:]
               l1     =  zh[:,levels_sel-a,:,:]     -  zhnew[:,ord_sel,:,:]
               l2     = -zh[:,(levels_sel-b),:,:]   +  zhnew[:,ord_sel,:,:]   
               
               if type_file == 'DOT':
                  
                  lenght = np.concatenate( (lenght[:,:,:,0][:,:,:, None], lenght), axis=3   )    
                  lenght = np.concatenate( (lenght[:,:,0,:][:,:, None,:], lenght), axis=2   )
                       
                  l1 = np.concatenate( (l1[:,:,:,0][:,:,:, None], l1), axis=3   )    
                  l1 = np.concatenate( (l1[:,:,0,:][:,:, None,:], l1), axis=2   )
                    
                  l2 = np.concatenate( (l2[:,:,:,0][:,:,:, None], l2), axis=3   )    
                  l2 = np.concatenate( (l2[:,:,0,:][:,:, None,:], l2), axis=2   )
                    
               if type_file == 'BDY':
                   
                  lenght = lenght.mean(axis=(2,3)) 
                  l1     = l1.mean(axis=(2,3))  
                  l2     = l2.mean(axis=(2,3))
                  
                  dic_3D[par][:,ord_sel,:]      = ( input_array[:,levels_sel - a,:] * l1[:,:,None] + input_array[:,levels_sel-b,:] * l2[:,:,None]  ) / lenght[:,:,None]
               
               else : 
                
                  dic_3D[par][:,ord_sel,:,:]      = ( input_array[:,levels_sel - a,:,:] * l1 + input_array[:,levels_sel-b,:,:] * l2  ) / lenght
               
               
    return dic_3D
#%%
def q_weighter( parameters,nc3Dfile, zhnew, zf, levels, type_file):
     
    conv    =  {0:1} | dict( zip( levels[1:], (np.array(levels)[1:]-np.array(levels)[:-1]) ) )
    order   =  { hl : index for index,hl in enumerate(levels) }
    i, j, k, l = zhnew.shape
   
    if type_file   == 'BDY': zf = zf.mean( axis=(2,3) )
    
    dic_3D = {}
    for par in parameters:
        
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
#%%

#%%
levels = [0,1,2,3,4,6,8,11,14,17,21,24] +[27,30,33,36,39,43,46,50] + [55, 58, 61, 63, 65, 67, 69, 71, 72,73, 75,76,77]


#start datum
datum_start=datetime.datetime(2023,7,6,0)

#end day
datum_end=datetime.datetime(2023,7,6,0)


input_dir = '/data/oko/dusan/mcip_kosymoko_2km_2022/'
output_dir = '/data/oko/dusan/mcip_kosymoko_2km_2022_33/'
param_int = ['PRES', 'TA', 'DENSA_J', 'DENS', 'JACOBM', 'JACOBF']
param_wei = ['QV', 'CFRAC_3D', 'QC', 'QR', 'QI', 'QS', 'QG'] 
param_dot = ['UWIND', 'VWIND', 'UWINDC', 'VWINDC', 'UHAT_JD', 'VHAT_JD']    
    

datum = datum_start
while datum <= datum_end :
      
      cro3d_path = f'{input_dir}/METCRO3D_PYCIP-{datum.isoformat()[:-9]}.nc'
      bdy3d_path = f'{input_dir}/METBDY3D_PYCIP-{datum.isoformat()[:-9]}.nc'
      dot3d_path = f'{input_dir}/METDOT3D_PYCIP-{datum.isoformat()[:-9]}.nc'
      
      with netCDF4.Dataset(cro3d_path) as cro3d, netCDF4.Dataset(dot3d_path) as dot3d, netCDF4.Dataset(bdy3d_path) as bdy3d:
                    
            print('zaciatok')
            zh              = np.array(cro3d['ZH'])
            zf              = np.array(cro3d['ZF']) 
            zfnew           = zf[:,levels,:,:]
            zhnew           = np.zeros( zfnew.shape )
            zhnew[:,1:,:,:] = (zfnew[:,1:,:,:] + zfnew[:,:-1,:,:])/2 
            zhnew[:,0,:,:]  = zh[:,0,:,:]
            
            zhbdy              = np.array(bdy3d['ZH'])
            zfbdy              = np.array(bdy3d['ZF']) 
            zfnewbdy           = zfbdy[:,levels,:]
            zhnewbdy           = np.zeros( zfnewbdy.shape )
            zhnewbdy[:,1:,:] = (zfnewbdy[:,1:,:] + zfnewbdy[:,:-1,:])/2 
            zhnewbdy[:,0,:]  = zhbdy[:,0,:]
            
            print('inter')
  
            int_cro = interp_levels(param_int, cro3d, zhnew, zh, levels,'CRO')    
            int_dot = interp_levels(param_dot, dot3d, zhnew, zh, levels,'DOT')
            int_bdy = interp_levels(param_int, bdy3d, zhnew, zh, levels,'BDY')    
      
            wei_cro = q_weighter(param_wei, cro3d, zhnew, zf, levels,'CRO')
            wei_bdy = q_weighter(param_wei, bdy3d, zhnew, zf, levels,'BDY')  
            
            vgvals  = cro3d.VGLVLS[levels]
            number_layers = vgvals.shape[0]

            print('koniec citania')                         
            for out_file_name in ['METBDY3D_PYCIP-','METCRO3D_PYCIP-','METDOT3D_PYCIP-']:
                
                              
                print(datum, out_file_name)
                with netCDF4.Dataset(f'{output_dir}/{out_file_name}{datum.isoformat()[:-9]}.nc',mode='w') as out:
                
                
                    if   out_file_name[3:8] == 'CRO3D' : inputs = cro3d
                    elif out_file_name[3:8] == 'DOT3D' : inputs = dot3d
                    elif out_file_name[3:8] == 'BDY3D' : inputs = bdy3d
            
                   # copy global atributes
        
                    for name in inputs.ncattrs():
                        
                        out.setncattr(name, inputs.getncattr(name))
                        
                        
                    out.setncattr('VGLVLS', vgvals) 
                    out.setncattr('NLAYS',  np.int32(len(levels))) 
                    
                    for name, dimension in inputs.dimensions.items():
                        
                        if name != 'LAY':
        
                           out.createDimension(name, size=len(inputs.dimensions[name]) if not dimension.isunlimited() else None)
                        
                        else:
                           
                          out.createDimension('LAY', size=number_layers)
                    
                    for name, var in inputs.variables.items():
                        
                        print(name,out_file_name[3:8] )
                        
                        out.createVariable(name, var.dtype, var.dimensions,fill_value=None)
                        out.variables[name].setncatts({a:var.getncattr(a) for a in var.ncattrs()})
                    
                        if name == 'TFLAG':
                            
                           out.variables[name][:] = inputs.variables[name][:]
                           
                        elif name == 'ZH':
                           
                           if    out_file_name[3:8] == 'BDY3D' : out.variables[name][:] = zhnewbdy
                           elif  out_file_name[3:8] == 'CRO3D' : out.variables[name][:] = zhnew 
  
                        elif name == 'ZF':
                            
                            if    out_file_name[3:8] == 'BDY3D' : out.variables[name][:] = zfnewbdy
                            elif  out_file_name[3:8] == 'CRO3D' : out.variables[name][:] = zfnew 

                        elif out_file_name[3:8] == 'CRO3D' : 
                           if name in param_int:
                                out.variables[name][:] = int_cro[name]
                           elif name in param_wei:
                                out.variables[name][:] = wei_cro[name]
                            
                        elif out_file_name[3:8] == 'BDY3D' : 
                             if name in param_int:
                                  out.variables[name][:] = int_bdy[name]
                             elif name in param_wei:
                                  out.variables[name][:] = wei_bdy[name]
                        
                        elif out_file_name[3:8] == 'DOT3D' : 
                             
                             out.variables[name][:] = int_dot[name]
          
    
      datum += datetime.timedelta(days=1)








"""

levels_19 = xr.open_dataset('/data/users/oko001/mcip_out_2021/METCRO3D_2021-01-03.nc')
levels_86 = xr.open_dataset('/data/oko/dusan/mcip_kosymoko_2km_87/METCRO3D_PYCIP-2021-01-03.nc')
levels_wrf = xr.open_dataset('/data/users/p6001/mcip_wrf_1/METCRO3D_2021-01-03.nc')



t,i,j =10, 150, 200
vyska_19  = levels_19['ZH'].data[t,:,i,j]
vyska_86  = levels_86['ZH'].data[t,:,i,j]
vyska_wrf = levels_wrf['ZH'].data[t,:,i,j]

plt.plot(vyska_19,'*')
plt.plot(vyska_86,'*')




vyska_19t = levels_19['TA'].data[t,:,i,j]
vyska_86t = levels_86['TA'].data[t,:,i,j]


plt.scatter( vyska_19t, vyska_19 )
plt.scatter( vyska_86t, vyska_86, alpha = 0.2 )



for var in levels_86.variables:
    if var != 'TFLAG':
        
       plt.scatter( levels_19[var].data[t,:,i,j], vyska_19, label = f'{var}; 19' )
       plt.scatter( levels_86[var].data[t,:-6,i,j], vyska_86[:-6], alpha = 0.2 ) 
       plt.scatter( levels_wrf[var].data[t,:,i,j], vyska_wrf ) 
       plt.legend()
       plt.show()
       plt.close()



levels_19dot = xr.open_dataset('/data/users/oko001/mcip_out_2021/METDOT3D_2021-01-03.nc')
levels_86dot = xr.open_dataset('/data/oko/dusan/mcip_kosymoko_2km_87/METDOT3D_PYCIP-2021-01-03.nc')
levels_wrfdot = xr.open_dataset('/data/users/p6001/mcip_wrf_1/METDOT3D_2021-01-03.nc')

#%%
v = 6
for var in levels_86dot.variables:
    if var != 'TFLAG':
        
       plt.scatter( levels_19dot[var].data[t,:,i,j], vyska_19, label = f'{var}; 19' )
       plt.scatter( levels_86dot[var].data[t,:-v,i,j], vyska_86[:-v], alpha = 0.2 ) 
       plt.scatter( levels_wrfdot[var].data[t,:,i,j], vyska_wrf ) 
       plt.legend()
       plt.show()
       plt.close()


plt.scatter(vyska_86[:-7],vyska_86[:-7])
plt.scatter(vyska_wrf,vyska_wrf)







plt.scatter(vyska_86[:10],vyska_86[:10])
plt.scatter(vyska_wrf[5:10],vyska_wrf[5:10])

#%%

############################################
# vyber spodnych hladin
############################################
hladiny = [0,1,2,3,4,6,8,11,14,17,21,24]

plt.plot(vyska_86[:25], np.arange(0,25), '*')
plt.plot(vyska_wrf[:10],np.arange(0,10), '*')
plt.plot(vyska_86[hladiny],np.arange(0,len(hladiny)), '*')

#%%
hladiny = [27,30,33,36,39,43,46,50]
plt.plot(vyska_86[25:50], np.arange(0,50 - 25), '*')
plt.plot(vyska_wrf[10:17],np.arange(0,17 - 10), '*')
plt.plot(vyska_86[hladiny],np.arange(0,len(hladiny)), '*', color='black')

#%%
hladiny =  [55, 58, 61, 63, 65, 67, 69, 71, 72,73, 75,76,77]
plt.plot(vyska_86[50:81], np.arange(0,81 - 50), '*')
plt.plot(vyska_wrf[18:],np.arange(0,31-18), '*')
plt.plot(vyska_86[hladiny],np.arange(0,len(hladiny)), '*', color='black')
#%% 33 hladin
hladiny = [0,1,2,3,4,6,8,11,14,17,21,24] +[27,30,33,36,39,43,46,50] + [55, 58, 61, 63, 65, 67, 69, 71, 72,73, 75,76,77]
plt.plot(vyska_86, np.arange(0,len(vyska_86)), '*')
plt.plot(vyska_wrf,np.arange(0,len(vyska_wrf)), '*')
plt.plot(vyska_86[hladiny],np.arange(0,len(hladiny)), '*', color='black')
#%%

levels_86['DENS'].data[t,hladiny,i,j]

#%%
for var in levels_86.variables:
    if var != 'TFLAG':
        
       plt.scatter( levels_19[var].data[t,:,i,j], vyska_19, label = f'{var}; 19' )
       plt.scatter( levels_86[var].data[t,hladiny,i,j], vyska_86[hladiny],color='black' ) 
       plt.scatter( levels_wrf[var].data[t,:,i,j], vyska_wrf, alpha = 0.5 ) 
       plt.legend()
       plt.show()
       plt.close()
#%%



(levels_wrf['ZF'][5,1:,10,11]+levels_wrf['ZF'][5,:-1,10,11])/2

levels_wrf['ZH'][5,:,10,11]

levels_wrf['ZF'][5,:,10,11]


def interp(zf): return zf
    


zfnew = levels_86['ZF'][:,hladiny,:,:].data

zhnew = np.zeros( zfnew.shape   )
zhnew[:,1:,:,:] = (zfnew[:,1:,:,:] + zfnew[:,:-1,:,:])/2 
zhnew[:,0,:,:] = levels_86['ZH'][:,0,:,:].data 

#%%
for i,j in enumerate(hladiny[:]):
   
    print( i,j, np.max( np.abs( zhnew[:,i,:,:] -  levels_86['ZH'][:,j,:,:]    )  ).data )

#%%

for i,j in enumerate(hladiny[:]):
    
    if j != i :
        
       print(i,j, hladiny[i], hladiny[i-1] ) 
    
    
       if hladiny[i] - hladiny[i-1] == 2 :
           
          print('dve vynechane')
      
       
       if hladiny[i] - hladiny[i-1] == 3 :
           
          print('tri vynechane')
        
       
       if hladiny[i] - hladiny[i-1] == 4 :
            
           print('styri vynechane')  
        
      
    print('######')
    
#%%
konvertor    =  {0:1} | dict( zip( hladiny[1:], (np.array(hladiny)[1:]-np.array(hladiny)[:-1]) ) )
poradie      =  { hl : index for index,hl in enumerate(hladiny) }
zh           = levels_86['ZH'].data


hladiny_no_int = [x for x in konvertor if konvertor[x] == 1 ]


dic_3D_cro = {}
dic_3D_cro['TA'] = np.zeros(zhnew.shape)

por_no_int = [ poradie[x] for x in hladiny_no_int]
dic_3D_cro['TA'][:,por_no_int,:,:] = levels_86['TA'][:,hladiny_no_int,:,:]
#------------------------------------------------------------------------------

hladiny_2_stp = np.array([x for x in konvertor if konvertor[x] == 2 ])
por_2_stp = [ poradie[x] for x in hladiny_2_stp]

lenght =  zh[:,hladiny_2_stp,:,:]     -  zh[:,(hladiny_2_stp-1),:,:]
l1     =  zh[:,hladiny_2_stp,:,:]     -  zhnew[:,por_2_stp,:,:]
l2     = -zh[:,(hladiny_2_stp-1),:,:] +  zhnew[:,por_2_stp,:,:]   
dic_3D_cro['TA'][:,por_2_stp,:,:]      = ( levels_86['TA'][:,hladiny_2_stp,:,:] * l1 + levels_86['TA'][:,(hladiny_2_stp-1),:,:] * l2  ) / lenght

#------------------------------------------------------------------------------    
hladiny_3_stp = np.array([x for x in konvertor if konvertor[x] == 3 ])
por_3_stp = [ poradie[x] for x in hladiny_3_stp]
#skuska = (zh[:,(hladiny_3_stp-1),:,:] > zhnew[:,por_3_stp,:,:])

dic_3D_cro['TA'][:,por_3_stp,:,:]  =  levels_86['TA'][:,hladiny_3_stp-1,:,:]

#------------------------------------------------------------------------------
hladiny_5_stp = np.array([x for x in konvertor if konvertor[x] == 5 ])
por_5_stp = [ poradie[x] for x in hladiny_5_stp]    
skuska = (zh[:,(hladiny_5_stp-2),:,:] - zhnew[:,por_5_stp,:,:])

dic_3D_cro['TA'][:,por_5_stp,:,:]  =  levels_86['TA'][:,hladiny_5_stp-2,:,:]

#------------------------------------------------------------------------------
hladiny_4_stp = np.array([x for x in konvertor if konvertor[x] == 4 ])
por_4_stp = [ poradie[x] for x in hladiny_4_stp]
lenght =  zh[:,hladiny_4_stp-1,:,:]   -  zh[:,(hladiny_4_stp-2),:,:]    
l1     =  zh[:,(hladiny_4_stp-1),:,:] -  zhnew[:,por_4_stp,:,:]
l2     = -zh[:,(hladiny_4_stp-2),:,:] +  zhnew[:,por_4_stp,:,:]

dic_3D_cro['TA'][:,por_4_stp,:,:]  = ( levels_86['TA'][:,hladiny_4_stp - 1,:,:] * l1 + levels_86['TA'][:,(hladiny_4_stp - 2),:,:] * l2  ) / lenght
#%%    
    
var = 'TA'    
plt.scatter( dic_3D_cro['TA'][t,:,i,j], zhnew[t,:,i,j],color='blue')    
plt.scatter( levels_86[var].data[t,hladiny,i,j], vyska_86[hladiny],color='black',alpha =0.5 )    
    
    
    
    
    
    
#%%    
    



#%%  
hladiny = [0,1,2,3,4,6,8,11,14,17,21,24] +[27,30,33,36,39,43,46,50] + [55, 58, 61, 63, 65, 67, 69, 71, 72,73, 75,76,77]
zh           = levels_86['ZH'].data 
zfnew = levels_86['ZF'][:,hladiny,:,:].data
zhnew = np.zeros( zfnew.shape   )
zhnew[:,1:,:,:] = (zfnew[:,1:,:,:] + zfnew[:,:-1,:,:])/2 
zhnew[:,0,:,:] = levels_86['ZH'][:,0,:,:].data    



param = ['PRES', 'TA', 'DENSA_J', 'DENS', 'JACOBM', 'JACOBF']

por = interp_levels(param, levels_86, zhnew, zh, hladiny,'CRO')    


others = ['QV', 'CFRAC_3D', 'QC', 'QR', 'QI', 'QS', 'QG'] 
#%%    
for var in param:
    
        
       plt.scatter( por[var][t,:,i,j], zhnew[t,:,i,j],color='yellow', alpha=0.5,label=f'{var}')
       plt.scatter( levels_86[var].data[t,hladiny,i,j], vyska_86[hladiny],color='black' ) 
       
       plt.legend()
       plt.show()
       plt.close()



#%%    
    
param_dot = ['UWIND', 'VWIND', 'UWINDC', 'VWINDC', 'UHAT_JD', 'VHAT_JD']    
    
por2 = interp_levels(param_dot, levels_86dot, zhnew, zh, hladiny, type_file = 'DOT')       
    
#%%    

for var in param_dot:
    
        
       plt.scatter( por2[var][t,:,i,j], zhnew[t,:,i,j],color='black', label=f'{var}')
       plt.scatter( levels_86dot[var].data[t,hladiny,i,j], vyska_86[hladiny],color='blue', alpha=0.5 ) 
       
       plt.legend()
       plt.show()
       plt.close()

    
#%%   

def q_weighter( parameters,nc3Dfile, zhnew, zf, levels, type_file):
     
    conv    =  {0:1} | dict( zip( levels[1:], (np.array(levels)[1:]-np.array(levels)[:-1]) ) )
    order   =  { hl : index for index,hl in enumerate(levels) }
    i, j, k, l = zhnew.shape
   
    if type_file   == 'BDY': zf = zf.mean( axis=(2,3) )
    
    dic_3D = {}
    for par in parameters:
        
        if type_file   == 'CRO': dic_3D[par] = np.zeros( ( i ,j, k, l ) )
        elif type_file == 'BDY': dic_3D[par] = np.zeros( ( i, j, (k+l)*2 + 4 ) )
             
        print(par)
        
        if par == 'CFRAC_3D':
           for lev in order: 
               dic_3D[par][:,order[lev],:] = np.max( nc3Dfile[par][:,lev-(conv[lev]-1) : lev+1 , :]  , axis=1 )
        
        else:
            for converted_cells in [1,2,3,4,5]:
            
                levels_sel = np.array( [x for x in conv if conv[x] == converted_cells ] )
                ord_sel    = [ order[x] for x in levels_sel]
                 
                if type_file == 'CRO':
                   dic_3D[par][:,ord_sel,:,:] = sum ( nc3Dfile[par][:,levels_sel -i,:,:] * zf[:,levels_sel-i,:,:] for i in range(0, converted_cells) ) /sum ( zf[:,levels_sel-i,:,:] for i in range(0, converted_cells) )
             
                elif type_file == 'BDY':

                   dic_3D[par][:,ord_sel,:] = sum ( nc3Dfile[par][:,levels_sel -i,:] * zf[:,levels_sel-i,None] for i in range(0, converted_cells) ) /sum ( zf[:,levels_sel-i,None] for i in range(0, converted_cells) )
                                        
               
    return dic_3D

#%%
skuska = q_weighter( others,levels_86, zhnew, levels_86['ZF'].data, hladiny)
#%%


for var in others:
    
        
       plt.scatter(skuska[var][t,:,i,j], zhnew[t,:,i,j],color='green', label=f'{var} max= {skuska[var].max()}',alpha=0.5)
       plt.scatter( levels_86[var].data[t,:,i,j], vyska_86,marker='.',color='black', label=f'{var} max= {levels_86[var].data.max() }' ) 
       plt.ylim(0,5000)
       plt.legend()
       plt.show()
       plt.close()


#%%
levels_19bdy   = xr.open_dataset('/data/users/oko001/mcip_out_2021/METBDY3D_2021-01-02.nc')
levels_86bdy   = xr.open_dataset('/data/oko/dusan/mcip_kosymoko_2km_87/METBDY3D_PYCIP-2021-01-01.nc')
levels_wrfbdy  = xr.open_dataset('/data/users/p6001/mcip_wrf_1/METBDY3D_2021-01-01.nc')


por3 = interp_levels(param, levels_86bdy, zhnew, zh, hladiny, type_file = 'BDY')

#%%
for var in param:
        
       plt.scatter( por3[var][t,:,500], zhnew[t,:,i,j],color='yellow', alpha=0.5,label=f'{var}')
       plt.scatter( levels_86bdy[var].data[t,hladiny,500], vyska_86[hladiny],color='black' ) 
       
       plt.legend()
       plt.show()
       plt.close()
#%%
skuska2 = q_weighter( others,levels_86bdy, zhnew, levels_86['ZF'].data, hladiny,'BDY')

#%%

for var in others:
    
        
       plt.scatter(skuska2[var][t,:,500], zhnew[t,:,i,j],color='green', label=f'{var} max= {skuska2[var].max()}',alpha=0.5)
       plt.scatter( levels_86bdy[var].data[t,:,500], vyska_86,marker='.',color='black', label=f'{var} max= {levels_86[var].data.max() }' ) 
       plt.ylim(0,5000)
       plt.legend()
       plt.show()
       plt.close()

"""





