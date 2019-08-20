import argparse
import sys
import random


def cigar_parse(cigar):
        cigar_listed=list(cigar)
        num=[]
        cigar_num_list=[]
        for i in range(len(cigar_listed)):
                if cigar_listed[i].isdigit():
                        num.append(cigar_listed[i])
                else:
                        num.append(cigar_listed[i])
                        cigar_num_list.append(num)
                        num=[]
        cigar_list=[]
        #print(cigar_num_list)
        for i in range(len(cigar_num_list)):
                cigar_list.append([])
                cigar_list[i].append(''.join(cigar_num_list[i][0:-1]))
                cigar_list[i].append(''.join(cigar_num_list[i][-1]))

        return cigar_list

def cigar_value(cigar_list):
	cigar_value=[]
	for i in range(len(cigar_list)):
		cigar_value.append(cigar_list[i][1])
	cigar_value=set(cigar_value)
	cigar_value=list(cigar_value)
	return cigar_value

def cigar_value_equal(Cigar_value,my_cigar_value):
	F_num=0
	more_cigar=[]
	for i in range(len(Cigar_value)):
		if Cigar_value[i] in my_cigar_value:
			pass
		else:
			print (Cigar_value[i],'is not in my_cigar_value')
			more_cigar.append(Cigar_value[i])
			F_num=F_um+1
	if F_num==0:
		return True
	else:
		return False


def flag_decision(flag):
    L=['A','B','C','D','E','F','G','H','I','J','K','L']
    d={'A':'PAIRED','B':'PROPER_PAIR','C':'UNMAP','D':'MUNMAP','E':'REVERSE','F':'MREVERSE','G':'READ1','H':'READ2','I':'SECONDARY','J':'QCFAIL','K':'DUP','L':'SUPPLEMENTARY'}

    value=bin(flag)
    L_value=list(value)
    L_value_full=L_value[2:-1]
    L_value_full.append(L_value[-1])     
    L_value_full.reverse()
    flag_string=[]
    for i in range(len(L_value_full)):
        if L_value_full[i]=='1':
            #print(d[L[i]],end=' ')
            flag_string.append(d[L[i]])
            
    if 'SUPPLEMENTARY' in flag_string:
        return True
    else:
        return False



def get_flag_value(aln_sam):
	flags={}
	f=open(aln_sam,'r')
	line=f.readline()
	column_1=line.split('\t')[0]
	column_1=list(column_1)
	while column_1[0]=='@':
        	line=f.readline()
        	column_1=line.split('\t')[0]
        	column_1=list(column_1)
	while line !='':
		if line.split('\t')[1] in flags.keys():
			flags[line.split('\t')[1]]=int(flags[line.split('\t')[1]])+1
		else:
			flags[line.split('\t')[1]]=1
		line=f.readline()
	f.close()
	return flags

def  get_reads_num(aln_sam):
	total_number=0
	reads_name=[]
	f=open(aln_sam,'r')
	line=f.readline()
	column_1=line.split('\t')[0]
	column_1=list(column_1)
	while column_1[0]=='@':
        	line=f.readline()
        	column_1=line.split('\t')[0]
        	column_1=list(column_1)
	while line !='':
		if line.split('\t')[0] in reads_name:
			pass
		else:
			reads_name.append(line.split('\t')[0])
		line=f.readline()
	f.close()
	return len(reads_name)


