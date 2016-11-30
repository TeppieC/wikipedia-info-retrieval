import sys
import sqlite3


'''
Run with the command: python3 q9.py <name_of_db>.db <name_of_queryfile>.txt

The table we used to store RDF data is called 'statement'

# Assume that 
# 1. The closing brace } will not be in the same line as the last statement.
# 2. All keywords in the provided query file should be in upper case. eg. SELECT or WHERE or FILTER
# 3. All statements should end with a period, otherwise the program will report the error.
# 4. All numeric filters will only perform on variables which are of numeric types(int/float/decimal with <=,>=,!=,=,<,> operators)
#		If a filter is performed on a non-numeric typed varaible, error will be prompt
# 5. All literals given in the filter has to be surrounded with double quotes
#		eg. FILTER (?number = "10") . where 10 is of a numeric type (int)
#			FILTER (regex(?v, "<text>")) where <text> is a string to be matched
# 6. All variables should be named with only one question mark, followed by alphabetic characters/digits
# 7. We assume that the database is in the same schema of q8.py, please see README.txt or q6.txt for details
# 8. All literals would be within double quotes, no matter which data type it is. (This is the one from the requirements page)
#		e.g  ?city dbo:populationTotal "1000000". ---- the object "1000000" will be considered as a numeric/int type by the program afterwards 

Glossary:

1. statements: are the lines inside WHERE clause of the pattern: subj1 pred1 obj1 .
	One line is one statement

2. triples: are the list of directives inside one statement. e.g [subj1, pred1, obj1] is a triple

3. varaible: the directives/identifiers which has a questionmark at the beginning. e.g ?city

4. one-variable-statement: the statement which has only one variable inside. The other two are prefixed nodes/literals
	aka. oneVarStmt
	e.g ?city rdf:type schema:City .

5. two-var-statement: the statement which has more than one(upto 3) variables inside.
	e.g ?city rdf:type ?schema .

6. filter variable: the variable which appears in the FILTER clause


Work flow of our program:

example:
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX schema: <http://schema.org/>
PREFIX dbr: <http://dbpedia.org/resource/>
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX foaf:	<http://xmlns.com/foaf/0.1/>
SELECT ?city  WHERE {
    ?city rdf:type schema:City .
  	?city dbo:populationTotal ?population. 
  	FILTER ( ?population >= "50000" ) .
} 

1. Extract all information from the query file. 

2. Create tables in the database, one table for each variable in the query file.
	e.g This will create tables named: city, population

3. Update the tables, by inserting into the data queried from all one-var-statements.
	e.g INSERT INTO city SELECT subject FROM statement WHERE predicate='rdf:type' and object='schema:city' 
		INSERT INTO population SELECT object FROM statement --just for example

4. Create one table for result, the colums are all varaibles appear in the SELECT clause, plus all filter varaibles.
	e.g CREATE TABLE result(...) the columns are city,population

5. Update the result table, from the table storing the RDF data and all tables created in step 2. The query will base
	on all two-var-statements. 
	e.g INSERT INTO result SELECT subject,object FROM city,population,statement WHERE predicate='dbo:populationTotal'

6. Once the result table is filled, apply filtering in python. Print the final result after filtering.
'''

