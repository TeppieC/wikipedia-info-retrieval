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
			temp = line.split(':', 1) # temp == ['PREFIX rdf', ' <http://www.w3.org/1999/02/22-rdf-syntax-ns#>']
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

	# extract all statements
	statements = extractStatements(queryStr)
	print(statements)
	fullStatements = replacePrefix(statements, prefix)
	print(fullStatements)

	# extracting all querying variables
	queryVars = extractVariables(queryStr)
	print(queryVars)

	# create the result table
	createResultTable(conn, queryVars)

	conn.commit()
	conn.close()

def createResultTable(conn, queryVars):
	variables = tuple(a[1:] for a in queryVars) # list comprehension for creating a tuple
	createStmt = 'CREATE TABLE result( ' + '%s VARCHAR(100),'*len(queryVars)%variables
	createStmt = createStmt[:-1]+');'
	print(createStmt)
	# create tables
	try:
		conn.execute(createStmt)
		print ("Table created successfully")
	except sqlite3.OperationalError as e:
		print("Table already existed for the operation")

def query(conn, queryVars):
	intersect = ' INTERSECT '

def oneVarStmt(stmt, var):
	nodeData = ''
	i=0
	for node in stmt:
		if isVariable(node):
			i+=1
			nodeData = node
	if i==0 and node==var:
		return True
	else:
		return False

def stmtsForVar(statements, var)

def CreateQuery(sub, pred, obj, varNode):
	if varNode=='subject':
		return 'SELECT subject FROM statement WHERE predicate=%s AND object=%s'%(pred, obj)
	elif varNode=='predicate':
		return 'SELECT predicate FROM statement WHERE subject=%s AND object=%s'%(sub, obj)
	elif varNode=='object':
		return 'SELECT object FROM statement WHERE subject=%s AND predicate=%s'%(sub, pred)

def queryInOneVarStmt(statements, var):
	for statement in statements:
		# first query for all statements with only one variable inside, the variable should be exactly 'var'
		if oneVarStmt(stmt, var): 
			pass

def queryForVar(conn, var, statements):
	pass

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

def isLexical(string):
	'''
	determine if the type of the literal is like "1904-10-08"^^xsd:date
	'''
	if "^^xsd" in string:
		return True
	else:
		return False

def replacePrefix(statements, prefixDict):
	outputStmts = []
	for statement in statements:
		outputStmt = []
		for node in statement:
			if isVariable(node):
				outputStmt.append(node)
			elif(node[0]=='<' and node[-1]=='>'):
				# for pure uri's
				outputStmt.append(node)
			elif isLexical(node):
				# for the lexical data types
				# "1904-10-08"^^xsd:date
				# "53.53333282470703125"^^xsd:float
				# "812201"^^xsd:nonNegativeInteger
				outputStmt.append(node)
			else:
				# for prefixed nodes
				nodeList = node.split(":")
				prefix = ''
				try:
					prefix = prefixDict[nodeList[0]]
				except KeyError: # for empty prefix/node
					prefix = '<_/>'
				print(prefix)
				print(nodeList)
				outputStmt.append(prefix[:-1] + nodeList[1] + prefix[-1])
		outputStmts.append(outputStmt)
	return outputStmts


def extractStatements(string):
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

def isVariable(string):
	return (string[0]=='?')

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