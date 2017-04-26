#encoding:utf-8
import requests
from bs4 import BeautifulSoup
from time import sleep
import MySQLdb
import MySQLdb.cursors
import sys
import requests
import bs4
from bs4 import BeautifulSoup
from time import sleep
from Insert_Venue_extend import extractPaper

def warnInfo(string):
	#with open("venue_log.txt","a") as fp:
	#	fp.write(string+'\n')
	print string

db = MySQLdb.connect(host='192.168.1.198', user='jingfei', passwd='hanjingfei007', db='citation', charset='utf8')
cursor = db.cursor()

#ACM Transactions on Autonomous and Adaptive Systems

headers = { 
            'Host':'dblp.uni-trier.de',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Accept':'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Referer':'http://dblp.uni-trier.de/',
            'Cookie': 'dblp-hideable-show-feeds=true; dblp-hideable-show-rawdata=true; dblp-view=y; dblp-search-mode=c',
            'Connection':'keep-alive',
            'Cache-Control':'max-age=0',}

class extractDatabase(object):
	def __init__(self,url, headers):
		#print "__init__"
		self.url = url
		self.headers = headers
	
	def _requestWeb(self, url):
		#print "_requestWeb"
		cnt_res = 1
		while(cnt_res <= 5):
			#print "VVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVVV"
			try:
				response = requests.get(url, headers = self.headers, timeout=10)
				return response
			except:
				cnt_res += 1
				continue
		raise Exception #如果链接失败，则抛出异常，被调用函数捕获

	def _extractLinkONE(self, soup):
		#抽取一级链接
		try:
			venue_res = soup.find("div", attrs={"id":"completesearch-venues"})
			div_hide_body = venue_res.find("div", {"class":"body hide-body"})
			link_tag = div_hide_body.ul.li.a
			venue_link = link_tag['href']
			return venue_link
		except:
			warnInfo("Level 1: No venue link can be gotten!")
			raise Exception

	def _extractLinkTWO(self, soup_ONE):
		#抽取二级链接
		div_main = soup_ONE.find("div", {"id":"main"})
		ul = div_main.find_all('ul', recursive=False)
		#判断当前ul已经被返回,否则返回异常
		try:
			assert type(ul) == bs4.element.ResultSet
		except:
			warnInfo("Level 2: No volume can be gotten!")
			raise Exception
		#判断ul是否为一个集合
		volume_link = []
		#只记录最后3次的名字
		index = 1
		for ul_element in ul:
			tmp_link = ul_element.li.a['href']
			volume_link.append(tmp_link)
			if index >= 3:
				break
			else:
				index += 1
		return volume_link #返回列表

	def _extractLinkTHREE(self, soup_TWO):
		try:
			li = soup_TWO.find_all("li", attrs={"class":"entry article"})
			paper_title_list = []
			#更新为得到文章列表，加入10篇论文即可
			index = 0
			for li_element in li:
				span = li_element.find("span",attrs={"class":"title"})
				paper_title =  span.text
				paper_title_list.append(paper_title)
				if index >= 10:
					break
				else:
					index += 1
			return paper_title_list #返回一个volume对应的文章列表
		except:
			warnInfo("Level 3: No paper can be gotten!")
			raise Exception

	def _parserDBLP(self, response):
		assert type(response) == requests.models.Response #判断response类型
		soup = BeautifulSoup(response.text)
		#判断是否只有唯一匹配
		try:
			venue_res = soup.find("div", attrs={"id":"completesearch-venues"})
			div_hide_body = venue_res.find("div", {"class":"body hide-body"})
			all_li = div_hide_body.ul.find_all('li')
			#只有唯一匹配才继续进行
			assert len(all_li) == 1
		except:
			warnInfo("No only MATCHES!")
			raise Exception
		#此时只有唯一匹配
		try:
			venue_link = self._extractLinkONE(soup)
		except:
			raise Exception
		try:
			res_ONE = self._requestWeb(venue_link)
		except:
			warnInfo("res_ONE: Connection FAILED! The url is: " + venue_link)
			raise Exception
		soup_ONE = BeautifulSoup(res_ONE.text)
		try:
			volume_link = self._extractLinkTWO(soup_ONE) #返回的volume_link为列表形式，因为可能有多个dblpname
		except:
			warnInfo("ul is not found????")
			raise Exception
		#得到volume_link之后继续爬该列表对应链接的文章的链接。
		dblpname_list = []
		for one_volume_link in volume_link:
			#对于每个链接，对应一个dblpname
			try:
				#尝试获取该论文的dblpname
				try:
					res_TWO = self._requestWeb(one_volume_link)
				except:
					warnInfo("res_TWO: Connection FAILED! The url is: " + one_volume_link)
					raise Exception
				soup_TWO = BeautifulSoup(res_TWO.text)
				try:
					#获得对应volume的paper的文章名列表
					paper_title_list = self._extractLinkTHREE(soup_TWO)
				except:
					#warnInfo("paper_title is not found????")
					raise Exception
				#对于给定的paper title，应该用extractPaper类抽取论文的dblp name
				mul_match = 0
				for paper_title in paper_title_list:
					line = paper_title.replace("%","%25").replace(" ", "%20").replace(",", "%2C").replace(":", "%3A").replace("?", "%3F").replace("&", "%26").replace("'","%27")
					url = "http://dblp.uni-trier.de/search?q=" + line

					cur_extract = extractPaper(url, headers, paper_title)
					try:
						dblpname = cur_extract.crawlWeb()
						dblpname_list.append(dblpname) #加入列表
						break #找到当前volume的dblpname之后则跳出循环

					except:
						mul_match += 1
						if mul_match >=5:
							warnInfo("The paper: %s is not in DBLP! IMPOSSIBLE!!" %paper_title)
							raise Exception
						else:
							continue
						#warnInfo("Current is not in DBLP, that is IMPOSSIBLE!")
						#raise Exception
			except:
				warnInfo("Current dblpname can't be GOTTEN!!")
				raise Exception

		return dblpname_list #返回该venue的dblpname列表



	def getDBLPname(self):
		try:
			response = self._requestWeb(self.url)
		except:
			warnInfo("Connection FAILED! The url is: " + self.url)
			raise Exception
		try:
			dblpname_list = self._parserDBLP(response)
		except:
			warnInfo("Parser DBLP FAILED!!")
			raise Exception
		return dblpname_list
		#此时应将dblpname_list写入数据库



