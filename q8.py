import sys
import sqlite3

'''
Assuming that if a rdf format txt file is valid, 
the delimator between triples are " .\n"
the delimator between different prediactes are " ;\n\t"
the delimator between different objects are " ,\n\t\t"
for example, in Edmonton.txt
'''
SEMICOLON_DELIMATOR = ' ; '
COMMA_DELIMATOR = ' ,   '
PERIOD_DELIMATOR = ' . '

def isValidPrefix(string):
	stringList = string.split(' ')
	if not len(stringList)==3:
		return False
	if stringList[0]!='@prefix' and stringList[0]!='@base':
		return False
	if stringList[1][-1]!=':':
		return False
	if stringList[2][0]!='<' or stringList[2][-1]!='>':
		return False
	return True

def splitBySemicolon(data):
	tripleList = data.strip(' ').split(';')
	
	# extract the subject
	subject = tripleList[0].split(' ')[0] 
	
	for i in range(1, len(tripleList)):
		#insert the subject to make these become valid triple
		tripleList[i] = subject + tripleList[i]

	return tripleList

def splitByComma(triple):
	statements = []

	#print(triple)
	nodes = triple.strip(' ').split(' ')
	#print(nodes)
	# validate the triple data
	while not len(nodes)==3:
		# special case for triple such as 'dbr:Edmonton dbp:leaderTitle "Governing body"@en'
		# the resulting nodes list for this triple will be in length 4, 
		# because space existed in the object as a literal string
		# to fix this issue:
		# 1. check if this length(>3) is resulting by spliting the spaces in literal strings
		# note that only literal strings can have spaces in themselves
		for i in range(2, len(nodes)):
			# for all possible extra nodes:
			if nodes[i].count('"')%2==1:
				#print("triggered")
				# if there is an odd number of " quotes in the node, 
				# eg:  '"Manager"@en，"Governing' has 3 '"''s
				# eg: 'body"@en，dbr:Legislative_Assembly_of_Alberta，dbr:List_of_House_members_of_the_42nd_Parliament_of_Canada，"Mayor"@en' also has 3
				nodes[i]+=" "
				nodes[i]+=nodes[i+1]
				nodes.remove(nodes[i+1])
				break
			else:
				# else, this is indeed an invalid triple				
				print('Invalid triple data', triple)
				sys.exit()

	#print(nodes)
	# extract all three nodes of one triple data
	subject = nodes[0]
	predicate = nodes[1]
	objects = nodes[2].split('，') # a list of all objects (used to be separated by commas)
	#print("Objects are: ", objects)

	# to construct all complete triple statements, 
	#  by correspond each obj in the objects list to the subject&predicates
	for obj in objects:
		try: 
			if obj[-3:]=='@en': # deal with the language tag with @en at the end	
				statements.append([subject,predicate,obj[:-3]])
				continue
			elif obj[-3]=='@': # won't deal with languages other than English	
				continue
		except IndexError: # in case that some objects will have shorter length, eg: 11
			# those cases are common cases, without language tags, leave it to the next line
			pass

		statements.append([subject,predicate,obj]) # deal with the other(common) cases without language tags
		#print("new statements appended: ", [subject,predicate,obj])

	#print("new statements:", statements)
	#print(" ")
	return statements


def isfloat(value):
	try:
		float(value)
		return True
	except ValueError:
		return False

def isBoolean(value):
	return (value=="false" or value=="true")

def isLexical(string):
	'''
	determine if the type of the literal is like "1904-10-08"^^xsd:date
	'''
	if "^^" in string:
		return True
	else:
		return False

def replacePrefix(prefixDict, statement):
	outputStmt = []
	for node in statement:
		if(node[0]=='<' and node[-1]=='>'):
			# for pure uri's
			outputStmt.append(node)
		elif node[0]=='"' and node[-1]=='"':
			# for string literals
			outputStmt.append(node+'^^xsd:string')
		elif node.isnumeric():
			# for int
			outputStmt.append('"'+node+'"^^xsd:integer')
		elif isfloat(node):
			# for float/decimal
			outputStmt.append('"'+node+'"^^xsd:decimal')
		elif isLexical(node):
			# for the lexical data types, store them directly
			# "1904-10-08"^^xsd:date
			# "53.53333282470703125"^^xsd:float
			# "812201"^^xsd:nonNegativeInteger
			outputStmt.append(node)
		elif isBoolean(node):
			outputStmt.append('"'+node+'"^^xsd:boolean')
		else:
			# for prefixed nodes
			nodeList = node.split(":")
			prefix = ''
			try:
				prefix = prefixDict[nodeList[0]]
			except KeyError: # for empty prefix/node
				prefix = '<_/>'
			outputStmt.append(prefix[:-1] + nodeList[1] + prefix[-1])
	return outputStmt


def main(db, filename):

	conn = sqlite3.connect(db)
	print ("Opened database successfully")

	# create tables
	try:
		create = 'CREATE TABLE statement('+ \
				 ' id INT PRIMARY KEY,' + \
				 ' subject VARCHAR(100),' + \
				 ' predicate VARCHAR(100),'+\
				 ' object VARCHAR(100));'
		conn.execute(create)

		print ("Table created successfully")

	except sqlite3.OperationalError as e:
		print(e)

	dataList = []
	dataString = ''
	# possess the original file
	with open(filename) as f:
		for line in f:
			dataString+=' '.join(line.rstrip('\n').split('\t')) # replace \n or \t with proper spaces
			dataString+=' '
	# now the original file is represented as a single string -- dataString

	# replace the extra spaces remaining in the dataString
	dataString = dataString.replace(SEMICOLON_DELIMATOR, ";")
	dataString = dataString.replace(COMMA_DELIMATOR, "，")
	#print(dataString)
	# extract each triple/prefix from the dataString, and store them into a list
	# each element of dataList is a prefix or a triple, 
	# the last element should be discard because it's empty
	dataList = dataString.split(PERIOD_DELIMATOR)[:-1] 
	#print('')
	#print(dataList)

	prefixList = {}
	statements = []
	for data in dataList:
		if data[0]=='@': # store the prefix or base directives
			if not isValidPrefix(data): # check for validity
				print('Error: wrong format for prefix directive')
				sys.exit()
			directives = data.split(' ')
			prefixList[directives[1][:-1]] = directives[2] # store the prefix information to the dictionary
		else: # store the triple data
			tripleList = splitBySemicolon(data)
			#print(tripleList)
			for triple in tripleList:
				statements += splitByComma(triple)

	'''
	for prefix,value in prefixList.items():
		print(prefix)
		print(value)
	'''
	statementsNew = []
	for statement in statements:
		#print(statement)
		statementsNew.append(replacePrefix(prefixList, statement))

	''' Inserting into database '''
	id = 0
	try:
		for statement in statementsNew:
			conn.execute("INSERT INTO statement (id, subject, predicate, object) VALUES (?,?,?,?)", (id, statement[0], statement[1], statement[2]));
			id+=1
	except sqlite3.IntegrityError:
		print('Data has already existed in the database./ Integrity Error: abort the commit.')
		conn.close()
		sys.exit()

	print("Table updated successfully")
	conn.commit()
	conn.close()

if __name__ == '__main__':

	if not len(sys.argv)==3:
		print("Missing arguments")
		sys.exit()
	
	db = sys.argv[1]
	# read in the filename to operate
	filename = sys.argv[2]

	main(db, filename)
