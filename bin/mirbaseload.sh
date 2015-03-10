#!/bin/sh
#
# miRBase Load Jobstream Wrapper
############################################################################
#
# Purpose:
#
# 	Parse the MGI-generated file microrna_master.txt 
#	into these output files:
#		1.  association marker/mirbase loader file
#		2.  coordinate loader file
#
#	We only load one coordinate per Marker.
#
#       (mirbaseload.py)
#
#	Load the output files into the database.
#		1. invoke association loader for marker/mirbase data
#		2. invoke coordinate loader
#		3. update MRK_Location_Cache table
#
Usage="mirbaseload.sh true|false"
#       true if reloading MRK_Location_Cache
# History
#
# 03/25/2010    sc
#       - TR 10021
#
# 05/03/2006	lec
#	- TR 7651
#
###########################################################################

#
#  Set up a log file for the shell script in case there is an error
#  during configuration and initialization.
#

cd `dirname $0`/..
LOG=`pwd`/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

#
#  Verify the argument(s) to the shell script.
#
if [ $# -ne 1 ]
then
    echo ${Usage} | tee -a ${LOG}
    exit 1
fi

LOAD_CACHE=$1

CONFIG_LOAD=`pwd`/mirbaseload.config

#
# verify & source the miRBASE load configuration file
#

if [ ! -r ${CONFIG_LOAD} ]
then
    echo "Cannot read configuration file: ${CONFIG_LOAD}"
    exit 1
fi

. ${CONFIG_LOAD}

# reality check for important configuration vars
echo "dbserver:${MGD_DBSERVER}"
echo "database:${MGD_DBNAME}"
echo "INFILE_NAME: ${INFILE_NAME}"
#
#  Source the DLA library functions.
#

if [ "${DLAJOBSTREAMFUNC}" != "" ]
then
    if [ -r ${DLAJOBSTREAMFUNC} ]
    then
        . ${DLAJOBSTREAMFUNC}
    else
        echo "Cannot source DLA functions script: ${DLAJOBSTREAMFUNC}" | tee -a ${LOG}
        exit 1
    fi
else
    echo "Environment variable DLAJOBSTREAMFUNC has not been defined." | tee -a ${LOG}
    exit 1
fi

#
# check that INFILE_NAME has been set and exists
#
if [ "${INFILE_NAME}" = "" ]
then
     # set STAT for endJobStream.py called from postload in shutDown
    STAT=1
    checkStatus ${STAT} "INFILE_NAME not defined"
fi

if [ ! -r ${INFILE_NAME} ]
then
    # set STAT for endJobStream.py called from postload in shutDown
    STAT=1
    checkStatus ${STAT} "Input file: ${INFILE_NAME} does not exist"
fi

##################################################################
##################################################################
#
# main
#
##################################################################
##################################################################

#
# createArchive including OUTPUTDIR, startLog, getConfigEnv, get job key
#

preload ${OUTPUTDIR}

#
# rm files and dirs from OUTPUTDIR
#

cleanDir ${OUTPUTDIR} 

#
# process the input file
#
echo "" >> ${LOG_DIAG} 
echo "`date`" >> ${LOG_DIAG} 
echo "Processing input file ${INFILE_NAME}" | tee -a ${LOG_DIAG}
${MIRBASELOAD}/bin/mirbaseload.py | tee -a ${LOG_DIAG} ${LOG_PROC}
STAT=$?
checkStatus ${STAT} "${MIRBASELOAD}/mirbaseload.py"

#
# run marker/mirbaseID association load
#
echo "" >> ${LOG_DIAG} 
echo "`date`" >> ${LOG_DIAG} 
echo "Running association load" | tee -a ${LOG_DIAG}
${ASSOCLOADER_SH} ${CONFIG_LOAD} ${ASSOCLOADCONFIG} >> ${LOG_DIAG}
STAT=$?
checkStatus ${STAT} "${ASSOCLOADER_SH}"

#
# run the coordinate load
#
echo "" >> ${LOG_DIAG}
echo "`date`" >> ${LOG_DIAG}
echo "Running coordinate load" | tee -a ${LOG_DIAG}
${COORDLOADER_SH} ${CONFIG_LOAD} ${COORDLOADCONFIG}  >> ${LOG_DIAG}
STAT=$?
checkStatus ${STAT} "${COORDLOADER_SH}"

if [ ${LOAD_CACHE} = "true" ]
then
    echo "" >> ${LOG_DIAG}
    echo "`date`" >> ${LOG_DIAG}
    echo "Running marker location cacheload"| tee -a ${LOG_DIAG}
    ${LOCATIONCACHE_SH} >> ${LOG_DIAG}
    STAT=$?
    checkStatus ${STAT} "${LOCATIONCACHE_SH}"
fi

#
# Perform post-load tasks.
#
shutDown

exit 0
