import sys
import sqlite3

'''
Run with the command: python3 q8.py <name_of_db>.db <name_of_rdf>.txt

1. Assume that the input file is in the same format as the examples 
from https://www.w3.org/TR/turtle/ up to section 2.6 or Edmonton.txt

2. Please remove all comments(start with #) in the txt file before running. 

3. blank node _:a will be stored as <a> in the database

4. The relational database schema is described in q6.txt

5. We dealt with the datatypes of integer/string/float/decimal. 
	The strings would be stored with double quotes.
	The int/float/decimal would be stored without double quotes.
	The other types would be stored in a lexical form. e.g "1904-10-08"^^xsd:date
	The data in other languages other than English would be ignored.

6. We handled all errors that we could thought of. The update would not be commited 
	if an error occurs. The program would shut down and give appropriate prompt on error.
'''

def isValidPrefix(string):
	stringList = string.split()
	if not len(stringList)==3:
		return False
	if stringList[0]!='@prefix' and stringList[0]!='@base'\
		and stringList[0]!='PREFIX' and stringList[0]!='BASE':
		return False
	if stringList[1][-1]!=':':
		return False
	if stringList[2][0]!='<' or stringList[2][-1]!='>':
		return False
	return True

def splitBySemicolon(data):
	tripleList = data.strip().split(' ;')
	
	# extract the subject
	subject = tripleList[0].split()[0] 
	
	for i in range(1, len(tripleList)):
		#insert the subject to make these become valid triple
		tripleList[i] = subject + tripleList[i]

	return tripleList


def splitByComma(triple):
	statements = []
	### Special case: To handle different input types, when doing the spliting based on white spaces
	### 	If comma is closely followed each object, replace them with &&&&
	###		If comma is followed with one space after one object, replace them with ||||
	print('Triple before replacing, after split by semicolon: ', triple)
	triple = triple.replace(' , ', '||||').replace(', ', '&&&&')
	print('Triple after replacing: ', triple)

	# Special case: to handle the multiple lines
	if triple.count("'''")>0:
		indexStart = triple.index("'''")+3
		indexEnd = triple[indexStart:].index("'''")
		triple =  triple[:indexStart]+triple[indexStart:indexEnd].replace(" ","|")+triple[indexEnd:]

	# Do the split based on white spaces
	nodes = triple.strip().split()


	# change the characters back
	for i in range(0, len(nodes)):
		nodes[i]=nodes[i].replace('||||', ' , ').replace('&&&&', ', ')
		if triple.count("'''")>0:
			nodes[i]=nodes[i].replace('|', ' ')


	#print(nodes)
	print('Nodes list generated: ', nodes)
	# validate the triple data
	while not len(nodes)==3:
		if len(nodes)<3:
			print('Invalid triple data: ', nodes)
			sys.exit()
		# Special case:  for triple such as 'dbr:Edmonton dbp:leaderTitle "Governing body"@en'
		# the resulting nodes list for this triple will be in length 4, 
		# because space existed in the object as a literal string
		# To fix this issue:
		# 	check if this length(>3) is resulting by spliting the spaces in literal strings
		# 	note that only literal strings can have spaces in themselves
		for i in range(2, len(nodes)):
			print('Looping inside the while loop')
			# for all possible extra nodes:
			if nodes[i].count('"')%2==1:
				# if there is an odd number of " quotes in the node, 
				# eg:  '"Manager"@en，"Governing' has 3 '"''s
				# eg: 'body"@en，dbr:Legislative_Assembly_of_Alberta，dbr:List_of_House_members_of_the_42nd_Parliament_of_Canada，"Mayor"@en' also has 3
				nodes[i]+=" "
				nodes[i]+=nodes[i+1]
				nodes.remove(nodes[i+1])
				break
			else:
				# else, this is indeed an invalid triple				
				print('Invalid triple data: did you forget any periods/commas/semicolons/triple node?', nodes)
				sys.exit()

	# extract all three nodes of one triple data
	subject = nodes[0]
	predicate = nodes[1]
	print('Objects string before spliting by comma is: ', nodes[2])
	objects = nodes[2].split(' , ') # a list of all objects (used to be separated by commas)

	for obj in objects:
		if obj.count('"')>2:
			print('More than 1 objects inside of this node, may be caused by wrong delimator: ', obj)
			temp = obj.split(', ')
			objects.remove(obj)
			objects+=temp

	# to construct all complete triple statements, 
	#  by correspond each obj in the objects list to the subject&predicates
	for obj in objects:
		print('Objects list extracted: ', objects)
		try: 
			if obj[-3:]=='@en': # deal with the language tag with @en at the end	
				statements.append([subject,predicate,obj[:-3]])
				continue
			elif obj[-3]=='@': # won't deal with languages other than English	
				continue
		except IndexError: # in case that some objects will have shorter length, eg: 11
			# those cases are common cases, without language tags, leave it to the next line
			pass

		statements.append([subject,predicate,obj]) # deal with the other(common) cases, without language tags
		#print("new statements appended: ", [subject,predicate,obj])

	#print("new statements:", statements)
	#print(" ")
	print('Statements list generated: ', statements)
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

