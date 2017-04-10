import MySQLdb
import MySQLdb.cursors
import sys

db = MySQLdb.connect(host='192.168.1.198', user='jingfei', passwd='hanjingfei007', db='citation', charset='utf8')
cursor = db.cursor()

sql_select = "SELECT CCF_id, dblp_id FROM citation.ccf, citation.dblp WHERE CCF_dblpname=dblp_name"

try:
	cursor.execute(sql_select)
	dblp2ccf_set = cursor.fetchall()
except:
	sys.exit("ERROR: SELECT tables failed!")

index = 1
for row_tuple in dblp2ccf_set:
	
	ccf_id = row_tuple[0]
	dblp_id = row_tuple[1]
	sql_insert = "INSERT INTO citation.dblp2ccf(dblp2ccf_id, dblp_dblp_id, ccf_CCF_id) VALUES('%d', '%d', '%d')" %(index, dblp_id, ccf_id)
	try:
		cursor.execute(sql_insert)
		db.commit()
		print "%dth item is inserted successfully!" %index
	except:
		sys.exit("ERROR: INSERT tables failed!")
	index += 1
		
