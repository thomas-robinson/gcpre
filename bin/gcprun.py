#!/bin/python
import os
import sys
import filecmp
import re
import argparse
import math
import time
import run_utils
corespernode = 48
submitProg = "sbatch --exclusive "

parser = argparse.ArgumentParser(description='Combines restart files and moves them to the archive folder')

parser.add_argument('-n','--cores','--ncores', type=str, help='The number of MPI ranks',required=True)
parser.add_argument('-c','--threads','--nthreads', type=str, help='The number of openMP threads',required=True)
parser.add_argument('-e','--experiment','--exp','-exp', type=str, help='The name of the experiment',required=True)
parser.add_argument('-x','--executable','--exec', type=str, help='The full path the executable',required=True)
parser.add_argument('-w','--workDir','--runDir', type=str, help='User specified work directory',required=False)
parser.add_argument('-s','--submit', action='store_true', help='Submit the run script to the queue',required=False)
parser.add_argument('--ht', action='store_true', help='Turn on hyperthreading',required=False)
parser.add_argument('--hours', type=str, help='The number of hours the experiment is run. Total = hours + days + months',required=False)
parser.add_argument('--days', type=str, help='The number of days the experiment is run. Total = hours + days + months',required=False)
parser.add_argument('--months', type=str, help='The number of months the experiment is run. Total = hours + days + months',required=False)
parser.add_argument('-v','--verbose', action='store_true', help='Prints more information.  Any value after -v truns this one',required=False)
parser.add_argument('-vv','--debug','-d', action='store_true', help='Prints even more information. Any value after -vv turns this on.',required=False)
parser.add_argument('-q','--quiet',action='store_true', help='Suppresses most of the output. Any value after -q turns this on.',required=False)

args = parser.parse_args()
if args.debug:
 print "Deal with comand line arguments"
 print "--exp --ncores --nthreads are required"
home = os.path.expanduser("~")
currentTime = time.mktime(time.localtime())
cores=args.cores
threads=args.threads
workDir=args.workDir
exp = args.experiment
submit = args.submit
executable = args.executable
if args.workDir:
 workDir=args.workDir
else:
 workDir = home+"/"+exp+"_"+cores+"x"+threads+"_"+str(currentTime)
verbose = args.verbose
vv = args.debug
q = args.quiet
ht = args.ht
nh = args.hours
nd = args.days
nm = args.months

if verbose or vv:
 print "Number of threads ", threads
 print "Number of cores ", cores
 print "workDir is ", workDir
 print "Experiment is ", exp
 print "Executable is ",executable
 print "Hyperthreading = ",ht
 print "submit = ",submit
 print "Hours  = ", nh
 print "Days   = ", nd
 print "Months = ", nm
 print "verbose = ", verbose
 print "debug = ", vv
 print "quiet = ", q
if ht:
   print "Hyperthreading not currently supported.  Run without --ht"
   sys.exit()
os.system("sleep 5")

try:
   os.environ['ARCHIVE_PATH']
except KeyError:
   print "You must set $ARCHIVE_PATH"
   print "This should be done with `module load gcpre`"
   print sys.exit(1)
archive=os.environ['ARCHIVE_PATH']
## Set up number of cores, nodes, and layouts
if verbose or vv:
 print "Checking the number of cores will work"
mod = int(cores) % 6
if mod != 0: 
  print "FATAL: The number of cores ("+str(cores)+") must be divisible by 6"
  sys.exit(0)
elif verbose or vv:
  print str(cores)+" is divisible by 6"
if verbose or vv:
 print "Calculate the number of nodes needed"
nodes = float(cores)*float(threads)/corespernode
nodes = math.ceil(nodes)
if not q:
 print "Number of nodes to request = ", int(nodes)
lay=int(cores)/6
mod4=lay%4
mod6=lay%6
mod3=lay%3

if mod4 == 0:
   layout = run_utils.reg_layout (lay,4)
   iolay="1,4"
elif mod6 == 0:
   layout = run_utils.reg_layout (lay,6)
   iolay="1,3"
elif mod3 == 0:
   layout = run_utils.reg_layout (lay,3)
   iolay="1,3"
else:
   print "FATAL: "+str(cores)+"/6 = "+str(lay)+" which is not divisible by 4, 6 or 3"
   sys.exit(1)
if verbose or vv:
 print "The layout is "+layout

