#!/usr/local/bin/python2.7
# mothur_script_Miseq
# main driver for Mothur pipeline
# Dominique brown
# partially adapted from Kira Vasquez, Randall Johnson and Nikhil Gowda code
# BSP CCR Genetics Core at Frederick National Laboratory
# Leidos Biomedical Research, Inc
# Created September-ish 2013
# Last Modified November 02, 2014

import os
import sys
import subprocess



### set up arguments ###

args = dict()
for a in sys.argv[1:len(sys.argv)]:
      args[a[0:a.find('=')]] = a[a.find('=')+1:len(a)]

print('\nArgs:')
print(args)
print('\n')
#################
summary = ""
fasta = ""
names = ""
groups = ""
taxonomy = ""
reference = ""
align= ""


### set up function system call with updating summary/fasta/names/groups filename ###
def sysio(cmd, updateSummary, updateFasta, updateNames, updateGroups, updateTax):
      global summary
      global fasta
      global names
      global groups
      global taxonomy
      p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
      out = p.communicate()[0]
      p.wait()
      if updateSummary:
            summary = out[out[0:out.rfind(".summary")].rfind("\n")+1:out[out.rfind(".summary"):len(out)].find("\n")+out.rfind(".summary")]
      if updateFasta:
            fasta = out[out[0:out.rfind(".fasta")].rfind("\n")+1:out[out.rfind(".fasta"):len(out)].find("\n")+out.rfind(".fasta")]
      if updateNames:
            names = out[out[0:out.rfind(".names")].rfind("\n")+1:out[out.rfind(".names"):len(out)].find("\n")+out.rfind(".names")]
      if updateGroups:
            groups = out[out[0:out.rfind(".groups")].rfind("\n")+1:out[out.rfind(".groups"):len(out)].find("\n")+out.rfind(".groups")]
      if updateTax:
            taxonomy = out[out[0:out.rfind(".taxonomy")].rfind("\n")+1:out[out.rfind(".taxonomy"):len(out)].find("\n")+out.rfind(".taxonomy")]
      return out


####################
#defaults
installed = '../MiSeqPipeline/'
execfile(installed+'defaults.py')
os.chdir('testing')
#################

#extract the sequence and quality score data from your fastq files, create the reverse complement of the reverse read and then join the reads into contigs

os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
                    "make.contigs(file="+files+", processors="+str(nprocessors)+")\"")  


fasta = files[0:files.find('files')] + 'trim.contigs.fasta'                   
groups = files[0:files.find('files')] + 'contigs.groups' 
print fasta
print groups                

########
#take care of any irregular lengths
          
os.system("mothur \"#set.logfile(name=master.logfile, append=T); screen.seqs(fasta="+fasta+", group="+groups+", maxambig="+maxambig+", maxlength="+maxlength+")\"")   

fasta = fasta[0:fasta.find('fasta')] + 'good.fasta'
groups = groups[0:groups.find("groups")] + "good.groups"
print fasta

#os.system("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+fasta+")\"") 


############################

###Processing improved sequences


#search for uniques and take away duplications
os.system("mothur \"#set.logfile(name=master.logfile, append=T); unique.seqs(fasta="+fasta+")\"")   

names=fasta[0:fasta.find('fasta')] + 'names'
fasta=fasta[0:fasta.find('fasta')] + 'unique.fasta'   
print fasta
print names


#generates a table where the rows are the names of the unique seqeunces and the columns are the names of the groups. The table is then filled with the number of times each unique sequence shows up in each group
                                 

os.system("mothur \"#set.logfile(name=master.logfile, append=T); count.seqs(name="+names+", group="+groups+")\"")  

count=fasta[0:fasta.find('unique.fasta')] + 'count_table'   
print count

#os.system("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+count+")\"")





#remove the leading and trailing dots we will set keepdots to false. You could also run this command using your primers of interest 


os.system("mothur \"#set.logfile(name=master.logfile, append=T); pcr.seqs(fasta="+pcrseqs_reference+", start="+pcrseqs_start+", end="+pcrseqs_end+", keepdots="+keepdots+", processors=8)\"") 

pcrseqs_reference=pcrseqs_reference[0:pcrseqs_reference.find('fasta')] + 'pcr.fasta'    

print pcrseqs_reference

#os.system("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+pcrseqs_reference+")\"")


#improve the overall alignment quality

os.system("mothur \"#set.logfile(name=master.logfile, append=T); align.seqs(fasta="+fasta+", reference="+pcrseqs_reference+")\"")   
align=fasta[0:fasta.find('unique.fasta')] + 'unique.align'
print align

os.system("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+align+", count="+count+")\"")
summary=fasta[0:fasta.find('fasta')] + 'summary'
print summary

########################

#To make sure that everything overlaps the same region we'll re-run screen.seqs to get sequences that start at or before position 1968 and end at or after position 11550

os.system("mothur \"#set.logfile(name=master.logfile, append=T); screen.seqs(fasta="+align+", count="+count+", summary="+summary+", start="+screenseqs_start+", end="+screenseqs_end+", maxhomop="+maxhomop+")\"")


os.system("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+align+", count="+count+")\"")
summary=summary[0:summary.find('summary')] + 'good.summary'
print summary

align=align[0:align.find('align')] + 'good.align'
print align                                                    
count=count[0:count.find('count')] + 'good.count_table'
print count
#we'll filter the sequences to remove the overhangs at both ends

os.system("mothur \"#set.logfile(name=master.logfile, append=T); filter.seqs(fasta="+align+", vertical="+vertical+", trump="+trump+")\"")  
fasta=fasta[0:fasta.find('fasta')] + 'good.filter.fasta'     
print fasta
#we've perhaps created some redundancy across our sequences by trimming the ends

os.system("mothur \"#set.logfile(name=master.logfile, append=T); unique.seqs(fasta="+fasta+", count="+count+")\"")
fasta=fasta[0:fasta.find('fasta')] + 'unique.fasta'
print fasta
count=count[0:count.find('good.count_table')] + 'unique.good.filter.count_table'
print count
#split the sequences by group and then sort them by abundance and go from most abundant to least and identify sequences that are within 2 nt of each other. If they are then they get merged. We generally favor allowing 1 difference for every 100 bp of sequence

os.system("mothur \"#set.logfile(name=master.logfile, append=T); pre.cluster(fasta="+fasta+", count="+count+", diffs="+diffs+")\"")
fasta=fasta[0:fasta.find('fasta')] + 'precluster.fasta'
print fasta
count=count[0:count.find('count')] + 'unique.precluster.count_table'
print count

######################

#removing chimeras
os.system("mothur \"#set.logfile(name=master.logfile, append=T); chimera.uchime(fasta="+fasta+", count="+count+", dereplicate="+dereplicate+")\"")
count=count[0:count.find('count')] + 'uchime.pick.count_table'
print count
accnos=fasta[0:fasta.find('fasta')] + 'uchime.accnos'
print accnos


######################

#remove those sequences from the fasta file

os.system("mothur \"#set.logfile(name=master.logfile, append=T); remove.seqs(fasta="+fasta+", accnos="+accnos+")\"")
fasta=fasta[0:fasta.find('fasta')] + 'pick.fasta'
print fasta
sysio("mothur \"#set.logfile(name=master.logfile, append=T); summarry.seqs(fasta="+fasta+", count="+count+")\"", True, False, False, False, False)
os.system("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+fasta+", count="+count+")\"")


#we need to see if there are any "undesirables" in our dataset. Sometimes when we pick a primer set they will amplify other stuff that gets to this point in the pipeline such as 18S rRNA gene fragments or 16S rRNA from Archaea, chloroplasts, and mitochondira. There's also just the random stuff that we want to get rid of.

