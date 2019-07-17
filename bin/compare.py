#!/bin/python

import os
import sys
import filecmp
import re
import argparse

## SET THE ARCHIVE LOCATION
try:
   os.environ['ARCHIVE_PATH']
except KeyError:
   print "You must set $ARCHIVE_PATH"
   print "This should be done with `module load gcpre`"
   print sys.exit(1)
archive = os.environ['ARCHIVE_PATH'] 

## Deal with comand line arguments
parser = argparse.ArgumentParser(description='Used to compare restart files on GCP')

parser.add_argument('-e','--experiment','--exp','-exp', type=str, help='-REQUIRED- The name of the experiment',required=True)
parser.add_argument('-l','--length','--len','-len', type=str, help='-REQUIRED- The length of the experiment',required=True)
parser.add_argument('-v','--verbose', action='store_true', help='Prints more information.  Any value after -v truns this one',required=False)
parser.add_argument('-vv','--debug','-d', action='store_true', help='Prints even more information. Any value after -vv turns this on.',required=False)
parser.add_argument('-q','--quiet',action='store_true', help='Suppresses most of the output. Any value after -q turns this on.',required=False)
parser.add_argument('--nccmp', type=str, help='Flags to pass to nccmp. dm is the default. This will overwrite the default.  You must include "d" or "m" here.  Do not include a "-" (dash)',required=False)

args = parser.parse_args()
if args.debug:
 print "Deal with comand line arguments"
 print "exp and length are required"
## exp and length are required
exp = args.experiment
length = args.length
verbose = args.verbose
vv = args.debug
q = args.quiet
nccmpFlags = "dm"
if args.nccmp:
 nccmpFlags = args.nccmp
if verbose or vv:
 print "Command-line args"
 print "experiment = ",exp
 print "length = ", length
 print "verbose = ", verbose
 print "debug = ", vv
 print "nccmp flags = ", nccmpFlags

if verbose or vv:
 print "Switch the exp variable to add the archive root"
exp = archive + "/" + exp

if vv:
 print "Set the directory"
 print os.listdir(exp+"/"+length)
dirs = os.listdir(exp+"/"+length)

nccmp = "/apps/spack/opt/spack/linux-centos7-x86_64/intel-19.0.1.144/nccmp-1.8.2.0-y6rqgbfkpjhvnwm5dhrxblw7n74tovoc/bin/nccmp"
nccmp = nccmp+" -"+nccmpFlags
if verbose or vv:
 print "The nccmp command used will be: "
 print nccmp
 os.system("sleep 1")

if verbose or vv:
	print dirs[0]," will be compared to everything else"
files=os.listdir(exp+"/"+length+"/"+dirs[0]+"/RESTART/")
if vv:
 print "List of files"
 print files
 os.system("sleep 5")

if verbose or vv:
 print "load modules intel nccmp"
os.system("module load intel")
os.system("module load nccmp")

if vv:
 print "Looping through directories and files and compare"
for j in range (len(dirs)):
    compfiles=os.listdir(exp+"/"+length+"/"+dirs[j]+"/RESTART/")
    if not q:
        print "Comparing "+dirs[0]+" and "+dirs[j]
    if verbose or vv:
        print "Checking that files have the same names and exist in both folders"
    qflag = 0
    for i in range (len(files)):
        if files[i] not in compfiles:
           if q:
              qflag = 1
           else:
              print files[i]+" exists in "+exp+"/"+length+"/"+dirs[0]+" but does not exist in "+exp+"/"+length+"/"+dirs[j]
    for i in range (len(compfiles)):
        if compfiles[i] not in files:
           if q:
              qflag = 1
           else:
              print compfiles[i]+" exists in "+exp+"/"+length+"/"+dirs[j] +" but does not exist in "+exp+"/"+length+"/"+dirs[0]
    if vv:
        print "Looping through and comparing files..."
    for i in range (len(files)):
        comp=""
        fname = files[i]
        if verbose or vv:
           print "Comparing "+fname
        if re.search('.nc',files[i]):
           if verbose or vv:
              print nccmp+" "+exp+"/"+length+"/"+dirs[0]+"/RESTART/"+files[i]+" "+exp+"/"+length+"/"+dirs[j]+"/RESTART/"+files[i]
           comp=os.system(nccmp+" "+exp+"/"+length+"/"+dirs[0]+"/RESTART/"+files[i]+" "+exp+"/"+length+"/"+dirs[j]+"/RESTART/"+files[i]+" >/dev/null 2>&1")
           if vv:
              print "Exit status = "+str(comp)
           if comp == 256 and not q:
              print "DIFFER : "+fname
              os.system(nccmp+" "+exp+"/"+length+"/"+dirs[0]+"/RESTART/"+files[i]+" "+exp+"/"+length+"/"+dirs[j]+"/RESTART/"+files[i])
           elif comp == 256 and q:
              qflag = 1
        else:
           if verbose or vv:
              print "diff "+exp+"/"+length+"/"+dirs[0]+"/RESTART/"+files[i]+" "+exp+"/"+length+"/"+dirs[j]+"/RESTART/"+files[i]
           comp=os.system("diff "+exp+"/"+length+"/"+dirs[0]+"/RESTART/"+files[i]+" "+exp+"/"+length+"/"+dirs[j]+"/RESTART/"+files[i]+" >/dev/null 2>&1")
           if vv:
              print "Exit status = "+str(comp)
           if comp == 256 and not q:
              print "DIFFER : "+fname+" using `diff`"
           elif comp == 256 and q:
              qflag = 1
    if q and qflag !=0:
        print "DIFFER: "+exp+"/"+length+"/"+dirs[0]+" and "+exp+"/"+length+"/"+dirs[j]+" are different."
