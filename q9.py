import sys
import sqlite3
# There can be blank lines in the query file, consisting of zero or more space characters (e.g., \s or \t)
def main(db, filename):

	conn = sqlite3.connect(db)
	print ("Opened database successfully")

	lines = []
	# possess the original file
	with open(filename) as f:
		for line in f:
			l = line.rstrip('\n')
			if not l=='':
				lines.append(l) # process the lines

	prefix = {}
	queryStr = ''
	queryVars = []
	triples = []

	# extract data
	for line in lines:
		# for each line of the file
		if isPrefix(line.strip()):
			temp = line.split(':') # temp == ['PREFIX rdf', ' <http://www.w3.org/1999/02/22-rdf-syntax-ns#>']
			parts = temp[0].split() # parts == ['PREFIX', 'rdf']
			parts.append(temp[1]) # parts == ['PREFIX', 'rdf', ' <http://www.w3.org/1999/02/22-rdf-syntax-ns#>']
			prefix[parts[1].strip()] = parts[2].strip() #store the prefix
		else:
			queryStr+=line

	# possess the query string
	queryStr.replace('\t',' ')
	queryStr.replace('\s',' ')
	queryStr.replace('\n',' ')
	print(queryStr)

	if not validateQuery(queryStr):
		print('Query not valid')
		sys.exit()	

	for key, value in prefix.items():
		print(key, value)

	queryVars = extractVariables(queryStr)
	print(queryVars)

	triples = extractTriples(queryStr)
	print(triples)



	conn.commit()
	conn.close()

def validatePrefix(line):
	pass

def validateQuery(string):
	# no more than one occurance of {,},SELECT,WHERE
	# SELECT occurs before WHERE
	# { occurs before }
	if not string.count('SELECT')==1:
		return False
	if not string.count('WHERE')==1:
		return False
	if not string.count('{')==1:
		return False
	if not string.count('}')==1:
		return False
	return True

def extractVariables(string):
	# return the list of variables to query
	start = string.index('SELECT')+len('SELECT')
	end = string.index('WHERE')
	variableStr = string[start:end].strip()
	variables = variableStr.split()
	for var in variables:
		if not (var[0]=='?' or var=='*'):
			print('Invalid variables to query')
			sys.exit()
	return variables

def extractTriples(string):
	# return the list of list of nodes to query
	start = string.index('{')+len('{')
	end = string.index('}')
	tripleStr = string[start:end].strip()
	triples = tripleStr.split('.')
	output = []
	for triple in triples:
		lst = triple.split()
		if lst: # if is not an empty list(may caused by tailing spaces)
			output.append(lst)
	return output

def isPrefix(string):
	if string.split(' ')[0]=='PREFIX':
		return True
	else:
		return False

def possessLines(lines):
	string=''
	for line in lines:
		string+=line
	string.replace('\t',' ')
	string.replace('\s',' ')
	string.replace('\n',' ')
	return string

if __name__ == '__main__':

	if not len(sys.argv)==3:
		print("Missing arguments")
		sys.exit()
	
	db = sys.argv[1]
	# read in the filename
	filename = sys.argv[2]

	main(db, filename)