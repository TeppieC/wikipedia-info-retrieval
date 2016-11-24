For q1:
	https://en.wikipedia.org/wiki/List_of_football_clubs_in_Italy
	seems not useful
	Another approach: Category:Football_venues_in_Italy
	Our approach: football clubs in italy --> stadiums used by the clubs --> the capacities of the stadiums

For q6,7,8:
	TODO: to distinguish float and decimal
	1. We store all literals in lexical
		17 --> "17"^^xsd:integer
		"mayor" --> "mayor"^xsd:integer
	2. We store all nodes of triples with complete uri
		dbr:Edmonton --> <http://dbpedia.org/resource/Edmonton>
	

	Do we assume that prefixes can be repeated? overriden throughout the file? 
	How do I know which type is the value, from the file? eg. if is int for population
		How to distinguish those types??? --> w/o quotes?
		** What do you mean by handling the types?
			To store them in their corresponding type in sqlite? or store which type they belong to and store themselves just as strings?
	Do we assume that all delimator/seperator is fixed? eg: ' ,\n\t\t'

How about empty nodes? _/??? or _???

FOR q9:
	SELECT and WHERE in capitalized forms?
	every line of query statement should be in the form of "subject predicate object . "

name the table as "statement"? is that okay? okay
return value should be in which form? For example:<http://dbpedia.org/resource/Edmonton>? okay