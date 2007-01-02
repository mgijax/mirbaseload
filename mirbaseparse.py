#!/usr/local/bin/python

#
# Program: mirbaseparse.py
#
# Original Author: Lori E. Corbani
#
# Purpose:
#
# 1.  To generate a association loader input file, 
#     a coordinate loader input file and a mapping loader input file
#     from the MGI-hand-curated file MicroRNAload.txt
#     which are then loaded into MGI via the association loader,
#     the coordinate loader and the mapping loader.
#
# Requirements Satisfied by This Program:
#
# Usage:  mirbaseparse.py
#
# Envvars:
#
# Inputs:
#
# INPUT_FILE:  a file of miRBase coordinates and marker associations
#
# field 1: mirBASE id
# field 2: MGI id
# field 3: marker symbol
# field 4: chromosome
# field 5: start bp
# field 6: end bp
# field 7: strand
#
# Outputs:
#
# INPUT_ASSOC_FILE:  an input file for marker/mirbase ID assocload
# INPUT_COORD_FILE:  an input file for coordload
# INPUT_MAPPING_FILE:  an input file for mappingload
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
#	- TR 4460/MGI 3.5
#

import sys
import os
import re
import db
import string
import mgi_utils
import loadlib

TAB = '\t'
CRT = '\n'

inFileName = os.environ['INPUT_FILE']
assocFileName = os.environ['INPUT_ASSOC_FILE']
coordFileName = os.environ['INPUT_COORD_FILE']
mappingFileName = os.environ['INPUT_MAPPING_FILE']

head, tail = os.path.split(sys.argv[0])
diagFileName = os.environ['OUTPUTDIR'] + '/' + tail + '.diagnostics'
errorFileName = os.environ['OUTPUTDIR'] + '/' + tail + '.error'

diagFile = ''		# file descriptor
errorFile = ''		# file descriptor

assocline = '%s\t%s\n'
coordline = '%s\t%s\t%s\t%s\t%s\t\n'
mappingline = '%s\t%s\tyes\t\tassembly\t\n'

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
 
    try:
	diagFile = open(diagFileName, 'w')
    except:
	exit(1, 'Could not open file %s\n' % diagFileName)
		
    try:
	errorFile = open(errorFileName, 'w')
    except:
	exit(1, 'Could not open file %s\n' % errorFileName)
		
    diagFile.write('Start Date/Time: %s\n\n' % (mgi_utils.date()))
    errorFile.write('Start Date/Time: %s\n\n' % (mgi_utils.date()))

def writeAssoc(assocDict):
	#
	# requires:
	#    assocDict (dictionary):  a key:value dictionary
	#
	# effects: 
	# 1. Writes each association to the output association file
	#
	# returns:  nothing
	#

    try:
	assocFile = open(assocFileName, 'w')
    except:
	exit(1, 'Could not open file %s\n' % assocFileName)
		
    assocFile.write('MGI\tmiRBase\n')
    for r in assocDict.keys():
        assocFile.write(assocDict[r])

    assocFile.close()

def writeCoord(coordDict):
	#
	# requires:
	#    coordDict (dictionary):  a key:value dictionary
	#
	# effects: 
	# 1. Writes each coordinate to the output coordinate file
	#
	# returns:  nothing
	#

    try:
	coordFile = open(coordFileName, 'w')
    except:
	exit(1, 'Could not open file %s\n' % coordFileName)
		
    for c in coordDict.keys():
        coordFile.write(coordDict[c])

    coordFile.close()

def writeMapping(mappingDict):
	#
	# requires:
	#    mappingDict (dictionary):  a key:value dictionary
	#
	# effects: 
	# 1. Writes each Mapping record to the output mapping file
	#
	# returns:  nothing
	#

    try:
	mappingFile = open(mappingFileName, 'w')
    except:
	exit(1, 'Could not open file %s\n' % mappingFileName)
		
    for r in mappingDict.keys():
        mappingFile.write(mappingDict[r])

    mappingFile.close()

def process():
	#
	# requires:
	#
	# effects: 
	#   input:  Micro RNA input file
	#   output: association loader file, coordinate loader file, mapping loader file
	#
	# returns:  nothing
	#

    assocDict = {}
    coordDict = {}
    mappingDict = {}

    try:
	inFile = open(inFileName, 'r')
    except:
	exit(1, 'Could not open file %s\n' % inFileName)
		
    lineNum = 0

    for line in inFile.readlines():

        tokens = string.split(line[:-1], TAB)

        try:
	    mirID = tokens[0]
	    markerID = tokens[1]
	    markerSymbol = tokens[2]
	    markerChr = tokens[3]
	    startCoord = tokens[4]
	    endCoord = tokens[5]
	    strand = tokens[6]

        except:
	    errorFile.write('Invalid Line (%d): %s\n' % (lineNum, line))
	    lineNum = lineNum + 1
	    continue
#
#	if string.find(mirChr, 'NT_') >= 0:
#	    errorFile.write('NT symbol skipped (%d): %s\n' % (lineNum, mirID))
#	    lineNum = lineNum + 1
#	    continue

	assocDict[markerID] = assocline % (markerID, mirID)
	coordDict[markerID] = coordline % (markerID, markerChr, startCoord, endCoord, strand)
	mappingDict[markerID] = mappingline % (markerID, markerChr)

        lineNum = lineNum + 1

    writeAssoc(assocDict)
    writeCoord(coordDict)
    writeMapping(mappingDict)

    inFile.close()

#
# Main Routine
#

init()
process()
exit(0)

