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

1. ,之前必须有间隔
2. 删掉statement中的某一项不行
3. 多加一个标点； 若是comma，就是少一项。若是period，就当做前一项的数据
4. :后面没东西，不算是错误。


TODO:
1. 写readme，标注一下怎么run
2. 写q6/7
3. 编写一个Q8/9测试集(用于submit)，可以从cities.txt修改
4. 测试Q8/9的稳定性  ***（重要）
	a) 通过老师邮件里的链接，对他要求的所有文件都执行一遍Q8，确保无误
		0) 任意加减node的数量，删除关键字，等等
	b) 通过不同的query file，确保Q9的稳定性
		0) 基础情况：有*/不是所有variable都要select等等等等
		1) 许多许多variables
		2) 多个不同的filter
		3) 同一个variable有多个不同种类的filter，可能filter相互矛盾
		4) 任意加减SELECT, prefix等关键字，逗号，句号，增减node的数量等等，这个要发挥想象力了。。
		5) 修改一些地方，制造明显的错误，保证程序会报错，也得发挥想象力。。。
		6) 我想不出来了，问问航爷吧。。。
5. 通过上步总结出的问题，实在修改不了的话，就写在程序开头的assumptions里面 ****（重要）