For q1:
	https://en.wikipedia.org/wiki/List_of_football_clubs_in_Italy
	seems not useful
	Another approach: Category:Football_venues_in_Italy
	Our approach: football clubs in italy --> stadiums used by the clubs --> the capacities of the stadiums

For q6,7,8:
	Do we assume that prefixes can be repeated? overriden throughout the file? 
	How do I know which type is the value, from the file? eg. if is int for population
		How to distinguish those types??? --> w/o quotes?
		** What do you mean by handling the types?
			To store them in their corresponding type in sqlite? or store which type they belong to and store themselves just as strings?
	Do we assume that all delimator/seperator is fixed? eg: ' ,   '

	A naive approach will get marks deducted?

	Everything need to be stored:
		every node, along with its prefix and data type
		every prefix defination
		every rdf statement

	默认language tag @位于-3

How should we deal with these types? 1. convert to pure literals such as float or int 2. cast to string
"53.53333282470703125"^^xsd:float
"812201"^^xsd:nonNegativeInteger
"1904-10-08"^^xsd:date
CHECK THE CODE COMMENT

all literals in the database should be stored with double quotes?
--> In Q4, when using the double quotes outside the integers, it will be an error
	for example, 	string type --> "mayor"
					int type --> "95504"
					float/decimal type --> "123.45"
					date type --> ""1904-10-08"
	therefore, when querying in Q9, the query will look like --> ?city dbp:populationTotal "95504"

How about empty nodes?