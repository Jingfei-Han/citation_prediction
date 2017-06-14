import MySQLdb
import MySQLdb.cursors
import sys
import re


db = MySQLdb.connect(host='127.0.0.1', user='root', passwd='hanjingfei007', db='aminer', charset='utf8')
cursor = db.cursor()

f = open(r'D:/Citation_prediction/AMiner/AMiner-Paper.txt', 'r')

dic = {
	'paper_id' : 0,
	'paper_title' : '0',
	'paper_publicationYear' : 0,
	'paper_abstract' : '',
	'venue_name' : ''
}
cur_index = 1
cnt_aff = 1
while True:
	
	line = f.readline()
	if line:
		if line == '\n': #Insert data into the table
			#if dic['paper_publicationYear'] < 2010: #Consider papers whose publication year greater or equal than 2010
			#	continue

			#if dic['paper_title'] == dic['venue_name']: #ERROR DATA, delete it.
			#	continue
			sql_select1 = "SELECT venue_id FROM venue WHERE venue_name='%s'" %(dic['venue_name'])
			try:
				cursor.execute(sql_select1)
				id = cursor.fetchone()[0]
			except:
				sql1 = "INSERT INTO venue(venue_id, venue_name) VALUES('%d', '%s')" % (cnt_aff, dic['venue_name'])
				try:
					cursor.execute(sql1)
					db.commit()
					id = cnt_aff
					cnt_aff += 1
				except:
					sys.exit("ERROR: INSERT INTO the TABLE venue failed!")


			sql2 = "INSERT INTO paper(paper_id, paper_title, paper_publicationYear, paper_abstract, venue_venue_id) \
					VALUES('%d', '%s', '%d', '%s', '%d')" %(dic['paper_id'], dic['paper_title'], dic['paper_publicationYear'], dic['paper_abstract'], int(id))
			try:
				cursor.execute(sql2)
				db.commit()
			except:
				#if cur_index%5000 == 0:
				print "Current %d record exist in the TABLE paper." %cur_index

			dic = {
				'paper_id' : 0,
				'paper_title' : '0',
				'paper_publicationYear' : 0,
				'paper_abstract' : '',
				'venue_name' : ''
			}
			if cur_index%10000 == 0:
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
			# if dic['venue_name'] == '':
			# 	continue
		elif line[1] == '!':
			dic['paper_abstract'] = line.replace('#!', '').strip().replace('\'', '\\\'')

		#Add CCF information
		
	else: #END OF FILE
		print "The %d papers are INSERTED FINISHED!" %(cur_index)
		break
f.close()