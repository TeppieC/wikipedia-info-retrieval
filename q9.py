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
			l = line.rstrip('\n').strip()
			if not l=='':
				lines.append(l) # process the lines

	prefix = {}
	queryVars = []
	triples = []

	# extract data
	for line in lines:
		# for each line of the file
		print(line+'|EOF') # for debug use
		if isPrefix(line):
			pass
		elif startWithSelect(line):
			if endWithBrace(line):
				# SELECT ?v1 ?v2 ?v3 WHERE {
				pass
			elif endWithWhere(line):
				# SELECT ?v1 ?v2 ?v3 WHERE
				pass
			else:
				# SELECT ?v1 ?v2 ?v3
				pass
		elif startWithWhere(line):
			if endWithBrace(line):
				pass
			else:




	conn.commit()
	conn.close()

def validatePrefix(line):
	pass

def validateQuery(line):
	# no more than one occurance of {,},SELECT,WHERE
	# SELECT occurs before WHERE
	# { occurs before }
	pass

def isPrefix(string):
	if string.split(' ')[0]=='PREFIX':
		return True
	else:
		return False

def startWithSelect(string):
	if string.split(' ')[0]=='SELECT':
		return True
	else:
		return False

def startWithWhere(string):
	if string.split(' ')[0]=='WHERE':
		return True
	else:
		return False

def endWithWhere(string):
	if string.split(' ')[-1]=='WHERE':
		return True
	else:
		return False

def startWithBrace(string):
	if string[0]=='{' or string[0]=='}':
		return True
	else:
		return False

def endWithBrace(string):
	if string[-1]=='}' or string[-1]=='{':
		return True
	else:
		return False

if __name__ == '__main__':

	if not len(sys.argv)==3:
		print("Missing arguments")
		sys.exit()
	
	db = sys.argv[1]
	# read in the filename
	filename = sys.argv[2]

	main(db, filename)