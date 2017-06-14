#encoding:utf-8

import MySQLdb
import MySQLdb.cursors


db = MySQLdb.connect(host="127.0.0.1", user="root", passwd = "hanjingfei007", db="aminer", charset="utf8")
cursor = db.cursor()

f = open(r'D:/Citation_prediction/AMiner/AMiner-Author2Paper.txt', 'r')

while True:
	line = f.readline()
	if line is None:
		print "FINISH!!"
		break
	dic = line.strip().split('\t')
	#dic's data: id, author, paper, order
	#mysql: a2p_id, author_author_id, paper_paper_id, a2p_order
	sql = "INSERT INTO a2p(a2p_id, author_author_id, paper_paper_id, a2p_order)\
		   VALUES('%d','%d','%d','%d')" %(int(dic[0]),int(dic[1]),int(dic[2]),int(dic[3]))
	try:
		cursor.execute(sql)
		db.commit()
	except:
		print "Not exist in author or paper!"
		pass
	if (int(dic[0]) % 10000 == 0):
		print (dic[0] + " is successfully!")

f.close()
