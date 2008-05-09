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

#
# create log file
#

LOG=`pwd`/`basename $0`.log
rm -rf ${LOG}
touch ${LOG}

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

# parse the input file
${MIRBASELOAD}/mirbaseparse.py
STAT=$?
checkStatus ${STAT} "${MIRBASELOAD}/mirbaseparse.py"

# run association marker/mirbase load
${ASSOCLOADER_SH} ${CONFIG_LOAD} ${ASSOCLOADCONFIG}
STAT=$?
checkStatus ${STAT} "${ASSOCLOADER_SH}"

# run the coordinate load
${COORDLOADER_SH} ${CONFIG_LOAD} ${COORDLOADCONFIG}
STAT=$?
checkStatus ${STAT} "${COORDLOADER_SH}"

# run the mapping load
#${MAPPINGLOADER_SH} ${MAPPINGLOADCONFIG}
#STAT=$?
#checkStatus ${STAT} "${MAPPINGLOADER_SH}"

# run the marker location cache
#${LOCATIONCACHE_SH}
#STAT=$?
#checkStatus ${STAT} "${LOCATIONCACHE_SH}"

#
# Perform post-load tasks.
#
shutDown

exit 0