def call_s_i_d(ref,pos,cigar,query):
	pos_ref=int(pos)-1-1
	pos_query=0-1
	sub=0
	insert=0
	delete=0
	insertion=[]	
	true_insert_num=0
	true_insert_num_query_left=0
	true_insert_num_query_right=0
	true_insert_num_query=0
	true_insert_event_num=0
	insert_event=0
	for i in  range(len(cigar)):
		if cigar[i][1]=='X':
			X_num=int(cigar[i][0])
			pos_ref=pos_ref+X_num
			pos_query=pos_query+X_num
			sub=sub+X_num
		#print(cigar[i])
		elif cigar[i][1]=='I':
			I_num=int(cigar[i][0])
			true_insert_event_num=true_insert_event_num+1
			#print(pos_query)
			if I_num==1:
				insert_event=insert_event+1
				Insert=[]
				insert_sequence=query[pos_query+1:pos_query+I_num+1]
				query_insert_two_side=query[pos_query:pos_query+I_num+2]
				ref_insert_two_side=ref[pos_ref:pos_ref+2]
				Insert.append(insert_sequence)
				Insert.append(ref_insert_two_side)
				insertion.append(Insert)
			#print(query[pos_query+1:pos_query+I_num+1])
				if insert_sequence[0]==ref_insert_two_side[0] or insert_sequence[-1]==ref_insert_two_side[-1]:
					true_insert_num=true_insert_num+1	
				if insert_sequence[0]==query_insert_two_side[0] or insert_sequence[-1]==query_insert_two_side[-1]:
					true_insert_num_query=true_insert_num_query+1
				if insert_sequence[0]==query_insert_two_side[0]:
					true_insert_num_query_left=true_insert_num_query_left+1
				if insert_sequence[0]==query_insert_two_side[-1]:
					true_insert_num_query_right=true_insert_num_query_right+1
			pos_query=pos_query+I_num
			insert=insert+I_num
			#ref[pos_ref+pos_query:pos_ref+pos_query+I_num])			
		elif cigar[i][1]=='D':
			D_num=int(cigar[i][0])
			#print(ref[pos_ref+1:pos_ref+D_num+1])
			pos_ref=pos_ref+D_num
			delete=delete+D_num
			#print(pos_ref,pos_query)
		elif cigar[i][1]=='N':
			N_num=int(cigar[i][0])
			pos_ref=pos_ref+N_num
		elif  cigar[i][1]=='S':
			S_num=int(cigar[i][0])
			pos_query=pos_query+S_num
		elif  cigar[i][1]=='H':
			pass
		elif  cigar[i][1]=='P':
			pass
		elif cigar[i][1]=='=':
			e_num=int(cigar[i][0])
			pos_ref=pos_ref+e_num
			pos_query=pos_query+e_num
		elif cigar[i][1]=='M':
			M_num=int(cigar[i][0])
			for num in range(M_num):
				pos_ref=pos_ref+1
				pos_query=pos_query+1
				if ref[pos_ref]==query[pos_query]:
					pass
				else:
					sub=sub+1
		else:
			pass
	
	sub_insert_delete=[]
	sub_insert_delete.append(sub)
	sub_insert_delete.append(insert)
	sub_insert_delete.append(delete)
	sub_insert_delete.append(insert_event)
	sub_insert_delete.append(true_insert_num)
	sub_insert_delete.append(true_insert_num_query)
	sub_insert_delete.append(true_insert_num_query_left)
	sub_insert_delete.append(true_insert_num_query_right)
	sub_insert_delete.append(true_insert_event_num)
	#print(insertion)
	return sub_insert_delete

