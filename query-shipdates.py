# Python 3.3.4
import xml.dom.minidom as dom
import urllib.request as url
import csv
import sys
import getopt

## CONFIG SECTION (feel free to change these parameters) ##

# This API key will stop working; we need to apply for a real one.
apikey = "1adecee8a60444738f280aad1cd87d0e"

# Input file is the CSV returned when Rory runs his report from Kaseya
# Input file path - should prompt user for this eventually but this config section is a bit of a hack anyways
infilepath = "./sample-input.csv"

# Output file path
outfilepath = "./cvm-pcs-shipdate.csv"
# PO filtered output path
outfilepath_2 = "./cvm-pcs-shipdate-pofiltered.csv"

# Do we want verbose updates?
verbose = False

# Are we filtering based on PO?
filter_po = False

# File input or cmd-line args?
file_input = False
input_file_set = False
output_file_set = False

## END CONFIG SECTION ##

## GLOBAL VARS ##

apiurl = "https://api.dell.com/support/v2/assetinfo/warranty/tags?apikey=" + apikey + "&svctags="

## END GLOBAL VARS ##

def process_shipdate(serial_num):
	if len(serial_num) == 7:
		if verbose:
			print("Working on {0}".format(serial_num))
		response = url.urlopen(apiurl + serial_num)
		shipdate = dom.parse(response).getElementsByTagName("a:ShipDate")
		date_nums = shipdate[0].firstChild.nodeValue.split('-')
		year = date_nums[0]
		month = date_nums[1]
		if verbose:
			print("System {0} was shipped {1}/{2}".format(serial_num, year, month))
		else:
			print("{0}/{1}".format(year,month))
	else:
		if verbose:
			print("No shipping info for system {0}".format(serial_num))

def process_shipdates(infilepath, outfilepath, outfilepath_2):
	# Open files
	infile = open(infilepath, 'r')
	outfile = open(outfilepath, 'w')
	if filter_po:
		outfile_2 = open(outfilepath_2, 'w')

	svctags = csv.DictReader(infile)
	fieldnames = svctags.fieldnames

	output = csv.DictWriter(outfile, fieldnames)
	output.writeheader()
	if filter_po:
		output_po = csv.DictWriter(outfile_2, fieldnames)
		output_po.writeheader()

	if verbose:
		i = 0

	for row in svctags:
		if verbose:
			i += 1
		if len(row["System Serial Number"]) == 7:
			if verbose:
				print("{0}:  Working on {1}".format(i, row["System Serial Number"]))
			response = url.urlopen(apiurl + row["System Serial Number"])
			shipdate = dom.parse(response).getElementsByTagName("a:ShipDate")
			date_nums = shipdate[0].firstChild.nodeValue.split('-')
			row["Ship Year"] = date_nums[0]
			row["Ship Month"] = date_nums[1]
			output.writerow(row)
		else:
			output.writerow(row)
			if verbose:
				print("{0}:  No shipping info for row {1}".format(i, row["System Serial Number"]))
		if  row["Purchase Order"][:3] != "290" and row["Purchase Order"][:4] != "2925" and filter_po:
				output_po.writerow(row)
				

	outfile.close()
	infile.close()

	if filter_po:
		outfile_2.close()

# Parse command line args

opts, args = getopt.getopt(sys.argv[1:],"io:vf:",["infile=", "outfile=", "verbose", "filterfile="])

for o, a in opts:
	if o in ("-v", "--verbose"):
		verbose = True
	elif o in("-i", "--infile"):
		infilepath = a
		file_input = True
		input_file_set = True
	elif o in ( "-o", "--outfile"):
		outfilepath = a
		output_file_set = True
	elif o in ("-f", "--filterfile="):
		filter_po = True
		outfilepath_2 = a
		output_file_set = True

if(output_file_set and not input_file_set):
	print ("Needs input file if you're going to make an output file.")
else:
	if input_file_set and output_file_set:
		process_shipdates(infilepath, outfilepath, outfilepath_2)
	else:
		for arg in args:
			if len(str(arg)) == 7:
				process_shipdate(str(arg))
