import MySQLdb
import MySQLdb.cursors
import requests
from bs4 import BeautifulSoup
import sys
from time import sleep
import re
from user_agent import generate_user_agent
import random

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

proxies_table = [] #proxies列表
fp = open("proxies.txt")
lines = fp.readlines()
len_proxies = len(lines)

for line in lines:
	proxies_table.append('https://'+line.replace('\n'," ").strip())

url = "https://b.ggkai.men/extdomains/scholar.google.com/"
def getProxies(len_proxies):
	x = random.randint(0, len_proxies-1)
	res = {"https":proxies_table[x]}
	return res

def Parser_google(urlTitle, paper_title, headers, proxies):
	flag_jump = 0
	while True:
		try:
			response = requests.get(urlTitle, headers = headers, proxies = proxies)
			sleep(2) #break 2 seconds			
			print "Connection sucessed!"
			break
		except:
			print "Connection FAILED! We need have a 5 seconds break."
			proxies = getProxies(len_proxies)
			flag_jump += 1
			if flag_jump > 5:
				print "This paper can't be connected!"
				return 
			sleep(5)

	print "The status code: %d" %response.status_code
	soup = BeautifulSoup(response.text)
	try:
		soup.find("a", text = re.compile("Try your query on the entire web")).get_text()
		print "Not found in goole scholar."
		return 
	except:
		try:
			soup.find("div", {"class":"gs_a"}).get_text()
			print "Found in google scholar."
		except:
			print "The paper " + paper_title +" need be checked by hand!"
			return 
	try:
		link = soup.find("a", text=re.compile("Cited")).get_text()
		paper_nbCitation = int(link.strip('Cited by'))
	except:
		paper_nbCitation = 0
	try:
		soup.find("span", attrs={"class":"gs_ctg2"}).get_text()
		paper_isseen = 1
	except:
		paper_isseen = 0
	return paper_nbCitation, paper_isseen

index = 1
for row_tuple in res_set:
	paper_id = int(row_tuple[0])
	paper_title = row_tuple[1]
		
	urlTitle = url + "scholar?hl=en&q="  +  str(paper_title.replace("+","%2B").replace("Fast track article: ","").replace("Research Article: ","").replace("Guest editorial: ","").replace("Letters: ","").replace("Editorial: ","").replace("Chaos and Graphics: ","").replace("Review: ","").replace("Education: ","").replace("Computer Graphics in Spain: ","").replace("Graphics for Serious Games: ","").replace("Short Survey: ","").replace("Brief paper: ","").replace("Original Research Paper: ","").replace("Review: ","").replace("Poster abstract: ","").replace("Erratum to: ","").replace("Review: ","").replace("Guest Editorial: ","").replace("Review article: ","").replace("Editorial: ","").replace("Short Communication: ","").replace("Invited paper: ","").replace("Book review: ","").replace("Technical Section: ","").replace("Fast communication: ","").replace("Note: ","").replace("Introduction: ","").replace(":","%3A").replace("'","%27").replace("&","%26").replace("(","%28").replace(")","%29").replace("/","%2F").replace(" ","+")) + '+' + '&btnG=&as_sdt=1%2C5&as_sdtp='
	
	proxies = getProxies(len_proxies)
	my_user_agent = generate_user_agent()
	headers['User-Agent'] = my_user_agent
	paper_nbCitation, paper_isseen = Parser_google(urlTitle, paper_title, headers, proxies)
	
	try:
		sql_update = "UPDATE test_citation.test_paper SET paper_nbCitation = '%d'\
				, paper_isseen= '%d' WHERE paper_id='%d'"\
				%(paper_nbCitation, paper_isseen, paper_id)
		cursor.execute(sql_update)
		db.commit()
	except:
		print "Update FAILED!"

	print "----------------------%d SUSCESSED!  ----------------------" %index
	index += 1