os.system("mothur \"#set.logfile(name=master.logfile, append=T); classify.seqs(fasta="+fasta+", count="+count+", reference="+classifyseqs_reference+", taxonomy="+taxonomy+", cutoff="+classifyseqs_cutoff+")\"")

taxonomy2=fasta[0:fasta.find('fasta')] + 'pds.wang.taxonomy'
print taxonomy2
##########################

#reads a taxonomy file and a taxon and generates a new file that contains only the sequences not containing that taxon
os.system("mothur \"#set.logfile(name=master.logfile, append=T); remove.lineage(fasta="+fasta+", count="+count+", taxonomy="+taxonomy2+", taxon="+taxon+")\"")
fasta=fasta[0:fasta.find('fasta')] + 'pick.fasta'
print fasta
count=count[0:count.find('count')] + 'pick.count_table'
print count
taxonomy2=taxonomy2[0:taxonomy2.find('taxonomy')] + 'pick.taxonomy'  
print taxonomy2
###Assessing error rates

#we want to pull the sequences out
os.system("mothur \"#set.logfile(name=master.logfile, append=T); get.groups(count="+count+", fasta="+fasta+", groups="+groups1+")\"")
fasta=fasta[0:fasta.find('fasta')] + 'pick.fasta'
print fasta
count=count[0:count.find('count')] + 'pick.count_table'
print count

 

#measure the error rates
os.system("mothur \"#set.logfile(name=master.logfile, append=T); seq.error(fasta="+fasta+", reference="+seqerror_reference+", aligned="+aligned+")\"")
summary=fasta[0:fasta.find('fasta')] + 'error.summary'
print summary

#can use R to get actual error rates
#s <- read.table(file="stability.trim.contigs.good.unique.good.filter.unique.precluster.pick.pick.pick.error.summary", header=T)
#ct <- read.table(file="stability.trim.contigs.good.unique.good.filter.unique.precluster.uchime.pick.pick.pick.count_table", header=T)
os.system("Rscript seqerror.R  "+summary+"  "+count+"") 
#help
#/Users/browndd/Desktop/MiseqPipeline
#This string of commands will produce a file for you
os.system("mothur \"#set.logfile(name=master.logfile, append=T); dist.seqs(fasta="+fasta+", cutoff="+distseqs_cutoff+")\"")
column=fasta[0:fasta.find('fasta')] + 'dist'
print column

os.system("mothur \"#set.logfile(name=master.logfile, append=T); cluster(column="+column+", count="+count+")\"")     #runs well
list=fasta[0:fasta.find('fasta')] + 'an.unique_list.list'
print list


os.system("mothur \"#set.logfile(name=master.logfile, append=T); make.shared(list="+list+", count="+count+", label=0.03)\"")
shared=fasta[0:fasta.find('fasta')] + 'an.unique_list.shared'
print shared
os.system("mothur \"#set.logfile(name=master.logfile, append=T); rarefaction.single(shared="+shared+")\"")
print shared

#os.system("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta = "+shared+")\"") # need fixed




###Preparing for analysis

#we want to remove the Mock sample from our dataset
os.system("mothur \"#set.logfile(name=master.logfile, append=T); remove.groups(count="+count+", fasta="+fasta+", taxonomy="+taxonomy2+", groups="+groups1+")\"")

###################################################

###OTUs

#clustering sequences into OTUs
os.system("mothur \"#set.logfile(name=master.logfile, append=T); dist.seqs(fasta="+fasta+", cutoff="+distseqs_cutoff+")\"")   #runs well

count=count[0:count.find('pick.count')] + 'count_table'
print count

os.system("mothur \"#set.logfile(name=master.logfile, append=T); cluster(column="+column+", count="+count+")\"")   #runs well



#we want to know how many sequences are in each OTU from each group 
os.system("mothur \"#set.logfile(name=master.logfile, append=T); make.shared(list="+list+", count="+count+", label="+label+")\"")
#os.system("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta = stability.trim.contigs.good.unique.good.filter.unique.precluster.pick.pick.pick.an.unique_list.fasta)\"") 




#We probably also want to know the taxonomy for each of our OTUs
os.system("mothur \"#set.logfile(name=master.logfile, append=T); classify.otu(list="+list+", count="+count+", taxonomy="+taxonomy2+", label="+label+")\"")

#################################

###Phylotypes

# you may desire to bin your sequences in to phylotypes according to their taxonomic classification
os.system("mothur \"#set.logfile(name=master.logfile, append=T); phylotype(taxonomy="+taxonomy2+")\"")




#want the genus-level shared file we'll do the following:
os.system("mothur \"#set.logfile(name=master.logfile, append=T); make.shared(list="+list+", count="+count+", label="+label2+")\"")




#We also want to know who these OTUs are 
os.system("mothur \"#set.logfile(name=master.logfile, append=T); classify.otu(list="+list+", count="+count+", taxonomy="+taxonomy2+", label="+label2+")\"")

#summary="stability.trim.contigs.good.unique.good.filter.unique.precluster.pick.pick.pick.an.unique_list.0.16.cons.tax.summary"



##########################################################
### Alpha Diversity ###
#if are_controls == 1:
#       #os.system("mothur \"#collect.single(shared="+x+".final.pick.an.0.03.subsample.shared, calc=chao-invsimpson, freq=100)\"")
# #if are_controls != 1:
#       #os.system("mothur \"#collect.single(shared="+x+".final.an.0.03.subsample.shared, calc=chao-invsimpson, freq=100)\"")

os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
        "collect.single(shared="+shared+", calc=chao-invsimpson, freq=100)\"")

sample_list = []
os.system("grep -l '0.03' *.invsimpson > .sample_list.out")  
num_lines3 = sum(1 for line in open('.sample_list.out'))
f = open('.sample_list.out')

for line in f:
      print line

for i in range(0, num_lines3):
      sample_list.append(f.readline())
      sample_list[i] = sample_list[i][:-1]

temp1 = []
summ = 0
invsimpson = []

for i in range(0, num_lines3):
      os.system("cut -f2 -s "+sample_list[i]+" | tail -n 5 > .temp_nums.out")  
      num_lines4 = sum(1 for line in open('.temp_nums.out'))
      f = open('.temp_nums.out')
      for j in range(0, num_lines4):
      	  temp1.append(f.readline())
      for z in range(0, num_lines4):
      	  summ += float(temp1[z])
      temp1 = []
      invsimpson.append(summ/num_lines4)
      summ = 0
      f.close()


f = open('.temp.adiv', 'w')   ###find .temp....
for i in range(0, len(invsimpson)):
      f.write(str(invsimpson[i]) + ' \n')
f.close()

#sample_list = []
#os.system("grep -l '0.03' "+x+"*.invsimpson > "+x+".sample_list.out")
#num_lines3 = sum(1 for line in open(''+x+'.sample_list.out'))
#f = open(''+x+'.sample_list.out')

#for i in range(0, num_lines3):
#       sample_list.append(f.readline())
#       sample_list[i] = sample_list[i][:-1]

#temp1 = []
#summ = 0
#invsimpson = []

#for i in range(0, num_lines3):
#       os.system("cut -f2 -s "+sample_list[i]+" | tail -n 5 > "+x+".temp_nums.out")
#       num_lines4 = sum(1 for line in open(''+x+'.temp_nums.out'))
#       f = open(''+x+'.temp_nums.out')
#       for j in range(0, num_lines4):
#       	  temp1.append(f.readline())
#       for z in range(0, num_lines4):
#       	  summ += float(temp1[z])
#       temp1 = []
#       invsimpson.append(summ/num_lines4)
#       summ = 0
      
#f = open(''+x+'.temp.adiv', 'w')
 #for i in range(0, len(invsimpson)):
  #     f.write(str(invsimpson[i]) + " \n")
      
