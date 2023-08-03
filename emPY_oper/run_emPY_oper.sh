#!/bin/bash

#datum=$(date +\%Y-\%m-\%d)
datum=$1
echo $datum
echo 'emfac'
/users/p6065/anaconda3/envs/supergeo/bin/python -u /users/oko001/cmaq_oper_scripts/emPY_oper/res_heat_time_factors.py  $datum $2 $3 > /work/users/oko001/cmaq_oper_logs/emPY_logs/emfac_$datum_$2_$3  2>&1
echo 'timeva'
/users/p6065/anaconda3/envs/supergeo/bin/python -u  /users/oko001/cmaq_oper_scripts/emPY_oper/time_variation/time_variation.py $datum $2 $3 > /work/users/oko001/cmaq_oper_logs/emPY_logs/time_var_$datum_$2_$3  2>&1
