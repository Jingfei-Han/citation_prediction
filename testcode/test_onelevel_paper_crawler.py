#encoding:utf-8
import MySQLdb
import MySQLdb.cursors
import requests
from bs4 import BeautifulSoup
from time import sleep
import re
from user_agent import generate_user_agent
import random
import subprocess
import shlex
import sys

db = MySQLdb.connect(host='localhost', user='root', passwd='hanjingfei007', db='test_citation', charset='utf8')
cursor = db.cursor()

my_user_agent = generate_user_agent()
"""
#goolge scholar headers
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
"""
#镜像headers
headers = {
	'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, sdch, br',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
	'Connection':'keep-alive',
	'Host':'b.ggkai.men',
	'Referer':'https://b.ggkai.men/extdomains/scholar.google.com/schhp?hl=en&num=20&as_sdt=0',
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
	'Cache-Control':'max-age=0',
	'Cookie':'NID=101=ZPX_tebnsmlbtsniyMAFKDXfTNmNmI9p9jF6HVl5luswkM7qLeWnkHFpPmdL0beGn0lCaJjGgevBsBOj2qnLDPHi2NCujP3CRk-8rUIfsHXc0ycB_ToZS5gAO5buBDzJ; GSP=LM=1492323405:S=6WH6FgIC17h7zhM5; Hm_lvt_df11358c4b6a37507eca01dfe919e040=1492323406,1492341461; Hm_lpvt_df11358c4b6a37507eca01dfe919e040=1492341461',
}

index = 0
sql_cnt = "SELECT COUNT(*) FROM test_citation.test_paper WHERE paper_nbCitation !=-1"
cursor.execute(sql_cnt)
index = cursor.fetchone()[0]
index += 1 #当前条数

sql_select = "SELECT paper_id, paper_title FROM test_citation.test_paper WHERE paper_nbCitation =-1"
cursor.execute(sql_select)
res_set = cursor.fetchall()

proxies_table = [] #proxies列表
fp = open("proxies.txt")
lines = fp.readlines()
#len_proxies = len(lines)

def PING(ip):
	#cmd = "ping -c 1 "+ ip #linux
	cmd = "ping -n 1 " + ip #windows
	args = shlex.split(cmd)
	try:
		subprocess.check_call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return True
	except:
		return False

for line in lines:
	cur_proxy = line.replace('\n'," ").strip()
	#ip_proxy = cur_proxy.split(":")[0]
	#只有当可以ping通时才考虑加入代理池
	#if PING(ip_proxy):
	proxies_table.append('https://' + cur_proxy)

len_proxies = len(proxies_table)

url = "https://b.ggkai.men/extdomains/scholar.google.com/"
def getProxies(len_proxies):
	#在返回之前保证该代理可以ping通
	while True:
		x = random.randint(0, len_proxies-1)
		ip = proxies_table[x].split(":")[1]
		ip = ip.replace("//", "").strip()
		if PING(ip):
			break
	res = {"https":proxies_table[x]}
	return res

def Parser_google(urlTitle, paper_title, headers, proxies=None):
	flag_jump = 0
	paper_nbCitation = -1
	paper_isseen = -1
	paper_citationURL = ""
	paper_pdfURL = ""
	while True:
		try:
			response = requests.get(urlTitle, headers = headers)#, proxies = proxies
			sleep(2) #break 2 seconds			
			print "Connection sucessed!"
			break
		except:
			print "Connection FAILED! We need have a 5 seconds break."
			#proxies = getProxies(len_proxies)
			flag_jump += 1
			if flag_jump > 5:
				print "This paper can't be connected!"
				return paper_nbCitation, paper_isseen, paper_citationURL, paper_pdfURL
			sleep(5)

	print "The status code: %d" %response.status_code
	soup = BeautifulSoup(response.text)
	try:
		soup.find("a", text = re.compile("Try your query on the entire web")).get_text()
		print "Not found in goole scholar."
		return paper_nbCitation, paper_isseen, paper_citationURL, paper_pdfURL
	except:
		try:
			soup.find("div", {"class":"gs_a"}).get_text()
			print "Found in google scholar."
		except:
			print "The paper " + paper_title +" need be checked by hand!"
			return paper_nbCitation, paper_isseen, paper_citationURL, paper_pdfURL
	try:
		link_raw = soup.find("a", text=re.compile("Cited"))
		link = link_raw.get_text()
		paper_citationURL = link_raw.get('href') #获得引用链接
		paper_nbCitation = int(link.strip('Cited by'))
	except:
		paper_nbCitation = 0
	try:
		link_pdf = soup.find("div", attrs={"class":"gs_ggsd"})
		paper_pdfURL = link_pdf.a['href']
		soup.find("span", attrs={"class":"gs_ctg2"}).get_text()
		paper_isseen = 1
	except:
		paper_isseen = 0
	return paper_nbCitation, paper_isseen, paper_citationURL, paper_pdfURL

reload(sys)
sys.setdefaultencoding("utf-8")

for row_tuple in res_set:
	paper_id = int(row_tuple[0])
	paper_title = row_tuple[1]
		
	urlTitle = url + "scholar?hl=en&q="  +  str(paper_title.replace("+","%2B").replace("Fast track article: ","").replace("Research Article: ","").replace("Guest editorial: ","").replace("Letters: ","").replace("Editorial: ","").replace("Chaos and Graphics: ","").replace("Review: ","").replace("Education: ","").replace("Computer Graphics in Spain: ","").replace("Graphics for Serious Games: ","").replace("Short Survey: ","").replace("Brief paper: ","").replace("Original Research Paper: ","").replace("Review: ","").replace("Poster abstract: ","").replace("Erratum to: ","").replace("Review: ","").replace("Guest Editorial: ","").replace("Review article: ","").replace("Editorial: ","").replace("Short Communication: ","").replace("Invited paper: ","").replace("Book review: ","").replace("Technical Section: ","").replace("Fast communication: ","").replace("Note: ","").replace("Introduction: ","").replace(":","%3A").replace("'","%27").replace("&","%26").replace("(","%28").replace(")","%29").replace("/","%2F").replace(" ","+")) + '+' + '&btnG=&as_sdt=1%2C5&as_sdtp='
	
	#proxies = getProxies(len_proxies)
	#proxies = {"https": "https://110.73.201.111:8123"}
	#my_user_agent = generate_user_agent()
	#headers['User-Agent'] = my_user_agent
	paper_nbCitation, paper_isseen, paper_citationURL, paper_pdfURL = Parser_google(urlTitle, paper_title, headers)
	if paper_nbCitation == -1:
		#当前论文未找到
		continue
	try:
		sql_update = "UPDATE test_citation.test_paper SET paper_nbCitation = '%d'\
				, paper_isseen= '%d', paper_citationURL = '%s', paper_pdfURL = '%s'\
				WHERE paper_id='%d'"\
				%(paper_nbCitation, paper_isseen, paper_citationURL.replace('\'', '\\\'').strip(), paper_pdfURL.replace('\'', '\\\'').strip(), paper_id)
		cursor.execute(sql_update)
		db.commit()
	except:
		print "Update FAILED!"

	print "----------------------%d SUSCESSED!  ----------------------" %index
	index += 1
