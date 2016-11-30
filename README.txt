Zhaorui Chen 1428317
Jinzhu Li 1461696

For q0:
	first we limit the type to be lake
	then we select lakes whose location object are Jasper_National_Park 

For q1:
	first limit the type to be SoccerClub
	for Italian soccer club select subject to be Football_clubs_in_Italy
	then select stadium whose type is Stadium
	connect team and staduim with object ground, which means the team has the ground staduim
	if available, use "OPTIONAL" to show the object capacity of the team

For q2:
	we assume the international airport is defined as those airpots with "International" in their names
	limit the type to be airport
	as we need the airport in Canada, select the city with Canada as object
	also connect the airport and city as airport has an city object
	finally we select the airport with "International" in their name using FILTER (regex(?v, "<text>"))

For q3:
	the club should have the league property called La_Liga
	"never been relegated" is an Unrelegated_association_football_clubs subject the club has
	then select players.
	player should have the club property which we select before. so we can connect players and clubs
	we assume "South American soccer players" means players whose birthplace is a country in South American
	which means these countries have Countries_in_South_America subject

For q4:
	basically the final has subject FIFA_World_Cup_finals
	then connect team and final according to that each final has team property
	count the number of country in result to check if the country(national soccer team) played more than 3 finals

For q5:
	the city has populationTotal object to let us know the population
	for every city in Alberta is a part of Alberta
	the hospital has an region object to be the city selected above
	finally calculate the ratio of population and number of hosptial and sort

For q6,7:
	Please check q6.txt for how we store the rdf data into the relational database. We have listed reasons and examples on how we do that. In q7.txt, we listed the indexes that are needed to created on the database.

For q8:
	run with: python3 q8.py <name_of_db>.db <name_of_rdf>.txt

	Please also check the header of our q8.py for the assumptions we made for the input file:
		1. Assume that the input file is in the same format as the examples 
			from https://www.w3.org/TR/turtle/ up to section 2.6 or Edmonton.txt

		2. blank node _:xxx will be stored as <xxx> in the database

		3. The relational database schema is described in q6.txt

		4. We dealt with the datatypes of integer/string/float/decimal. 
			The strings would be stored with double quotes.
			The int/float/decimal would be stored without double quotes.
			The other types would be stored in a lexical form. e.g "1904-10-08"^^xsd:date
			The data in other languages other than English would be ignored.

		5. We handled all errors that we could thought of. The update would not be commited 
			if an error occurs. The program would shut down and give appropriate prompt on error.


FOR q9:
	Run with the command: python3 q9.py <name_of_db>.db <name_of_queryfile>.txt

	Please check the header of our q9.py for details. 
	1) We listed the explanation of the terms we used to name the variables.
	2) We have also used a small example to illustrate how our program runs on queries.
	3) The following are the assumptions we made on the format of input files(also in the header of q9.py):
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

