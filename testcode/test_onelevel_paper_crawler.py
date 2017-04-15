import MySQLdb
import MySQLdb.cursors
import requests
from bs4 import BeautifulSoup
import sys
from time import sleep
import re
from user_agent import generate_user_agent

db = MySQLdb.connect(host='localhost', user='root', passwd='hanjingfei007', db='test_citation', charset='utf8')
cursor = db.cursor()

my_user_agent = generate_user_agent()
headers = {
	'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, sdch, br',
	'Accept-Language':'zh-CN,en-US;q=0.8,zh;q=0.5,en;q=0.3',
	'Connection':'keep-alive',
	'Host':'scholar.google.com',
	'Referer':'https://www.google.com',
	'User-Agent': my_user_agent,
	'Cache-Control':'max-age=0',
}

sql_select = "SELECT paper_id, paper_title FROM test_citation.test_paper"
cursor.execute(sql_select)
res_set = cursor.fetchall()

#url = https://a.ggkai.men/extdomains/scholar.google.com/scholar?hl=en&q=PAPER+NAME&btnG=&as_sdt=1%2C5&as_sdtp=
index = 1
for row_tuple in res_set:
	paper_id = int(row_tuple[0])
	paper_title = row_tuple[1]
		
	urlTitle = "https://scholar.google.com/scholar?hl=en&q="  +  str(paper_title.replace("+","%2B").replace("Fast track article: ","").replace("Research Article: ","").replace("Guest editorial: ","").replace("Letters: ","").replace("Editorial: ","").replace("Chaos and Graphics: ","").replace("Review: ","").replace("Education: ","").replace("Computer Graphics in Spain: ","").replace("Graphics for Serious Games: ","").replace("Short Survey: ","").replace("Brief paper: ","").replace("Original Research Paper: ","").replace("Review: ","").replace("Poster abstract: ","").replace("Erratum to: ","").replace("Review: ","").replace("Guest Editorial: ","").replace("Review article: ","").replace("Editorial: ","").replace("Short Communication: ","").replace("Invited paper: ","").replace("Book review: ","").replace("Technical Section: ","").replace("Fast communication: ","").replace("Note: ","").replace("Introduction: ","").replace(":","%3A").replace("'","%27").replace("&","%26").replace("(","%28").replace(")","%29").replace("/","%2F").replace(" ","+")) + '+' + '&btnG=&as_sdt=1%2C5&as_sdtp='
	flag_jump = 0
	flag_scholar = 1 #Record if we can get paper in google scholar
	flag_connection = 1 #Record if we can request html successfully
	while True:
		try:
			response = requests.get(urlTitle, headers = headers)
			sleep(2) #break 2 seconds
			#Success, change the headers
			my_user_agent = generate_user_agent()
			headers['User-Agent'] = my_user_agent
			print "Connection sucessed!"
			break
		except:
			print "Connection FAILED! We need have a 5 seconds break."
			flag_jump += 1
			if flag_jump > 5:
				print "This paper can't be connected!"
				flag_connection = 0
				break
			sleep(5)
	
	if flag_connection == 0:
		print "Continue the next paper due to error."
		continue
	soup = BeautifulSoup(response.text)
	try:
		soup.find("a", text = re.compile("Try your query on the entire web")).get_text()
		print "Not found in goole scholar."
		flag_scholar = 0
		break
	except:
		try:
			linkinfo = soup.find("div", {"class":"gs_a"}).get_text()
			print "Found in google scholar."
		except:
			print "The paper " + paper_title +" need be checked by hand!"
			continue
	if flag_scholar==0:
		print "Continue the next paper due to error."
		continue
	try:
		link = soup.find("a", text=re.compile("Cited")).get_text()
		paper_nbCitation = int(link.strip('Cited by'))
	except:
		paper_nbCitation = 0
	try:
		temp = soup.find("span", attrs={"class":"gs_ctg2"}).get_text()
		paper_isseen = 1
	except:
		paper_isseen = 0
	
	sql_update = "UPDATE test_citation.test_paper SET paper_nbCitation = '%d'\
				, paper_isseen= '%d' WHERE paper_id='%d'"\
				%(paper_nbCitation, paper_isseen, paper_id)
	try:
		cursor.execute(sql_update)
		db.commit()
	except:
		print "Update FAILED!"

	print "----------------------%d SUSCESSED!  ----------------------" %index
	index += 1