## Cores is divisible by 6 (checked above)
ocean_layout = run_utils.reg_layout (int(cores),6)
oceanio = "1,3"
if verbose or vv:
 print "The ocean/ice layout is "+ocean_layout
#####################################################################################
if verbose or vv:
 print "Make the tmp directory to work in and copy templates there"
os.system("mkdir /tmp/scriptwork")
os.system("cp /apps/gcpre/google/scripts/"+exp+"_run_script.sh /tmp/scriptwork")
os.system("cp /apps/gcpre/google/scripts/"+exp+"_input.nml /tmp/scriptwork")

if verbose or vv:
 print "Open template /tmp/scriptwork/"+exp+"_run_script.sh"
f=open("/tmp/scriptwork/"+exp+"_run_script.sh",'r')
if verbose or vv:
 print "Open script for writing /tmp/scriptwork/"+cores+"_"+threads+"_"+exp+"_run_script.sh"
new=open("/tmp/scriptwork/"+cores+"_"+threads+"_"+exp+"_run_script.sh",'w')

if verbose or vv:
 print "Edit the script template"
run_utils.template_script(f,new,cores,nodes,exp,threads,workDir,executable,vv)
if verbose:
 print "Close script templates"
elif vv:
 print "Close /tmp/scriptwork/"+exp+"_run_script.sh and /tmp/scriptwork/"+cores+"_"+threads+"_"+exp+"_run_script.sh" 
f.close()
new.close()

## Edit the namelist
if verbose or vv:
 print "Open template /tmp/scriptwork/"+exp+"input.nml"
nml=open("/tmp/scriptwork/"+exp+"_input.nml",'r')
if verbose or vv:
 print "Open namelist for writing /tmp/scriptwork/"+exp+"_input.nml."+cores
newnml=open("/tmp/scriptwork/"+exp+"_input.nml."+cores,'w')
if verbose or vv:
 print "Edit the namelist template"
run_utils.template_nml(nml,newnml,cores,nodes,threads,layout,iolay,ocean_layout,oceanio,nh,nd,nm,vv)
if verbose:
 print "Close namelist templates"
elif vv:
 print "Close /tmp/scriptwork/"+exp+"_input.nml and /tmp/scriptwork/"+exp+"_input.nml."+cores
nml.close()
newnml.close()

if not q:
 print "Setting up  ",workDir
if verbose or vv:
 print "mkdir -p "+workDir
 print "mkdir -p "+workDir+"/INPUT"
 print "mkdir -p "+workDir+"/RESTART"
os.system("mkdir -p "+workDir)
os.system("mkdir -p "+workDir+"/INPUT")
os.system("mkdir -p "+workDir+"/RESTART")
if verbose or vv:
 print "cp /tmp/scriptwork/"+exp+"_input.nml."+cores+" "+workDir+"/input.nml"
 print "cp /tmp/scriptwork/"+cores+"_"+threads+"_"+exp+"_run_script.sh "+ workDir
 print "cp /home/data/AM4/AM4_run/*table " + workDir
os.system("cp /tmp/scriptwork/"+exp+"_input.nml."+cores+" "+workDir+"/input.nml" )
os.system("cp /tmp/scriptwork/"+cores+"_"+threads+"_"+exp+"_run_script.sh "+ workDir) 
os.system("cp /home/data/AM4/AM4_run/*table " + workDir)
if verbose or vv:
  print "ls "+ workDir
  os.system("ls " + workDir)
os.system("ln -s /home/data/AM4/AM4_run/INPUT/* "+workDir+"/INPUT")
if vv:
  print "ls "+ workDir + "/INPUT"
  os.system("ls -lh " + workDir + "/INPUT")

## If submitting the script, submit it
if submit:
   if verbose or vv:
      print submitProg+" "+workDir+"/"+cores+"_"+threads+"_"+exp+"_run_script.sh"
   elif not q:
      print "Submitting with "+ submitProg
   os.system(submitProg+" "+workDir+"/"+cores+"_"+threads+"_"+exp+"_run_script.sh")
elif not q:
   print "The run script is located at "+workDir+"/"+cores+"_"+threads+"_"+exp+"_run_script.sh"

## Clean up /tmp
if verbose or vv:
 print "rm -rf /tmp/scriptwork"
os.system("rm -rf /tmp/scriptwork")
