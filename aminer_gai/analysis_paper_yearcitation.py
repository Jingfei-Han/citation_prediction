#encoding:utf-8
import MySQLdb
import MySQLdb.cursors
import sys

#数据库参数
#sql_ip = "shhr.online" #数据库地址
#port = 33755 #数据库端口号
sql_ip = "localhost"
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