sql_select = "SELECT CCF_id, CCF_name, CCF_abbreviation, CCF_type FROM ccf WHERE CCF_id<10000000 AND CCF_dblpname IS NULL"
try:
	#Record the number of items of table dblp
	cursor.execute(sql_select)
	ccf_set = cursor.fetchall()
except:
	sys.exit("ERROR: SELECT the TABLE ccf failed!")

for row_tuple in ccf_set:

	CCF_id = int(row_tuple[0])
	CCF_name = row_tuple[1]
	CCF_abbreviation = row_tuple[2]
	CCF_type = row_tuple[3]
	if CCF_type == 'conference':
		#当前为会议
		if CCF_abbreviation != '':
			sql_update = "UPDATE ccf SET CCF_dblpname = '%s' WHERE CCF_id = '%d' " %(CCF_abbreviation, CCF_id)
			try:
				cursor.execute(sql_update)
				db.commit()
				print "%dth ccf venue's dblpname is updated successfully!" %CCF_id
			except:
				sys.exit("ERROR: Update the TABLE ccf failed!")
		else:
			print "CCF_abbreviation is empty, so we don't unpdate the conference: %s" %CCF_name
			continue
	else :
		#当前为期刊
		line = CCF_name.replace("%","%25").replace(" ", "%20").replace(",", "%2C").replace(":", "%3A").replace("?", "%3F").replace("&", "%26").replace("'","%27")
		url = "http://dblp.uni-trier.de/search?q=" + line
		#url = 'http://dblp.uni-trier.de/search?q=Cybernetics%20and%20Systems'
		assert CCF_type == 'journal'
		#sys.exit("Current venue is '%s'") %CCF_type
		cur_extract_database = extractDatabase(url, headers)

		dblpname_list = [] #初始化为空列表
		try:
			dblpname_list = cur_extract_database.getDBLPname()
		except:
			warnInfo("Get DBLP LIST FAILED!!")
			dblpname = "NOT IN DBLP" #没有找到，则得到dblpname为NOT IN DBLP
			dblpname_list.append(dblpname)
			#continue

		#得到dblpname_list之后，尝试写入数据库
		assert len(dblpname_list) >= 1
		try:
			if len(dblpname_list) == 1:
				#只有唯一一个dblp名
				print "The venue :'%s' DBLP name is: '%s'" %(CCF_name, dblpname_list[0])
				sql_update = "UPDATE ccf SET CCF_dblpname = '%s' WHERE CCF_id = '%d'" %(dblpname_list[0], CCF_id)
			elif len(dblpname_list) == 2:
				#有两个dblp名
				print "The venue :'%s' DBLP name is: '%s' and '%s'" %(CCF_name, dblpname_list[0], dblpname_list[1])
				sql_update = "UPDATE ccf SET CCF_dblpname = '%s', CCF_dblpname2 = '%s' WHERE CCF_id = '%d'" %(dblpname_list[0], dblpname_list[1], CCF_id)
			else:
				#有至少3个dblp名，只取前3个
				print "The venue :'%s' DBLP name is: '%s' and '%s' and '%s'" %(CCF_name, dblpname_list[0], dblpname_list[1], dblpname_list[2])
				sql_update = "UPDATE ccf SET CCF_dblpname = '%s', CCF_dblpname2 = '%s', CCF_dblpname3 = '%s' WHERE CCF_id = '%d'" %(dblpname_list[0], dblpname_list[1], dblpname_list[2], CCF_id)
			#更新数据库
			try:
				cursor.execute(sql_update)
				db.commit()
				print "%dth ccf venue's dblpname is updated successfully!" %CCF_id
			except:
				sys.exit("ERROR: Update the TABLE ccf failed!")
			#del dblp_name #Delete last variable
		except :
			print "Not found the venue: '%s' IN DBLP" %CCF_name


