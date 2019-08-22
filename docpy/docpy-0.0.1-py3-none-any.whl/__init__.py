##########################################
##### Python Documentation Generator #####
#####         by Chris Pyles         #####
##########################################

import runpy
import inspect
import sys
import glob
import argparse
import re
import os

from regexes import *

# create CLI argument parser and extract arguments
parser = argparse.ArgumentParser(description="generate Markdown documentation for Python files")
parser.add_argument("-a", "--append", dest="append", help="file to which to append generated Markdown")
parser.add_argument("-o", "--output", dest="out", help="file to save generated Markdown to")
parser.add_argument("-s", "--sub", dest="sub", help="file with ::DOCUMENTATION:: tag to replace Markdown")
parser.add_argument("-t", "--template", dest="temp", help="template file with ::DOCUMENTATION:: tag, needs OUT argument")
parser.add_argument(dest="files", nargs=argparse.REMAINDER, help="files to be documented")
namespace = vars(parser.parse_args())

folder = namespace["files"][0]
name_regex = r"\/[\w*]*\.\w+"
folder = re.sub(name_regex, "", folder)
try:
	old_folder = os.getcwd()
	os.chdir(folder)
	changed_dir = True
except FileNotFoundError:
	pass

if changed_dir:
	files = []
	for file in namespace["files"]:
		match = re.search(name_regex, file)
		if match:
			files += [match[0][1:]]
		else:
			files += [file]
	namespace["files"] = files

# print(os.getcwd())

docstrings, classes, methods = {}, [], []
for file in namespace["files"]:
	file_name = file[:-3]

	with open(file) as f:
		objects = parse_file(f)

	for obj in objects:
		signature = re.search(r" (\w+(\(.*\))?):", obj.signature)[1]

		if signature[0] == "_":
			continue

		docstring = re.sub(r"[\t\"\n]", "", obj.docstring)

		if obj.parent:
			parent = re.sub(r"[\t\"\n]", "", obj.parent)
			parent = re.search(r" (\w+(\(.*\))?):", parent)[1]
			docstrings[file_name + "." + parent + "." + signature] = docstring
			methods += [file_name + "." + parent + "." + signature]

		else:
			docstrings[file_name + "." + signature] = docstring

			if re.match(r"class", obj.signature):
				classes += [file_name + "." + signature]

if changed_dir:
	os.chdir(old_folder)

# print(docstrings)
# print(classes)
# print(methods)

markdown = ""
prevClass = False
for obj in docstrings:
	string = docstrings[obj]
	if obj in classes:
		if markdown != "":
			markdown += "---\n\n"
		name = "**_class_ `" + obj + "`**"
		prevClass = True
	elif obj in methods:
		name = "**_method_ `" + obj + "`**"
		prevClass = True
	else:
		if prevClass:
			markdown += "---\n\n"
		name = "**_function_ `" + obj + "`**"
		prevClass = False

	markdown += name + "\n\n" + string + "\n\n"

markdown = markdown[:-1]

if namespace["temp"]:
	if namespace["out"]:
		with open(namespace["temp"]) as f:
			contents = f.read()

		with open(namespace["out"], "w+") as f:
			f.write(re.sub("::DOCUMENTATION::", markdown, contents))

	else:
		print("You did not pass an OUT argument.")

elif namespace["sub"]:
	with open(namespace["sub"]) as f:
		contents = f.read()
		contents = re.sub("::DOCUMENTATION::", markdown, contents)
		f.write(contents)

elif namespace["append"]:
	with open(namespace["append"], "a+") as f:
		f.write(markdown)

elif namespace["out"]:
	with open(namespace["out"], "w+") as f:
		f.write(markdown)

else:
	print(markdown)
