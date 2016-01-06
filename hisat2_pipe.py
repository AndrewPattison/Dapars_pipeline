#!/usr/bin/python
""" This pipelie is designed to take a human fastq file and allign it using hisat2 to GRCh38 ensembl assembly 82.
Usage: python hisat2_pipe.py <input file name/fiile names> <output file prefix>"""

import sys
import os.path
from subprocess import call 


def run_aligner (arguments):
	
	fq_files = arguments
	
	for some_file in fq_files:
		split_fq = some_file.split(".")
		fq_file = split_fq[0]

		call (["mkdir","raw_fastq_files", "sam_files", "bam_files", "sorted_bams"])

		if os.path.isfile("sam_files/"+ fq_file + ".sam") == False:
			call (["hisat2", "-q", "-p", "8", "-x", "~/reference/Ens_GRCc38_82", "-U", "raw_fastq_files/" + some_file, "-S", "sam_files/"+ fq_file + ".sam"])
		
		if os.path.isfile("bam_files/" + fq_file+ ".bam") == False:		
			call (["samtools", "view","-o", "bam_files/" + fq_file+ ".bam", "-bS", "-@", "7", "sam_files/"+ fq_file + ".sam"])
		
		if os.path.isfile("sorted_bams/"+fq_file + "_sorted"+".bam") == False:			
			call (["samtools", "sort", "-@12",  "bam_files/" + fq_file+ ".bam", "sorted_bams/"+fq_file + "_sorted"]) 

		call (["samtools", "index", "sorted_bams/"+ fq_file + "_sorted.bam"]) 
	return

if __name__ == "__main__":

    run_aligner (sys.argv[1:])
    print "done"