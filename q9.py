import sys
import sqlite3
# There can be blank lines in the query file, consisting of zero or more space characters (e.g., \s or \t)
# assume that 
# 1. the closing brace } will not be in the same line as the last statement.
# 2. there will always be one SELECT ... WHERE statement in each query
# 3. All statements should be end with a period, otherwise the program will report the error.
# 4. All filter varaiables are within the querying variables. ????????????????????????????????????????????????????????????


#TODO:
# put filter vars into query
# extract query results in python, do the comparision in python
hasTwoVarStmt = False

def main(db, filename):

	conn = sqlite3.connect(db)
	print ("Open database successfully")

	# variables
	lines = []
	prefix = {}
	queryStr = ''
	queryLines = []
	queryVars = []
	allVars = []
	triples = []
	filters = []

	# possess the original file
	with open(filename) as f:
		for line in f:
			l = line.rstrip('\n')
			if not l=='':
				lines.append(l) # process the lines

	braces = ['{','}']
	start = False # a switch to determine if the line is a statement
	# extract data from file
	for line in lines:
		line = clearSpaces(line)
		if line:
			#print('|'+line+'|')
			# for each line of the file
			if isPrefix(line): # extracting prefix definations
				#print(line)
				if not isValidPrefix(line):
					print('prefix is not valid.')
					sys.exit()
				temp = line.split(':', 1) # temp == ['PREFIX rdf', ' <http://www.w3.org/1999/02/22-rdf-syntax-ns#>']
				parts = temp[0].split() # parts == ['PREFIX', 'rdf']
				parts.append(temp[1]) # parts == ['PREFIX', 'rdf', ' <http://www.w3.org/1999/02/22-rdf-syntax-ns#>']
				prefix[parts[1].strip()] = parts[2].strip() #store the prefix
			else:
				queryStr+=' '
				queryStr+=line
				if line[-1] in braces:
					start = not start # toggle the switch
					continue
				if start:
					queryLines.append(line)

	print(queryLines)

	# validating the query
	queryStr = clearSpaces(queryStr)
	if not isValidQuery(queryStr):
		print('Query not valid')
		sys.exit()
	print('query string is: ', queryStr)

	#for key, value in prefix.items():
	#	print(key, value)

	# extract all querying statements inside the braces
	[statements, filters] = extractStatements(queryLines)
	print('statements', statements)
	print('filters', filters)

	statements = replacePrefix(statements, prefix)
	print('full statements', statements)

	# extracting all variables created in the query
	allVars = extractAllVariables(statements)
	print('allvars', allVars)
	# extracting all querying variables
	queryVars = extractVariables(queryStr)
	print('queryVars', queryVars)
	if queryVars[0]=='*':
		queryVars = allVars
	
	
	# create the result table
	createResultTable(conn, queryVars)
	for var in allVars:
		queryInOneVarStmt(conn, statements, var)

	queryForRelations(conn, statements, queryVars, allVars)
	if not hasTwoVarStmt:
		print('No statements has more than 1 variable')
		queryOnlyOneVar(conn, queryVars, allVars)

	result = printResultWithoutFilter(conn)
	filtering(filters, result)
	dropTables(conn, allVars)


	conn.commit()
	conn.close()


def queryOnlyOneVar(conn, queryVars, allVars):
	'''
	If there is no statement with more than one variables,
	cartesian product the tables of each querying variable and insert into result table
	'''
	select_variables = tuple(a[1:] for a in queryVars) # list comprehension for creating a tuple
	select_clause = 'SELECT distinct '+ '%s, '*len(queryVars)%select_variables
	select_clause = select_clause[:-2]+' '

	from_tables = tuple(a[1:] for a in allVars) # list comprehension for creating a tuple
	from_clause = 'FROM '+ '%s, '*len(allVars)%from_tables
	from_clause+='statement '

	queryStr = concat(select_clause, from_clause, ';')

	insert_stmt = 'INSERT INTO result '

	print(insert_stmt + queryStr)
	conn.execute(insert_stmt + queryStr)