def replacePrefix(prefixDict, statement, hasEmptyPrefix, hasBase, base):
	outputStmt = []
	print('Statement is: ',statement)
	for node in statement:
		print('----Node is: ', node)
		if(node[0]=='<' and node[-1]=='>'):
			if not hasBase:
				# for absolute iris
				outputStmt.append(node)
			else:
				outputStmt.append('<'+base[1][1:-1]+node[1:-1]+'>')
				#print('after prefix with base:|', '<'+base[1][1:-1]+node[1:-1]+'>', '|')
		elif node=='a':
			outputStmt.append('<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>')
		elif node[0]=='"' and node[-1]=='"':
			# for string literals
			outputStmt.append(node)
			#outputStmt.append(node+'^^xsd:string')
		elif node[:3]=="'''":
			outputStmt.append(node)
		elif node.isnumeric():
			# for int
			outputStmt.append(node)
			#outputStmt.append('"'+node+'"^^xsd:integer')
		elif isfloat(node):
			# for float/decimal
			outputStmt.append(node)
			#outputStmt.append('"'+node+'"^^xsd:decimal')
		elif isLexical(node):
			# for the lexical data types, store them directly
			# "1904-10-08"^^xsd:date
			# "53.53333282470703125"^^xsd:float
			# "812201"^^xsd:nonNegativeInteger
			dataType = node[node.index(':')+1:]
			if dataType=='float' or dataType=='nonNegativeInteger' or dataType=='string' \
				or dataType=='<http://www.w3.org/2001/XMLSchema#string>'\
				or dataType=='<http://www.w3.org/2001/XMLSchema#float>'\
				or dataType=='<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>':
				outputStmt.append(node[1:node.index('^^')-1])
			else:
				outputStmt.append(node)
		elif isBoolean(node):
			outputStmt.append(node)
			#outputStmt.append('"'+node+'"^^xsd:boolean')
		else:
			# for prefixed nodes
			nodeList = node.split(":")
			prefix = ''
			if not len(nodeList)==2:
				if node[0]==':' and hasEmptyPrefix:
					'''
					@prefix : <http://another.example/> .    # empty prefix
					:subject5 :predicate5 :object5 .        # prefixed name, e.g. http://another.example/subject5
					'''
					outputStmt.append('')
				#print('h|', node)
				print('Invalid prefix delcaration: ', nodeList)
				print('Did you miss the colon?')
				sys.exit()
			try:
				if nodeList[0]=='_': # for empty prefix
					prefix = '<>'
				else:
					prefix = prefixDict[nodeList[0]]
			except KeyError: 
				print('Undefined prefix identifier: ', nodeList[0])
				print('Did you miss the @ identifier for prefix defination?')
				sys.exit()
			outputStmt.append(prefix[:-1] + nodeList[1] + prefix[-1])
	return outputStmt

def printResult(conn):
	'''
	print the result without any filtering
	'''
	#conn.commit()
	cur = conn.cursor()
	print('#'*90)
	cur.execute('SELECT * FROM statement;')
	count = 0
	print('|       %s      |'*4%('ID','subject', 'predicate', 'object'))
	for row in cur:
		print(row)
		count+=1
	print('%d rows'%count)

