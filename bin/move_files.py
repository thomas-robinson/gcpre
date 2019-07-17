#!/bin/python

import os
import sys
import re
import argparse

hours = re.compile('\s*hours\s*=\s*\d*.*')
days = re.compile('\s*days\s*=\s*\d*.*')
months = re.compile('\s*months\s*=\s*\d*.*')
nh = 0
nd = 0
nm = 0


parser = argparse.ArgumentParser(description='Combines restart files and moves them to the archive folder')

parser.add_argument('-n','--cores','--ncores', type=str, help='The number of cores the experiment ran on',required=True)
parser.add_argument('-c','--threads','--nthreads', type=str, help='The number of threads the experiment ran on',required=True)
parser.add_argument('-w','--workDir','--runDir', type=str, help='The work directory that the experiment ran in',required=True)
parser.add_argument('-e','--experiment','--exp','-exp', type=str, help='-REQUIRED- The name of the experiment',required=True)
parser.add_argument('-v','--verbose', action='store_true', help='Prints more information.  Any value after -v truns this one',required=False)
parser.add_argument('-vv','--debug','-d', action='store_true', help='Prints even more information. Any value after -vv turns this on.',required=False)
parser.add_argument('-q','--quiet',action='store_true', help='Suppresses most of the output. Any value after -q turns this on.',required=False)

args = parser.parse_args()
if args.debug:
 print "Deal with comand line arguments"
 print "--exp --ncores --nthreads --workDir are required"

cores=args.cores
threads=args.threads
runDir=args.workDir
exp = args.experiment
verbose = args.verbose
vv = args.debug
q = args.quiet

if verbose or vv:
 print "Number of threads ", threads
 print "Number of cores ", cores
 print "runDir is ", runDir
 print "Experiment is ", exp
 print "verbose = ", verbose
 print "debug = ", vv
 print "quiet = ", q
try:
   os.environ['ARCHIVE_PATH']
except KeyError:
   print "You must set $ARCHIVE_PATH"
   print "This should be done with `module load gcpre`"
   print sys.exit(1)
archive=os.environ['ARCHIVE_PATH']
if vv:
 print archive

if verbose or vv:
 print "Find the amount of time the model ran"
if verbose or vv:
 print "Open the namelist file"
if vv:
 print runDir+"/input.nml"
f = open(runDir+"/input.nml" , 'r')
for line in f:
#   print line
   m = days.match(line)
   if m:
      if vv:
       print(line)
      words = line.split('=')
      if vv:
       print words
      nocom = words[1].split(',')
      if vv:
       print nocom
      nd = nocom[0].lstrip()
      if verbose or vv:
       print "Days = ",nd
   m = hours.match(line)
   if m:
      if vv:
       print(line)
      words = line.split('=')
      if vv:
       print words
      nocom = words[1].split(',')
      if vv:
       print nocom
      nh = nocom[0].lstrip()
      if verbose or vv:
       print "Hours = ",nh
   m = months.match(line)
   if m:
      if vv:
       print(line)
      words = line.split('=')
      if vv:
       print words
      nocom = words[1].split(',')
      if vv:
       print nocom
      nm = nocom[0].lstrip()
      if verbose or vv:
       print "months = ",nm
if vv:
 print "Set up folder starting with "+archive+'/'+exp+'/'
folder = archive+'/'+exp+'/'
os.system("mkdir "+folder)
os.system("chmod 777 "+folder)
if int(nm) > 0 :
 folder = folder+str(nm)+'m'
if int(nd) > 0 :
 folder = folder+str(nd)+'d'
if int(nh) > 0 :
 folder = folder+str(nh)+'h'
os.system("mkdir "+folder)
os.system("chmod 777 "+folder)
if vv:
 print "folder = "+folder
folder = folder+'/intel_'+cores+'x'+threads+'_'+str(nm)+'m'+str(nd)+'d'
if vv or verbose:
 print "The files will be moved to "+folder


exists = os.path.isdir(folder)
if verbose or vv:
 print "Status of "+folder+" existing: ", exists
if exists:
    for i in range(1,200):
       check = os.path.isdir(folder+'_'+str(i))
       if vv:
        print "Status of "+folder+" existing: ",check
       if not check:
          if verbose or vv:
           print "mkdir "+folder+'_'+str(i)
          os.system("mkdir "+folder+'_'+str(i))
          if not q:
           print "cp -r "+runDir+"/RESTART "+folder+'_'+str(i)
          os.system("cp -r "+runDir+"/RESTART "+folder+'_'+str(i))
          if not q:
           print "cp -r "+runDir+"/input.nml "+folder+'_'+str(i)
          os.system("cp -r "+runDir+"/input.nml "+folder+'_'+str(i))
          if not q:
           print "cp -r "+runDir+"/fms.out "+folder+'_'+str(i)
          os.system("cp -r "+runDir+"/fms.out "+folder+'_'+str(i))
          if q:
           print "Copied files into "+folder+'_'+str(i)
          if vv:
           print "Break the directory create loop"
          break
       if i == 999:
          print "The maxmimum number of directories is reached"
          print "Not making a new output directory."
          quit()
else:
    if verbose or vv:
     print "mkdir -p "+folder
    os.system("mkdir -p "+folder)
    if not q:
     print "cp -r "+runDir+"/fms.out "+folder
    os.system("cp -r "+runDir+"/fms.out "+folder)
    if not q:
     print "cp -r "+runDir+"/input.nml "+folder
    os.system("cp -r "+runDir+"/input.nml "+folder)
    if not q:
     print "cp -r "+runDir+"/RESTART "+folder
    os.system("cp -r "+runDir+"/RESTART "+folder)
    if q:
     print "Files copied to "+folder
if verbose or vv:
 print "Close the file"
f.close() 
