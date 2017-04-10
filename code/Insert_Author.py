# So complicate, I create two tables: author, affiliation

import MySQLdb
import MySQLdb.cursors
import sys


db = MySQLdb.connect(host='localhost', user='root', passwd='hanjingfei007', db='citation1', charset='utf8')
cursor = db.cursor()

f = open(r'../AMiner/AMiner-Author.txt', 'r')
#i = 0

sql_select = "SELECT COUNT(*) FROM affiliation"
try:
	cursor.execute(sql_select)
	cnt_aff = cursor.fetchone()[0]
	cnt_aff += 1
except:
	sys.exit("ERROR: SELECT the TABLE affiliation failed!")

dic = {
	'author_id' : '0',
	'author_name' : '0',
	'author_NbTotPubPaper' : '0',
	'author_H_Index' : '0',
	'author_tag' : '',
	'affiliation_name' : ''
}
cur_index = 1
while True:
	
	line = f.readline()
	if line:
		if line == '\n': #Insert data into the table
			sql_select1 = "SELECT affiliation_id FROM affiliation WHERE affiliation_name='%s'" %(dic['affiliation_name'])
			try:
				cursor.execute(sql_select1)
				id = cursor.fetchone()[0]
			except:
				sql1 = "INSERT INTO citation1.affiliation(affiliation_id, affiliation_name) VALUES('%d', '%s')" % (cnt_aff, dic['affiliation_name'])
				try:
					cursor.execute(sql1)
					db.commit()
					id = cnt_aff
					cnt_aff += 1
				except:
					sys.exit("ERROR: INSERT INTO the TABLE affiliation failed!")

			sql2 = "INSERT INTO citation1.author(author_id, author_name, author_NbTotPubPaper, author_H_Index, author_tag, affiliation_affiliation_id) \
					VALUES('%d', '%s', '%d', '%d', '%s', '%d')" %(dic['author_id'], dic['author_name'], dic['author_NbTotPubPaper'], dic['author_H_Index'], dic['author_tag'], id)
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
				'affiliation_name' : ''
			}
			if cur_index%1000 == 0:
				print "The %dth author is INSERTED successfuly!" %cur_index
			cur_index += 1
			continue
		elif line[1] == 'i':
			dic['author_id'] = int(line.replace('#index', '').strip())
		elif line[1] == 'n':
			dic['author_name'] = line.replace('#n', '').strip().replace('\'', '`')
		elif line[1] == 'a':
			dic['affiliation_name'] = line.replace('#a', '').strip().replace('\'', '`')
		elif line[1:3] == 'pc':
			dic['author_NbTotPubPaper'] = int(line.replace('#pc', '').strip())
		elif line[1] == 'h':
			dic['author_H_Index'] = int(line.replace('#hi', '').strip())
		elif line[1] == 't':
			dic['author_tag'] = line.replace('#t', '').strip().replace('\'', '`')
		
	else: #END OF FILE
		print "The %d authors are INSERTED FINISHED!" %(cur_index)
		break
f.close()