### Generating Graphics Data File ###
#NEED TO DEVELOP A WAY TO HANDLE METADATA - FOR NOW MANUAL INPUT

#seqs = ["meta", "nseqs"]
#adiv = ["meta", "adiv"]
#barcode = ["meta", "Barcode"]
#variables = []
#num_lines = sum(1 for line in open('.temp.numseqs'))   ###find .temp....
#print "You must enter at least one set of independent categorical or continuous variables that describe each sample in order to generate plots!"
#cont = "1"

#while cont == "1":
 #     newvar = raw_input("Enter the name describing the first variable (eg. gender, age, etc.): ")
  #    newvarlist = []
   #   success = False
    #  while not success:
#            type = raw_input("Enter the type of variable that it is, cat for catergorical or cont for continuous (eg. gender is cat, age is cont): ")      
 #           if "cat" in type:
  #                newvarlist.append('cat')
   #               success = True
    #        if "cont" in type:
     #             newvarlist.append('cont')
      #            success = True
#      newvarlist.append(newvar)
 #     f = open('.temp.locs')   ###find .temp....
  #    for i in range(0, num_lines) :
   #         bcode = f.readline()
    #        value = raw_input("Enter value of " +newvar+ " describing " +bcode+ "(be sure to be consistent!) : ")
    #        newvarlist.append(value)
 #     f.close()
  #    variables.append(newvarlist)
   #   print ""
    #  print "Entry for variable completed."
     # print ""
 #     cont = raw_input("Are there more variables to define and enter? Enter 1 for yes or 2 for no: ")

#f = open('.temp.numseqs')   ###find .temp....
#for i in range(0, num_lines) :
#    seqs.append(f.readline())

#f.close()

#f = open('.temp.adiv')    ###find .temp....
#for i in range(0, num_lines) :
#    adiv.append(f.readline())

#f.close()

#f = open('.temp.locs')    ###find .temp....
#for i in range(0, num_lines) :
#    barcode.append(f.readline())

#f.close()

#for i in range(2, num_lines+2) :
#    barcode[i] = barcode[i][:-2]
#    adiv[i] = adiv[i][:-2]
 #   seqs[i] = seqs[i][:-2]

#f = open('graphics_data.txt', 'w')
#for i in range(0, num_lines+2):
 #     f.write(barcode[i]+"\t"+seqs[i]+"\t"+adiv[i]+"\t")
 #     for j in range(0, len(variables)):
  #          f.write(variables[j][i]+"\t")
#      f.write("\n")

#f.close()

 ### beta diversity ###


os.system("mothur \"#summary.shared(shared="+shared+", calc=thetayc)\"")

summary ="stability.trim.contigs.good.unique.good.filter.unique.precluster.pick.pick.pick.an.unique_list.summary"    ####find correct summary file

os.system("cut -f2 "+summary+" > .temp_sample1.out")     
num_lines5 = sum(1 for line in open('.temp_sample1.out'))
sample1 = []
f = open('.temp_sample1.out')

for i in range(0, num_lines5):
      sample1.append(f.readline())
   ###   f.close()

for i in range(0, len(sample1)):
      sample1[i] = sample1[i][:-1]

sample1[0] = "sample1"

os.system("cut -f3 "+summary+" > .temp_sample2.out")     
sample2 = []

f = open('.temp_sample2.out')

for i in range(0, num_lines5):
      sample2.append(f.readline())
#      f.close()

for i in range(0, len(sample2)):
      sample2[i] = sample2[i][:-1]

sample2[0] = "sample2"

os.system("cut -f5 "+summary+" > .temp_bdiv.out")   
bdiv = []
f = open('.temp_bdiv.out')

for i in range(0, num_lines5):
      bdiv.append(f.readline())
#      f.close()

for i in range(0, len(bdiv)):
      bdiv[i] = bdiv[i][:-1]

bdiv[0] = "bdiv"

os.system("cut -f7 "+summary+" > .temp_cmin.out")   
cmin = []
f = open('.temp_cmin.out')

for i in range(0, num_lines5):
      cmin.append(f.readline())
#f.close()

for i in range(0, len(cmin)):
      cmin[i] = cmin[i][:-1]

for i in range(1, len(cmin)):
      cmin[i] = 1 - float(cmin[i])

for i in range(1, len(cmin)):
      cmin[i] = str(cmin[i])

cmin[0] = "cmin"

os.system("cut -f6 "+summary+" > "".temp_cmax.out") 
cmax = []
f = open('.temp_cmax.out')  

for i in range(0, num_lines5):
      cmax.append(f.readline())

f.close()

for i in range(0, len(cmax)):
      cmax[i] = cmax[i][:-1]

for i in range(1, len(cmax)):
      cmax[i] = 1 - float(cmax[i])

for i in range(1, len(cmax)):
      cmax[i] = str(cmax[i])

cmax[0] = "cmax"

with open('beta_data.out', 'w') as f:                   
      for f1, f2, f3, f4, f5 in zip(sample1, sample2, bdiv, cmin, cmax):
            f.write(f1+"\t"+f2+"\t"+f3+"\t"+f4+"\t"+f5+"\n")
#f.close()






### USING mbGRAPHCIS R PACKAGE TO PRODUCE GRAPHS ###
seqs = ["meta", "nseqs"]
adiv = ["meta", "adiv"]
#num_lines = sum(1 for line in open('.temp.numseqs'))

#f = open('.temp.numseqs')    ## find 
#for i in range(0, num_lines) :
 #   seqs.append(f.readline())
#f.close()

f = open('.temp.adiv')   
for i in range(0, num_lines) :
    adiv.append(f.readline())
#f.close()

for i in range(2, num_lines+2) :
    barcode[i] = barcode[i][:-2]
    adiv[i] = adiv[i][:-2]
    seqs[i] = seqs[i][:-2]

#num_lines = sum(1 for line in open(metadata))
#f1 = open(metadata)
#lines = f1.readlines()
#f2 = open("final_data.txt", "w")   
for i in range(0, num_lines) :
      tabs = lines[i].split("\t")
      tabs[len(tabs)-1] = tabs[len(tabs)-1][0:tabs[len(tabs)-1].find('\n')]
      tabs.append(seqs[i])
      tabs.append(adiv[i])
      f2.write("\t".join(tabs)+"\n")
#f1.close()
#f2.close()

if not len(indvars) == 0 :
      f1 = open("final_data.txt")
      f2 = open("mb_graphics_data.txt", "w")
      lines = f1.readlines()
      numcols = len(lines[0].split("\t"))
      columns_to_ignore = []
      for i in range(0, numcols) :
            if lines[0].split("\t")[i] == "cat" or lines[0].split("\t")[i] == "cont" :
                  if not lines[1].split("\t")[i] in indvars :
                        columns_to_ignore.append(i)
      for i in range(0, num_lines) :
            tabs = lines[i].split("\t")
            tabs[len(tabs)-1] = tabs[len(tabs)-1][0:tabs[len(tabs)-1].find('\n')]
            tabs = [j for k, j in enumerate(tabs) if k not in columns_to_ignore]
            tabs.append(seqs[i])
            tabs.append(adiv[i])
            f2.write("\t".join(tabs)+"\n")
      f1.close()
      f2.close()
else:
      import shutil 
      shutil.copy2("final_data.txt", "mb_graphics_data.txt")   

#import inspect
#filename = inspect.getframeinfo(inspect.currentframe()).filename
#path = os.path.dirname(os.path.abspath(filename))      

os.system("Rscript graphall.R "+taxonomy+" "+shared+" "+min_stack_proportion+"")

#########os.system("Rscript graphall.R "+txconsensus+" "+txshared+" "+min_stack_proportion+"")







