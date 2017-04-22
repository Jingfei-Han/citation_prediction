#encoding:utf-8
#该程序用于向citation数据库中插入paper表和venue表。dblp_dblp_id 初始化为 MAX_ID
import MySQLdb
import MySQLdb.cursors
import sys
import re
MAX_ID = 999999999

db = MySQLdb.connect(host='192.168.1.198', user='jingfei', passwd='hanjingfei007', db='citation', charset='utf8')
cursor = db.cursor()

f = open(r'/home/jingfei/AMiner/AMiner-Paper.txt', 'r') #From server to run.
#i = 0
sql_select = "SELECT COUNT(*) FROM venue"
try:
	cursor.execute(sql_select)
	cnt_aff = cursor.fetchone()[0]
	cnt_aff += 1
except:
	sys.exit("ERROR: SELECT the TABLE venue failed!")

dic = {
	'paper_id' : 0,
	'paper_title' : '0',
	'paper_publicationYear' : 0,
	'paper_nbCitation' : -1,
	'paper_abstract' : '',
	'paper_isseen' : 0,
	'venue_name' : ''
}
cur_index = 1
while True:
	
	line = f.readline()
	if line:
		if line == '\n': #Insert data into the table
			if dic['paper_publicationYear'] < 2000: #Consider papers whose publication year greater or equal than 2000
				continue

			if dic['paper_title'] == dic['venue_name']: #ERROR DATA, delete it.
				continue

			sql_select1 = "SELECT venue_id FROM venue WHERE venue_name='%s'" %(dic['venue_name'])
			try:
				cursor.execute(sql_select1)
				id = cursor.fetchone()[0]
			except:
				sql1 = "INSERT INTO venue(venue_id, venue_name, dblp_dblp_id) VALUES('%d', '%s', '%d')" % (cnt_aff, dic['venue_name'], MAX_ID)
				try:
					cursor.execute(sql1)
					db.commit()
					id = cnt_aff
					cnt_aff += 1
				except:
					sys.exit("ERROR: INSERT INTO the TABLE venue failed!")

			#去掉paper title中的无用字段。
			dic['paper_title'] = dic['paper_title'].replace("Fast track article: ","").replace("Research Article: ","").replace("Guest editorial: ","").replace("Letters: ","").replace("Editorial: ","").replace("Chaos and Graphics: ","").replace("Review: ","").replace("Education: ","").replace("Computer Graphics in Spain: ","").replace("Graphics for Serious Games: ","").replace("Short Survey: ","").replace("Brief paper: ","").replace("Original Research Paper: ","").replace("Review: ","").replace("Poster abstract: ","").replace("Erratum to: ","").replace("Review: ","").replace("Guest Editorial: ","").replace("Review article: ","").replace("Editorial: ","").replace("Short Communication: ","").replace("Invited paper: ","").replace("Book review: ","").replace("Technical Section: ","").replace("Fast communication: ","").replace("Note: ","").replace("Introduction: ","")
			
			sql2 = "INSERT INTO paper(paper_id, paper_title, paper_publicationYear, paper_nbCitation, paper_abstract, paper_isseen, venue_venue_id) \
					VALUES('%d', '%s', '%d', '%d', '%s', '%s', '%d')" %(dic['paper_id'], dic['paper_title'], dic['paper_publicationYear'], dic['paper_nbCitation'], dic['paper_abstract'], dic['paper_isseen'], int(id))
			try:
				cursor.execute(sql2)
				db.commit()
			except:
				if cur_index%5000 == 0:
					print "Current %d record exist in the TABLE paper." %cur_index

			dic = {
				'paper_id' : 0,
				'paper_title' : '0',
				'paper_publicationYear' : 0,
				'paper_nbCitation' : -1,
				'paper_abstract' : '',
				'paper_isseen' : 0,
				'venue_name' : ''
			}
			if cur_index%1000 == 0:
				print "The %dth paper is INSERTED successfuly!" %cur_index
			cur_index += 1
			continue
		elif line[1] == 'i':
			dic['paper_id'] = int(line.replace('#index', '').strip())
		elif line[1] == '*':
			dic['paper_title'] = line.replace('#*', '').strip().replace('\'', '\\\'')
		elif line[1] == 't':
			str = line.replace('#t', '').replace(':','').strip()
			if str=='':
				dic['paper_publicationYear'] = 0;
			else:
				convert = re.search(r'(\d+)', str).group()
				dic['paper_publicationYear'] = int(convert)
		elif line[1] == 'c':
			dic['venue_name'] = line.replace('#c', '').strip().replace('\'', '\\\'')
			if dic['venue_name'] == '':
				continue
		elif line[1] == '!':
			dic['paper_abstract'] = line.replace('#!', '').strip().replace('\'', '\\\'')

		
	else: #END OF FILE
		print "The %d papers are INSERTED FINISHED!" %(cur_index)
		break
f.close()