global hasTwoVarStmt # To handle special case: when there is no two variable statements.
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
	global hasTwoVarStmt
	hasTwoVarStmt = False

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
			# for each line of the file
			if isPrefix(line): # extracting prefix definations
				if not isValidPrefix(line):
					print('prefix is not valid.')
					sys.exit()
				temp = line.split(':', 1) # temp == ['PREFIX rdf', ' <http://www.w3.org/1999/02/22-rdf-syntax-ns#>']
				if temp[0].strip()=='PREFIX' and len(temp)==2: # e.g line == PREFIX : <http://dbpedia.org/ontology/>
					prefix[' '] = temp[1].strip()
					continue
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

	# extract all querying statements inside the braces
	[statements, filters] = extractStatements(queryLines)
	print('statements', statements)
	print('filters', filters)
	if filters:
		[numFilters, regFilters] = extractFilters(filters)
		print('filters', filters)
		filterVars = set()
		for filterStmt in numFilters:
			filterVars.add(filterStmt[0])
		for filterStmt in regFilters:
			filterVars.add(filterStmt[0])
		print('filterVars, ', filterVars)

	statements = replacePrefix(statements, prefix)
	print('full statements', statements)

	# extracting all variables created in the query
	allVars = extractAllVariables(statements)
	print('allvars', allVars)
	# extracting all querying variables
	queryVars = extractVariables(queryStr)
	if not queryVars:
		print('You need to query variables')
		dropTables(conn, allVars)
		sys.exit()

	if queryVars[0]=='*':
		queryVars = allVars
	for var in queryVars:
		if not var in allVars:
			print('Selecting variables that is not existed: ', var)
			dropTables(conn, allVars)
			sys.exit()

	# adding the filtering variables into query variables
	# even though we dont need to display them ,they need to be queried
	resultVars = queryVars
	resultCols = len(resultVars)
	print('resultVars', resultVars)
	print('# of cols:', resultCols)

	if filters:
		for var in filterVars:
			if var not in queryVars:
				queryVars.append(var)
		print('queryVars', queryVars)
	
	
	# create the result table
	createResultTable(conn, queryVars)
	for var in allVars:
		queryInOneVarStmt(conn, statements, var)

	queryForRelations(conn, statements, queryVars, allVars)
	if not hasTwoVarStmt:
		#print('No statements has more than 1 variable')
		queryOnlyOneVar(conn, queryVars, allVars)

	result = queryResultBeforeFilter(conn)
	if filters:
		filtering(conn, numFilters, regFilters, result, queryVars, resultCols)
	else:
		printResultWithoutFilter(conn, queryVars)
	dropTables(conn, allVars)


	conn.commit()
	conn.close()












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
			output[1].append(content[1:-1])
			print('Filter is: ', content)
		else:
			triple = line.split()
			for i in range(0, len(triple)):
				node = triple[i]
				if isLiteral(node) and isNumeric(node[1:-1]):
					triple[i] = node[1:-1]
					print('Number:', triple)
			print(triple)
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
				node = node[:node.index('^^')]
				if isNumeric(node[1:-1]): # if is of numeric types that we need to handle
					node = node[1:-1]
					outputStmt.append(node)
				else: # if is of string type or any other types
					outputStmt.append(node)
			elif isLiteral(node):
				outputStmt.append(node)
			elif isNumeric(node):
				outputStmt.append(node)
			else:
				# for prefixed nodes
				if node[0]!='<': # if the node is not a prefixed node, nor a literal
					print('here:', node)
					nodeList = node.split(":")
					prefix = ''
					try:
						if nodeList[0]=='_': # for blank node
							prefix = '<_/>'
						elif len(nodeList)==2 and node[0]==':':
							prefix = prefixDict[' ']
						else:
							prefix = prefixDict[nodeList[0]]
					except KeyError: 
						print('Error on: ', nodeList[0])
						print('Did you miss the @ identifier / or double quotes of the literals?')
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
	for char in variableStr:
		if not (char==' ' or char.isalpha() or char=='?' or char=='*'):
			print('Invalid variables to select: ', variableStr)
			sys.exit()
	variables = variableStr.split()
	# validating
	for var in variables:
		if not (var[0]=='?' or var=='*'):
			print('Invalid format for variables to query')
			sys.exit()
	return variables

