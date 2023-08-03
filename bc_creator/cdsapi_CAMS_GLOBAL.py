#!/usr/bin/env /users/p6065/anaconda3/envs/cdsapi/bin/python

import datetime
import cdsapi


datum_start = datetime.datetime(2021,1,1)
datum_end   = datetime.datetime(2021,1,31)

c = cdsapi.Client()

datum = datum_start
while datum <= datum_end :


       ds=f'{datum}'[:10]
       print(f'{ds}')
       
       c.retrieve(
            'cams-global-atmospheric-composition-forecasts',
            {
              'date': f'{ds}/{ds}',
              'type': 'forecast',
              'format': 'grib',
              'variable': [
                    'ammonium_aerosol_mass_mixing_ratio', 'carbon_monoxide', 'dust_aerosol_0.03-0.55um_mixing_ratio',
                    'dust_aerosol_0.55-0.9um_mixing_ratio', 'dust_aerosol_0.9-20um_mixing_ratio', 'ethane',
                    'formaldehyde', 'hydrogen_peroxide', 'hydrophilic_black_carbon_aerosol_mixing_ratio',
                    'hydrophilic_organic_matter_aerosol_mixing_ratio', 'hydrophobic_black_carbon_aerosol_mixing_ratio', 'hydrophobic_organic_matter_aerosol_mixing_ratio',
                    'hydroxyl_radical', 'isoprene', 'methane',
                    'nitrate_coarse_mode_aerosol_mass_mixing_ratio', 'nitrate_fine_mode_aerosol_mass_mixing_ratio', 'nitric_acid',
                    'nitrogen_dioxide', 'nitrogen_monoxide', 'ozone',
                    'peroxyacetyl_nitrate', 'propane', 'sea_salt_aerosol_0.03-0.5um_mixing_ratio',
                    'sea_salt_aerosol_0.5-5um_mixing_ratio', 'sea_salt_aerosol_5-20um_mixing_ratio', 'sulphate_aerosol_mixing_ratio',
                    'sulphur_dioxide',
              ],
              'model_level': [
                  '24', '45',
                  '57', '62', '65',
                  '67', '72', '77',
                  '82', '87', '92',
                  '97', '102', '107',
                  '110', '113', '115',
                  '116', '117', '118',
                  '119', '120', '121',
                  '122', '123', '124',
                  '125', '126', '127',
                  '128', '129', '130',
                  '131', '132', '133',
                  '134', '135', '136',
                  '137',
              ],
              'time': '00:00',
              'leadtime_hour': [
                  '0', '3', '6',
                  '9', '12', '15',
                  '18', '21', '24',
              ],
              'area': [
                    55, 10, 40,
                    30,
              ],
            },
            f'/data/users/oko001/CAMS_DATA/download_{ds}_mod.grib')

       datum += datetime.timedelta(days=1)

