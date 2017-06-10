#encoding:utf-8
import pandas as pd 
from pandas import Series, DataFrame
import numpy as np
import matplotlib.pyplot as plt
import MySQLdb

from analysis_pandas import generate_relationship, get_paper, get_a2p, get_author


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
	#画比例图，归到0,1之间
	# prop.div(prop.sum(1).astype(float), axis = 0).plot(kind='bar', ax=axes[0], stacked=True, ylim=[0,1], colormap='gist_rainbow', legend=False, grid=True, title = 'Total')
	# prop_China.div(prop_China.sum(1).astype(float), axis = 0).plot(kind='bar', ax=axes[1], stacked=True, ylim=[0,1], colormap='gist_rainbow', legend=False, grid=True, title = 'China')
	# prop_Australia.div(prop_Australia.sum(1).astype(float), axis = 0).plot(kind='bar', ax=axes[2], stacked=True, ylim=[0,1], colormap='gist_rainbow', legend=False, grid=True, title = 'Australia')

	#画比例图，不归一
	prop.plot(kind='bar', ax=axes[0], stacked=True, colormap='gist_rainbow', legend=False,  title = 'Total')
	prop_China.plot(kind='bar', ax=axes[1], stacked=True, colormap='gist_rainbow', legend=False, title = 'China')
	prop_Australia.plot(kind='bar', ax=axes[2], stacked=True, colormap='gist_rainbow', legend=False, title = 'Australia')

def draw_paper_distribution(df_paper, paper_publicationYear, Hindex_lowerbound, Hindex_higherbound):
	if paper_publicationYear != -1:
		df_paper = df_paper[df_paper['paper_publicationYear'] == paper_publicationYear]
	if Hindex_lowerbound != -1:
		df_paper = df_paper[df_paper['author_H_Index'] >= Hindex_lowerbound]
	if Hindex_higherbound != -1:
		df_paper = df_paper[df_paper['author_H_Index'] <= Hindex_higherbound]

	grouped = df_paper.groupby(['paper_label']).size().reindex(['A,A*','A,A','A,B','B,A*','B,A','B,B','B,C','C,A*','C,A','C,B','C,C'])
	grouped_China = df_paper[df_paper['country']=='China'].groupby(['paper_label']).size().reindex(['A,A*','A,A','A,B','B,A*','B,A','B,B','B,C','C,A*','C,A','C,B','C,C'])
	grouped_Australia = df_paper[df_paper['country']=='Australia'].groupby(['paper_label']).size().reindex(['A,A*','A,A','A,B','B,A*','B,A','B,B','B,C','C,A*','C,A','C,B','C,C'])

	

	#发表的venue的个数
	cnt_venue = df_paper.drop_duplicates(['paper_label','CCF_id']).groupby(['paper_label']).size().reindex(['A,A*','A,A','A,B','B,A*','B,A','B,B','B,C','C,A*','C,A','C,B','C,C'])
	cnt_venue_China = df_paper[df_paper['country']=='China'].drop_duplicates(['paper_label','CCF_id']).groupby(['paper_label']).size().reindex(['A,A*','A,A','A,B','B,A*','B,A','B,B','B,C','C,A*','C,A','C,B','C,C'])
	cnt_venue_Australia = df_paper[df_paper['country']=='Australia'].drop_duplicates(['paper_label','CCF_id']).groupby(['paper_label']).size().reindex(['A,A*','A,A','A,B','B,A*','B,A','B,B','B,C','C,A*','C,A','C,B','C,C'])

	prop = grouped / cnt_venue
	prop_China = grouped_China / cnt_venue_China
	prop_Australia = grouped_Australia / cnt_venue_Australia

	fig, axes = plt.subplots(1,3)
	prop.plot(kind='bar', ax=axes[0], title='Total')
	prop_China.plot(kind='bar', ax=axes[1], title='China')
	prop_Australia.plot(kind='bar', ax=axes[2], title='Australia')

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