def extractFilters(filters):
	'''
	assume that all filters are in the form of FILTER(?var<="number") or FILTER(?var,<text>)
	'''
	output = [[],[]]
	for filt in filters:
		filt = filt.strip()
		if isRegexFilter(filt):
			#print('|'+filt+'|')
			filterVar = filt[filt.index('?'):filt.index(',')].strip()
			matchString = filt[filt.index('"')+1:-2].strip()
			output[1].append((filterVar, matchString))

		elif isNumericFilter(filt):
			if not filt[0]=='?':
				print('Wrong format of filter: ', filt)
				sys.exit()
			#print(filt)
			index = 1
			for char in filt[1:]:
				#print(char)
				if char.isalpha():
					index+=1
				else:
					break
			#print(index)
			filterVar = filt[:index].strip()
			#print(filterVar)
			indexLiteralStart = filt.index('"')
			#print('start', indexLiteralStart)
			indexLiteralEnd = filt[indexLiteralStart+1:].index('"')+indexLiteralStart+1
			#print('end', indexLiteralEnd)
			literal = filt[indexLiteralStart+1:indexLiteralEnd].strip()
			#print(literal)
			operator = filt[index:indexLiteralStart].strip()
			#print(operator)
			if not operator in ['<=','>=','=','!=','>','<']:
				print('Invalid operator for numeric filters: ', operator)
				sys.exit()
			if not isNumeric(literal):
				print('Need numeric literals for numeric filters: ', literal)
				sys.exit()

			output[0].append((filterVar, operator, literal))
		else:
			print('Invalid filter statement: ', filt)
			print('Filters should be in either the two following forms:')
			print('FILTER (?number >= "10") or  FILTER (regex(?variable, "<text>"))')

	return output











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
			#print('one var stmt for ', var, statement)
			sql_stmt = stmtForVar(statement, var)
			insert_stmt += sql_stmt
			insert_stmt += ' INTERSECT '
			exce = True
		if var in statement:
			pos.add(statement.index(var))
	if exce:
		#print(insert_stmt[:-11]+';')
		conn.execute(insert_stmt[:-11]+';')
	else:
		pos = list(pos)
		for p in pos:
			if p==0:
				insert_stmt = 'INSERT INTO %s '%(var[1:])
				insert_stmt+='select distinct subject from statement;'
				#print(insert_stmt)
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
	for node in stmt:
		if isVariable(node):
			i+=1
			nodeData = node
			
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
	Query functions for statements with more than 1 variables 
