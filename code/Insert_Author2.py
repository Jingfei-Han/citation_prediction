# Simple version, I create one table: author

import MySQLdb
import MySQLdb.cursors
import sys


db = MySQLdb.connect(host='192.168.1.198', user='jingfei', passwd='hanjingfei007', db='citation', charset='utf8')
cursor = db.cursor()

f = open(r'/home/jingfei/AMiner/AMiner-Author.txt', 'r')
#i = 0

dic = {
	'author_id' : '0',
	'author_name' : '0',
	'author_NbTotPubPaper' : '0',
	'author_H_Index' : '0',
	'author_tag' : '',
	'author_affiliation_name' : ''
}
cur_index = 1
while True:
	
	line = f.readline()
	if line:
		if line == '\n': #Insert data into the table

			sql2 = "INSERT INTO author(author_id, author_name, author_NbTotPubPaper, author_H_Index, author_tag, author_affiliation_name) \
					VALUES('%d', '%s', '%d', '%d', '%s', '%s')" %(dic['author_id'], dic['author_name'], dic['author_NbTotPubPaper'], dic['author_H_Index'], dic['author_tag'], dic['author_affiliation_name'])
			try:
				cursor.execute(sql2)
				db.commit()
			except:
				print "Current record exist in the TABLE author."

			dic = {
				'author_id' : '0',
				'author_name' : '0',
				'author_NbTotPubPaper' : '0',
				'author_H_Index' : '0',
				'author_tag' : '',
				'author_affiliation_name' : ''
			}
			if cur_index%10000 == 0:
				print "The %dth author is INSERTED successfuly!" %cur_index
			cur_index += 1
			continue
		elif line[1] == 'i':
			dic['author_id'] = int(line.replace('#index', '').strip())
		elif line[1] == 'n':
			dic['author_name'] = line.replace('#n', '').strip().replace('\'', '\\\'')
		elif line[1] == 'a':
			dic['author_affiliation_name'] = line.replace('#a', '').strip().replace('\'', '\\\'')
		elif line[1:3] == 'pc':
			dic['author_NbTotPubPaper'] = int(line.replace('#pc', '').strip())
		elif line[1] == 'h':
			dic['author_H_Index'] = int(line.replace('#hi', '').strip())
		elif line[1] == 't':
			dic['author_tag'] = line.replace('#t', '').strip().replace('\'', '\\\'')
		
	else: #END OF FILE
		print "The %d authors are INSERTED FINISHED!" %(cur_index-1)
		break
f.close()
