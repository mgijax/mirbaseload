#!/usr/local/bin/python

#
# Program: mirbaseload.py
#
# Original Author: Lori E. Corbani
#
# Purpose:
#
# 1.  To generate a association load input file, 
#     and a coordinate load input file 
#     from the MGI-hand-curated file microrna_master.txt
#     which are then loaded into MGI via the association load
#     and the coordinate load.
#
# Requirements Satisfied by This Program:
#
# Usage:  mirbaseload.py 
#
# Envvars:
#
# Inputs:
#
# INFILE_NAME:  a file of miRBase coordinates and marker associations
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
# 03/25/2010	sc
#	- TR 10021
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

inFileName = os.environ['INFILE_NAME']
assocFileName = os.environ['INPUT_ASSOC_FILE']
coordFileName = os.environ['INPUT_COORD_FILE']

head, tail = os.path.split(sys.argv[0])

assocline = '%s\t%s\n'
coordline = '%s\t%s\t%s\t%s\t%s\t\n'

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
	db.useOneConnection()
    except:
	pass

    sys.exit(status)
 
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

    print "Total associations written to assocload file: %s" % len(assocDict)
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

    print "Total coordinates written to coordload file: %s" % len(coordDict)
    for c in coordDict.keys():
        coordFile.write(coordDict[c])

    coordFile.close()

def process():
	#
	# requires:
	#
	# effects: 
	#   input:  Micro RNA input file
	#   output: association load file and coordinate load file
	#
	# returns:  nothing
	#

    assocDict = {}
    coordDict = {}

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
	    markerSymbol = tokens[2] # we don't use this
	    markerChr = tokens[3]
	    startCoord = tokens[4]
	    endCoord = tokens[5]
	    strand = tokens[6]

        except:
	    errorFile.write('Invalid Line (%d): %s\n' % (lineNum, line))
	    lineNum = lineNum + 1
	    continue

	assocDict[markerID] = assocline % (markerID, mirID)
	coordDict[markerID] = coordline % (markerID, markerChr, startCoord, endCoord, strand)

        lineNum = lineNum + 1

    writeAssoc(assocDict)
    writeCoord(coordDict)

    inFile.close()

#
# Main Routine
#

process()
exit(0)