'''

def queryForRelations(conn, statements, queryVars, allVars):
	
	select_variables = tuple(a[1:] for a in queryVars) # list comprehension for creating a tuple
	select_clause = 'SELECT '+ '%s, '*len(queryVars)%select_variables
	select_clause = select_clause[:-2]+' '

	from_tables = tuple(a[1:] for a in allVars) # list comprehension for creating a tuple
	from_clause = 'FROM '+ '%s, '*len(allVars)%from_tables
	from_clause+='statement '

	insert_stmt = 'INSERT INTO result '
	twoVarStatements = twoVarStmts(statements) # get all statements with more than 1 variables
	#print('has %d  two var stmts'%(len(twoVarStatements)))

	global hasTwoVarStmt
	if len(twoVarStatements):
		print(hasTwoVarStmt)
		hasTwoVarStmt = True

	queryStr = ''
	exce = False
	for stmt in twoVarStatements:
		where_clause = twoVarWhereClause(stmt[0], stmt[1], stmt[2], stmt[3])
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
				#print('node is :', node)
				#print(i)
				index=i
			i+=1
		stmt.append(index)
		#print(stmt)
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
	if "^^" in string:
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

def isNumeric(string):
	if string.isnumeric():
		return True
	elif string[0]=='-' and string[1:].isnumeric():
		return True
	elif isfloat(string):
		return True
	elif string.count('^^')>0:
		i = string.index('^^')
		dataType = string[i+2:].strip()
		if dataType =='<http://www.w3.org/2001/XMLSchema#string>'\
			or dataType=='<http://www.w3.org/2001/XMLSchema#float>'\
			or dataType=='<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>'\
			or dataType=='xsd:integer' or dataType=='xsd:float' or dataType=='xsd:nonNegativeInteger':
			return True
		else:
			return False
	else:
		return False

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

def queryResultBeforeFilter(conn):
	'''
	return the result after querying the database without any filtering
	'''
	#conn.commit()
	cur = conn.cursor()
	cur.execute('SELECT * FROM result;')
	output = []
	for row in cur:
		#print(row)
		output.append(list(row))
	return output

def printResultWithoutFilter(conn, queryVars):
	'''
	print the result without any filtering
	'''
	#conn.commit()
	cur = conn.cursor()
	print('#'*90)
	print('Final Result')
	cur.execute('SELECT * FROM result;')
	count = 0
	print('|     %s     |'*len(queryVars)%tuple(queryVars))
	for row in cur:
		res = tuple(row)
		print('| %s |'*len(res)%res)
		count+=1

	print('%d results'%count)

def filtering(conn, numFilters, regFilters, result, queryVars, resultCols):
	print('Filtering the result')

	print('Temporary results')
	count = 0
	for row in result:
		print(row)
		count+=1
	print(count, ' results')

	#output = []
	print('Filters')
	for f in numFilters:
		filterResult = []
		print(f)
		var = f[0][1:]
		op = f[1]
		num = float(f[2])
		index = queryVars.index(f[0])
		for row in result:
			compareCol = row[index]
			if isNumeric(compareCol):
				compareCol = float(compareCol)
				print('compares: ', compareCol,' with ', num, 'operator:', op)
				if op=='=':
					if compareCol==num:
						filterResult.append(row)
				elif op=='>':
					if compareCol>num:
						filterResult.append(row)
				elif op=='<':
					if compareCol<num:
						filterResult.append(row)
				elif op=='>=':
					if compareCol>=num:
						filterResult.append(row)
				elif op=='<=':
					if compareCol<=num:
						filterResult.append(row)
				elif op=='!=':
					if not compareCol==num:
						filterResult.append(row)
				else:
					print('Invalid operator: ', op)
					dropTables(conn, allVars)
					sys.exit()
			else:
				print('Wrong type of variable: ', queryVars[index])
				print('The variable should be in numeric types, in order to perform numeric filtering')
		#output = filterResult
		result = filterResult


	for f in regFilters:
		filterResult = []
		print(f)
		var = f[0][1:]
		string = f[1]
		index = queryVars.index(f[0])
		for row in result:
			compareCol = row[index]
			#print('compares: ', compareCol,' with ', string)
			if string.lower() in compareCol.lower():
				filterResult.append(row)
		result = filterResult

	print('#'*90)
	print('Final Result')
	print('|   %s   |'*resultCols%tuple(queryVars)[:resultCols])
	count = 0
	for row in result:
		res = tuple(row[:resultCols])
		print('| %s |'*resultCols%res)
		count+=1
	print(count, ' results')

def isNumericFilter(filt):
	'''
	return if given string filt is a numeric filter
	'''
	# extracted filters should be in the form of: ?number = "10"
	if (">=" in filt) or \
		("<=" in filt) or \
		("=" in filt) or \
		("!=" in filt) or \
		(">" in filt) or \
		("<" in filt):
		return True

def isRegexFilter(filt):
	'''
	return if given string filt is a regex filter
	'''

	# extracted filters should be in the form of: regex(?v, "<text>")
	# TODO: validate
	if filt[:5]=='regex':
		return True
	else:
		return False

def dropTables(conn, allVars):
	cur = conn.cursor()
	try:
		for var in allVars:
			drop = 'drop table %s;'%(var[1:])
			cur.execute(drop)
		cur.execute('drop table result')
	except sqlite3.OperationalError:
		pass

if __name__ == '__main__':

	if not len(sys.argv)==3:
		print("Missing arguments")
		sys.exit()
	
	db = sys.argv[1]
	# read in the filename
	filename = sys.argv[2]

	main(db, filename)