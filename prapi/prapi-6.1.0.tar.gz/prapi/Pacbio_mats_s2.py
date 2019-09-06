def Pacbio_mats_s2(Output_dir,i):
	pass
	cmd="awk '{ split($2,ic_1,","); sum_ic_1=0; for (x in ic_1) sum_ic_1 += ic_1[x]; split($4,ic_2,","); sum_ic_2=0; for (x in ic_2) sum_ic_2 += ic_2[x]; split($3,sc_1,","); sum_sc_1=0; for (x in sc_1) sum_sc_1 += sc_1[x]; split($5,sc_2,","); sum_sc_2=0; for (x in sc_2) sum_sc_2 += sc_2[x]; if ( NR==1 || ( (sum_ic_2 + sum_sc_2 > 0) && (sum_ic_1 + sum_sc_1 > 0) && (sum_ic_1 != 0 || sum_ic_2 != 0) && (sum_sc_1 != 0 || sum_sc_2 != 0) && $6!=0 && $7!=0 ) ) {print $0}}' ${prefix}/JC/temp/JCEC.RNASeq.${i}.MATS.input.txt > ${prefix}/JC/temp/${i}.JCEC.input.txt"
	
