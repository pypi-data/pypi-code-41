'''
jsonMerge.py
Author: Jonathan Hoyle
Description: Merges all items from json files into a single file, then deletes the original files
'''
# Imports
import json, glob, os
from addict import Dict
# Makes sure the program is running in the proper directory
os.chdir("C://Users//Shipping//Documents//Integration Dev//SquarespaceUploader//jsons")
# Creates a list to store the results in
result = []
# For every json file
for f in glob.glob("*.json"):
    # Open that json file
    with open(f, "r") as infile:
        # And append its parsed file to the list
        result.append(json.load(infile))
# Initialize the final json data with the first given data
endResult = result[0]
# Try built in merging method
try:
    # Loop through the other json dicts
    for d in range(1, len(result)):
        # Merge the current json into the final json
        endResult.update(result[d])
except:
    # Then for the remaining files
    for d in range(1, len(result)):
        # Loop through each item
        for i in range(0, len(result[d])):
            # And append it to the final list of items
            endResult.append(result[d][i])
# Open the result file with write permissions
with open("merged_file.json", "w") as outfile:
    # And dump the json into that file
    json.dump(endResult, outfile)
# Finally, find each json file
for f in glob.glob("*.json"):
    # And provided it's not the end result file
    if "merged_file" not in f:
        # Delete it
        os.system('del ' + f)