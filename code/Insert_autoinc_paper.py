#encoding:utf-8
import MySQLdb
import MySQLdb.cursors

sql_ip = "192.168.1.198"
#sql_ip = "127.0.0.1"
db = MySQLdb.connect(host=sql_ip, user='jingfei', passwd='hanjingfei007', db='citation', charset='utf8')

cursor = db.cursor()

sql_select = "SELECT paper_id FROM paper" #找到所有paper_id
try:
	cursor.execute(sql_select)
	paper_id_set = cursor.fetchall() #Find all papers from citation1.paper, where venue_venue_id is a particular value.
except:
	sys.exit("ERROR: SELECT the TABLE paper failed!")

index_id = 1
for paper_id_tuple in paper_id_set:
	paper_id = paper_id_tuple[0]
	sql_update = "UPDATE paper SET index_id = '%d' WHERE paper_id='%d'" %(index_id, paper_id)
	try:
		cursor.execute(sql_update)
		db.commit()
		print "The venue %d paper's index_id is update SUCCESSFULLY!" %index_id
	except:
		sys.exit("This sql sentence : "  + sql_update +"  FAILED!")
	index_id += 1