def main(db, filename):

	conn = sqlite3.connect(db)
	print ("Opened database successfully")

	# create tables
	try:
		create = 'CREATE TABLE statement('+ \
				 ' id INT PRIMARY KEY,' + \
				 ' subject TEXT,' + \
				 ' predicate TEXT,'+\
				 ' object TEXT);'
		conn.execute(create)

		print ("Table created successfully")

	except sqlite3.OperationalError as e:
		print('Table already existed in the database.')
		print('Please remove it before re-running this program')
		sys.exit()

	dataList = []
	dataString = ''
	# possess the original file
	with open(filename) as f:
		for line in f:
			line = line.replace('\t',' ').replace('\n', ' ').replace('\s',' ').strip()
			print("new line is: ",line)
			try:
				if line[-1]=='.' and line[-2]!=' ':
					line = line[:-1]+' . '
				elif line[-1]==',' and line[-2]!=' ':
					line = line[:-1]+' , '
				elif line[-1]==';' and line[-2]!=' ':
					line = line[:-1]+' ; '
			except IndexError:
				pass
			dataString+=' '.join(line.rstrip('\n').split('\t')) # replace \n or \t with proper spaces
			dataString+=' '
	# now the original file is represented as a single string -- dataString

	# deal with PREFIX
	while True:
		try:
			i = dataString.index('PREFIX')
			#print('index is:',i)
		except ValueError:
			break
		subStr1 = dataString[:i]
		subStr2 = dataString[i:]
		subStr2 = subStr2.replace('PREFIX','@prefix')
		j = subStr2.index('>')
		subStr2 = subStr2[:j+1]+' .'+subStr2[j+1:]
		dataString = subStr1+subStr2
		#print('datastring is: ', dataString)

	# deal with BASE
	while True:
		try:
			i = dataString.index('BASE')
			#print('index is:',i)
		except ValueError:
			break
		subStr1 = dataString[:i]
		subStr2 = dataString[i:]
		subStr2 = subStr2.replace('BASE','@base')
		j = subStr2.index('>')
		subStr2 = subStr2[:j+1].strip()+' .'+subStr2[j+1:]
		dataString = subStr1+subStr2
		#print('datastring is: ', dataString)

	print('Final datastring is: ', dataString)
	# extract each triple/prefix from the dataString, and store them into a list
	# each element of dataList is a prefix or a triple, 
	# the last element should be discard because it's empty
	dataList = dataString.split(' . ')[:-1]
	#print('')
	print('Final datalist is: ', dataList)

	prefixList = {}
	base = []
	hasEmptyPrefix = False
	hasBase = False
	statements = []
	for data in dataList:
		data = data.strip()
		if data[0:7]=='@prefix' or data[0:6]=='PREFIX': # store the prefix or base directives
			if not isValidPrefix(data): # check for validity
				print('Wrong format for prefix defination: ', data)
				sys.exit()
			directives = data.split()
			prefixList[directives[1][:-1]] = directives[2] # store the prefix information to the dictionary
			#print('prefix')
		elif data[0:5]=='@base' or data[0:4]=='BASE':
			hasBase = True
			base = data.split()
			print('base is:', base)
		else: # store the triple data
			print('&&&&&&&&&&& split by semicolon &&&&&&&&&&&&')
			tripleList = splitBySemicolon(data)
			print('^^^^^^^^^^^^^ split by comma ^^^^^^^^^^^^^^^')
			print('Triple List is: ',tripleList)
			#print(tripleList)
			for triple in tripleList:
				statements+=splitByComma(triple)


	print('-------------------Replacing prefixes---------------------')
	print('Final statements List is: ', statements)
	statementsNew = []
	for statement in statements:
		#print(statement)
		statementsNew.append(replacePrefix(prefixList, statement, hasEmptyPrefix, hasBase, base))

	''' Inserting into database '''
	id = 0
	try:
		for statement in statementsNew:
			conn.execute("INSERT INTO statement (id, subject, predicate, object) VALUES (?,?,?,?)", (id, statement[0], statement[1], statement[2]))
			id+=1
	except sqlite3.IntegrityError:
		print('integrity error: Data has already existed in the database.')
		conn.close()
		sys.exit()

	printResult(conn)

	print('NOTE: Please check with sqlite3 <name_of_db>.db for exact results/schema')
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