'''
main function below
'''							
def main_procedure(args):
	f1=open(args.ref_fasta,'r')
	f1.readline()
	ref=f1.readline()
	f1.close()



	print(get_flag_value(args.aln_sam))
	total_reads_true_number=get_reads_num(args.aln_sam)
	print(total_reads_true_number)

	f2=open(args.aln_sam,'r')
	line=f2.readline()
	column_1=line.split('\t')[0]
	column_1=list(column_1)
	while column_1[0]=='@':
		line=f2.readline()
		column_1=line.split('\t')[0]
		column_1=list(column_1)

	total_sub=0
	total_insert=0
	total_delete=0
	total_length=0
	total_reads_number=0
	total_valid_reads_number=0
	total_insert_event=0
	total_true_insert_num=0
	total_true_insert_num_query=0
	total_true_insert_num_query_left=0
	total_true_insert_num_query_right=0
	total_true_insert_event_num=0
	my_cigar_value=['M','I','D','N','S','H','P','=','X']
	sub_insert_delete=[]
	toatal_valid_reads_name=[]
	while line !='':
		total_reads_number=total_reads_number+1
		if line.split('\t')[1]=='4':
			line=f2.readline()
		elif int(line.split('\t')[4])>=args.MapQ_cut_off and flag_decision(int(line.split('\t')[1]))==False:
			total_valid_reads_number=total_valid_reads_number+1
			if line.split('\t')[0] in toatal_valid_reads_name:
				pass
			else:
				toatal_valid_reads_name.append(line.split('\t')[0])
			pos=line.split('\t')[3]
			cigar=line.split('\t')[5]
			query=line.split('\t')[9]
			query_name=line.split('\t')[0]
			cigar=cigar_parse(cigar)
			Cigar_value=cigar_value(cigar)
			value_result=cigar_value_equal(Cigar_value,my_cigar_value)
			if value_result == True:
				pass
			else:
				print ('my_cigar_value is not incomplete')
				break
			#print(cigar)
			s_i_d=call_s_i_d(ref,pos,cigar,query)
			sub_insert_delete.append(s_i_d)
			total_sub=total_sub+int(s_i_d[0])
			total_insert=total_insert+int(s_i_d[1])
			total_delete=total_delete+int(s_i_d[2])
			total_length=total_length+len(query)
			total_insert_event=total_insert_event+int(s_i_d[3])
			total_true_insert_num=total_true_insert_num+int(s_i_d[4])
			total_true_insert_num_query=total_true_insert_num_query+int(s_i_d[5])
			total_true_insert_num_query_left=total_true_insert_num_query_left+int(s_i_d[6])
			total_true_insert_num_query_right=total_true_insert_num_query_right+int(s_i_d[7])
			total_true_insert_event_num=total_true_insert_event_num+int(s_i_d[8])
			#print(s_i_d,len(query),query_name,Cigar_value)	
			line=f2.readline()
		else:
			line=f2.readline()
	f2.close()
	print('sub:insertion:deletion:total_length',total_sub,total_insert,total_delete,total_length)
	print('erro_ratio',float(total_sub/total_length),float(total_insert/total_length),float(total_delete/total_length))
	print('total_reads_number:valid_reads_number',total_valid_reads_number,total_reads_number)
	print('aln_sam_reads_use_ratio',float(total_valid_reads_number/total_reads_number))
	print('sing_base_insert_true_ref',float(total_true_insert_num/total_insert_event))
	print('sing_base_insert_true_query',float(total_true_insert_num_query/total_insert_event))
	print('sing_base_insert_true_query_left',float(total_true_insert_num_query_left/total_insert_event))
	print('sing_base_insert_true_query_right',float(total_true_insert_num_query_right/total_insert_event))
	print('total_insert_event',total_true_insert_event_num)
	print('sing_base_insert_ratio',float(total_insert_event/total_true_insert_event_num))
	print('toatal_valid_reads_name_number',len(toatal_valid_reads_name))
	print('true_reads_use_ratio',float(len(toatal_valid_reads_name)/total_reads_true_number))
	#print (sub_insert_delete)


def main():
#if __name__=='__main__':
	full_command = ' '.join(('"' + x + '"' if ' ' in x else x) for x in sys.argv)
	#print(full_command)
	if '--helpall' in sys.argv or '--allhelp' in sys.argv or '--all_help' in sys.argv:
        	sys.argv.append('--help_all')
	show_all_args = '--help_all' in sys.argv
	#print(show_all_args)
	Description='This is hlz copyright'
	parser = argparse.ArgumentParser(description=Description,add_help=False)

	help_group = parser.add_argument_group('Help')
	help_group.add_argument('-h', '--help', action='help',
                            help='Show This help message and exit')
	help_group.add_argument('--help_all', action='help',
                            help='Show a help message with all program options')

	MapQ_group = parser.add_argument_group('MapQ')
	MapQ_group.add_argument('-Mc','--MapQ_cut_off',type=int,
                        help='minimal MapQ to be used')

	input_group = parser.add_argument_group('Input')
	input_group.add_argument('-ref','--ref_fasta',required=False,
                    help="fasta must if and only if two lines")
	input_group.add_argument('-sam','--aln_sam',
                    help="need a sam file")

	group=parser.add_argument_group('group',
                                        'this is a group'
                                        if show_all_args else argparse.SUPPRESS)
	
	if len(sys.argv) == 1:
		parser.print_help(file=sys.stderr)
		sys.exit(1)

	args = parser.parse_args()

	main_procedure(args)
