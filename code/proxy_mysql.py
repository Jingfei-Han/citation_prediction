#encoding:utf-8
import MySQLdb
import MySQLdb.cursors
import requests
import sys
from time import sleep

db = MySQLdb.connect(host='192.168.1.198', user='jingfei', passwd='hanjingfei007', db='citation', charset='utf8')
cursor = db.cursor()

# fp = open("proxies.txt", "r")
# lines = fp.readlines()
# #将https代理写入数据库
# proxies_type = "https"
# proxies_status = 3 #来自网上试用代理
# index = 1
# for line in lines:
# 	if line == "\n":
# 		#EOF
# 		print "Read fininsh!"
# 		break
# 	line = line.replace("\n", "").strip()
# 	proxies_link = proxies_type + "://" + line
# 	sql_select = "SELECT COUNT(*) FROM proxies WHERE proxies_link='%s'" %proxies_link
# 	sql_insert = "INSERT INTO proxies(proxies_type, proxies_link, proxies_status) \
# 					VALUES('%s', '%s', '%d')" %(proxies_type, proxies_link, proxies_status)
# 	cursor.execute(sql_select)
# 	cnt = cursor.fetchone()[0]
# 	if cnt == 0:
# 		#不存在该proxies,应写入数据库
# 		try:
# 			cursor.execute(sql_insert)
# 			print "------------------------------%d success--------------------------"%index
# 			index += 1
# 			db.commit()
# 		except:
# 			print "Insert failed!"

#直接利用API
reload(sys)
sys.setdefaultencoding("utf-8")

index = 1
headers = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, sdch',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
	'Cache-Control':'max-age=0',
	'Connection':'keep-alive',
	'Cookie':'JSESSIONID=6B1F5C8E32BF1F7A805E8015C5A6CB95; UM_distinctid=15bdce0a8406d-01be6d01a603b3-4e47052e-100200-15bdce0a84176b; source=BD; medium=cpc; term=%25E8%25AE%25AF%25E4%25BB%25A3%25E7%2590%2586; CNZZDATA1260873131=1791296618-1494055822-null%7C1494055822; _ga=GA1.2.729395311.1494059363; _gid=GA1.2.1025405930.1494060273; Hm_lvt_c1c9e8373d7f000ad58265f0b17f1cff=1494059363; Hm_lpvt_c1c9e8373d7f000ad58265f0b17f1cff=1494060273',
	'Host':'www.xdaili.cn',
	'Referer':'http://www.xdaili.cn/geturlcuts.html',
	'Upgrade-Insecure-Requests':'1',
	'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
}
url = "http://www.xdaili.cn/ipagent//newExclusive/getIp?spiderId=1bd6cbfc87ea4f989b6871e9702bbe0f&orderno=MF2017562714d7PgbZ&returnType=1&count=1"
while True:
	while True:
		try:
			res = requests.get(url, headers = headers)
			line = str(res.text)
			line = line.replace("\n", "").strip()
			assert "ERRORCODE" not in line
			break
		except:
			print "Too frequency!"
			sleep(3)

	print "Proxies is: ", line
	proxies_type = "https"
	proxies_status = 3 #来自网上试用代理
	proxies_link = proxies_type + "://" + line
	sql_select = "SELECT COUNT(*) FROM proxies WHERE proxies_link='%s'" %proxies_link
	sql_insert = "INSERT INTO proxies(proxies_type, proxies_link, proxies_status) \
					VALUES('%s', '%s', '%d')" %(proxies_type, proxies_link, proxies_status)
	cursor.execute(sql_select)
	cnt = cursor.fetchone()[0]
	if cnt == 0:
		#不存在该proxies,应写入数据库
		try:
			cursor.execute(sql_insert)
			print "------------------------------%d success--------------------------"%index
			index += 1
			db.commit()
		except:
			print "Insert failed!"
	sleep(10)

