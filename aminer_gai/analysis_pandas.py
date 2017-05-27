#encoding:utf-8
import pandas as pd 
from pandas import Series, DataFrame
import MySQLdb


def generate_relationship(sql_ip, port, user, passwd, db):
	#根据数据库信息， 返回df_relationship，其中包含源和目的的发表年份、标签、最大H因子、第一作者所属国家

	conn = MySQLdb.connect(host=sql_ip, user=user, port=port, passwd=passwd, db=db, charset='utf8')

	sql_paper = "SELECT paper_id, paper_title, paper_publicationYear, paper_nbCitation, paper_label FROM paper"
	sql_a2p = "SELECT * FROM a2p"
	sql_author = "SELECT * FROM author"
	sql_relationship = "SELECT relationship_src, relationship_dst FROM relationship"

	df_paper = pd.read_sql(sql_paper, conn)
	df_a2p = pd.read_sql(sql_a2p, conn)
	df_author = pd.read_sql(sql_author, conn)
	df_relationship = pd.read_sql(sql_relationship, conn)

	#合并, 内连接
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
	df_paper = pd.merge(df_paper, df_Hindex, left_on='paper_id', right_on='paper_id') #在paper表上加上Max H因子

	#找到每篇论文第一作者的国籍，写入df_paper中
	df_sub = df[df['a2p_order']==1]
	df_sub2 = df_sub[['paper_id', 'author_affiliation_name']]
	df_sub_China = df_sub2[df_sub2['author_affiliation_name'].str.contains('China')].copy()
	df_sub_Australia = df_sub2[df_sub2['author_affiliation_name'].str.contains('Australia')].copy()

	df_sub_China['country'] = 'China'
	df_sub_Australia['country'] = 'Australia'
	df_country = pd.concat([df_sub_China, df_sub_Australia])

	#df_paper_inter = pd.merge(df_paper, df_country) #只包括中国和澳大利亚作者
	df_paper_outer = pd.merge(df_paper, df_country, how = 'outer')#包括所有国家作者，但是大部分国籍为NAN(除中澳外的其他国家)

	df_relationship = pd.merge(df_relationship, df_paper_outer[['paper_id','paper_publicationYear','paper_label','author_H_Index', 'country']], left_on='relationship_src', right_on='paper_id')
	del df_relationship['paper_id']
	#换列名
	df_relationship.columns = ['relationship_src', 'relationship_dst', 'relationship_src_publicationYear', 'relationship_src_label', 'relationship_src_maxHindex', 'relationship_src_country']

	df_relationship = pd.merge(df_relationship, df_paper_outer[['paper_id','paper_publicationYear','paper_label','author_H_Index', 'country']], left_on='relationship_dst', right_on='paper_id')
	del df_relationship['paper_id']
	df_relationship.columns = ['relationship_src', 'relationship_dst', 'relationship_src_publicationYear', 'relationship_src_label', 'relationship_src_maxHindex', 'relationship_src_country', 'relationship_dst_publicationYear', 'relationship_dst_label', 'relationship_dst_maxHindex', 'relationship_dst_country']
	#此时的df_relationship包含源和目的的发表年份、标签、最大H因子、第一作者所属国家

	return df_relationship

	#***************************************************以下分析均基于df_relationship*********************************************************

def get_table(df_relationship, src_publicationYear, dst_publicationYear, src_country, dst_country):
	"""
	params:
	src_publicationYear : 源论文集的发表年份 (-1表示不限制)
	dst_publicationYear : 引用论文的发表截止年份（从源论文发表的年份直到目的年份） (-1表示不限制)
	src_country : 源论文集的国家 （'NULL'表示不限制）
	dst_country : 目的论文集的国家 （'NULL'表示不限制）
	"""
	#只考虑CCF和CORE交叉部分的情况目前，因此先处理df_relationship
	df_tmp = df_relationship[(df_relationship['relationship_src_label'].notnull()) & (df_relationship['relationship_dst_label'].notnull())]
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

# if __name__ == '__main__':
# 	#数据库参数
# 	#sql_ip = "shhr.online" #数据库地址
# 	#port = 33755 #数据库端口号
# 	#sql_ip = "192.168.1.198"
# 	sql_ip = "127.0.0.1"
# 	port = 3306
# 	#user = "jingfei" #用户名
# 	user = "root"
# 	passwd = "hanjingfei007"
# 	db = "aminer_gai"

# 	df_relationship = generate_relationship(sql_ip, port, user, passwd, db)
# 	# 要求参数
# 	# src_publicationYear : 源论文集的发表年份 (-1表示不限制)
# 	# dst_publicationYear : 引用论文的发表截止年份（从源论文发表的年份直到目的年份） (-1表示不限制)
# 	# src_country : 源论文集的国家 （'NULL'表示不限制）
# 	# dst_country : 目的论文集的国家 （'NULL'表示不限制）
#	dic = {'src_publicationYear' : 2000, 'dst_publicationYear' : -1, 'src_country' : 'NULL', 'dst_country' : 'Australia'}
# 	src_publicationYear = 2000
# 	dst_publicationYear = -1
# 	src_country = 'NULL'
# 	dst_country = 'NULL'
# 	result = get_table(df_relationship, dic['src_publicationYear'], dic['dst_publicationYear'], dic['src_country'], dic['dst_country'])
# 	print result