''' 
	Helper functions to extract data from the .txt files 
'''

def clearSpaces(string):
	return string.replace('\t',' ').replace('\n',' ').replace('\s',' ').strip()

def isFilter(string):
	return string[:6]=='FILTER'

def extractStatements(queryLines):
	output = [[],[]]
	for line in queryLines:
		if not line[-1]=='.':
			print('Need period after each line of the statements')
			sys.exit()

		line = line[:-1].strip()
		if isFilter(line):
			content = line[6:].strip()
			output[1].append(content)
			print('Filter is: ', content)
		else:
			triple = line.split()
			output[0].append(triple)
		
	return output

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
				outputStmt.append(node[:node.index('^^')]) ##############################
			elif isLiteral(node):
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
						print('Did you miss the @ identifier for prefix defination?')
						sys.exit()
					print(prefix)
					print(nodeList)
					outputStmt.append(prefix[:-1] + nodeList[1] + prefix[-1])
		outputStmts.append(outputStmt)
	return outputStmts

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
			print('Invalid format for variables to query')
			sys.exit()
	# TODO: handle *
	return variables






''' 
	Query functions for statements with only 1 variable
'''

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

	pos = set()
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
		if var in statement:
			pos.add(statement.index(var))
	if exce:
		print(insert_stmt[:-11]+';')
		conn.execute(insert_stmt[:-11]+';')
	else:
		pos = list(pos)
		for p in pos:
			if p==0:
				insert_stmt = 'INSERT INTO %s '%(var[1:])
				insert_stmt+='select distinct subject from statement;'
				print(insert_stmt)
				conn.execute(insert_stmt)
			elif p==1:
				insert_stmt = 'INSERT INTO %s '%(var[1:])
				insert_stmt+='select distinct predicate from statement;'
				conn.execute(insert_stmt)
			elif p==2:
				insert_stmt = 'INSERT INTO %s '%(var[1:])
				insert_stmt+='select distinct object from statement;'
				conn.execute(insert_stmt)

def isOneVarStmt(stmt, var):
	'''
	Return true if the stmt is a statement containing only one variable
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
	'''
	return string of a sql statement querying for a variable, 
	given one line statement containing this variable
	'''
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







''' 
	Query functions for statements with more than 1 variables 
'''

def queryForRelations(conn, statements, queryVars, allVars):
	
	select_variables = tuple(a[1:] for a in queryVars) # list comprehension for creating a tuple
	select_clause = 'SELECT '+ '%s, '*len(queryVars)%select_variables
	select_clause = select_clause[:-2]+' '
	#print('select is :', select_clause)

	from_tables = tuple(a[1:] for a in allVars) # list comprehension for creating a tuple
	from_clause = 'FROM '+ '%s, '*len(allVars)%from_tables
	from_clause+='statement '
	#print('from is: ', from_clause)

	insert_stmt = 'INSERT INTO result '
	twoVarStatements = twoVarStmts(statements) # get all statements with more than 1 variables
	if twoVarStatements:
		hasTwoVarStmt = True

	queryStr = ''
	exce = False
	for stmt in twoVarStatements:
		where_clause = twoVarWhereClause(stmt[0], stmt[1], stmt[2], stmt[3])
		#print('where clause is:', where_clause)
		queryStr+=concat(select_clause, from_clause, where_clause)
		queryStr+=' INTERSECT '
		exce = True

	if exce:
		print(insert_stmt + queryStr[:-11] + ';')
		conn.execute(insert_stmt + queryStr[:-11] + ';')

def twoVarStmts(statements):
	'''
	return a list consisting of all statements which have two or more variables in it
	'''
	output = []
	for stmt in statements:
		if (stmt[0][0]=='?' and stmt[1][0]=='?') \
			or (stmt[0][0]=='?' and stmt[2][0]=='?') \
			or (stmt[1][0]=='?' and stmt[2][0]=='?'):
			output.append(stmt)

	# to find which of the 3 places of this statement
	# is not a variable to query
	# index==-1 if the statement consists of 3 variables
	# index==0 if the subject of the statement is not a variable
	# index==1 if the predicate of the statement is not a variable
	# index==2 if the object of the statement is not a variable
	for stmt in output:
		index=-1
		i = 0
		for node in stmt:
			if node[0]!='?':
				print('node is :', node)
				print(i)
				index=i
			i+=1
		stmt.append(index)
		print(stmt)
	return output

def twoVarWhereClause(sub, pred, obj, index):
	if sub[0]=='?':
		sub = sub[1:]
	if pred[0]=='?':
		pred = pred[1:]
	if obj[0]=='?':
		obj = obj[1:]
	if index==-1:
		return " WHERE subject=%s AND predicate=%s AND object=%s "%(sub,pred,obj)
	else:
		if index==0:
			return " WHERE subject='%s' AND predicate=%s AND object=%s "%(sub,pred,obj)
		elif index==1:
			return " WHERE subject=%s AND predicate='%s' AND object=%s "%(sub,pred,obj)
		else:
			return " WHERE subject=%s AND predicate=%s AND object='%s' "%(sub,pred,obj)

def concat(select_clause, from_tables, where_clause):
	return select_clause+from_tables+where_clause







'''
	Helper functions to examine data-types and validate inputs