#####################################################


















#if are_controls == 1:
 #    os.system("mothur \"#summary.shared(shared="+x+".final.pick.an.shared, calc=thetayc)\"")

  #   os.system("cut -f2 "+x+".final.pick.an.shared.summary > "+x+".temp_sample1.out")
   #  num_lines5 = sum(1 for line in open(''+x+'.temp_sample1.out'))
#     sample1 = []
#     f = open(''+x+'.temp_sample1.out')
#     for i in range(0, num_lines5):
#         sample1.append(f.readline())
#     f.close()
       
#     for i in range(0, len(sample1)):
#         sample1[i] = sample1[i][:-1]
 #        sample1[0] = "sample1"

#     os.system("cut -f3 "+x+".final.pick.an.shared.summary > "+x+".temp_sample2.out")
#     sample2 = []
#     f = open(''+x+'.temp_sample2.out')
#     for i in range(0, num_lines5):
#         sample2.append(f.readline())
#     f.close()
#     for i in range(0, len(sample2)):
#         sample2[i] = sample2[i][:-1]
#         sample2[0] = "sample2"

#     os.system("cut -f5 "+x+".final.pick.an.shared.summary > "+x+".temp_bdiv.out")
#      bdiv = []
#      f = open(''+x+'.temp_bdiv.out')
#      for i in range(0, num_lines5):
#       	  bdiv.append(f.readline())
#      f.close()
#      for i in range(0, len(bdiv)):
#       	  bdiv[i] = bdiv[i][:-1]
#      bdiv[0] = "bdiv"

#      os.system("cut -f6 "+x+".final.pick.an.shared.summary > "+x+".temp_cmin.out")
#      cmin = []
#      f = open(''+x+'.temp_cmin.out')
#      for i in range(0, num_lines5):
#       	  cmin.append(f.readline())
#      f.close()
       
#      for i in range(0, len(cmin)):
#       	  cmin[i] = cmin[i][:-1]
      
#      for i in range(1, len(cmin)):
#       	  cmin[i] = 1 - float(cmin[i])
#      
#      for i in range(1, len(cmin)):
#       	  cmin[i] = str(cmin[i])
#      cmin[0] = "cmin"

#      os.system("cut -f7 "+x+".final.pick.an.shared.summary > "+x+".temp_cmax.out")
#      cmax = []
#      f = open(''+x+'.temp_cmax.out')
#      for i in range(0, num_lines5):
#       	  cmax.append(f.readline())
#      f.close()
      
#      for i in range(0, len(cmax)):
#       	  cmax[i] = cmax[i][:-1]
       
#      for i in range(1, len(cmax)):
#       	  cmax[i] = 1 - float(cmax[i])

 #     for i in range(1, len(cmax)):
 #      	  cmax[i] = str(cmax[i])
#      cmax[0] = "cmax"

# if are_controls != 1:
 #      os.system("mothur \"#summary.shared(shared="+x+".final.an.shared, calc=thetayc)\"")

#       os.system("cut -f2 "+x+".final.an.shared.summary > "+x+".temp_sample1.out")
#       num_lines5 = sum(1 for line in open(''+x+'.temp_sample1.out'))
#       sample1 = []
#       f = open(''+x+'.temp_sample1.out')
#       for i in range(0, num_lines5):
#       	  sample1.append(f.readline())
#       f.close()
#       for i in range(0, len(sample1)):
#       	  sample1[i] = sample1[i][:-1]
#       sample1[0] = "sample1"


#       os.system("cut -f3 "+x+".final.an.shared.summary > "+x+".temp_sample2.out")
 #      sample2 = []
#       f = open(''+x+'.temp_sample2.out')
#       for i in range(0, num_lines5):
#       	  sample2.append(f.readline())
#       f.close()
#       for i in range(0, len(sample2)):
#       	  sample2[i] = sample2[i][:-1]
#       sample2[0] = "sample2"

#       os.system("cut -f5 "+x+".final.an.shared.summary > "+x+".temp_bdiv.out")
#       bdiv = []
#       f = open(''+x+'.temp_bdiv.out')
#       for i in range(0, num_lines5):
#       	  bdiv.append(f.readline())
#       f.close()
#       for i in range(0, len(bdiv)):
#       	  bdiv[i] = bdiv[i][:-1]
#       bdiv[0] = "bdiv"

#       os.system("cut -f6 "+x+".final.an.shared.summary > "+x+".temp_cmin.out")
#       cmin = []
#       f = open(''+x+'.temp_cmin.out')
#       for i in range(0, num_lines5):
#       	  cmin.append(f.readline())
#       f.close()
#       for i in range(0, len(cmin)):
#       	  cmin[i] = cmin[i][:-1]
#       for i in range(1, len(cmin)):
#       	  cmin[i] = 1 - float(cmin[i])
#       for i in range(1, len(cmin)):
#       	  cmin[i] = str(cmin[i])
#       cmin[0] = "cmin"

#       os.system("cut -f7 "+x+".final.an.shared.summary > "+x+".temp_cmax.out")
#       cmax = []
#       f = open(''+x+'.temp_cmax.out')
#       for i in range(0, num_lines5):
#       	  cmax.append(f.readline())
#       f.close()
#       for i in range(0, len(cmax)):
#       	  cmax[i] = cmax[i][:-1]
#       for i in range(1, len(cmax)):
#       	  cmax[i] = 1 - float(cmax[i])
#       for i in range(1, len(cmax)):
#       	  cmax[i] = str(cmax[i])
#       cmax[0] = "cmax"

# with open(''+x+'.beta_data.out', 'w') as f:
#       for f1, f2, f3, f4, f5 in zip(sample1, sample2, bdiv, cmin, cmax):
#       	  f.write(f1+"\t"+f2+"\t"+f3+"\t"+f4+"\t"+f5+"\n")
# f.close()































#summ = numpy.genfromtxt(summary, skiprows=1, dtype='str')

#tmp = 0
#for i in summ[:,3]:
 #   if int(i) < 200: # count number of reads that are less than 200 bp long
     #   tmp += 1

#if tmp / summ.shape[0] > 0.2:
     # warnings.warn(str(tmp / summ.shape[0] * 100) +
      #              "% of unique reads are shorter than 200 bp.", Warning)


#fasta = fasta[0:fasta.find('fasta')] + 'trim.fasta'
#names = names[0:names.find('names')] + 'trim.names'
#os.system("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+fasta+", name="+names+")\"")


# save some effort by only analyzing unique sequences
#os.system("mothur \"#unique.seqs(fasta="+fasta+", name="+names+")\"")

#fasta = fasta[0:fasta.find('fasta')] + 'unique.fasta'
#names = names[0:names.find('names')] + 'unique.names'
#out = sysio("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+fasta+", name="+names+")\"", True, False, False, False, False)
#out = out[out.find("97.5%-tile:")+12:len(out)]
#out = out[out.find("\t")+1:len(out)]
#out = out[out.find("\t")+1:len(out)]
#3nbases = out[0:out.find("\t")]

# initial alignment
# oops...If you didn't get them flipped in the correct direction - use flip=T
#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
              #      "align.seqs(fasta="+fasta+", reference=silva.bacteria.fasta, flip=F, processors="+str(nprocessors)+")\"")

#fastacheck = fasta[0:fasta.find('fasta')] + 'align'
#out = sysio("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+fastacheck+", name="+names+")\"", True, False, False, False, False)
#out = out[out.find("97.5%-tile:")+12:len(out)]
#out = out[out.find("\t")+1:len(out)]
#out = out[out.find("\t")+1:len(out)]
#nbasesafter = out[0:out.find("\t")]

