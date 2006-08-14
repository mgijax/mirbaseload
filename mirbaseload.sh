#!/bin/sh -f -x

#
# miRBase Load Jobstream Wrapper
#
# Usage:
# 	mirbaseload.sh
#
# Purpose:
#
# 	Parse the MGI-generated file MicroRNAload into these output files:
#		1.  association marker/mirbase loader file
#		2.  coordinate loader file
#		3.  mapping loader file
#
#	We only load one coordinate per Marker.
#
#       (mirbaseparse.py)
#
#	Load the output files into the database.
#		1. invoke association loader for marker/mirbase data
#		2. invoke coordinate loader
#		3. invoke mapping loader
#		4. update MRK_Location_Cache table
#
# History
#
# 05/03/2006	lec
#	- TR 7651
#

cd `dirname $0`

CONFIG_COMMON=`pwd`/common.config.sh
CONFIG_LOAD=`pwd`/mirbaseload.config

#
# verify & source the DLA common configuration file
#

if [ ! -r ${CONFIG_COMMON} ]
then
    echo "Cannot read configuration file: ${CONFIG_COMMON}"
    exit 1
fi

. ${CONFIG_COMMON}

#
# verify & source the UniSTS load configuration file
#

if [ ! -r ${CONFIG_LOAD} ]
then
    echo "Cannot read configuration file: ${CONFIG_LOAD}"
    exit 1
fi

. ${CONFIG_LOAD}

#
# create log file
#

LOG=${LOGDIR}/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

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
# Perform pre-load tasks.
#
preload

#
# remove old output and generated input files
#
rm -rf ${OUTPUT_ASSOC_FILE} ${OUTPUT_COORD_FILE} ${OUTPUT_MAPPING_FILE}
rm -rf ${INPUT_ASSOC_FILE} ${INPUT_COORD_FILE} ${INPUT_MAPPING_FILE}

#
# parse pass for associations and coordinates
#
echo 'Parsing input file for Associations and Coordinates...' | tee -a ${LOG}
${MIRBASEINSTALLDIR}/mirbaseparse.py | tee -a ${LOG}
STAT=$?
checkStatus ${STAT} "mirbaseparse.py"

# create a symbolic link between the parser output file and the loader input file

ln -s ${OUTPUT_ASSOC_FILE} ${INPUT_ASSOC_FILE}
ln -s ${OUTPUT_COORD_FILE} ${INPUT_COORD_FILE}
ln -s ${OUTPUT_MAPPING_FILE} ${INPUT_MAPPING_FILE}

# run association marker/mirbase load
${ASSOCLOADER_SH} ${CONFIG_LOAD} ${RADAR_DBSCHEMADIR}/Configuration.sh ${MGD_DBSCHEMADIR}/Configuration.sh ${ASSOCCONFIG}
STAT=$?
checkStatus ${STAT} "${ASSOCLOADER_SH}"

# run the coordinate load
${COORDLOADER_SH} ${CONFIG_LOAD} ${RADAR_DBSCHEMADIR}/Configuration.sh ${MGD_DBSCHEMADIR}/Configuration.sh ${COORDLOADCONFIG}
STAT=$?
checkStatus ${STAT} "${COORDLOADER_SH}"

# run the marker location cache
${LOCATIONCACHE_SH}
STAT=$?
checkStatus ${STAT} "${LOCATIONCACHE_SH}"

# run the mapping load
${MIRBASEINSTALLDIR}/mirbasemapping.py | tee -a ${LOG}
STAT=$?
checkStatus ${STAT} "mirbasemapping.py"
${MAPPINGLOADER_SH}
STAT=$?
checkStatus ${STAT} "${MAPPINGLOADER_SH}"

#
# Perform post-load tasks.
#
shutDown

exit 0

