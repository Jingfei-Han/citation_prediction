#encoding:utf-8
import pandas as pd 
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt
import MySQLdb

from analysis_pandas import generate_relationship


def draw_ref_distribution(df_relationship, dst_publicationYear, Hindex_lowerbound, Hindex_higherbound):

	if dst_publicationYear != -1:
		#目的的发表年份受限，应按发表年份删选
		df_relationship = df_relationship[df_relationship['relationship_dst_publicationYear'] == dst_publicationYear]
	if Hindex_lowerbound != -1:
		df_relationship = df_relationship[df_relationship['relationship_dst_maxHindex'] >= Hindex_lowerbound]

	if Hindex_higherbound != -1:
		df_relationship = df_relationship[df_relationship['relationship_dst_maxHindex'] <= Hindex_higherbound]
	
	grouped = df_relationship.groupby(['relationship_dst_label', 'relationship_src_label'])
	grouped_China = df_relationship[df_relationship['relationship_dst_country'] == 'China'].groupby(['relationship_dst_label', 'relationship_src_label'])
	grouped_Australia = df_relationship[df_relationship['relationship_dst_country'] == 'Australia'].groupby(['relationship_dst_label', 'relationship_src_label'])
		

	#各类venue的个数
	cnt_venue = df_relationship.drop_duplicates(['relationship_src_label', 'relationship_dst_label', 'relationship_src_ccfid']).groupby(['relationship_dst_label', 'relationship_src_label']).size().unstack()
	cnt_venue_China = df_relationship[df_relationship['relationship_dst_country'] == 'China'].drop_duplicates(['relationship_src_label', 'relationship_dst_label', 'relationship_src_ccfid']).groupby(['relationship_dst_label', 'relationship_src_label']).size().unstack()
	cnt_venue_Australia = df_relationship[df_relationship['relationship_dst_country'] == 'Australia'].drop_duplicates(['relationship_src_label', 'relationship_dst_label', 'relationship_src_ccfid']).groupby(['relationship_dst_label', 'relationship_src_label']).size().unstack()

	#各类引用情况
	cnt_ref = grouped.size().unstack()
	cnt_ref_China = grouped_China.size().unstack()
	cnt_ref_Australia = grouped_Australia.size().unstack()

	#计算比值
	prop = cnt_ref / cnt_venue
	prop_China = cnt_ref_China / cnt_venue_China
	prop_Australia = cnt_ref_Australia / cnt_venue_Australia

	# #画图
	# fig, axes = plt.subplots(1,3)
	# #plt.title('Total')
	# prop.plot(kind='bar', ax=axes[0])

	# #plt.title('China')
	# prop_China.plot(kind='bar', ax=axes[1])

	# #plt.title('Australia')
	# prop_Australia.plot(kind='bar', ax=axes[2])

	#画图, 规格化
	fig, axes = plt.subplots(1,3)
	#plt.title('Total')
	prop.div(prop.sum(1).astype(float), axis = 0).plot(kind='bar', ax=axes[0], stacked=True, ylim=[0,1], colormap='gist_rainbow', legend=False, grid=True, title = 'Total')

	#plt.title('China')
	prop_China.div(prop_China.sum(1).astype(float), axis = 0).plot(kind='bar', ax=axes[1], stacked=True, ylim=[0,1], colormap='gist_rainbow', legend=False, grid=True, title = 'China')

	#plt.title('Australia')
	prop_Australia.div(prop_Australia.sum(1).astype(float), axis = 0).plot(kind='bar', ax=axes[2], stacked=True, ylim=[0,1], colormap='gist_rainbow', legend=False, grid=True, title = 'Australia')

def draw_all_ref(df_relationship):
	"""
	我们对于学者水平按照分布进行如下定义：
	1)顶尖学者(前1%)： H因子：[35, 60]
	2)高H因子学者(前10%)：H因子：[19,34]
	3)较高H因子学者（前25%）：H因子：[12, 18]
	4)中等H因子学者(前50%): H因子：[7, 11]
	5)较低H因子学者（前75%）：H因子：[3, 6]
	6)低H因子学者（前100%）：H因子：[0,2]
	"""
	draw_ref_distribution(df_relationship, -1, 35, 60)
	draw_ref_distribution(df_relationship, -1, 19, 34)
	draw_ref_distribution(df_relationship, -1, 12, 18)
	draw_ref_distribution(df_relationship, -1, 7, 11)
	draw_ref_distribution(df_relationship, -1, 3, 6)
	draw_ref_distribution(df_relationship, -1, 0, 2)



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

	#conn = MySQLdb.connect(host=sql_ip, user=user, port=port, passwd=passwd, db=db, charset='utf8')

	df_relationship = generate_relationship(sql_ip, port, user, passwd, db)
	#draw_ref_distribution(df_relationship)
	draw_all_ref(df_relationship)