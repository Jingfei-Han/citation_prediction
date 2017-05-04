#encoding:utf-8
import MySQLdb
import MySQLdb.cursors
import requests
from bs4 import BeautifulSoup
from time import sleep
import re
import random
import sys
import threading



def warnInfo(string):
	#with open("venue_log.txt","a") as fp:
	#	fp.write(string+'\n')
	print string


class extractCitation(object):
	def __init__(self,url, headers, paper_title):
		#print "__init__"
		self.url = url
		self.headers = headers
		self.paper_title = paper_title
	
	def _requestWeb(self):
		#print "_requestWeb"
		cnt_res = 1
		while(cnt_res <= 5):
			#print "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
			try:
				response = requests.get(self.url, headers = self.headers, timeout=10)
				random_time = random.randint(1,3) #随机停止1到3秒
				sleep(random_time)
				return response
			except:
				cnt_res += 1
				sleep(2) #等待两秒
				continue
		raise Exception #如果链接失败，则抛出异常，被调用函数捕获

	def _parseGoogle(self, response):
		#解析google页面
		paper_nbCitation = -1
		paper_isseen = -1
		paper_citationURL = ""
		paper_pdfURL = ""

		#print "The status code: %d" %response.status_code
		soup = BeautifulSoup(response.text)
		try:
			soup.find("a", text = re.compile("Try your query on the entire web")).get_text()
			warnInfo("PAPER: " + paper_title + " :Not found in goole scholar.\n") 
			raise Exception
		except:
			try:
				soup.find("div", attrs={"class":"gs_a"}).get_text()
				#print "Found in google scholar."
			except:
				warnInfo("The paper " + paper_title +" need be checked by hand!\n")
				raise Exception

		#判断第一个名字是否与paper title相同
		try:
			gs_ccl_results = soup.find("div", attrs={"id":"gs_ccl_results"})
			gs_r = gs_ccl_results.find("div", attrs={"class":"gs_r"})
			#gs_r为第一个结果的div
			assert gs_r.name == 'div'
			cur_title = gs_r.h3.a.text #当前得到的文章title
		except:
			warnInfo("Get Current paper title FAILED!")
			raise Exception
		try:
			#去掉所有非字母字符来比较，使用filter
			#因为paper_title和cur_title是unicode类型，不能用str.isalpha，应使用unicode.isalpha
			paper_title_tmp = filter(unicode.isalpha, self.paper_title).lower()
			cur_title_tmp = filter(unicode.isalpha, cur_title).lower()
			assert paper_title_tmp == cur_title_tmp
		except:
			warnInfo("The two papers are different!\nCurrent: '%s'\nOrigin: '%s'\n"%(cur_title, paper_title))
			raise Exception

		#查看是否存在引用
		try:
			link_raw = gs_r.find("a", text=re.compile("Cited"))
			link = link_raw.get_text()
			paper_citationURL = link_raw.get('href') #获得引用链接
			paper_nbCitation = int(link.strip('Cited by')) #获得引用数
		except:
			paper_nbCitation = 0 #没有找到Cited by， 则引用数为0
		#查看是否存在pdf
		try:
			gs_r.find("span", attrs={"class":"gs_ctg2"}).get_text() #找到[pdf]
			link_pdf = gs_r.find("div", attrs={"class":"gs_ggsd"})
			paper_pdfURL = link_pdf.a['href'] #获得pdf链接
			paper_isseen = 1
		except:
			paper_isseen = 0 #没有找到[pdf],则pdf不可得到
		return paper_nbCitation, paper_isseen, paper_citationURL, paper_pdfURL

	def crawlWeb(self):
		#print "crawlWeb"
		try:
			response = self._requestWeb()
		except:
			warnInfo("Connection FAILED! The url is: " + self.url)
			raise Exception
		try:
			#获取网页成功
			paper_nbCitation, paper_isseen, paper_citationURL, paper_pdfURL = self._parseGoogle(response)	
		except:
			#获取网页失败
			warnInfo("Parser is FAILED! The url is: " + self.url)
			raise Exception #
		return paper_nbCitation, paper_isseen, paper_citationURL, paper_pdfURL #返回paper信息，包括paper_nbCitation, paper_issen, paper_citationURL, paper_pdfURL

