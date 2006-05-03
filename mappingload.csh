#!/bin/csh -f

#
# Wrapper script to create & load new mapping experiments
#
# Usage:  mappingload.csh
#

cd ${MAPPINGDATADIR}

setenv MODE		full
setenv JNUM		J:105741
setenv EXPERIMENTTYPE	"TEXT-Physical Mapping"
setenv CREATEDBY	mirbase_load

setenv LOG	$0.log

date >& $LOG

${MAPPINGLOADERDIR} -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} -M${MODE} -I${INPUT_MAPPING_FILE} -R${JNUM} -E"${EXPERIMENTTYPE}" -C${CREATEDBY} >>& $LOG

date >>& $LOG