'''

def isValidQuery(string):
	# no more than one occurance of {,},SELECT,WHERE
	# SELECT occurs before WHERE
	# { occurs before }
	if not string.count('SELECT')==1:
		print('Missing SELECT')
		return False
	if not string.count('WHERE')==1:
		print('Missing WHERE')
		return False
	if not string.count('{')==1:
		print('Missing braces')
		return False
	if not string.count('}')==1:
		print('Missing braces')
		return False
	return True

def isLexical(string):
	'''
	determine if the type of the literal is like "1904-10-08"^^xsd:date
	'''
	if "^^xsd" in string:
		return True
	else:
		return False

def isLiteral(node):
	'''
	determine if an input node is a literal
	'''
	nodeList = node.split(":")
	if isLexical(node):
		return True
	elif len(nodeList)==1 and (node[0]=='"' and node[-1]=='"'):
		return True
	else:
		return False

def isfloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

def isUri(string):
	return (string[0]=='<' and string[-1]=='>')

def isPrefix(string):
	if string.split()[0]=='PREFIX':
		return True
	else:
		return False

def isValidPrefix(string):
	stringList = string.split()
	if not len(stringList)==3:
		return False
	if stringList[0]!='PREFIX':
		return False
	if stringList[1][-1]!=':':
		return False
	if stringList[2][0]!='<' or stringList[2][-1]!='>':
		return False
	return True

def isVariable(string):
	return (string[0]=='?')

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

def printResultWithoutFilter(conn):
	'''
	return the result after querying the database without any filtering
	'''
	conn.commit()
	cur = conn.cursor()
	cur.execute('SELECT * FROM result;')
	output = []
	for row in cur:
		#print(row)
		output.append(list(row))
	return output

def filtering(filters, result):
	print('Filtering the result')

	print('Filters')
	for f in filters:
		print(f)

	print('Temporary results')
	count = 0
	for row in result:
		print(row)
		count+=1
	print(count, ' results')

	for filterStmt in filters:
		if isNumericFilter(filterStmt):
			pass
		elif isRegexFilter(filterStmt):
			pass

def isNumericFilter(stmt):
	return True

def isRegexFilter(stmt):
	return True

def dropTables(conn, allVars):
	cur = conn.cursor()
	for var in allVars:
		drop = 'drop table %s;'%(var[1:])
		cur.execute(drop)
	cur.execute('drop table result')

if __name__ == '__main__':

	if not len(sys.argv)==3:
		print("Missing arguments")
		sys.exit()
	
	db = sys.argv[1]
	# read in the filename
	filename = sys.argv[2]

	main(db, filename)