def SQL_Operation(cur_index_id, nb_venue, headers):	
	sql_ip = "192.168.1.198"
	#sql_ip = "127.0.0.1"
	db = MySQLdb.connect(host=sql_ip, user='jingfei', passwd='hanjingfei007', db='citation', charset='utf8')
	cursor = db.cursor()

	while(cur_index_id <= nb_venue):
		warnInfo("*********************%d HAHA*******************" %cur_index_id)
		sql_select_paper = "SELECT paper_title, paper_publicationYear FROM paper WHERE index_id='%d'" %cur_index_id
		try:
			cursor.execute(sql_select_paper)
			paper_tuple = cursor.fetchone()
			paper_title = paper_tuple[0] #找到当前论文题目
			paper_publicationYear = str(paper_tuple[1])
		except:
			sys.exit("ERROR: SELECT the TABLE paper failed!")

		url = "https://a.ggkai.men/extdomains/scholar.google.com/"
		#weizhui = '&btnG=&as_sdt=1%2C5&as_sdtp=&as_ylo=%d&as_yhi=%d' %(paper_publicationYear, paper_publicationYear)
		urlTitle = url + "scholar?hl=en&q="  +  str(paper_title.replace(":","%3A").replace("'","%27").replace("&","%26").replace("(","%28").replace(")","%29").replace("/","%2F").replace(" ","+")) + '+' + '&btnG=&as_sdtp=&as_ylo=' + paper_publicationYear + '&as_yhi=' + paper_publicationYear
		
		cur_extract = extractCitation(urlTitle, headers, paper_title)
		try:
			paper_nbCitation, paper_isseen, paper_citationURL, paper_pdfURL = cur_extract.crawlWeb()
		except:
			#出现错误，需要赋一个特殊值
			paper_nbCitation = -2 #-2表示找过，但是没有找到
			paper_isseen = -2 #-2表示找过，但没找到
			paper_citationURL = ''
			paper_pdfURL = ''

		#无论解析阶段是否出现异常都写入数据库
		try:
			sql_update = "UPDATE paper SET paper_nbCitation = '%d'\
					, paper_isseen= '%d', paper_citationURL = '%s', paper_pdfURL = '%s'\
					WHERE index_id='%d'"\
					%(paper_nbCitation, paper_isseen, paper_citationURL.replace('\'', '\\\'').strip(), paper_pdfURL.replace('\'', '\\\'').strip(), cur_index_id)
			cursor.execute(sql_update)
			db.commit()
		except:
			print "UPDATE FAILED!"

		print "----------------------%d SUSCESSED!  ----------------------" %cur_index_id 
		cur_index_id += 1


if __name__ == "__main__":
	start_paper = int(sys.argv[1])
	end_paper = int(sys.argv[2])

	#TEST
	#start_paper = 1
	#end_paper = 100

	reload(sys)
	sys.setdefaultencoding("utf-8")

	db = MySQLdb.connect(host='192.168.1.198', user='jingfei', passwd='hanjingfei007', db='citation', charset='utf8')
	cursor = db.cursor()

	#这里记录参数，命令行访问格式为:
	#python Crawl_paper.py A Conference

	#CCF_classification = sys.argv[1]
	#CCF_type = sys.argv[2]

	#写入log文件需要改下名字
	#fp = open("./log/LOG_paper_"+CCF_classification + "_"+CCF_type+".txt", "a")

	#用于测试
	#CCF_classification = 'A'
	#CCF_type = 'Conference'

	#镜像headers
	headers = {
		'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		'Accept-Encoding':'gzip, deflate, sdch, br',
		'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
		'Connection':'keep-alive',
		'Host':'a.ggkai.men',
		'Referer':'https://a.ggkai.men/extdomains/scholar.google.com/schhp?hl=en&num=20&as_sdt=0',
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
		'Cache-Control':'max-age=0',
		'Cookie':'NID=101=ZPX_tebnsmlbtsniyMAFKDXfTNmNmI9p9jF6HVl5luswkM7qLeWnkHFpPmdL0beGn0lCaJjGgevBsBOj2qnLDPHi2NCujP3CRk-8rUIfsHXc0ycB_ToZS5gAO5buBDzJ; GSP=LM=1492323405:S=6WH6FgIC17h7zhM5; Hm_lvt_df11358c4b6a37507eca01dfe919e040=1492323406,1492341461; Hm_lpvt_df11358c4b6a37507eca01dfe919e040=1492341461',
	}

	"""
	index = 0
	#此处用于按CCF分类来爬虫
	#sql_cnt = "SELECT COUNT(*) FROM citation.paper WHERE paper_nbCitation !=-1"
	sql_cnt = "SELECT COUNT(*) FROM paper\
				WHERE venue_venue_id IN(\
					SELECT venue_id FROM venue\
					WHERE dblp_dblp_id IN(\
						SELECT dblp_id\
						FROM ccf, dblp\
						WHERE CCF_dblpname = dblp_name\
						AND CCF_type = '%s'\
						AND CCF_classification = '%s'\
					)\
				)" %(CCF_type, CCF_classification)

	sql_cnt_index = "SELECT COUNT(*) FROM paper\
				WHERE venue_venue_id IN(\
					SELECT venue_id FROM venue\
					WHERE dblp_dblp_id IN(\
						SELECT dblp_id\
						FROM ccf, dblp\
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
	"""
	sql_select = "SELECT index_id FROM paper WHERE paper_nbCitation = -1 AND index_id>='%d' AND index_id<='%d'" %(start_paper, end_paper)	

	cursor.execute(sql_select)
	cur_index_id = cursor.fetchone()[0]

	#SQL_Operation(1, 100, headers)

	interval = (end_paper - cur_index_id + 1) / 4
	t = []
	for i in range(3):
		tmp = threading.Thread(target=SQL_Operation, args=(cur_index_id+i*interval, cur_index_id+(i+1)*interval+2, headers))
		t.append(tmp)
		t[i].start()

	tmp3 = threading.Thread(target=SQL_Operation, args=(cur_index_id+3*interval, end_paper, headers))
	tmp3.start()
	#SQL_Operation(cur_venue_id, nb_venue, cursor, headers)



