#!/usr/local/bin/python

#
# Program: mirbasemapping.py
#
# Original Author: Lori E. Corbani
#
# Purpose:
#
# 1.  To generate a mapping loader input file from miRBase Coordinates
#
# Requirements Satisfied by This Program:
#
# Usage:  mirbasemapping.py
#
# Envvars:
#
# Inputs:
#
#	None
#
# Outputs:
#
# 	OUTPUT_MAPPING_FILE:  an input file for mappingload
#
# Processing:
#
# Exit Codes:
#
# Assumes:
#
# Bugs:
#
# Implementation:
#
#    Modules:
#
# Modification History:
#
# 05/02/2006	lec
#	- TR 7651
#

import sys
import os
import db
import string
import mgi_utils
import loadlib

TAB = '\t'
CRT = '\n'

mappingFileName = os.environ['OUTPUT_MAPPING_FILE']

head, tail = os.path.split(sys.argv[0])
diagFileName = os.environ['OUTPUTDIR'] + '/' + tail + '.diagnostics'
errorFileName = os.environ['OUTPUTDIR'] + '/' + tail + '.error'

diagFile = ''		# file descriptor
errorFile = ''		# file descriptor
mappingFile = ''	# file descriptor

def exit(status, message = None):
	#
	# requires: status, the numeric exit status (integer)
	#           message (string)
	#
	# effects:
	# Print message to stderr and exits
	#
	# returns:
	#
 
    if message is not None:
	sys.stderr.write('\n' + str(message) + '\n')
 
    try:
	diagFile.write('\n\nEnd Date/Time: %s\n' % (mgi_utils.date()))
	errorFile.write('\n\nEnd Date/Time: %s\n' % (mgi_utils.date()))
	diagFile.close()
	errorFile.close()
        mappingFile.close()
    except:
	pass

    try:
	db.useOneConnection()
    except:
	pass

    sys.exit(status)
 
def init():
	#
	# requires: 
	#
	# effects: 
	# 1. Processes command line options
	# 2. Initializes global file descriptors/file names
	#
	# returns:
	#
 
    global diagFile, errorFile, diagFileName, errorFileName
    global mappingFile
 
    try:
	diagFile = open(diagFileName, 'w')
    except:
	exit(1, 'Could not open file %s\n' % diagFileName)
		
    try:
	errorFile = open(errorFileName, 'w')
    except:
	exit(1, 'Could not open file %s\n' % errorFileName)
		
    try:
	mappingFile = open(mappingFileName, 'w')
    except:
	exit(1, 'Could not open file %s\n' % mappingFileName)
		
    diagFile.write('Start Date/Time: %s\n' % (mgi_utils.date()))
    errorFile.write('Start Date/Time: %s\n' % (mgi_utils.date()))

    db.useOneConnection(1)
 
    # Log all SQL
    db.set_sqlLogFunction(db.sqlLogAll)

    # Set Log File Descriptor
    db.set_sqlLogFD(diagFile)

def process():
	#
	# requires:
	#
	# effects: 
	#   output:  Mapping file
	#
	# returns:  nothing
	#

    mappingline = '%s\t%s\tn\t\tassembly\t\n'

    results = db.sql('select m.accID, l.chromosome, l.sequenceNum ' + \
	'from MRK_Location_Cache l, ACC_Accession m ' + \
	'where l.provider = "miRBase" ' + \
	'and l._Marker_key = m._Object_key ' + \
	'and m._MGIType_key = 2 ' + \
	'and m._LogicalDB_key = 1 ' + \
	'and m.prefixPart = "MGI:" ' + \
	'and m.preferred = 1 ' + \
	'order by l.sequenceNum, l.startCoordinate, l.endCoordinate', 'auto')
    for r in results:
	mappingFile.write(mappingline % (r['accID'], r['chromosome']))

#
# Main Routine
#

init()
process()
exit(1)

