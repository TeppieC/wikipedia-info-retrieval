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

Q8部分测试结果
1. ,之前必须有间隔
2. 删掉statement中的某一项不行
3. 多加一个标点； 若是comma，就是少一项。若是period，就当做前一项的数据
4. :后面没东西，不算是错误。

Q8的TODO：
1. 处理@base/BASE/PREFIX
2. 处理a
3. 处理prefix没名字的情况
@prefix : <http://another.example/> .    # empty prefix
:subject5 :predicate5 :object5 .        # prefixed name, e.g. http://another.example/subject5

:subject6 a :subject7 .                 # same as :subject6 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> :subject7 .
@prefix : <http://example.org/elements> .                                                                              
<http://en.wikipedia.org/wiki/Helium>                                                                                  
    :atomicNumber 2 ;               # xsd:integer                                                                      
    :atomicMass 4.002602 ;          # xsd:decimal                                                                      
    :specificGravity 1.663E-4 .     # xsd:double      

4. 处理<http://example.org/#spiderman> <http://xmlns.com/foaf/0.1/name> "Человек-паук"@ru .
5. 处理multiple line
show:218 show:blurb '''This is a multi-line                        # literal with embedded new lines and quotes
literal with many quotes (""""")
and up to two sequential apostrophes ('').''' .
6. 在确认一下literal的存储方法, string/float/decimal/date/boolean/integer
7. 确认一下boolean

Q9TODO:
1. handle lexical literal cases
2. handle date/...
3. to meet all assumptions
4. check if absolute iri works??
5. 若select中出现了where里面没有的variable,throw error
6. assume that the variable in the filters would appear at least once in the statements inside the where clause

TODO:
1. 写readme，介绍一下数据库的构成，罗列一下Q8/9中的各种assumption，介绍一下命名，标注一下怎么run
2. 写q6/7
3. 编写一个Q8/9测试集(用于submit)，可以从cities.txt修改
4. 测试Q8/9的稳定性  ***（重要）
	a) 通过老师邮件里的链接，对他要求的所有文件都执行一遍Q8，确保无误
		0) 任意加减node的数量，删除关键字，等等
	b) 通过不同的query file，确保Q9的稳定性
		0) 基础情况：有*/不是所有variable都要select等等等等
		1) 许多许多variables
		2) 多个不同的filter
		很多空行/tab和\n混用等
		PREFIX的格式错误能不能detect
		{}的位置， 关键字的位置
		3) 同一个variable有多个不同种类的filter，可能filter相互矛盾
		4) 任意加减SELECT, prefix等关键字，逗号，句号，增减node的数量等等，这个要发挥想象力了。。
		5) 修改一些地方，制造明显的错误，保证程序会报错，也得发挥想象力。。。
		6) 我想不出来了，问问航爷吧。。。
5. 通过上步总结出的问题，实在修改不了的话，就写在程序开头的assumptions里面 ****（重要）
