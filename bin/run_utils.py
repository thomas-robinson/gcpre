#!/bin/python
import re

def reg_layout (lay,ld):
   l1=lay/ld
   l2=ld
   return str(int(l1)) + "," + str(int(l2))


def template_script(infile,outfile,cores,nodes,exp,threads,workDir,executable,vv):
## Used to fill in the run script template
 totalcores = int(cores) * int(threads)
 for line in infile:
   newline = line
   newline = re.sub(r'TOTALNPES',str(totalcores),newline)
   newline = re.sub(r'MPINPES',cores,newline)
   newline = re.sub(r'EXPERIMENT',exp,newline)
   newline = re.sub(r'OMPTHREADS',threads,newline)
   newline = re.sub(r'WORKDIR',workDir,newline)
   newline = re.sub(r'NODES',str(int(nodes)),newline)
   newline = re.sub(r'EXECPATH',executable,newline)

   if vv:
    print newline
   outfile.write(newline)
 return 0

def template_nml(infile,outfile,cores,nodes,threads,layout,iolay,ocean_layout,oceanio,hours,days,months,vv):
## Used to fill in the namelist template
 for line in infile:
   newline = line
   newline = re.sub(r'TOTALNPES',cores,newline)
   newline = re.sub(r'OMPTHREADS',threads,newline)
   newline = re.sub(r'NODES',str(int(nodes)),newline)
   newline = re.sub(r'OCEANLAYOUT',ocean_layout,newline)
   newline = re.sub(r'LAYOUT',layout,newline)
   newline = re.sub(r'IOLAY',iolay,newline)
   newline = re.sub(r'OCEANIO',oceanio,newline)
   if hours:
      newline = re.sub(r'HOURS',hours,newline)
   else:
      newline = re.sub(r'HOURS',"0",newline)
   if days:
      newline = re.sub(r'DAYS',days,newline)
   else:
      newline = re.sub(r'DAYS',"0",newline)
   if months:
      newline = re.sub(r'MONTHS',months,newline)
   else:
      newline = re.sub(r'MONTHS',"0",newline)
   if vv:
    print newline
   outfile.write(newline)
 return 0

