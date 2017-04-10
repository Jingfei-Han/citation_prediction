import MySQLdb
import MySQLdb.cursors
import sys
import re

db = MySQLdb.connect(host='localhost', user='root', passwd='hanjingfei007', db='citation', charset='utf8')
cursor = db.cursor()

sql_select_cnt = "SELECT COUNT(*) FROM citation.dblp WHERE dblp_id<10000000"
try:
	#Record the number of items of table dblp
	cursor.execute(sql_select_cnt)
	cnt_venue = cursor.fetchone()[0]
	cnt_venue += 1
except:
	sys.exit("ERROR: SELECT the TABLE venue failed!")

#cnt_venue = 1
cnt_index = cnt_venue


sql_select = "SELECT venue_dblpname FROM citation.venue WHERE venue_dblpname IS NOT NULL"

try:
	#Get the set of venue's dblpname where the dblpname is not null.
	cursor.execute(sql_select)
	venue_set = cursor.fetchall()
except:
	sys.exit("ERROR: SELECT the TABLE dblp failed!")

for onevenue_tuple in venue_set:
	onevenue = onevenue_tuple[0]
	#Whether the venue' last character is )
	if onevenue[-1] == ')':
		pattern = re.match(r'(.*)(\(.*\))', onevenue)
		onevenue = pattern.group(1)
	onevenue = onevenue.strip()
	sql_select1 = "SELECT dblp_id FROM citation.dblp WHERE dblp_name='%s'" %onevenue
	try:
		#Search the dblp id
		cursor.execute(sql_select1)
		id = cursor.fetchone()[0]
		sql_update = "UPDATE citation.venue SET dblp_dblp_id='%d' WHERE venue_dblpname='%s'" %(id, onevenue)
		try:
			cursor.execute(sql_update)
			db.commit()
		except:
			sys.exit("ERROR: Update the TABLE dblp failed!")
	except:
		sql1 = "INSERT INTO citation.dblp(dblp_id, dblp_name) VALUES('%d', '%s')" % (cnt_venue, onevenue)
		try:
			cursor.execute(sql1)
			db.commit()
		except:
			sys.exit("ERROR: INSERT INTO the TABLE dblp failed!")

		sql_update = "UPDATE citation.venue SET dblp_dblp_id='%d' WHERE venue_dblpname='%s'" %(cnt_venue, onevenue)
		try:
			cursor.execute(sql_update)
			db.commit()
		except:
			sys.exit("ERROR: Update the TABLE dblp failed!")

		cnt_venue += 1

	if(cnt_index % 10 == 0):
		print "The %dth venue is updated correctly!" %cnt_index
	cnt_index += 1

print "All dblp venues are updated SUCCESSFULLY!"