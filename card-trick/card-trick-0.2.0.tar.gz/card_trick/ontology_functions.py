import pronto
import json
import tarfile
import tempfile
from requests import get
import shutil
import os, sys
import pkgutil
import pandas as pd
from copy import deepcopy

############################################
def update_ontology(path, quiet):
	"""
	Download latest ontology from CARD and extract aro.obo file to ~/.card-trick/ or user provided folder
	Params:
		path: It could any given path or default ('{0}/.card-trick'.format(os.path.expanduser("~")))
	Returns:
		aro.boo file absolute path
	"""
	url = 'https://card.mcmaster.ca/latest/ontology'
	_, file_name = tempfile.mkstemp('.tar.bz2')
	tmp_dir = tempfile.mkdtemp()
	
	if not quiet:
		print ("+ Downloading latest ontology from CARD databases from %s..." %url)
	
	# get latest database file and write to temp file
	with open(file_name, "wb") as file:
		response = get(url)
		file.write(response.content)
	
	# extract tar.bz2 file to temp dir
	with tarfile.open(file_name, "r:bz2") as tar_file:
		tar_file.extractall(tmp_dir)
	
	## path is always provided. It could be:
	### user provided path 
	###	or
	###	'{0}/.card-trick'.format(os.path.expanduser("~"))
	destDir = path

	# check if ~/.card_shark dir exists and make it if not
	if not os.path.exists(destDir):
		os.makedirs(destDir)
	
	# copy aro.obo ontology file to directory
	shutil.copyfile('{0}/aro.obo'.format(tmp_dir), '{0}/aro.obo'.format(destDir))

	if not quiet:
		print ("+ Ontology from CARD database saved in %s..." %destDir)

	return ('{0}/aro.obo'.format(destDir))
	

############################################
def parse_ontology(obo_file, quiet):
	"""
	Parse aro.obo ontology from CARD
	Params:
		obo_file: File path to the aro.obo file
	Returns:
		dataframe in csv and json format
	"""
	
	if not quiet:
		print ("+ Parsing ontology information...")

	## get ontology using pr
	o = pronto.Ontology(obo_file)
	
	## init dataframe
	main_colnames = ('name', 'desc', 'xref', 'parents')
	dataF = pd.DataFrame(columns=main_colnames)

	# loop through all terms in the ontology
	for term_name in o.terms:
		term = o.terms[term_name]
		
		## parse data and populate			
		if 'xref' in term.other:
			xref_str = ','.join(term.other['xref'])
			xref=xref_str
		else:
			xref='NaN'

		## term.rparents
		parents = [t.name for t in term.rparents()] ## rparents = recursive parents
		if not parents:
			parents ='NaN'		
		else:
			parents_str = ",".join(parents)
		
		### common columns		
		dataF1 = pd.DataFrame(columns=main_colnames)
		dataF1.loc[term.id] = (term.name, term.desc, xref, parents_str)		
		
		# get relationships for each term
		# variable amount of columns for each entry
		relations = term.relations
		for rel in relations:
			########################
			## rel can be:	
				## 'can_be'
				## 'confers_resistance_to'
				## 'confers_resistance_to_drug'
				## 'derives_from'
				## 'evolutionary_variant_of'
				## 'has_part'
				## 'is_a'
				## 'part_of'
				## 'participates_in'
				## 'regulates'
				## 'targeted_by'
				## 'targeted_by_drug'
				## ...
			########################

			## get names from relations: 
			entity = [ent.name + ' [' + ent.id + ']' for ent in relations[rel]]
			if not entity:
				entity='NaN'
			else:		
				entity_str = ','.join(entity)
			
			## Create empty column if does not exist
			if not rel.obo_name in dataF1:
				dataF1[rel.obo_name] = ""

			## add item
			dataF1.loc[term.id][rel.obo_name] = entity_str


		## append dataframe for each term, dataF1, to the main dataframe: dataF
		dataF = dataF.append(dataF1, sort=True).fillna('NaN')

	## sort columns dataframe
	all_columns = list(dataF.columns)
	
	## prefer order for tabs in csv dataframe generated
	new_column_names = ['name', 'is_a', 'desc', 'parents', 'derives_from', 'can_be', 'has_part', 'part_of', 'participates_in', 'regulates', 'confers_resistance_to', 'confers_resistance_to_drug', 'evolutionary_variant_of', 'targeted_by', 'targeted_by_drug', 'xref']

	#### check if missing columns
	additional_colnames = [value for value in all_columns if value not in new_column_names] 
	if (additional_colnames):
		new_column_names = new_column_names + additional_colnames
	
	## re-index dataframe based on order
	dataF = dataF.reindex(columns=new_column_names)

	## Dump dataframe into csv and json for later analysis
	write_ontology(dataF, obo_file, "csv", quiet)
	return(dataF)

