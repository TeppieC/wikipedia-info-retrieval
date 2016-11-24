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
	allVars = []
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
			if line[-1]=='.' and line[-2]!=' ':
				queryStr+=line[:-1]
				queryStr+=' '
				queryStr+='. '
			else:
				queryStr+=line

	# possess the query string
	queryStr.replace('\t',' ')
	queryStr.replace('\s',' ')
	queryStr.replace('\n',' ')
	print('query string is: ', queryStr)

	if not validateQuery(queryStr):
		print('Query not valid')
		sys.exit()	

	for key, value in prefix.items():
		print(key, value)

	# extract all querying statements inside the braces
	statements = extractStatements(queryStr)
	print('statements', statements)
	statements = replacePrefix(statements, prefix)
	print('full statements', statements)

	# extracting all variables created in the query
	allVars = extractAllVariables(statements)

	# extracting all querying variables
	queryVars = extractVariables(queryStr)
	print('queryVars', queryVars)
	if queryVars[0]=='*':
		queryVars = allVars

	# create the result table
	#createResultTable(conn, queryVars)
	for var in queryVars:
		queryInOneVarStmt(conn, statements, var)
	
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

def isOneVarStmt(stmt, var):
	'''
	Return true if the stmt is a one-variable statement of var
	otherwise false.
	'''
	nodeData = ''
	i=0
	#print('stmt is: ', stmt)
	for node in stmt:
		#print('node is: ', node)
		if isVariable(node):
			#print('is variable')
			i+=1
			nodeData = node
			#print('nodeData is: ', nodeData)

	#print('After: ')
	#print(nodeData)
	#print(var)
	if i==1 and nodeData==var:
		# if the given var occurs only once in the stmt
		return True
	else:
		# if the given var is not in stmt, or the stmt contains 
		# more than one variables
		return False

def stmtForVar(stmt, var):
	nodeType = {0:'subject', 1:'predicate', 2:'object'}
	#find whether the variable is a subject, predicate or object.
	varNode = nodeType[stmt.index(var)] 
	#print(varNode)
	return oneVarQueryString(stmt[0], stmt[1], stmt[2], varNode)

def oneVarQueryString(sub, pred, obj, varNode):
	'''
	return the string of a sqlite query for a given variable
	'''
	if varNode=='subject':
		return "SELECT subject FROM statement WHERE predicate='%s' AND object='%s'"%(pred, obj)
	elif varNode=='predicate':
		return "SELECT predicate FROM statement WHERE subject='%s' AND object='%s'"%(sub, obj)
	elif varNode=='object':
		return "SELECT object FROM statement WHERE subject='%s' AND predicate='%s'"%(sub, pred)

def queryInOneVarStmt(conn, statements, var):
	'''
	query in the database for a given variable -- var.
	The function will query according to all statements in the file which only has "var" as its variable.
		eg. ?city dbo:country dbr:Canada. is the statement that this function will possess. In this case, 
			var is ?city. The function will find and query in all such statements for ?city.
	The function will create a table for the results after querying all one-variable statements on this var.
		eg. table will be named as ?city
	'''
	create_stmt = 'CREATE TABLE %s (%s TEXT)'%(var[1:], var[1:])
	conn.execute(create_stmt)

	insert_stmt = 'INSERT INTO %s '%(var[1:])
	exce = False
	for statement in statements:
		# first query for all statements with only one variable inside, the variable should be exactly 'var'
		if isOneVarStmt(statement, var):
			print('one var stmt for ', var, statement)
			sql_stmt = stmtForVar(statement, var)
			insert_stmt += sql_stmt
			insert_stmt += ' INTERSECT '
			exce = True
	if exce:
		print(insert_stmt[:-11]+';') #.............................. may exceed
		conn.execute(insert_stmt[:-11]+';')

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

def extractAllVariables(statements):
	allVars = set()
	for statement in statements:
		for node in statement:
			if isVariable(node):
				allVars.add(node)
	return list(allVars)


def extractVariables(string):
	# return the list of variables to query
	start = string.index('SELECT')+len('SELECT')
	end = string.index('WHERE')
	variableStr = string[start:end].strip()
	variables = variableStr.split()
	# validating
	for var in variables:
		if not (var[0]=='?' or var=='*'):
			print('Invalid variables to query')
			sys.exit()
	# TODO: handle *
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
				if node[0]!='<': # if the node is not a prefixed node, nor a literal
					print('here:', node)
					nodeList = node.split(":")
					prefix = ''
					try:
						if nodeList[0]=='_': # for empty prefix
							prefix = '<_/>'
						else:
							prefix = prefixDict[nodeList[0]]
					except KeyError: 
						print('Undocumentable prefix defination: ', nodeList[0])
						sys.exit()
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

	# possess the triple statements at first,
	# in case that teh string is split on wrong locations
	possessedTripleStr = replaceTripleStr(tripleStr)
	print("possessed: ", possessedTripleStr)

	triples = possessedTripleStr.split('.')
	print(triples)
	output = []

	for triple in triples:
		lst = triple.split()
		print('lst: ', lst)
		if lst: # if is not an empty list(may caused by tailing spaces)
			output.append(lst)
	
	for i in range(0, len(output)):
		stmt = output[i]
		for j in range(0, len(stmt)):
			node = output[i][j]
			output[i][j] = node.replace('/////', '.').replace('$$$$$', ',').replace('######',' ')
			print('change back: ', output[i][j])
	print(output)
	return output

def replaceSpaceInStr(tripleStr):
	allNodes = tripleStr.split()
	for i in range(0, len(allNodes)):
		try:
			if allNodes[i][0]=='"' and allNodes[i][-1]!='"' \
				and allNodes[i+1][0]!='"' and allNodes[i+1][-1]=='"':
				allNodes[i] = allNodes[i]+'######'+allNodes[i+1]
				allNodes.remove(allNodes[i+1])
		except:
			pass
	return ' '.join(allNodes)


def replaceTripleStr(tripleStr):
	tripleStr = replaceSpaceInStr(tripleStr)
	print('hehehe', tripleStr)
	allNodes = tripleStr.split()
	for i in range(0, len(allNodes)):
		node = allNodes[i]
		if isUri(node):
			print('AAAAAAAAAAAAAA URI', node)
			node = node.replace('.', '/////')
			node = node.replace(',', '$$$$$')
			allNodes[i] = node
		elif isfloat(node):
			print('AAAAAAAAAAAAAA decimal/float', node)
			node = node.replace('.', '/////')
			allNodes[i] = node
	print(allNodes)
	return ' '.join(allNodes)

def isfloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

def isLiteral(node):
	nodeList = node.split(":")
	if isLexical(node):
		return True
	elif len(nodeList)==1 or (node[0]=='"' and node[-1]=='"'):
		return True
	else:
		return False

def isUri(string):
	return (string[0]=='<' and string[-1]=='>')

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