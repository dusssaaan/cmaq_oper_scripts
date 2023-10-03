#!/bin/csh -f

# ======================= BCONv5.3.X Run Script ======================== 
# Usage: run.bcon.csh >&! bcon.log &                                
#
# To report problems or request help with this script/program:        
#             http://www.cmascenter.org
# ==================================================================== 

# ==================================================================
#> Runtime Environment Options
# ==================================================================

#> Choose compiler and set up CMAQ environment with correct 
#> libraries using config.cmaq. Options: intel | gcc | pgi
 setenv compiler intel 

/users/oko001/cmaq_oper_scripts/CMAQ_v5.3.3_oper/bcon
#> Set General Parameters for Configuring the Simulation
 set VRSN     = v532                    #> Code Version
 set APPL     = reg_00_0_24             #> Application Name
 set BCTYPE   = regrid                  #> Boundary condition type [profile|regrid]
 set compilerString = intel 

#> Set the build directory:
 set BLD      = /users/oko001/cmaq_oper_scripts/CMAQ_v5.3.3_oper/bcon/BLD_BCON_${VRSN}_${compilerString}
 set EXEC     = BCON_${VRSN}.exe  
 cat $BLD/BCON_${VRSN}.cfg; echo " "; set echo
 
 setenv INPDIR  /data/users/oko001/cmaq_oper_data/
#> Horizontal grid definition 
 setenv GRID_NAME ala2km_87               #> check GRIDDESC file for GRID_NAME options
#setenv GRIDDESC $CMAQ_DATA/$APPL/met/mcip/GRIDDESC #> grid description file 
 setenv GRIDDESC ${INPDIR}/static_and_default_files/GRIDDESC_2km
 setenv IOAPI_ISPH 20                     #> GCTP spheroid, use 20 for WRF-based modeling

#> I/O Controls
 setenv IOAPI_LOG_WRITE F     #> turn on excess WRITE3 logging [ options: T | F ]
 setenv IOAPI_OFFSET_64 YES   #> support large timestep records (>2GB/timestep record) [ options: YES | NO ]
 setenv EXECUTION_ID $EXEC    #> define the model execution id

# =====================================================================
#> BCON Configuration Options
#
# BCON can be run in one of two modes:                                     
#     1) regrids CMAQ CTM concentration files (BC type = regrid)     
#     2) use default profile inputs (BC type = profile)
# =====================================================================

 setenv BCON_TYPE ` echo $BCTYPE | tr "[A-Z]" "[a-z]" `

# =====================================================================
#> Input/Output Directories
# =====================================================================

 set OUTDIR   = /data/users/oko001/cmaq_oper_data/bcon_files/       #> output file directory

# =====================================================================
#> Input Files
#  
#  Regrid mode (BC = regrid) (includes nested domains, windowed domains,
#                             or general regridded domains)
#     CTM_CONC_1 = the CTM concentration file for the coarse domain          
#     MET_CRO_3D_CRS = the MET_CRO_3D met file for the coarse domain
#     MET_BDY_3D_FIN = the MET_BDY_3D met file for the target nested domain
#                                                                            
#  Profile mode (BC type = profile)
#     BC_PROFILE = static/default BC profiles 
#     MET_BDY_3D_FIN = the MET_BDY_3D met file for the target domain 
#
# NOTE: SDATE (yyyyddd), STIME (hhmmss) and RUNLEN (hhmmss) are only 
#       relevant to the regrid mode and if they are not set,  
#       these variables will be set from the input MET_BDY_3D_FIN file
# =====================================================================
#> Output File
#     BNDY_CONC_1 = gridded BC file for target domain
# =====================================================================
 
    set DATE = $1
    set YYYYJJJ  = `date -ud "${DATE}" +%Y%j`   #> Convert YYYY-MM-DD to YYYYJJJ
    set YYMMDD   = `date -ud "${DATE}" +%y%m%d` #> Convert YYYY-MM-DD to YYMMDD
    set YYYYMMDD = `date -ud "${DATE}" +%Y%m%d` #> Convert YYYY-MM-DD to YYYYMMDD
#   setenv SDATE           ${YYYYJJJ}
#   setenv STIME           000000
#   setenv RUNLEN          240000

 if ( $BCON_TYPE == regrid ) then 
    setenv CTM_CONC_1     ${INPDIR}/bcon_files/CONC_CAMS_POST_33_${DATE}_00_0_24.nc
    setenv MET_CRO_3D_CRS ${INPDIR}/mcip_files/METCRO3D_PYCIP-${DATE}_00_for_0+24.nc #/work/MOD3DATA/2016_12US1/met/mcip_v43_wrf_v381_ltng/METCRO3D.12US1.35L.${YYMMDD}
    setenv MET_BDY_3D_FIN ${INPDIR}/mcip_files/METBDY3D_PYCIP-${DATE}_00_for_0+24.nc
    setenv BNDY_CONC_1    "$OUTDIR/BCON_${VRSN}_${APPL}_${BCON_TYPE}_${YYYYMMDD} -v"
 endif

 if ( $BCON_TYPE == profile ) then
    setenv BC_PROFILE $BLD/avprofile_cb6r3m_ae7_kmtbr_hemi2016_v53beta2_m3dry_col051_row068.csv
    setenv MET_BDY_3D_FIN /data/users/oko001/mcip_out_2021/METBDY3D_2022-01-27.nc
    setenv BNDY_CONC_1    "$OUTDIR/BCON_${VRSN}_${APPL}_${BCON_TYPE} -v"
 endif

# =====================================================================
#> Output File
# =====================================================================
 
#>- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

 if ( ! -d "$OUTDIR" ) mkdir -p $OUTDIR

 ls -l $BLD/$EXEC; size $BLD/$EXEC
 unlimit
 limit

#> Executable call:
 time $BLD/$EXEC

 exit() 