#if int(nbasesafter)/int(nbases) <= 0.5 :
 #     print("Warning: Attempting to flip direction and re-allign sequences.")
  #    os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
   #                 "align.seqs(fasta="+fasta+", reference=silva.bacteria.fasta, flip=T, processors="+str(nprocessors)+")\"")
    #  fastacheck = fasta[0:fasta.find('fasta')] + 'align'
#      out = sysio("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+fastacheck+", name="+names+")\"", True, False, False, False, False)
 #     out = out[out.find("97.5%-tile:")+12:len(out)]
  #    out = out[out.find("\t")+1:len(out)]
   #   out = out[out.find("\t")+1:len(out)]
#      nbasesafter = out[0:out.find("\t")]
#            if int(nbasesafter)/int(nbases) <= 0.5 :
 #           raise Exception("Error in aligning sequences! nbases too low.")
  #    fasta =  fastacheck
   #   print("Flipping was successful!")

# screen the sequences so we only keep the stuff in the region we are interested in :)
# 0:seqname 1:start 2:end 3:nbases 4:ambigs 5:polymer 6:numSeqs
#sysio("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+fasta+", name="+names+")\"", True, False, False, False, False)

#summ = numpy.genfromtxt(summary, skiprows=1, dtype='str')
#end = map(int, summ[:,2])

#if numpy.percentile(end, 25) != numpy.percentile(end, 75):
#    warnings.warn("Sequence endings are not consistent. Check to see if they have been flipped.", Warning)
#end = str(int(numpy.percentile(end, 50)))

#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
 #                   "screen.seqs(fasta="+fasta+", name="+names+", group="+groups+
  #                               ", end="+end+", optimize=start, criteria=95, processors="+str(nprocessors)+")\"")

#fasta = fasta[0:fasta.find('align')] + 'good.align'
#names = names[0:names.find('names')] + 'good.names'
#groups = groups[0:groups.find('groups')] + 'good.groups'

#os.system("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+fasta+", name="+names+")\"")


# filter the sequences so they all overlap the same region
#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
 #                   "filter.seqs(fasta="+fasta+", vertical=T, trump=., processors="+str(nprocessors)+")\"")

#fasta = fasta[0:fasta.find('align')] + 'filter.fasta' ####################################
#print fasta

# should get some more unique sequences
#os.system("mothur \"#set.logfile(name=master.logfile, append=T); unique.seqs(fasta="+fasta+", name="+names+")\"")

#fasta = fasta[0:fasta.find('fasta')] + 'unique.fasta'
#print fasta
#names = names[0:names.find('names')] + 'filter.names'

#os.system("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+fasta+", name="+names+")\"")


# precluster to help get rid of sequencing errors - also helps with computational efficiency
#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
 #                   "pre.cluster(fasta="+fasta+", name="+names+", group="+groups+", diffs=2)\"")

#fasta = fasta[0:fasta.find('fasta')] + 'precluster.fasta'
#print fasta
#names = names[0:names.find('names')] + 'unique.precluster.names'

#os.system("mothur \"#set.logfile(name=master.logfile, append=T); summary.seqs(fasta="+fasta+", name="+names+")\"")


# identify likely chimeras
#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
 #                   "chimera.uchime(fasta="+fasta+", name="+names+", group="+groups+", processors="+str(nprocessors)+")\"")

#accnos = fasta[0:fasta.find('fasta')] + 'uchime.accnos'
#tmp = numpy.genfromtxt(accnos, dtype='str')

# remove identified chimeras, throwing exception if all sequences were flagged as chimeras
#if tmp.shape[0] > 0:
  #  os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
  #                      "remove.seqs(accnos="+accnos+", fasta="+fasta+", name="+names+", " +
 #                                   "group="+groups+", dups=T)\"")
#else:
 #   raise Exception("All sequences flagged as chimeras!")

################# NIKHIL #################

#fasta = fasta[0:fasta.find('fasta')] + 'pick.fasta'
#print fasta
#names = names[0:names.find('names')] + 'pick.names'
#groups = groups[0:groups.find('groups')] + 'pick.groups'

# classify sequences using given taxonomy trainset
#os.system()
#out = sysio("mothur \"#set.logfile(name=master.logfile, append=T);" +
  #        "classify.seqs(fasta="+fasta+", name="+names+", group="+groups+
 #         ", template=trainset7_112011.pds.fasta, taxonomy=trainset7_112011.pds.tax, cutoff=80, processors="+str(nprocessors)+")\"", False, False, False, False, True)


#taxonomy = fasta[0:fasta.find('fasta')] + 'pds.taxonomy'
#accnos = fasta[0:fasta.find('fasta')] + 'pds.flip.accnos'

# remove contaminant mitochondria/chloroplast sequences
#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" + 
  #        "remove.lineage(fasta="+fasta+", name="+names+", group="+groups+", taxonomy="+taxonomy+
 #         ", taxon=Mitochondria-Cyanobacteria_Chloroplast-unknown)\"")

#taxonomy = taxonomy[0:taxonomy.find('taxonomy')] + 'pick.taxonomy'
#names = names[0:names.find('names')] + 'pick.names'
#fasta = fasta[0:fasta.find('fasta')] + 'pick.fasta'
#groups = groups[0:groups.find('groups')] + 'pick.groups'

# summary??

# final files
#os.system("cp "+fasta+" final.fasta")
#fasta = 'final.fasta'
#os.system("cp "+names+" final.names")
#names = 'final.names'
#os.system("cp "+groups+" final.groups")
#groups = 'final.groups'
#os.system("cp "+taxonomy+" final.taxonomy")
#taxonomy = 'final.taxonomy'

### get sequence data ###

#os.system("rm .seq_data.out") #in case a prior file by this name existed
#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" + 
 #         "count.groups(group="+groups+")\" > .seq_data.out")

### pull apart data in x.seq_data.out ###

#num_lines = sum(1 for line in open('.seq_data.out'))
#data = []
#f = open('.seq_data.out')
#for i in range(0, num_lines) :
 #     text = f.readline()
 #     if 'contains' in text:
#      	   data.append(text)
#f.close()
#locs = []
#nums = []
#for i in range(0, len(data)):
#      data[i] = data[i][:-2]
#for i in range(0, len(data)):
 #     temp1,_,temp2 = data[i].partition(' contains ')
  #    locs.append(temp1)
 #     nums.append(temp2)

### print warnings, find optimal sequence size and save ctrl seqs to file ###

#if arecontrols:
  #    ctrls = []
   #   num_lines2 = sum(1 for line in open(controlsfile))
  #    f = open(controlsfile)
   #   for i in range(0, num_lines2):
   #   	  ctrls.append(f.readline())
    #  f.close()
   #   for i in range(0, len(ctrls)):
  # 3   	  ctrls[i] = ctrls[i][:-1]
  #    ctrl_nums = []
 #     ctrl_warn = []
#      ctrl_locs = []
#      for i in range(0, len(ctrls)):
# #     	  for j in range(0, len(locs)-1):
 ##     	      if ctrls[i] == locs[j]:
#	      	 ctrl_locs.append(locs.pop(j))
#	      	 ctrl_nums.append(nums.pop(j))
 #     for i in range(0, len(ctrl_nums)):
 #     	  if float(ctrl_nums[i]) > 1000:
 #     	     ctrl_warn.append(ctrl_locs[i])

   #   f = open('.control.seqs', 'w')
   #   for i in range(0, len(ctrls)):
   #   	  f.write(ctrls[i] + ": " + ctrl_nums[i] + " \n")
   #   f.close()

  #    print ""
  #    print "Warning: the following control samples have an unusually high number of sequences: " + str(ctrl_warn)




#f.close()

#f = open('.temp.locs', 'w')
#for i in range(0, len(locs)):
 #     f.write(str(locs[i]) + " \n")
#f.close()

