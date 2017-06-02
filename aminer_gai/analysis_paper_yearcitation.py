#encoding:utf-8
import MySQLdb
import MySQLdb.cursors
import sys
import matplotlib.pyplot as plt

def draw_set_paper_plot(cursor):
	sql_set = "SELECT paper_id FROM paper WHERE paper_publicationYear = '2000' AND paper_nbCitation = '20'"
	try:
		cursor.execute(sql_set)
		res_set = cursor.fetchall()
	except:
		sys.exit("HAHA")

	cnt = 0
	cnt_max = 200
	for row in res_set:
		paper_id = int(row[0])
		analyze_one_paper(paper_id, cursor)
		if cnt >10:
			break
		cnt += 1
	plt.show()

def analyze_one_paper(paper_id, cursor):
	#查找该paper的发表年份
	sql_year = "SELECT paper_publicationYear FROM paper WHERE paper_id='%d'" %paper_id
	#查找引用该paper的文章id
	sql_citation = "SELECT relationship_dst FROM relationship WHERE relationship_src='%d'" %paper_id

	#给出paper_id和发表年份,每年引用的次数
	sql_year_nbcitation = "\
	select paper_publicationyear, count(paper_id)\
	from paper,\
	(\
	select relationship_dst as id\
	from relationship\
	where relationship_src =  '%d'\
	) as temp1\
	where paper_id = temp1.id\
	group by paper_publicationyear\
	" %paper_id

	#给出paper_id和发表年份和作者的H因子
	sql_max_Hindex = "\
	select paper_id, paper_publicationyear, max(author_H_Index)\
	from paper, author, a2p, \
	(\
	select relationship_dst as id\
	from relationship\
	where relationship_src =  '%d'\
	) as temp1\
	where paper_id = temp1.id\
	and paper_id = paper_paper_id\
	and author_id = author_author_id\
	group by paper_id" %paper_id

	year = get_publicationyear(sql_year, cursor)
	print "paper_id: ", paper_id, " paper_publicationYear: ", year

	#画图
	#plt.figure(figsize=(38,28))
	# plt.subplot(1,2,1)
	# plot_onepaper_Hindex(sql_max_Hindex, cursor)

	# plt.subplot(1,2,2)
	plot_onepaper_year_nbCitation(sql_year_nbcitation, cursor)

	#plt.show()

def get_publicationyear(sql_year, cursor):
	#返回当前文章的发表年份
	try:
		cursor.execute(sql_year)
		res = cursor.fetchone()[0]
	except:
		sys.exit("Year: query failed!")
	return res

def plot_onepaper_Hindex(sql_max_Hindex, cursor):
	#画出当前论文在每一年的引用的最大H因子，散点图
	try:
		cursor.execute(sql_max_Hindex)
		res = cursor.fetchall()
	except:
		sys.exit("H Index: query failed!")
	x = []
	y = []
	for row in res:
		paper_id = int(row[0])
		paper_publicationyear = int(row[1])
		paper_max_Hindex = float(row[2])

		x.append(paper_publicationyear)
		y.append(paper_max_Hindex)
	#plt.figure(1)
	plt.scatter(x, y)
	plt.xlim(1999, 2015)
	plt.title("H index")
	plt.xlabel("Year")
	plt.ylabel("Max H index")


def plot_onepaper_year_nbCitation(sql_year_nbcitation, cursor):
	#画出每一年的引用量分布图， 折线图
	try:
		cursor.execute(sql_year_nbcitation)
		res = cursor.fetchall()
	except:
		sys.exit("Year number of citation: query failed!")
	x = []
	y = []
	for row in res:
		paper_publicationyear = int(row[0])
		cnt = int(row[1])

		x.append(paper_publicationyear)
		y.append(cnt)

	#这里计算y的cusum结果
	y  = reduce(lambda x,z: x+[x[-1]+z], y, [0])[1:]
	plt.plot(x, y)
	plt.xlim(1999, 2015)
	plt.title("Year number of citation")
	plt.xlabel("Year")
	plt.ylabel("number of citation")

if __name__ == "__main__":

	#数据库参数
	#sql_ip = "shhr.online" #数据库地址
	#port = 33755 #数据库端口号
	sql_ip = "192.168.1.198"
	port = 3306
	user = "jingfei" #用户名
	passwd = "hanjingfei007"
	db = "aminer_gai"

	db = MySQLdb.connect(host=sql_ip, user='jingfei', port=port, passwd=passwd, db=db, charset='utf8')
	cursor = db.cursor()

	#设置paper_id
	# paper_id_1 = 760805 #nbCitation:3873
	# paper_id_2 = 292088 #nbCitation:71
	# analyze_one_paper(paper_id_1, cursor)
	# analyze_one_paper(paper_id_2, cursor)
	# plt.show()

	draw_set_paper_plot(cursor)
	#plt.show()