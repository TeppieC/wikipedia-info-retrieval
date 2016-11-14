import sys
import sqlite3

SEMICOLON_DELIMATOR = ' ; '
COMMA_DELIMATOR = ' ,   '
PERIOD_DELIMATOR = ' . '

class Triple():
	"""docstring for Triple"""
	def __init__(self, dataString):
		self.dataString = dataString

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

def isValidTriple(string):
	#根据;分完以后，再根据空格分割，第一个必须有三部分，之后的必须至少两部分
	pass

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

	print(triple)
	nodes = triple.strip(' ').split(' ')
	print(nodes)
	# validate the triple data
	if not len(nodes)==3:
		print('Invalid triple data', triple)
		sys.exit()
	subject = nodes[0]
	predicate = nodes[1]
	objects = nodes[2].split(',') # a list of all objects

	for obj in objects:
		if obj[-3]=='@': # won't deal with languages other than English
			continue
		statements.append([subject,predicate,obj])

	return statements


def main(dataList):
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

	for prefix,value in prefixList.items():
		print(prefix)
		print(value)

	for statement in statements:
		print(statement)
'''
dbr:Edmonton	rdfs:label	"Edmonton"@it ,
		"Edmonton"@en ,
		"Edmonton"@es ,
		"Edmonton"@de ,
		"\u0625\u062F\u0645\u0648\u0646\u062A\u0648\u0646"@ar ,
		"Edmonton"@fr ,
		"\u042D\u0434\u043C\u043E\u043D\u0442\u043E\u043D"@ru ,
		"\u57C3\u5FB7\u8499\u987F"@zh ,
		"Edmonton"@pl ,
		"Edmonton"@pt ,
		"Edmonton"@nl ,
		"\u30A8\u30C9\u30E2\u30F3\u30C8\u30F3"@ja ;
	rdfs:seeAlso	dbr:Economy_of_Alberta ,
		dbr:The_Edmonton_Capital_Region ,
		dbr:List_of_neighbourhoods ,
		dbr:List_of_airports ,
		dbr:Landmark ,
		dbr:Edmonton ,
		dbr:List_of_attractions ,
		dbr:North_Saskatchewan_River_valley_parks_system .
		'''

if __name__ == '__main__':

	if not len(sys.argv)==3:
		print("Missing arguments")
		sys.exit()
	
	conn = sqlite3.connect(sys.argv[1])
	print ("Opened database successfully")

	# create tables
	try:	
		conn.execute('''
			CREATE TABLE statement(
			   	id INT PRIMARY KEY,
			   	sub_id INT,
			   	pred_id INT,
			   	obj_id INT
			);''')

		conn.execute('''
			CREATE TABLE node(
				node_id INT,
				uri VARCHAR(100),
				value VARCHAR(100),
				type VARCHAR(10),
				has_prefix VARCHAR(10)
			);''')

		conn.execute('''
			CREATE TABLE prefix(
				abbr VARCHAR(10),
				url VARCHAR(100)
			);''')
		print ("Table created successfully")

	except sqlite3.OperationalError as e:
		print("Table already existed for the operation")

	# read in the filename to operate
	filename = sys.argv[2]

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
	dataString = dataString.replace(COMMA_DELIMATOR, ",")
	#print(dataString)
	# extract each triple/prefix from the dataString, and store them into a list
	# each element of dataList is a prefix or a triple, 
	# the last element should be discard because it's empty
	dataList = dataString.split(PERIOD_DELIMATOR)[:-1] 
	#print(dataList)
	
	main(dataList)

	conn.commit()
	conn.close()