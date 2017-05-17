#encoding:utf-8
import MySQLdb
import MySQLdb.cursors
import sys
import matplotlib.pyplot as plt

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

def analyze_one_paper(paper_id):
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

	#画图
	plt.figure(1)
	plot_onepaper_Hindex(sql_max_Hindex)
	plt.figure(2)
	plot_onepaper_year_nbCitation(sql_year_nbcitation)


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
	plt.plot(x, y)
	plt.xlim(2000, 2014)
	plt.title("H index")
	plt.xlabel("Year")
	plt.ylabel("Max H index")
	plt.show()

def plot_onepaper_year_nbCitation(sql_year_nbcitation, cursor):
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
	plt.plot(x, y)
	plt.xlim(2000, 2014)
	plt.title("Year number of citation")
	plt.xlabel("Year")
	plt.ylabel("number of citation")
	plt.show()

if __name__ == "__main__":
	#设置paper_id
	paper_id = 760805
	analyze_one_paper(paper_id)