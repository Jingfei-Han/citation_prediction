#encoding:utf-8
import pandas as pd 
from pandas import Series, DataFrame
import MySQLdb
import numpy as np


def generate_relationship(sql_ip, port, user, passwd, db):
	#根据数据库信息， 返回df_relationship，其中包含源和目的的发表年份、标签、最大H因子、第一作者所属国家

	conn = MySQLdb.connect(host=sql_ip, user=user, port=port, passwd=passwd, db=db, charset='utf8')

	sql_paper = "SELECT paper_id, paper_title, paper_publicationYear, paper_nbCitation, paper_label, venue_venue_id FROM paper"
	sql_a2p = "SELECT * FROM a2p"
	sql_author = "SELECT * FROM author"
	sql_relationship = "SELECT relationship_src, relationship_dst FROM relationship"

	sql_venue = "SELECT * FROM venue"
	sql_dblp2ccf = "SELECT * FROM dblp2ccf"
	sql_ccf = "SELECT * FROM ccf"

	df_paper = pd.read_sql(sql_paper, conn)
	df_a2p = pd.read_sql(sql_a2p, conn)
	df_author = pd.read_sql(sql_author, conn)
	df_relationship = pd.read_sql(sql_relationship, conn)

	df_venue = pd.read_sql(sql_venue, conn)
	df_dblp2ccf = pd.read_sql(sql_dblp2ccf, conn)
	df_ccf = pd.read_sql(sql_ccf, conn)
	#*********************************************此部分得到论文的最大H因子********************************************************
	#合并, 内连接为了得到每个论文作者的最大H因子
	df = pd.merge(df_paper, pd.merge(df_author, df_a2p, left_on='author_id', right_on='author_author_id'), left_on='paper_id', right_on='paper_paper_id')

	#查看df的列名
	#df.columns

	#按paper_id分组
	group_paper = df.groupby(df['paper_id'])
	#得到paper的最大H因子
	res_Hindex = group_paper.author_H_Index.max()
	#计数，得到最大H因子的个数
	#res = res_Hindex.value_counts()

	#找到作者最大H因子，写到df_paper中
	df_Hindex = DataFrame(res_Hindex)
	df_Hindex['paper_id'] = df_Hindex.index

	#*************************************此部分得到论文的J/C、computercategory***************************************************
	df2_part1 = pd.merge(df_paper, df_venue, left_on='venue_venue_id', right_on='venue_id')
	df2_part2 = pd.merge(df_ccf, df_dblp2ccf, left_on='CCF_id', right_on='ccf_CCF_id')
	df2_part2 = df2_part2[df2_part2['dblp_dblp_id']<999999999]
	df2 = pd.merge(df2_part1, df2_part2, left_on='dblp_dblp_id', right_on='dblp_dblp_id')
	df2 = df2[['paper_id', 'CCF_type', 'computercategory_computerCategory_id']]
	df2 = df2.drop_duplicates(['paper_id']) #去掉重复的paper_id数据

	df_paper = pd.merge(df_paper, df_Hindex, left_on='paper_id', right_on='paper_id', how='outer') #在paper表上加上Max H因子
	df_paper = pd.merge(df_paper, df2, left_on='paper_id', right_on='paper_id', how='outer') #在paper表上加上J/C, computer类别

	#找到每篇论文第一作者的国籍，写入df_paper中
	df_sub = df[df['a2p_order']==1]
	df_sub2 = df_sub[['paper_id', 'author_affiliation_name']]
	df_sub_China = df_sub2[df_sub2['author_affiliation_name'].str.contains('China')].copy()
	df_sub_Australia = df_sub2[df_sub2['author_affiliation_name'].str.contains('Australia')].copy()

	df_sub_China['country'] = 'China'
	df_sub_Australia['country'] = 'Australia'
	df_country = pd.concat([df_sub_China, df_sub_Australia])
	df_country = df_country.drop_duplicates(['paper_id']) #去除2446篇第一作者来自两个国家的情况，这里将澳大利亚的情况去掉

	#df_paper_inter = pd.merge(df_paper, df_country) #只包括中国和澳大利亚作者
	df_paper_outer = pd.merge(df_paper, df_country, how = 'outer')#包括所有国家作者，但是大部分国籍为NAN(除中澳外的其他国家)

	df_relationship = pd.merge(df_relationship, df_paper_outer[['paper_id','paper_publicationYear','paper_label','author_H_Index', 'CCF_type', 'computercategory_computerCategory_id', 'country']], left_on='relationship_src', right_on='paper_id')
	del df_relationship['paper_id']
	#换列名
	df_relationship.columns = ['relationship_src', 'relationship_dst', 'relationship_src_publicationYear', 'relationship_src_label', 'relationship_src_maxHindex', 'relationship_src_type', 'relationship_src_computerCategory', 'relationship_src_country']

	df_relationship = pd.merge(df_relationship, df_paper_outer[['paper_id','paper_publicationYear','paper_label','author_H_Index', 'CCF_type', 'computercategory_computerCategory_id', 'country']], left_on='relationship_dst', right_on='paper_id')
	del df_relationship['paper_id']
	df_relationship.columns = ['relationship_src', 'relationship_dst', 'relationship_src_publicationYear', 'relationship_src_label', 'relationship_src_maxHindex', 'relationship_src_type', 'relationship_src_computerCategory', 'relationship_src_country', 'relationship_dst_publicationYear', 'relationship_dst_label', 'relationship_dst_maxHindex', 'relationship_dst_type', 'relationship_dst_computerCategory', 'relationship_dst_country']
	#此时的df_relationship包含源和目的的发表年份、标签、最大H因子、type、 CCF类别、第一作者所属国家

	return df_relationship

	#***************************************************以下分析均基于df_relationship*********************************************************

