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

How about empty nodes? _/??? or _???

有关q8和q9：
	1. q9中会给出"53.53333282470703125"^^xsd:float这种形式的数据进行filter query，
		因此，在q8中，需要将所有的int/float/decimal存为^^xsd:...形式的，带有double quote的字符
			若原来就是这种形式，将他们直接放进去；若原来是单纯的float/int形式，把他们变成xsd的形式
	2. 对于q8中的delimitor，似乎并不一定是固定的格式，还得再想想，下周问一次ta确定一下