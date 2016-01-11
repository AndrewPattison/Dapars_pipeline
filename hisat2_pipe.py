#!/usr/bin/python
""" This pipelie is designed to take a human fastq file and allign it using hisat2 to GRCh38 ensembl assembly 82.
Usage: python hisat2_pipe.py <input fiile names refernce directory bam_file_start (-b)>"""

import sys
import os.path
import glob
import datetime
from subprocess import call 

def run_dp ():
	# Build the DaPars index
	if os.path.isfile("genome_locations/extracted_3_p_utrs.bed") == False:
	 	call(["python", "pipeline/DaPars_Extract_Anno.py", "-b", glob.glob("genome_locations/*.bed")[0], "-s", glob.glob("genome_locations/*.txt")[0], "-o", "genome_locations/extracted_3_p_utrs.bed"])
	#Run the main DaPars tool config file will need to be set up first.
	if os.path.isfile("dp_out/*.txt") == False:
		call(["python", "pipeline/DaPars_main.py", "pipeline/DaPars_configure.txt"])
	if os.path.isfile("gff_files/dp.gff") == False:
	#Turn the dapars output into a gff file
		call(["python", "pipeline/dp_to_gff.py", str(glob.glob("dp_out/*.txt")[0]), "gff_files/dp.gff"])
	return


def add_chr (file_name):
	with open(file_name+".chr", 'w') as chr_write:
		 with open(file_name) as f:
			for line in f:
				chr_write.write("chr"+line)
	return

def get_chr_names_from_fai(reference_directory):
    index_file = glob.glob(reference_directory +"/*.fai")
    assert len(index_file) == 1, "You have more than one reference file"
    with open("genome_locations/genome.txt", "w") as out_f:
    	with open (index_file[0]) as f:
    		for line in f:
    			split_line = line.split("\t")
    			out_f.write(split_line[0] + "\t"+ split_line[1]+"\n")
    return 



def run_aligner (arguments, reference_directory, bs = False):

	fq_files = arguments

	if os.path.isfile("genome_locations/genome.txt") == False:		
		get_chr_names_from_fai(reference_directory)
	if os.path.isfile("genome_locations/genome.txt.chr") == False:	
		add_chr("genome_locations/genome.txt")


	for some_file in fq_files:
		split_fq = some_file.split(".")
		fq_file = split_fq[0]
		print "processing "+ fq_file

		if bs == False:	
			if os.path.isfile("sam_files/"+ fq_file + ".sam") == False:
				f= logfile
				call (["hisat2", "-q", "-p", "12", "-x", "~/reference/Ens_GRCc38_82", "-U", "raw_fastq_files/" + some_file, "-S", "sam_files/"+ fq_file + ".sam"], stderr = f)
				
			if os.path.isfile("bam_files/" + fq_file+ ".bam") == False:		
				call (["samtools", "view","-o", "bam_files/" + fq_file+ ".bam", "-bS", "-@", "12", "sam_files/"+ fq_file + ".sam"])
		
		if os.path.isfile("sorted_bams/"+fq_file + "_sorted"+".bam") == False:			
			call (["samtools", "sort", "-@12",  "bam_files/" + fq_file+ ".bam", "sorted_bams/"+fq_file + "_sorted"]) 

		if os.path.isfile("sorted_bams/"+ fq_file + "_sorted.bam.bai") == False:		
			call (["samtools", "index", "sorted_bams/"+ fq_file + "_sorted.bam"]) 

		if os.path.isfile("bed_files/"+fq_file + "_sorted"+".bed") == False:
			f = open ("bed_files/"+fq_file + "_sorted"+".bed", "w")
			call (["bamToBed","-split", "-i", "sorted_bams/"+fq_file + "_sorted"+".bam"], stdout = f) 
			f.close()

		if os.path.isfile("bed_files/"+ fq_file + "_sorted"+".bed.chr") == False:
			add_chr("bed_files/"+fq_file + "_sorted"+".bed")

		if os.path.isfile("wiggle_files/"+fq_file + "_sorted"+".wig") == False:
			f = open ("wiggle_files/"+fq_file + "_sorted"+".wig", "w")
			call (["genomeCoverageBed", "-split", "-i", "bed_files/"+fq_file + "_sorted"+".bed.chr", "-bg", "-g", "genome_locations/genome.txt.chr"], stdout = f) 
			f.close()

		if os.path.isfile("tdf_files/"+fq_file+".tdf") == False:
			call([ "igvtools", "toTDF", "wiggle_files/"+fq_file + "_sorted"+".wig", "tdf_files/"+fq_file+".tdf",glob.glob(reference_directory +"*.fa")[0]])
			 #igvtools toTDF wiggle_files/MCF_10_2_sorted.wig  tdf_files/test.tdf ~/reference/Homo_sapiens.GRCh38.dna.primary_assembly.fa


		

	return

if __name__ == "__main__":
	call (["mkdir","tdf_files", "gff_files","raw_fastq_files", "sam_files", "bam_files", "sorted_bams", "bed_files", "wiggle_files", "genome_locations", "dp_out", "logs"])
	logfile = open ("logs/" +"pipeline_run_on_"+ str(datetime.datetime.now()).replace(" ","")+".txt", "w")
	sys.stdout = logfile
	if sys.argv[-1] == "-b":
		reference_directory = sys.argv[-2]
		run_aligner (sys.argv[1:-2], reference_directory, bs= True)
	else:

		reference_directory = sys.argv[-1]
		run_aligner (sys.argv[1:-1], reference_directory, bs= False)
	run_dp()
	print "done"
	logfile.close()
	