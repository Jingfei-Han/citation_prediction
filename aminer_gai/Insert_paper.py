#encoding:utf-8
import MySQLdb
import MySQLdb.cursors
import sys
import re
#数据库参数
sql_ip = "shhr.online" #数据库地址
port = 33755 #数据库端口号
user = "jingfei" #用户名
passwd = "hanjingfei007"
db = "aminer_gai"

db = MySQLdb.connect(host=sql_ip, user='jingfei', port=port, passwd=passwd, db=db, charset='utf8')
cursor = db.cursor()

f = open(r'D:/Citation_prediction/AMiner/AMiner-Paper.txt', 'r')

sql_select = "SELECT COUNT(*) FROM venue WHERE venue_id < 999999999"
try:
	cursor.execute(sql_select)
	cnt_aff = cursor.fetchone()[0]
	cnt_aff += 1 #记录下面一个该开始的位置
except:
	sys.exit("ERROR: SELECT the TABLE venue failed!")

dic = {
	'paper_id' : 0,
	'paper_title' : '0',
	'paper_publicationYear' : 0,
	'paper_nbCitation' : 0,
	'paper_abstract' : '',
	'venue_name' : '',
	'paper_citation_id' : '',
}
cur_index = 1
citation_list = [] #设置引用列表为空
while True:
	
	
	line = f.readline()
	if line:
		if line == '\n': #Insert data into the table
			#if dic['paper_publicationYear'] < 2010: #Consider papers whose publication year greater or equal than 2010
			#	continue

			if dic['paper_title'] == dic['venue_name']: #ERROR DATA, delete it.
				#不考虑paper名和venue名相同的文章
				continue

			#记录引用量
			dic['paper_nbCitation'] = len(citation_list)
			dic['paper_citation_id'] = ",".join(citation_list)#引用id之间用逗号连接

			#将引用列表赋为空
			citation_list = []

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
					print ("ERROR: INSERT INTO the TABLE venue failed!")

			sql2 = "INSERT INTO paper(paper_id, paper_title, paper_publicationYear, paper_nbCitation, paper_abstract, paper_citation_id, venue_venue_id) \
					VALUES('%d', '%s', '%d', '%d', '%s', '%s', '%d')" %(dic['paper_id'], dic['paper_title'], dic['paper_publicationYear'], dic['paper_nbCitation'], dic['paper_abstract'], dic['paper_citation_id'], int(id))
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
				'ccf_CCF_id' : 9999,
				'core_CORE_id' : 9999,
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
			#如果发表年份不存在，这里默认设置为0
			if str=='':
				dic['paper_publicationYear'] = 0;
			else:
				convert = re.search(r'(\d+)', str).group()
				dic['paper_publicationYear'] = int(convert)
		elif line[1] == 'c':
			dic['venue_name'] = line.replace('#c', '').strip().replace('\'', '\\\'')
			if dic['venue_name'] == '':
				#不考虑venue_name 为空的
				continue
		elif line[1] == '!':
			dic['paper_abstract'] = line.replace('#!', '').strip().replace('\'', '\\\'')
		elif line[1] == '%':
			citation_list.append(line.replace('#%', '').strip()) #字符串类型list

		#Add CCF information
		
	else: #END OF FILE
		print "The %d papers are INSERTED FINISHED!" %(cur_index)
		break
f.close()