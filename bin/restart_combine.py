#!/bin/python

import os
import sys
import filecmp
import re
import argparse
import math
import time
import run_utils

parser = argparse.ArgumentParser(description='Used to compare restart files on GCP')

parser.add_argument('-w','--workDir','--runDir', type=str, help='The directory that the model was run.',required=True)
parser.add_argument('-v','--verbose', action='store_true', help='Prints more information.  Any value after -v truns this one',required=False)
parser.add_argument('-vv','--debug','-d', action='store_true', help='Prints even more information. Any value after -vv turns this on.',required=False)
parser.add_argument('-q','--quiet',action='store_true', help='Suppresses most of the output. Any value after -q turns this on.',required=False)

args = parser.parse_args()
if args.debug:
 print "Deal with comand line arguments"
 print "exp and length are required"


workDir = args.workDir
verbose = args.verbose
vv = args.debug
q = args.quiet
if verbose or vv:
 print "Command-line args"
 print "experiment = ",exp
 print "verbose = ", verbose
 print "debug = ", vv
 print "quiet = ", q



files=os.listdir(workDir+"/RESTART/")
resList=[]
if verbose or vv:
 print "Find all of the restart names and minimum numbers"
for f in files:
   if not q:
     print "Processing "+f
   resName=re.split(r'.00',f)
#   print resName
#   if resName not in resList[:]:
   if next((item for item in resList if item["name"] == resName[0]),False):
     for i in range(len(resList)):
         if  vv:
            print resName[0]+" is already in the list"
         if resList[i]['name'] == resName[0] and len(resName) == 2:
            if resList[i]['minimum'] > resName[1]:
                if vv:
                  print "Updating the minumum of "+resName[0]+" to "+resName[1]
                resList[i]['minimum'] = resName[1]    
   else:
     if len(resName) > 1:
         if verbose or vv:
            print "Adding "+resName[0]+" to the list"
         resList.append({"name": resName[0] , "minimum": resName[1]})
     else:
         if verbose or vv:
            print "Adding " + resName[0]
         if vv:
            print "Setting the minimum number for "+resName[0]+"to 99"
         resList.append({"name": resName[0] , "minimum": "99"})

## Loop through the files and use the proper combine program to combine the restarts
for i in range(len(resList)):
 if int(resList[i]['minimum']) < int(99):
   iscomp = os.system("/apps/gcpre/google/bin/is-compressed "+resList[i]['name']+".????")
#   print resName[0],iscomp
   if iscomp == 512:
      if verbose or vv:
       print "Doing nothing for "+resName[0]
   elif iscomp == 0:
      if verbose or vv:
       print resList[i]['name']+" has a compressed axis.  Using combine-ncc"
       print "/apps/gcpre/google/bin/combine-ncc "+resList[i]['name']+".???? "+resList[i]['name']
      os.system("/apps/gcpre/google/bin/combine-ncc "+resList[i]['name']+".???? "+resList[i]['name'])
      if verbose or vv:
       print "rm "+resList[i]['name']+".00*"
      os.system("rm "+resList[i]['name']+".00*")
#      print resName[0]+" is compressed"
   else:
      if verbose or vv:
       print resList[i]['name']+" DOes not have a compressed axis, using mppnccombine"
      if verbose or vv:
       print "/apps/gcpre/google/bin/mppnccombine -n "+resList[i]['minimum']+" -r "+resList[i]['name']
      os.system("/apps/gcpre/google/bin/mppnccombine -n "+resList[i]['minimum']+" -r "+resList[i]['name']) 
 else:
      if verbose or vv:
       print resList[i]['name']+" does not need to be combined"

