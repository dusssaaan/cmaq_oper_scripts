d={}

input_path = '/data/users/oko001/cmaq_oper_data/static_and_default_files/input_emPY/'

# TNO bez SK, plosne

d['TNO_SK_2015_A']={
'source_type':'A',
'type':'csv',
'input_file': input_path + 'TNO_2015_A',
'sep':';',
'encoding':'utf-8',
'cat_internal':'SNAP',
'x':'Lon',
'y':'Lat',
'grid_dx':0.125,
'grid_dy':0.0625,
'filter':["ISO3 != 'SVK'"],
'EPSG':4326,
'new_pollutants':'NO2= 0.05*NOX, NO= 0.652*NOX-0.652*NO2, BZN=0.016*NMVOC, NMBVOC=NMVOC-BZN',
'def_emis':{'NO2': 'NO2', 'NO': 'NO','BZN':'BZN','CO': 'CO', 'SO2': 'SO2', 'PM_CRS': 'PMC', 'PM2_5_EC': 'PEC', 'PM2_5_OC': 'POC', 'PM2_5_NA': 'PNA', 'PM2_5_SO4': 'PSO4', 'PM2_5_OTHR': 'PMOTHR', 'NBMVOC': 'NMBVOC', 'CH4': 'CH4', 'NH3': 'NH3'},
'emission_inventory':{1: 1010, 2: 1020, 34: 1040, 5: 1050, 6: 1060, 71: 1071, 72: 1072, 73: 1073, 74: 1074, 75: 1075, 8: 1080, 9: 1090, 10: 1100},
'units':'tonne/year',
 }

# TNO bez SK, bodove

d['TNO_SK_2015_P']={
'source_type':'P',
'type':'csv',
'input_file': input_path + 'TNO_2015_P',
'sep':';',
'encoding':'utf-8',
'cat_internal':'SNAP',
'x':'Lon',
'y':'Lat',
'def_heights':False,
'ID': 'ID',
'filter':["ISO3 != 'SVK'"],
'EPSG':4326,
'new_pollutants':'NO2= 0.05*NOX, NO= 0.652*NOX-0.652*NO2, BZN=0.016*NMVOC, NMBVOC=NMVOC-BZN',
'def_emis':{'NO2': 'NO2', 'NO': 'NO','BZN':'BZN','CO': 'CO', 'SO2': 'SO2', 'PM_CRS': 'PMC', 'PM2_5_EC': 'PEC', 'PM2_5_OC': 'POC', 'PM2_5_NA': 'PNA', 'PM2_5_SO4': 'PSO4', 'PM2_5_OTHR': 'PMOTHR', 'NBMVOC': 'NMBVOC', 'CH4': 'CH4', 'NH3': 'NH3'},
'emission_inventory':{1: 1010, 34: 1040, 5: 1050, 8: 1080, 9: 1090, 10: 1100},
'units':'tonne/year',
 }

# polnohosp. emisie
# plosne
d['pol_v1']={
'source_type':'A',
'type':'csv',
'input_file': input_path + 'polnohosp_plosne_uniform',
'sep':',',
'encoding':'utf-8',
'one_cat':2100,
'x':'x',
'y':'y',
'grid_dx':100,
'grid_dy':100,
'EPSG':3035,
'new_pollutants':'NO2= 0.05*NOX, NO= 0.652*NOX-0.652*NO2, BZN=0.016*NMVOC, NMBVOC=NMVOC-BZN,PMC=PM10-PM2_5',
'def_emis':{'NH3': 'NH3', 'NMVOC': 'NMVOC','NOX':'NOX','PM25': 'PM2_5','PM10': 'PM10','CH4': 'CH4','CO': 'CO' },
'units':'tonne/year',
 }
# ako body druzstva
d['pol_point']={
'source_type':'P',
'type':'shape',
'one_cat':2100,
'def_heights':'zero',
'shape_file': input_path + 'polnohosp_zbgis/zbgis_emisie.shp',
'def_emis':{'NH3': 'NH3', 'NMVOC': 'NMVOC','NOX':'NOX','PM25': 'PM2_5','PM10': 'PM10','CH4': 'CH4','CO': 'CO' },
'new_pollutants':'NO2= 0.05*NOX, NO= 0.652*NOX-0.652*NO2, BZN=0.016*NMVOC, NMBVOC=NMVOC-BZN,PMC=PM10-PM2_5',
'units':'tonne/year',
 }

# neuplne kominy, nahradit, chyba napr NMVOC 
d['kominy_2022']={
'source_type':'P',
'type':'csv',
'input_file':input_path + 'kominy_cmaq_2022_v1',
'sep':',',
'encoding':'utf-8',
'cat_internal':'SNAP',
'x':'lon_dom',
'y':'lat_dom',
'def_heights':True,
'ID': 'N',
'EPSG':4326,
'new_pollutants':'NO2= 0.05*NOX, NO= 0.652*NOX-0.652*NO2,PMC=PM10-PM2_5',
'def_emis':{'nox': 'NOX','benzen':'BZN','co': 'CO', 'so2': 'SO2', 'PM10 (t)': 'PM10','PM2,5 (t)': 'PM2_5'},
'emission_inventory':{1: 2010},
'units':'tonne/year',
'height': 'Vyska',
'diameter': 'stack diameter',
'temperature': 'TeplotaSpalin',
'velocity': 'RychlostSpalin',
 }


# CDV

d['CDV_2019_new']={
'source_type':'L',
'shape_file': input_path + 'shape_doprv_zjed_2020/shape_doprv_zjed_2020.shp',
'one_cat':2070,
'def_emis':{'BaP': 'BAP','NO2':'NO2', 'NO':'NO', 'PM10':'PM10','PM2':'PM2_5','Benzen':'BZN','SO2':'SO2','NMVOC':'NMVOC', 'NH3':'NH3','CO':'CO'},
'new_pollutants':'CH4=0.06*NMVOC, NMBVOC=NMVOC-CH4, PMC = PM10 - PM2_5',
'units':'kg/year',
}

# kureniska

d['SVK_resHeat_15_85']={
'source_type':'A',
'type':'csv+shape',
'input_file': input_path + 'SK_2015_resHeat_N15-L85_all_fuels_NA_SO4_FPRM.csv',
'shape_file': input_path + 'geom/Slovakia_zastavane2.shp',
'sep':';',
'encoding':'utf-8',
'cat_internal':'SRC_TYPE',
'source_id':'ZSJ',
'shape_id':'ZSJ_ID',
'def_emis':{'SO2_g': 'SO2', 'NH3_g': 'NH3', 'CH4_g': 'CH4', 'CO_g': 'CO', 'NOX_g': 'NOX', 'NMVOC_g': 'NMVOC', 'C6H6_g': 'BZN', 'BAP_mg': 'BAP', 'PM10_g': 'PM10', 'PM2_5_g': 'PM2_5', 'BC_g': 'PEC', 'OC_g': 'POC', 'NA_g': 'PNA', 'SO4_g': 'PSO4'},
'new_pollutants':'NMBVOC=NMVOC-BZN, PMC = PM10 - PM2_5, PMOTHR = PM2_5-PEC-POC-PNA-PSO4,NO2= 0.05*NOX, NO= 0.652*NOX-0.652*NO2',
'emission_inventory':{202020101: 2021, 2020202: 2022, 202020301: 2023, 202020302: 2023, 202020303: 2023, 202020304: 2023, 202020401: 2024},
'units':'g/year',
 }