#low_warn = [] #This part grabs all samples with fewer than 3000 sequences
#for i in range(0, len(nums)):
  #    if float(nums[i]) < 3000:
  #    	   low_warn.append(locs[i])
#print ""
#print "Warning: the following samples have an unusually low number of sequences, they will be thrown out: " + str(low_warn)

### user may choose to keep low-sequence samples ###

#low_seq_nums = []
#for i in range(0, len(low_warn)):
  #    for j in range(0, len(nums)-1):
   #         if locs[j] == low_warn[i]:
   #              low_seq_nums.append(nums[j])
#p#rint ""
#for i in range(0, len(low_warn)):
 #     print low_warn[i] + " has " + low_seq_nums[i] + " sequences." #Prints those samples and their # of seqs

#Following loop removes those found low sequences names and numbers from the orig lists
#for i in range(0, len(low_warn)):
 #     for j in range(0, len(nums)-1):
 #           if locs[j] == low_warn[i]:
 ##                 locs.pop(j)
 #                 nums.pop(j)
#highest = 0 #This part finds the sample with the highest number of sequences
#for i in range(0, len(nums)):
   #   if float(nums[i]) > float(highest):
#            highest = float(nums[i])
#lowest = highest

#The following part finds the sample with the lowest number of sequences (which is consider the ideal lowest)
#for i in range(0, len(nums)):
# #     if float(nums[i]) < lowest:
 #           lowest = float(nums[i])
 #           ideal_loc = locs[i]
#print ""
#Following asks the user what the lowest should be. Recomends the ideal lowest. (Should we just use the ideal lowest?)
#print("The lowest number of sequences will be set to " + str(lowest) + " from " + ideal_loc + ".")

### remove controls ###

#if are_controls == 1:
   #   os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
    #            "remove.groups(fasta="+fasta+", accnos="+x+".control.samples, group="+groups+
    #            ", name="+names+".final.names, taxonomy="+taxonomy+")\"")
    #  fasta = fasta[0:fasta.find('fasta')] + 'pick.fasta'
    #  taxonomy = taxonomy[0:taxonomy.find('taxonomy')] + 'pick.taxonomy'
  #    names = names[0:names.find('names')] + 'pick.names'
   #   groups = groups[0:groups.find('groups')] + 'pick.groups'

### OTUs ###

#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
  #        "dist.seqs(fasta="+fasta+", cutoff=0.15, processors="+str(nprocessors)+")\"")

#dist = fasta[0:fasta.find('fasta')] + 'dist'

#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
 #         "cluster(column="+dist+", name="+names+")\"")

#list = fasta[0:fasta.find('fasta')] + 'an.list'

#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
 #         "make.shared(list="+list+", group="+groups+", label=0.03)\"")

#shared = list[0:list.find('list')] + 'shared'

#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
 #         "sub.sample(shared="+shared+", size="+str(int(lowest))+")\"")

#sharedold = shared #FIGURE OUT WHATS HAPPENING HERE - THIS IS BAD NOMENCLATURE - but works for now ;)
#shared = list[0:shared.find('shared')] + '0.03.subsample.shared'

#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
 #         "classify.otu(list="+list+", name="+names+", taxonomy="+taxonomy+", label=0.03)\"")

#txconsensus = taxonomy[0:taxonomy.find('taxonomy')] + 'an.0.03.cons.taxonomy'

#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
#          "phylotype(taxonomy="+taxonomy+", name="+names+", label=1)\"")

#txlist = fasta[0:fasta.find('fasta')] + 'tx.list'

#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
#          "make.shared(list="+txlist+", group="+groups+", label=1)\"")

#txshared = txlist[0:txlist.find('list')] + 'shared'

#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
  #        "sub.sample(shared="+txshared+", size="+str(int(lowest))+")\"")

#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
   #       "classify.otu(list="+txlist+", name="+names+", taxonomy="+taxonomy+", label=1)\"")
#txconsensus = taxonomy[0:taxonomy.find('taxonomy')] + 'tx.1.cons.taxonomy'

### Alpha Diversity ###

#os.system("mothur \"#set.logfile(name=master.logfile, append=T);" +
 #         "collect.single(shared="+shared+", calc=chao-invsimpson, freq=100)\"")

#sample_list = []
#os.system("grep -l '0.03' *.invsimpson > .sample_list.out")
#num_lines3 = sum(1 for line in open('.sample_list.out'))
#f = open('.sample_list.out')
#for i in range(0, num_lines3):
   #   sample_list.append(f.readline())
   #   sample_list[i] = sample_list[i][:-1]
#f.close()
#temp1 = []
#summ = 0
#invsimpson = []
#for i in range(0, num_lines3):
   #   os.system("cut -f2 -s "+sample_list[i]+" | tail -n 5 > .temp_nums.out")
   #   num_lines4 = sum(1 for line in open('.temp_nums.out'))
   #   f = open('.temp_nums.out')
    #  for j in range(0, num_lines4):
    #  	  temp1.append(f.readline())
    #  for z in range(0, num_lines4):
      #	  summ += float(temp1[z])
     # temp1 = []
     # invsimpson.append(summ/num_lines4)
     # summ = 0
     # f.close()
#f = open('.temp.adiv', 'w')
#for i in range(0, len(invsimpson)):
    #  f.write(str(invsimpson[i]) + ' \n')
#f.close()

### Generating Graphics Data File ###
#NEED TO DEVELOP A WAY TO HANDLE METADATA - FOR NOW MANUAL INPUT
#seqs = ["meta", "nseqs"]
#adiv = ["meta", "adiv"]
#barcode = ["meta", "Barcode"]
#variables = []
#num_lines = sum(1 for line in open('.temp.numseqs'))
#print "You must enter at least one set of independent categorical or continuous variables that describe each sample in order to generate plots!"
#cont = "1"
#while cont == "1":
#      newvar = raw_input("Enter the name describing the first variable (eg. gender, age, etc.): ")
#      newvarlist = []
#      success = False
#      while not success:
#            type = raw_input("Enter the type of variable that it is, cat for catergorical or cont for continuous (eg. gender is cat, age is cont): ")#            if "cat" in type:
#                  newvarlist.append('cat')
#                  success = True
#            if "cont" in type:
#                  newvarlist.append('cont')
#                  success = True
#      newvarlist.append(newvar)
#      f = open('.temp.locs')
#      for i in range(0, num_lines) :
#            bcode = f.readline()
#            value = raw_input("Enter value of " +newvar+ " describing " +bcode+ "(be sure to be consistent!) : ")
#            newvarlist.append(value)
#      f.close()
#      variables.append(newvarlist)
#      print ""
#      print "Entry for variable completed."
#      print ""
#      cont = raw_input("Are there more variables to define and enter? Enter 1 for yes or 2 for no: ")
#
#f = open('.temp.numseqs')
#for i in range(0, num_lines) :
#    seqs.append(f.readline())
#f.close()
#
#f = open('.temp.adiv')
#for i in range(0, num_lines) :
#    adiv.append(f.readline())
#f.close()
#
#f = open('.temp.locs')
#for i in range(0, num_lines) :
#    barcode.append(f.readline())
#f.close()

#for i in range(2, num_lines+2) :
#    barcode[i] = barcode[i][:-2]
#    adiv[i] = adiv[i][:-2]
#    seqs[i] = seqs[i][:-2]
#
#f = open('graphics_data.txt', 'w')
#for i in range(0, num_lines+2):
#      f.write(barcode[i]+"\t"+seqs[i]+"\t"+adiv[i]+"\t")
#      for j in range(0, len(variables)):
#            f.write(variables[j][i]+"\t")
#      f.write("\n")
#f.close()

### Beta Diversity ###

