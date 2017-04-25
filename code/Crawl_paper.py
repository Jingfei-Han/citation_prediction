#encoding:utf-8
import MySQLdb
import MySQLdb.cursors
import requests
from bs4 import BeautifulSoup
from time import sleep
import re
import random
import sys

db = MySQLdb.connect(host='localhost', user='jingfei', passwd='hanjingfei007', db='citation', charset='utf8')
cursor = db.cursor()

#这里记录参数，命令行访问格式为:
#python Crawl_paper.py A Conference
CCF_classification = sys.argv[1]
CCF_type = sys.argv[2]
#写入log文件需要改下名字
fp = open("./log/LOG_paper_"+CCF_classification + "_"+CCF_type+".txt", "a")

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

#sql_cnt = "SELECT COUNT(*) FROM citation.paper WHERE paper_nbCitation !=-1"
sql_cnt = "SELECT COUNT(*) FROM citation.paper\
			WHERE venue_venue_id IN(\
				SELECT venue_id FROM citation.venue\
				WHERE dblp_dblp_id IN(\
					SELECT dblp_id\
					FROM citation.ccf, citation.dblp\
					WHERE CCF_dblpname = dblp_name\
					AND CCF_type = '%s'\
					AND CCF_classification = '%s'\
				)\
			)" %(CCF_type, CCF_classification)

sql_cnt_index = "SELECT COUNT(*) FROM citation.paper\
			WHERE venue_venue_id IN(\
				SELECT venue_id FROM citation.venue\
				WHERE dblp_dblp_id IN(\
					SELECT dblp_id\
					FROM citation.ccf, citation.dblp\
					WHERE CCF_dblpname = dblp_name\
					AND CCF_type = '%s'\
					AND CCF_classification = '%s'\
				)\
			)\
			AND paper_nbCitation != -1" %(CCF_type, CCF_classification)

cursor.execute(sql_cnt)
total = cursor.fetchone()[0] #总共的论文数量

cursor.execute(sql_cnt_index)
index = cursor.fetchone()[0]
index += 1 #当前条数

info_print = "Now we prepare to crawl %s CCF classification and %s Venue paper" %(CCF_classification, CCF_type)
info_cnt = "Total: %5d    Current: %5d" %(total, index)
print info_print
print info_cnt
fp.write(info_print + "\n")
fp.write(info_cnt + "\n")

#sql_select = "SELECT paper_id, paper_title\
#			FROM citation.paper WHERE paper_nbCitation =-1"

sql_select = "SELECT paper_id, paper_title\
			FROM citation.paper\
			WHERE venue_venue_id IN(\
				SELECT venue_id\
				FROM citation.venue\
				WHERE dblp_dblp_id IN (\
					SELECT dblp_id\
					FROM citation.ccf, citation.dblp\
					WHERE CCF_dblpname = dblp_name\
					AND CCF_type = '%s'\
					AND CCF_classification = '%s'\
				)\
			)\
			AND paper_nbCitation = -1" %(CCF_type, CCF_classification)			

cursor.execute(sql_select)
res_set = cursor.fetchall()



url = "https://b.ggkai.men/extdomains/scholar.google.com/"

def Parser_google(urlTitle, paper_title, headers, proxies=None):
	flag_jump = 0
	paper_nbCitation = -2
	paper_isseen = -1
	paper_citationURL = ""
	paper_pdfURL = ""
	while True:
		try:
			response = requests.get(urlTitle, headers = headers, timeout=10)
			#time_sleep = random.randint(1,3)
			#sleep(time_sleep) #break 2 seconds
			break
		except:
			print "Connection FAILED! We need have 3 seconds break."
			fp.write("Connection FAILED! We need have a 5 seconds break.\n") 
			flag_jump += 1
			if flag_jump > 5:
				fp.write("This paper can't be connected!\n") 
				return paper_nbCitation, paper_isseen, paper_citationURL, paper_pdfURL
			sleep(3)

	#print "The status code: %d" %response.status_code
	soup = BeautifulSoup(response.text)
	try:
		soup.find("a", text = re.compile("Try your query on the entire web")).get_text()
		fp.write("PAPER: " + paper_title + " :Not found in goole scholar.\n") 
		return paper_nbCitation, paper_isseen, paper_citationURL, paper_pdfURL
	except:
		try:
			soup.find("div", {"class":"gs_a"}).get_text()
			#print "Found in google scholar."
		except:
			fp.write("The paper " + paper_title +" need be checked by hand!\n")
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
		
	urlTitle = url + "scholar?hl=en&q="  +  str(paper_title.replace(":","%3A").replace("'","%27").replace("&","%26").replace("(","%28").replace(")","%29").replace("/","%2F").replace(" ","+")) + '+' + '&btnG=&as_sdt=1%2C5&as_sdtp='
	
	paper_nbCitation, paper_isseen, paper_citationURL, paper_pdfURL = Parser_google(urlTitle, paper_title, headers)
	if paper_nbCitation == -1:
		#当前论文未找到
		continue
	try:
		sql_update = "UPDATE citation.paper SET paper_nbCitation = '%d'\
				, paper_isseen= '%d', paper_citationURL = '%s', paper_pdfURL = '%s'\
				WHERE paper_id='%d'"\
				%(paper_nbCitation, paper_isseen, paper_citationURL.replace('\'', '\\\'').strip(), paper_pdfURL.replace('\'', '\\\'').strip(), paper_id)
		cursor.execute(sql_update)
		db.commit()
	except:
		fp.write("Update FAILED!\n")
	print "----------------------%d SUSCESSED!  ----------------------" %index 
	fp.write("----------------------%d SUSCESSED!  ----------------------\n" %index) 
	index += 1

fp.close()
