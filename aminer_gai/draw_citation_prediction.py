#encoding:utf-8
import pandas as pd 
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt
import MySQLdb

from analysis_pandas import generate_relationship

def draw_totaltrend(conn):
	sql_paper = "SELECT paper_id, paper_publicationYear FROM paper"
	df_paper = pd.read_sql(sql_paper, conn)
	grouped = df_paper.groupby(['paper_publicationYear']).size()
	grouped.plot(kind='bar')



if __name__ == '__main__':
	#数据库参数
	#sql_ip = "shhr.online" #数据库地址
	#port = 33755 #数据库端口号
	#sql_ip = "192.168.1.198"
	sql_ip = "127.0.0.1"
	port = 3306
	#user = "jingfei" #用户名
	user = "root"
	passwd = "hanjingfei007"
	db = "aminer_gai"

	conn = MySQLdb.connect(host=sql_ip, user=user, port=port, passwd=passwd, db=db, charset='utf8')

	#df_relationship = generate_relationship(sql_ip, port, user, passwd, db)