#out = sysio("mothur \"#summary.shared(shared="+sharedold+", calc=thetayc)\"", True, False, False, False, False)

#summary = sharedold + '.summary'

#os.system("cut -f2 "+summary+" > .temp_sample1.out")
#num_lines5 = sum(1 for line in open('.temp_sample1.out'))
#sample1 = []
#f = open('.temp_sample1.out')
#for i in range(0, num_lines5):
    #  sample1.append(f.readline())
#f.close()
#for i in range(0, len(sample1)):
 #     sample1[i] = sample1[i][:-1]
#sample1[0] = "sample1"

#os.system("cut -f3 "+summary+" > .temp_sample2.out")
#sample2 = []
#f = open('.temp_sample2.out')
#for i in range(0, num_lines5):
 #     sample2.append(f.readline())
#f.close()
#for i in range(0, len(sample2)):
 #     sample2[i] = sample2[i][:-1]
#sample2[0] = "sample2"

#os.system("cut -f5 "+summary+" > .temp_bdiv.out")
#bdiv = []
#f = open('.temp_bdiv.out')
#for i in range(0, num_lines5):
 #     bdiv.append(f.readline())
#f.close()
#for i in range(0, len(bdiv)):
 #     bdiv[i] = bdiv[i][:-1]
#bdiv[0] = "bdiv"

#os.system("cut -f7 "+summary+" > .temp_cmin.out")
#cmin = []
#f = open('.temp_cmin.out')
#for i in range(0, num_lines5):
 #     cmin.append(f.readline())
#f.close()
#for i in range(0, len(cmin)):
 #     cmin[i] = cmin[i][:-1]
#for i in range(1, len(cmin)):
 #     cmin[i] = 1 - float(cmin[i])
#for i in range(1, len(cmin)):
 #     cmin[i] = str(cmin[i])
#cmin[0] = "cmin"

#os.system("cut -f6 "+summary+" > "".temp_cmax.out")
#cmax = []
#f = open('.temp_cmax.out')
#for i in range(0, num_lines5):
 #     cmax.append(f.readline())
#f.close()
#for i in range(0, len(cmax)):
 #     cmax[i] = cmax[i][:-1]
#for i in range(1, len(cmax)):
 #     cmax[i] = 1 - float(cmax[i])
#for i in range(1, len(cmax)):
 #     cmax[i] = str(cmax[i])
#cmax[0] = "cmax"

#with open('beta_data.out', 'w') as f:
 #     for f1, f2, f3, f4, f5 in zip(sample1, sample2, bdiv, cmin, cmax):
  #          f.write(f1+"\t"+f2+"\t"+f3+"\t"+f4+"\t"+f5+"\n")
#f.close()


### USING mbGRAPHCIS R PACKAGE TO PRODUCE GRAPHS ###
#seqs = ["meta", "nseqs"]
#adiv = ["meta", "adiv"]
#num_lines = sum(1 for line in open('.temp.numseqs'))

#f = open('.temp.numseqs')
#for i in range(0, num_lines) :
 #   seqs.append(f.readline())
#f.close()

#f = open('.temp.adiv')
#for i in range(0, num_lines) :
 #   adiv.append(f.readline())
#f.close()

#for i in range(2, num_lines+2) :
 #   barcode[i] = barcode[i][:-2]
  #  adiv[i] = adiv[i][:-2]
  #  seqs[i] = seqs[i][:-2]

#num_lines = sum(1 for line in open(metadata))
#f1 = open(metadata)
#lines = f1.readlines()
#f2 = open("final_data.txt", "w")
#for i in range(0, num_lines) :
#      tabs = lines[i].split("\t")
 #     tabs[len(tabs)-1] = tabs[len(tabs)-1][0:tabs[len(tabs)-1].find('\n')]
  #    tabs.append(seqs[i])
   #   tabs.append(adiv[i])
    #  f2.write("\t".join(tabs)+"\n")
#f1.close()
#f2.close()

#if not len(indvars) == 0 :
 #     f1 = open("final_data.txt")
  #    f2 = open("mb_graphics_data.txt", "w")
   #   lines = f1.readlines()
    #  numcols = len(lines[0].split("\t"))
     # columns_to_ignore = []
#      for i in range(0, numcols) :
 #           if lines[0].split("\t")[i] == "cat" or lines[0].split("\t")[i] == "cont" :
 #                 if not lines[1].split("\t")[i] in indvars :
 #                       columns_to_ignore.append(i)
 #     for i in range(0, num_lines) :
 #           tabs = lines[i].split("\t")
 #           tabs[len(tabs)-1] = tabs[len(tabs)-1][0:tabs[len(tabs)-1].find('\n')]
 #           tabs = [j for k, j in enumerate(tabs) if k not in columns_to_ignore]
 #           tabs.append(seqs[i])
 #           tabs.append(adiv[i])
#            f2.write("\t".join(tabs)+"\n")
#      f1.close()
#      f2.close()
#else:
 #     import shutil 
  #    shutil.copy2("final_data.txt", "mb_graphics_data.txt")

#import inspect
#filename = inspect.getframeinfo(inspect.currentframe()).filename
#path = os.path.dirname(os.path.abspath(filename))      
#os.system("Rscript "+path+"graphall.R "+txconsensus+" "+txshared+" "+min_stack_proportion+"")

#########os.system("Rscript graphall.R "+txconsensus+" "+txshared+" "+min_stack_proportion+"")




#################################### IGNORE VVVVVVVVV



#os.system("mothur \"#summary.seqs(fasta="+x+".shhh.trim.unique.good.filter.unique.precluster.pick.fasta, name="+x+".shhh.trim.unique.good.filter.unique.precluster.pick.names)\"")

#os.system("mothur \"#classify.seqs(fasta="+x+".shhh.trim.unique.good.filter.unique.precluster.pick.fasta, name="+x+".shhh.trim.unique.good.filter.unique.precluster.pick.names, group="+x+".shhh.good.pick.groups, template=trainset7_112011.pds.fasta, taxonomy=trainset7_112011.pds.tax, cutoff=80, processors=12)\"")

#os.system("mothur \"#remove.lineage(fasta="+x+".shhh.trim.unique.good.filter.unique.precluster.pick.fasta, name="+x+".shhh.trim.unique.good.filter.unique.precluster.pick.names, group="+x+".shhh.good.pick.groups, taxonomy="+x+".shhh.trim.unique.good.filter.unique.precluster.pick.pds.taxonomy, taxon=Mitochondria-Cyanobacteria_Chloroplast-unknown)\"")
#os.system("mothur \"#summary.seqs(fasta="+x+".shhh.trim.unique.good.filter.unique.precluster.pick.pick.fasta, name="+x+".shhh.trim.unique.good.filter.unique.precluster.pick.pick.names)\"")

### shortening to final file names ###

#os.system("mothur \"#system(cp "+x+".shhh.trim.unique.good.filter.unique.precluster.pick.pick.fasta "+x+".final.fasta)\"")
#os.system("mothur \"#system(cp "+x+".shhh.trim.unique.good.filter.unique.precluster.pick.pick.names "+x+".final.names)\"")
#os.system("mothur \"#system(cp "+x+".shhh.good.pick.pick.groups "+x+".final.groups)\"")
#os.system("mothur \"#system(cp "+x+".shhh.trim.unique.good.filter.unique.precluster.pick.pds.pick.taxonomy "+x+".final.taxonomy)\"")

# ### get sequence data ###

# #os.system("mothur \"#count.groups(group="+x+".final.groups)\" > "+x+".seq_data.out")

# ### pull apart data in x.seq_data.out ###

