#encoding:utf-8
import MySQLdb
import MySQLdb.cursors
import sys
import re
import time
#数据库参数
#sql_ip = "shhr.online" #数据库地址
#port = 33755 #数据库端口号
sql_ip = "localhost"
port = 3306
user = "jingfei" #用户名
passwd = "hanjingfei007"
db = "aminer"

db = MySQLdb.connect(host=sql_ip, user=user, port=port, passwd=passwd, db=db, charset='utf8')
cursor = db.cursor()

#f = open(r'D:/Citation_prediction/AMiner/AMiner-Paper.txt', 'r')
f = open("/home/jingfei/AMiner/AMiner-Paper.txt", "r")

cur_index = 1
citation_list = [] #设置引用列表为空
while True:
    line = f.readline()
    if line:
        if line == '\n':
            #sql_citation = "UPDATE paper SET paper_nbCitation='%d' WHERE paper_id= '%d'" %(length, relationship_dst)
            #try:
#               cursor.execute(sql_citation)
#               db.commit()
#           except:
#               sys.exit("Update failed!")
            
            for relationship_src in citation_list:
                sql1 = "INSERT INTO relationship(relationship_src, relationship_dst)\
						VALUES('%d', '%d')" %(relationship_src, relationship_dst)
                try:
                    cursor.execute(sql1)
                    db.commit()
                except:
					#没有插入成功就不用管， 直接去掉就行
                    print "The realtionship is Failed!"
            
            """
			params = [(i, relationship_dst) for i in citation_list]
			if len(params) == 0:
				continue
			else:
				print "haha"
			sql1 = "INSERT INTO relationship(relationship_src, relationship_dst)\
						VALUES('%d', '%d')"
			try:
				cursor.executemany(sql1, params)
				db.commit()
			except:
				print "%d Batch failed!" %cur_index
				for relationship_src in citation_list:
					sql1_tmp = "INSERT INTO relationship(relationship_src, relationship_dst)\
							VALUES('%d', '%d')" %(relationship_src, relationship_dst)
					try:
						cursor.execute(sql1_tmp)
						db.commit()
					except:
						#没有插入成功就不用管， 直接去掉就行
						pass
					else:
						print "%d Modified successfuly!" %cur_index
            """
			#将引用列表赋为空
            citation_list = []
            
            if cur_index%1000 == 0:
                print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), " The %dth relationship is INSERTED successfuly!" %cur_index
            cur_index += 1
            continue

        elif line[1] == 'i':
            relationship_dst = int(line.replace('#index', '').strip())
        
        elif line[1] == '%':
            citation_list.append(int(line.replace('#%', '').strip())) #int型List

        #Add CCF information
		
    else: #END OF FILE
        print "The %d relationships are INSERTED FINISHED!" %(cur_index)
        break
f.close()
