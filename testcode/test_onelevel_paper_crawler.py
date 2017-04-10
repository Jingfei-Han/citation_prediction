import MySQLdb
import MySQLdb.cursors
import requests
from bs4 import BeautifulSoup
import sys
from time import sleep

db = MySQLdb.connect(host='localhost', user='jingfei', passwd='hanjingfei007', db='test_citation', charset='utf8')
cursor = db.cursor()

headers = {
	accept:*/*
	Accept-Encoding:gzip, deflate, sdch, br
	Accept-Language:zh-CN,zh;q=0.8
	Connection:keep-alive
	Cookie:BAIDUID=2EDDCF89DFBFFAA52F74EC6ACE46406C:FG=1; BIDUPSID=2EDDCF89DFBFFAA52F74EC6ACE46406C; PSTM=1491555541; HMACCOUNT=48D2E8AE0BA20ADB; PSINO=1; H_PS_PSSID=1463_21113_20930; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598
	Host:hm.baidu.com
	Referer:https://a.ggkai.men/
	User-Agent:Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36
}

sql_select = "SELECT paper_title FROM test_citation.test_paper"
cursor.execute(sql_select)
res_set = cursor.fetchall()

#url = https://a.ggkai.men/extdomains/scholar.google.com/scholar?hl=en&q=PAPER+NAME&btnG=&as_sdt=1%2C5&as_sdtp=

for row_tuple in res_set:
	paper_title = res_set[0]
		
    urlTitle = "https://a.ggkai.men/extdomains/scholar.google.com/scholar?hl=en&q="  +  str(row1Title.replace("+","%2B").replace("Fast track article: ","").replace("Research Article: ","").replace("Guest editorial: ","").replace("Letters: ","").replace("Editorial: ","").replace("Chaos and Graphics: ","").replace("Review: ","").replace("Education: ","").replace("Computer Graphics in Spain: ","").replace("Graphics for Serious Games: ","").replace("Short Survey: ","").replace("Brief paper: ","").replace("Original Research Paper: ","").replace("Review: ","").replace("Poster abstract: ","").replace("Erratum to: ","").replace("Review: ","").replace("Guest Editorial: ","").replace("Review article: ","").replace("Editorial: ","").replace("Short Communication: ","").replace("Invited paper: ","").replace("Book review: ","").replace("Technical Section: ","").replace("Fast communication: ","").replace("Note: ","").replace("Introduction: ","").replace(":","%3A").replace("'","%27").replace("&","%26").replace("(","%28").replace(")","%29").replace("/","%2F").replace(" ","+")) + '+' + '&btnG=&as_sdt=1%2C5&as_sdtp='
	flag_jump = 0
	while True:
		try:
			response = requests.get(url, headers = headers)
			break
		except:
			print "Connection FAILED! We need have a 5 seconds break."
			flag_jump += 1
			if flag_jump > 5:
				print "This paper can't be connected!"
				break
			sleep(5)

		soup = BeautifulSoup(response.text)
		try:
			