# num_lines = sum(1 for line in open(''+x+'.seq_data.out'))
# data = []
# f = open(''+x+'.seq_data.out')
# for i in range(0, num_lines-2) :
#       if i > 28:
#       	   data.append(f.readline())
#       else:
# 	   f.readline()
# f.close()
# locs = []
# nums = []
# for i in range(0, len(data)):
#       data[i] = data[i][:-2]
# for i in range(0, len(data)):
#       temp1,_,temp2 = data[i].partition(' contains ')
#       locs.append(temp1)
#       nums.append(temp2)

# ### print warnings, find optimal sequence size and save ctrl seqs to file ###

# are_controls = raw_input("Do you have controls? Enter 1 for 'yes' or 2 for 'no': ")
# are_controls = int(are_controls)
# if are_controls == 1:
#       ctrls = []
#       num_lines2 = sum(1 for line in open(''+x+'.control.samples'))
#       f = open(''+x+'.control.samples')
#       for i in range(0, num_lines2):
#       	  ctrls.append(f.readline())
#       f.close()
#       for i in range(0, len(ctrls)):
#       	  ctrls[i] = ctrls[i][:-1]
#       ctrl_nums = []
#       ctrl_warn = []
#       ctrl_locs = []
#       for i in range(0, len(ctrls)):
#       	  for j in range(0, len(locs)-1):
#       	      if ctrls[i] == locs[j]:
# 	      	 ctrl_locs.append(locs.pop(j))
# 	      	 ctrl_nums.append(nums.pop(j))
#       for i in range(0, len(ctrl_nums)):
#       	  if float(ctrl_nums[i]) > 1000:
#       	     ctrl_warn.append(ctrl_locs[i])

#       f = open(''+x+'.control.seqs', 'w')
#       for i in range(0, len(ctrls)):
#       	  f.write(ctrls[i] + ": " + ctrl_nums[i] + " \n")
#       f.close()

#       print ""
#       print "Warning: the following control samples have an unusually high number of sequences: " + str(ctrl_warn)


# f = open(''+x+'.temp.numseqs', 'w')
# for i in range(0, len(nums)):
#       f.write(str(nums[i]) + " \n")
# f.close()


# low_warn = []
# for i in range(0, len(nums)):
#       if float(nums[i]) < 3000:
#       	   low_warn.append(locs[i])
# print ""
# print "Warning: the following samples have an unusually low number of sequences: " + str(low_warn)

# ### user may choose to keep low-sequence samples ###

# low_seq_nums = []
# for i in range(0, len(low_warn)):
#       for j in range(0, len(nums)-1):
#       	   if locs[j] == low_warn[i]:
# 	      low_seq_nums.append(nums[j])
# print ""
# for i in range(0, len(low_warn)):
#       print low_warn[i] + " has " + low_seq_nums[i] + " sequences."


# for i in range(0, len(low_warn)):
#       for j in range(0, len(nums)-1):
#       	   if locs[j] == low_warn[i]:
# 	      locs.pop(j)
# 	      nums.pop(j)
# highest = 0
# for i in range(0, len(nums)):
#       if nums[i] > highest:
#       	   highest = nums[i]
# lowest = highest

# for i in range(0, len(nums)):
#       if nums[i] < lowest:
#       	   lowest = nums[i]
# 	   ideal_loc = locs[i]
# print ""
# lowest = raw_input("We recommend that the lowest number of sequences should be " + lowest + " from " + ideal_loc + ". What would you like to set the lowest allowed number of sequences to? ")

# ### remove controls ###

# if are_controls == 1:
#       os.system("mothur \"#remove.groups(fasta="+x+".final.fasta, accnos="+x+".control.samples, group="+x+".final.groups, name="+x+".final.names, taxonomy="+x+".final.taxonomy)\"")

# ### OTU section ###

# #if are_controls == 1:
#       #os.system("mothur \"#dist.seqs(fasta="+x+".final.pick.fasta, cutoff=0.15, processors=12)\"")

#       #os.system("mothur \"#cluster(column="+x+".final.pick.dist, name="+x+".final.pick.names)\"")

#       #os.system("mothur \"#make.shared(list="+x+".final.pick.an.list, group="+x+".final.pick.groups, label=0.03)\"")

#       #os.system("mothur \"#sub.sample(shared="+x+".final.pick.an.shared, size="+lowest+")\"")

#       #os.system("mothur \"#classify.otu(list="+x+".final.pick.an.list, name="+x+".final.pick.names, taxonomy="+x+".final.pick.taxonomy, label=0.03)\"")

#       #os.system("mothur \"#phylotype(taxonomy="+x+".final.pick.taxonomy, name="+x+".final.pick.names, label=1)\"")

#       #os.system("mothur \"#make.shared(list="+x+".final.pick.tx.list, group="+x+".final.pick.groups, label=1)\"")

#       #os.system("mothur \"#sub.sample(shared="+x+".final.pick.tx.shared, size="+lowest+")\"")

#       #os.system("mothur \"#classify.otu(list="+x+".final.pick.tx.list, name="+x+".final.pick.names, taxonomy="+x+".final.pick.taxonomy, label=1)\"")

# #if are_controls != 1:
#       #os.system("mothur \"#dist.seqs(fasta="+x+".final.fasta, cutoff=0.15, processors=12)\"")

#       #os.system("mothur \"#cluster(column="+x+".final.dist, name="+x+".final.names)\"")

#       #os.system("mothur \"#make.shared(list="+x+".final.an.list, group="+x+".final.groups, label=0.03)\"")

#       #os.system("mothur \"#sub.sample(shared="+x+".final.an.shared, size="+lowest+")\"")

#       #os.system("mothur \"#classify.otu(list="+x+".final.an.list, name="+x+".final.names, taxonomy="+x+".final.taxonomy, label=0.03)\"")

#       #os.system("mothur \"#phylotype(taxonomy="+x+".final.taxonomy, name="+x+".final.names, label=1)\"")

#       #os.system("mothur \"#make.shared(list="+x+".final.tx.list, group="+x+".final.groups, label=1)\"")

#       #os.system("mothur \"#sub.sample(shared="+x+".final.tx.shared, size="+lowest+")\"")

#       #os.system("mothur \"#classify.otu(list="+x+".final.tx.list, name="+x+".final.names, taxonomy="+x+".final.taxonomy, label=1)\"")

# ### alpha diversity ###

# #if are_controls == 1:
#       #os.system("mothur \"#collect.single(shared="+x+".final.pick.an.0.03.subsample.shared, calc=chao-invsimpson, freq=100)\"")
# #if are_controls != 1:
#       #os.system("mothur \"#collect.single(shared="+x+".final.an.0.03.subsample.shared, calc=chao-invsimpson, freq=100)\"")

# sample_list = []
# os.system("grep -l '0.03' "+x+"*.invsimpson > "+x+".sample_list.out")
# num_lines3 = sum(1 for line in open(''+x+'.sample_list.out'))
# f = open(''+x+'.sample_list.out')
# for i in range(0, num_lines3):
#       sample_list.append(f.readline())
#       sample_list[i] = sample_list[i][:-1]
# f.close()
# temp1 = []
# summ = 0
# invsimpson = []
# for i in range(0, num_lines3):
#       os.system("cut -f2 -s "+sample_list[i]+" | tail -n 5 > "+x+".temp_nums.out")
#       num_lines4 = sum(1 for line in open(''+x+'.temp_nums.out'))
#       f = open(''+x+'.temp_nums.out')
#       for j in range(0, num_lines4):
#       	  temp1.append(f.readline())
#       for z in range(0, num_lines4):
#       	  summ += float(temp1[z])
#       temp1 = []
#       invsimpson.append(summ/num_lines4)
#       summ = 0
#       f.close()
# f = open(''+x+'.temp.adiv', 'w')
# for i in range(0, len(invsimpson)):
#       f.write(str(invsimpson[i]) + " \n")
# f.close()