############################################
def write_ontology(dataFrame_all, name, option, quiet):
	"""
	write the CARD ontology dataframe (all or subset) to csv & json files
	"""
	
	dump_csv = name + ".csv"
	dump_tsv = name + ".tsv"
	dump_json = name + ".json"

	if option == 'csv':
		if not quiet:
			print ("+ Writing information in csv format files...")
		dataFrame_all.to_csv(dump_csv)

	elif option == 'tsv':
		if not quiet:
			print ("+ Writing information in tsv format files...")
		dataFrame_all.to_csv(dump_tsv, sep='\t')

	elif option == 'json':
		if not quiet:
			print ("+ Writing information in json format files...")
		dataFrame_all.to_json(dump_json)
	
	elif option == 'stdout':
		if not quiet:
			print ("+ Writing information to screen...")
		dataFrame_all.to_csv(sys.stdout, sep='\t')
	
	elif option == 'all':	
		if not quiet:
			print ("+ Writing information in tsv, csv and json format files...")
		dataFrame_all.to_csv(dump_tsv, sep='\t')
		dataFrame_all.to_csv(dump_csv)
		dataFrame_all.to_json(dump_json)

############################################
def search(input_list, dataF, type_term, quiet):
	"""
	search ortology data for term provided
	Params:
		input_list: Contains term(s) to search
		dataF: dataF containing information
		type_term: type of term to search or any
		
	Returns:
		dataframe in csv and json format

	"""
	
	##############
	if not quiet:
		print ("+ Start the search for the terms provided")

	## init results frame
	results_DF = pd.DataFrame()

	### term:
	### 'ARO', 'gene', 'antibiotic', 'target', 'any'
	for elem in input_list:

		## ARO id is the index of the dataframe
		## exact match
		if type_term == 'ARO':
			results_DF = pd.concat([results_DF, dataF.loc[[elem], :] ])

		## gene names are in column name
		## partial match
		elif type_term == 'gene':
			results_DF = pd.concat([results_DF, dataF[dataF['name'].str.contains(elem, na=False, case=False)] ] )
			
		#### RESISTANCE
		## partial match
		## antibiotic, following original card-trick, could be the antibiotic to which a gene provides resistance
		## Columns to search in dataframe could be:
			## 'confers_resistance_to'
			## 'confers_resistance_to_drug'
		elif type_term == 'antibiotic':
			results_DF = pd.concat([results_DF, dataF[ dataF['confers_resistance_to'].str.contains(elem, na=False, case=False)] ] )
			results_DF = pd.concat([results_DF, dataF[ dataF['confers_resistance_to_drug'].str.contains(elem, na=False, case=False) ] ] )
		
		#### SUSCEPTIBILITY
		## In this case, we can retrieve the mechanisms involved targeted by a given drug
		## partial match
		## 'targeted_by'
		## 'targeted_by_drug'
		elif  type_term == 'target':
			results_DF = pd.concat([results_DF, dataF[dataF['targeted_by'].str.contains(elem, na=False, case=False)] ] )
			results_DF = pd.concat([results_DF, dataF[dataF['targeted_by_drug'].str.contains(elem, na=False, case=False)] ] )
	
		### 
		## Searches all columns of the dataframe and retrieves 
		## any given row contain any partial match of the terms provided
		elif type_term == 'any':
			for col in dataF.columns:
				results_DF = pd.concat([results_DF, dataF.loc[dataF[col].str.contains(elem, na=False, case=False)] ] )

	## drop columns if all values contain NaN
	results_DF = results_DF.drop_duplicates()
	results_DF_filter = results_DF.dropna(how='all', axis=1) 

	## return dataframe
	return(results_DF_filter)