def get_overlap(df_relationship):
	df_tmp = df_relationship[(df_relationship['relationship_src_label'].notnull()) & (df_relationship['relationship_dst_label'].notnull())]
	return df_tmp

def get_table(df_relationship, src_publicationYear, dst_publicationYear, src_country, dst_country):
	"""
	params:
	src_publicationYear : 源论文集的发表年份 (-1表示不限制)
	dst_publicationYear : 引用论文的发表截止年份（从源论文发表的年份直到目的年份） (-1表示不限制)
	src_country : 源论文集的国家 （'NULL'表示不限制）
	dst_country : 目的论文集的国家 （'NULL'表示不限制）
	"""
	#只考虑CCF和CORE交叉部分的情况目前，因此先处理df_relationship
	df_tmp = get_overlap(df_relationship)
	if src_publicationYear != -1:
		#源的发表年份受限，应按发表年份删选
		df_tmp = df_tmp[df_tmp['relationship_src_publicationYear'] == src_publicationYear]
	if dst_publicationYear != -1:
		#目的截止年份受限
		df_tmp = df_tmp[df_tmp['relationship_dst_publicationYear'] <= dst_publicationYear]
	if src_country != 'NULL':
		df_tmp = df_tmp[df_tmp['relationship_src_country'] == src_country]
	if dst_country != 'NULL':
		df_tmp = df_tmp[df_tmp['relationship_src_country'] == dst_country]

	df_tmp = df_tmp[['relationship_src', 'relationship_src_label', 'relationship_dst', 'relationship_dst_label']] #只要标签个数统计

	#获取发表年份为2000年，且源和目的的label都存在的所有relationship，不考虑国家
	#df_2000_withLabel_withoutCountry = df_relationship[(df_relationship['relationship_src_publicationYear'] == 2000) & (df_relationship['relationship_src_label'].notnull()) & (df_relationship['relationship_dst_label'].notnull())]
	#df_2000_withLabel_withoutCountry = df_2000_withLabel_withoutCountry[['relationship_src', 'relationship_src_label', 'relationship_dst', 'relationship_dst_label']]

	#按源和目的的label聚合
	grouped = df_tmp.groupby(['relationship_src_label', 'relationship_dst_label'])
	result = grouped.count().unstack().fillna(0) #得到表格结果，列表示源的标签，行表示目的的标签，值表示引用量
	return result

