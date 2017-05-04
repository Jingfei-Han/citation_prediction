#encoding:utf-8
import MySQLdb
import MySQLdb.cursors
import sys

db = MySQLdb.connect(host='192.168.1.198', user='jingfei', passwd='hanjingfei007', db='citation', charset='utf8')
cursor = db.cursor()
"""
#先将CCF的dblpname插入到dblp表中

sql_index = "SELECT COUNT(*) FROM dblp"
cnt_index = 1
try:
	cursor.execute(sql_index)
	cnt_index = cursor.fetchone()[0]
	cnt_index += 1
except:
	sys.exit("Current index FAILED!")

sql1_select = "SELECT CCF_dblpname FROM ccf WHERE CCF_dblpname!='NOT IN DBLP' "
try:
	cursor.execute(sql1_select)
	insert_set1 = cursor.fetchall()
except:
	sys.exit("ERROR: SELECT FAILED!")

for row_tuple in insert_set1:
	CCF_dblpname = row_tuple[0]
	#先查找
	try:
		cursor.execute("SELECT * FROM dblp WHERE dblp_name = CCF_dblpname")
		cur_id = cursor.fetchone()[0]
	except:

		#sql1_insert = "INSERT INTO dblp(dblp_id, dblp_name) VALUES('"

"""

sql_select = "SELECT CCF_id, dblp_id FROM citation.ccf, citation.dblp WHERE CCF_dblpname=dblp_name OR CCF_dblpname2=dblp_name OR CCF_dblpname3=dblp_name"

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
		
