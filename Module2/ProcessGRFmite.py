from Bio import SeqIO
import multiprocessing
from multiprocessing import Pool
import pandas as pd
import argparse
import regex as re
import os

parser = argparse.ArgumentParser()#pylint: disable=invalid-name
parser.add_argument("-g", "--genomeFile", help="Genome file in fasta format", required=True)
parser.add_argument("-name", "--genomeName", help="Genome Name", required=True)
parser.add_argument("-p", "--path", help="Source code path", required=True)
parser.add_argument("-t", "--processer", help="Number of processer", required=True)
parser.add_argument("-d", "--currentD", help="Path of current directory", required=True)


args = parser.parse_args()#pylint: disable=invalid-name

genome_file = args.genomeFile
genome_Name = args.genomeName
path=args.path
t=args.processer
dir=args.currentD
spliter="-+-"
targetDir=dir+"/"+genome_Name+"/"



def getContigNames(genomeFile,genomeName):
    records=list(SeqIO.parse(genomeFile,"fasta"))
    l=[rec.id for rec in records]
    f=pd.DataFrame(l)
    f.to_csv("%sContig.name"%(genomeName+spliter),header=None,index=None)



def RenameFasta(contigFile,genomeName):
    names=pd.read_csv(contigFile,header=None)
   # names=pd.read_table(contigFile,header=None)
    l_name=list(names[0].astype(str))
    for name in l_name:
        cp="cp %s/candidate.fasta %s"%(name,genomeName+spliter+name+spliter+"GRFmite.fa")
        os.system(cp)
        rm="rm -r %s"%(name)
        os.system(rm)
        rm = "rm %s"%(genomeName+spliter+name+".fa")
        os.system(rm)


def TArepeats(s):
    t=s.upper().count("T")
    a=s.upper().count("A")
    ta=t+a
    if (ta>len(s)*0.7):
        return True
    else:
        return False


def checkN(s):
    n=s.upper().count("N")
    if n>0:
        return True
    else:
        return False

def checkNPer(s):
    n=s.upper().count("N")
    p=n/len(s)
    if p>=0.20:
        return True
    else:
        return False

def findDigitsSum(string):
    pattern = '(\d+)'
    l = re.findall(pattern,string)
    return sum([int(i) for i in l])


def getSeqID(file):
    remove=[]
    records=list(SeqIO.parse(file,"fasta"))
    for rec in records:
        s=str(rec.seq)
        tirLen = findDigitsSum(rec.id.split(":")[-2])
        tir=str(rec.seq)[0:tirLen]
        if (TArepeats(s)==True or checkNPer(s)==True or TArepeats(tir)==True or checkN(tir)==True or len(s)<50):
            remove.append(rec.id)
    records=list(SeqIO.parse(file,"fasta"))
    l=[]
    for rec in records:
        tsd=rec.id.split(":")[-1]
        if (len(tsd)>6 or tsd=="TAA" or tsd=="TTA" or tsd=="TA" or str(rec.seq)[0:4]=="CACT") or str(rec.seq)[0:4]=="GTGA":
            l.append(rec.id)
    SeqIO.write((rec for rec in records if rec.id in l and rec.id not in remove), file+spliter+"p","fasta")
    


if __name__ == '__main__':
    os.chdir(targetDir)
#    getContigNames(genome_file, genome_Name)
#    RenameFasta("%sContig.name"%(genome_Name+spliter),genome_Name)
    Allfiles=os.listdir(".")
    files=[i for i in Allfiles if i[-10:]=="GRFmite.fa"]
    pool = multiprocessing.Pool(int(t))
    pool.map(getSeqID,files)
    pool.close()
    pool.join()
    




