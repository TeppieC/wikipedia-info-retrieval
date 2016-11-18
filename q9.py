import sys
import sqlite3

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

	for line in lines:
		# for each line of the file
		print(line)

	conn.commit()
	conn.close()

if __name__ == '__main__':

	if not len(sys.argv)==3:
		print("Missing arguments")
		sys.exit()
	
	db = sys.argv[1]
	# read in the filename
	filename = sys.argv[2]

	main(db, filename)