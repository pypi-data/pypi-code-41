import os, sys
import card_trick
import json
import pkgutil
import pandas as pd

############################################
def update(options):
	"""
	execute the update command that updates the CARD database
	"""
	
	path_to_store_db = ""
	aro_obo_file = ""
	if (options.path): ## user provides a path to store database
		path_to_store_db = os.path.abspath(options.path)
	else: ## default: home
		home = os.path.expanduser("~")
		path_to_store_db = '{0}/.card-trick'.format(home)
	
	## uptade database in a path
	aro_obo_file = card_trick.ontology_functions.update_ontology(path_to_store_db, options.quiet)
	
	## get ontology and save it in csv
	card_trick.ontology_functions.parse_ontology(aro_obo_file, options.quiet)

############################################
def search(options):
	"""
	execute the search command, to search the ontology
	"""
	
	#####
	if options.path: ## user provides a folder
		path = os.path.abspath(options.path)
	else: ## default
		home = os.path.expanduser("~")
		path = '{0}/.card-trick'.format(home)

	## batch
	if options.batch: ## user provides a folder
		batch_file = os.path.abspath(options.input)
		input_list = [line.rstrip('\n') for line in open(batch_file)]
	else:
		input_list = [options.input]

	## type of term to search
	type_term = options.term

	## load data first
	### read csv from file into pandas dataframe
	csv_file = '{0}/aro.obo.csv'.format(path)
	if os.path.exists(csv_file):
		if not options.quiet:
			print ("+ Get ontology data...")
		dataF = pd.read_csv(csv_file, index_col=0)
	else:
		## no database is available, download
		if not options.quiet:
			print ("\n+ Downloading the database and parsing ontology first...")
		
		## uptade database in a path
		aro_obo_file = card_trick.ontology_functions.update_ontology(path, options.quiet)
	
		## get ontology and save it: csv & json
		dataF = card_trick.ontology_functions.parse_ontology(aro_obo_file, options.quiet)

	### generate search for input
	# search for terms provided	
	matching_terms = card_trick.ontology_functions.search(input_list, dataF, type_term, options.quiet)

	## search using a second term
	if options.input_2:
		## batch
		if options.batch_2: ## user provides a folder
			batch_file2 = os.path.abspath(options.input_2)
			input_list2 = [line.rstrip('\n') for line in open(batch_file2)]
		else:
			input_list2 = [options.input_2]

		## type of term to search
		type_term2 = options.term_2	
	
		# search for terms provided	
		matching_terms2 = card_trick.ontology_functions.search(input_list2, matching_terms, type_term2, options.quiet)
		
		## checking there is something to report
		if matching_terms2.empty:
			if not options.quiet:
				print ('+ No available information provided for the second term')
		else:
			matching_terms = matching_terms2

	## print terms retrieved
	if not matching_terms.empty: ## prevent printing if nothing returned
		out_name = options.output_name
		card_trick.ontology_functions.write_ontology(matching_terms, out_name, options.format_output, options.quiet)
	else:
		if not options.quiet:
			print ('+ No available information for this term provided')
	
	## return info
	return (matching_terms)
