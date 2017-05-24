#encoding:utf-8
import pandas as pd 
from pandas import Series, DataFrame
import MySQLdb

#数据库参数
#sql_ip = "shhr.online" #数据库地址
#port = 33755 #数据库端口号
sql_ip = "192.168.1.198"
port = 3306
user = "jingfei" #用户名
passwd = "hanjingfei007"
db = "aminer_gai"

conn = MySQLdb.connect(host=sql_ip, user='jingfei', port=port, passwd=passwd, db=db, charset='utf8')

sql_paper = "SELECT paper_id, paper_title, paper_publicationYear, paper_nbCitation FROM paper"
sql_a2p = "SELECT * FROM a2p"
sql_author = "SELECT * FROM author"

df_paper = pd.read_sql(sql_paper, conn)
df_a2p = pd.read_sql(sql_a2p, conn)
df_author = pd.read_sql(sql_author, conn)

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

df_paper = pd.merge(df_paper, df_country)