def draw_all_paper(df_paper):
	draw_paper_distribution(df_paper, -1, 35, 60)
	draw_paper_distribution(df_paper, -1, 19, 34)
	draw_paper_distribution(df_paper, -1, 12, 18)
	draw_paper_distribution(df_paper, -1, 7, 11)
	draw_paper_distribution(df_paper, -1, 3, 6)
	draw_paper_distribution(df_paper, -1, 0, 2)


#-----------------------------------------------------------------------------------------------------------------------#
def maxHindex_2_averageCitation(df_paper, paper_publicationYear, color='b'):
	#画出在给定年份发表的文章中，作者最大H因子与平均论文引用量的散点图
	if paper_publicationYear != -1:
		df_paper = df_paper[df_paper['paper_publicationYear']==paper_publicationYear][['paper_nbCitation','author_H_Index']]
	res = df_paper.groupby(['author_H_Index']).mean()
	res['author_H_Index'] = res.index 
	res.plot(kind='scatter', x='author_H_Index', y='paper_nbCitation', xlim=[0,65], color=color)

def firstHindex_2_maxHindex(conn):
	#画出第一作者H因子和最大H因子的关系
	df_a2p = get_a2p(conn)
	df_author = get_author(conn)
	df_merge = pd.merge(df_a2p, df_author, left_on='author_author_id', right_on='author_id', how='inner')
	df_merge = df_merge[['paper_paper_id','a2p_order','author_H_Index']]

	df_first = df_merge.drop_duplicates(['paper_paper_id'])[['paper_paper_id','author_H_Index']]
	df_first.columns=['paper_id', 'first_Hindex']
	#df_last = df_merge.drop_duplicates(['paper_paper_id'], take_last=True)
	res_Hindex = df_merge.groupby(['paper_paper_id']).author_H_Index.max()
	df_max = DataFrame(res_Hindex)
	df_max['paper_id'] = df_max.index
	df_max.columns = ['max_Hindex', 'paper_id']
	df_scatter = pd.merge(df_first, df_max)
	#df_scatter.plot(kind='scatter', x='first_Hindex', y='max_Hindex', xlim=[0, 65], ylim=[0, 65]) #点数太多了
	res = df_scatter.groupby(['first_Hindex']).mean()
	res['first_Hindex'] = res.index
	res.plot(kind = 'scatter', x = 'first_Hindex', y='max_Hindex', xlim=[0, 65], ylim=[0, 65])

def topreasearch_situation(df_paper, df_relationship, paper_publicationYear):
	#在指定年份中引用量前100的研究中，每年高水平H因子作者引用的次数,高水平指的是H因子在35以上的
	df_tmp = df_paper
	if paper_publicationYear != -1:
		df_tmp = df_paper[df_paper['paper_publicationYear'] == paper_publicationYear]
	df_100 = df_tmp.sort_index(by='paper_nbCitation', ascending=False)[:100]
	df1 = pd.merge(df_100, df_relationship, left_on = 'paper_id', right_on='relationship_src')
	#找最大H因子在35以上的
	df1 = df1[(df1['relationship_dst_maxHindex']>=35) & (df1['relationship_dst_maxHindex']<=60)]
	group_series = df1.groupby(['relationship_dst_publicationYear']).size()
	df2 = DataFrame(group_series)
	df2['year'] = df2.index
	if paper_publicationYear == -1:
		df2.columns = ['Total', 'year']
	else:
		df2.columns = [str(paper_publicationYear), 'year']
	return df2

def top_allyear(df_paper, df_relationship):
	df_set = topreasearch_situation(df_paper, df_relationship, -1) #总的情况
	for paper_publicationYear in range(2000,2006):
		df_tmp = topreasearch_situation(df_paper, df_relationship, paper_publicationYear)
		df_set = pd.merge(df_set, df_tmp, how='outer')
	




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

	df_paper, df_relationship = generate_relationship(sql_ip, port, user, passwd, db)
	#draw_ref_distribution(df_relationship)
	#draw_all_ref(df_relationship)