#!/bin/bash

datum=$1
end=$(($3+24))
#echo ${end}
#echo ${datum}
echo 'cams postproc'
/users/p6065/anaconda3/envs/supergeo/bin/python -u /users/oko001/cmaq_oper_scripts/bc_creator/cams_post.py  $datum $2 $3 > /work/users/oko001/cmaq_oper_logs/bc_creator_logs/cams_post_${datum}_$2_$3_${end}  2>&1
echo 'bcon'
export LD_LIBRARY_PATH=/users/p6001/netcdf-fortran-4.5.2/netcdf-fortran-4.5.2-intel-netcdf4/lib:/users/p6001/netcdf-c-4.7.1/netcdf-c-4.7.1-intel-netcdf4/lib:/opt/intel/oneapi/vpl/2021.6.0/lib:/opt/intel/oneapi/tbb/2021.4.0/env/../lib/intel64/gcc4.8:/opt/intel/oneapi/mpi/2021.4.0//libfabric/lib:/opt/intel/oneapi/mpi/2021.4.0//lib/release:/opt/intel/oneapi/mpi/2021.4.0//lib:/opt/intel/oneapi/mkl/2021.4.0/lib/intel64:/opt/intel/oneapi/ippcp/2021.4.0/lib/intel64:/opt/intel/oneapi/ipp/2021.4.0/lib/intel64:/opt/intel/oneapi/dnnl/2021.4.0/cpu_dpcpp_gpu_dpcpp/lib:/opt/intel/oneapi/debugger/10.2.4/gdb/intel64/lib:/opt/intel/oneapi/debugger/10.2.4/libipt/intel64/lib:/opt/intel/oneapi/debugger/10.2.4/dep/lib:/opt/intel/oneapi/dal/2021.4.0/lib/intel64:/opt/intel/oneapi/compiler/2021.4.0/linux/lib:/opt/intel/oneapi/compiler/2021.4.0/linux/lib/x64:/opt/intel/oneapi/compiler/2021.4.0/linux/lib/emu:/opt/intel/oneapi/compiler/2021.4.0/linux/lib/oclfpga/host/linux64/lib:/opt/intel/oneapi/compiler/2021.4.0/linux/lib/oclfpga/linux64/lib:/opt/intel/oneapi/compiler/2021.4.0/linux/compiler/lib/intel64_lin:/opt/intel/oneapi/ccl/2021.4.0/lib/cpu_gpu_dpcpp

/users/oko001/cmaq_oper_scripts/CMAQ_v5.3.3_oper/bcon/run_regrid_33_$2_$3_${end}.csh $datum > /work/users/oko001/cmaq_oper_logs/bc_creator_logs/bcon_${datum}_$2_$3_${end}  2>&1