def get_table2(df_relationship):
	#得到2000年、源是computer类别是8（人工智能）、源和目的都是Conference的字表视图
	df_relationship = get_overlap(df_relationship)
	#df_relationship[ (df_relationship['relationship_src_publicationYear'] == 2000) & (df_relationship['relationship_src_type'] == 'conference') & (df_relationship['relationship_dst_type'] == 'conference') & (df_relationship['relationship_src_computerCategory'] == 8)]
	df_relationship_cur = df_relationship[df_relationship['relationship_src_publicationYear'] == 2000]
	df_relationship_cur = df_relationship_cur[df_relationship_cur['relationship_src_label'] == 'A,A*']
	df_relationship_cur = df_relationship_cur[df_relationship_cur['relationship_src_type'] == 'conference']
	df_relationship_cur = df_relationship_cur[df_relationship_cur['relationship_dst_type'] == 'conference']
	df_relationship_cur = df_relationship_cur[df_relationship_cur['relationship_src_computerCategory'] == 8]

def Compute_geometric_mean(lis):
	#计算列表list的几何均值
	n = len(lis)
	x = np.asarray(lis)
	res = np.exp(1.0/n) * (np.log(x+1).sum())#平滑
	return res

def Compute_arithmetic_mean(lis):
	#计算列表list的几何均值
	n = len(lis)
	#x = np.asarray(lis)
	res = 1.0/n * sum(lis)
	return res

def get_paperset_GM(df_relationship, src_publicationYear, src_label, src_computerCategory, src_type, dst_country):
	#只考虑CCF和CORE交叉部分的情况目前，因此先处理df_relationship
	#df_tmp = get_overlap(df_relationship)
	df_tmp = df_relationship
	if src_publicationYear != -1:
		#源的发表年份受限，应按发表年份删选
		df_tmp = df_tmp[df_tmp['relationship_src_publicationYear'] == src_publicationYear]
	if src_label != -1:
		#目的截止年份受限
		df_tmp = df_tmp[df_tmp['relationship_src_label'] == src_label]
	if src_computerCategory != -1:
		df_tmp = df_tmp[df_tmp['relationship_src_computerCategory'] == src_computerCategory]
	if src_type != 'NULL':
		df_tmp = df_tmp[df_tmp['relationship_src_type'] == src_type]
	if dst_country != 'NULL':
		df_tmp = df_tmp[df_tmp['relationship_dst_country'] == dst_country]
	

	res = df_tmp.groupby(['relationship_src'])['relationship_dst'].count()
	lis = list(res)
	if len(lis) == 0:
		return 0
	#gm = Compute_geometric_mean(lis)
	gm = Compute_arithmetic_mean(lis)
	return gm




if __name__ == '__main__':
	#数据库参数
	#sql_ip = "shhr.online" #数据库地址
	#port = 33755 #数据库端口号
	sql_ip = "192.168.1.198"
	#sql_ip = "127.0.0.1"
	port = 3306
	user = "jingfei" #用户名
	#user = "root"
	passwd = "hanjingfei007"
	db = "aminer_gai"

	df_relationship = generate_relationship(sql_ip, port, user, passwd, db)
# 	# 要求参数
# 	# src_publicationYear : 源论文集的发表年份 (-1表示不限制)
# 	# dst_publicationYear : 引用论文的发表截止年份（从源论文发表的年份直到目的年份） (-1表示不限制)
# 	# src_country : 源论文集的国家 （'NULL'表示不限制）
# 	# dst_country : 目的论文集的国家 （'NULL'表示不限制）
#	dic = {'src_publicationYear' : 2000, 'dst_publicationYear' : -1, 'src_country' : 'NULL', 'dst_country' : 'NULL'}
# 	src_publicationYear = 2000
# 	dst_publicationYear = -1
# 	src_country = 'NULL'
# 	dst_country = 'NULL'
# 	result = get_table(df_relationship, dic['src_publicationYear'], dic['dst_publicationYear'], dic['src_country'], dic['dst_country'])
# 	print result
	
	label = ['A,A*', 'A,A', 'A,B', 'A,C', 'B,A*', 'B,A', 'B,B', 'B,C', 'C,A*', 'C,A', 'C,B', 'C,C',]
	# for i in label:
	# 	res = get_paperset_GM(df_relationship, 2000, i, -1, 'NULL', 'China')
	# 	print i, ' : ', res
	for i in label:
		res = get_paperset_GM(df_relationship, 2000, i, -1, 'NULL', 'NULL')
		print res