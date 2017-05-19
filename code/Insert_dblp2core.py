import MySQLdb
import MySQLdb.cursors
import sys

db = MySQLdb.connect(host='192.168.1.198', user='jingfei', passwd='hanjingfei007', db='aminer_gai', charset='utf8')
cursor = db.cursor()

sql_select = "SELECT CORE_id, dblp_id FROM core, dblp WHERE CORE_dblpname=dblp_name OR CORE_dblpname2=dblp_name OR CORE_dblpname3=dblp_name"

try:
	cursor.execute(sql_select)
	dblp2core_set = cursor.fetchall()
except:
	sys.exit("ERROR: SELECT tables failed!")

index = 1
for row_tuple in dblp2core_set:
	
	core_id = row_tuple[0]
	dblp_id = row_tuple[1]
	sql_insert = "INSERT INTO dblp2core(dblp2core_id, dblp_dblp_id, core_CORE_id) VALUES('%d', '%d', '%d')" %(index, dblp_id, core_id)
	try:
		cursor.execute(sql_insert)
		db.commit()
		print "%dth item is inserted successfully!" %index
	except:
		sys.exit("ERROR: INSERT tables failed!")
	index += 1
		
