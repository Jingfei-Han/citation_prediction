#encoding:utf-8
#Crawl the venue's dblp name from dblp website
import MySQLdb
import MySQLdb.cursors
import sys
import requests
from bs4 import BeautifulSoup
from time import sleep
import sys

def warnInfo(string):
	print string


class extractPaper(object):
	def __init__(self,url, headers, paper_title):
		self.url = url
		self.headers = headers
		self.paper_title = paper_title
	
	def _requestWeb(self):
		cnt_res = 1
		while(cnt_res <= 5):
			try:
				response = requests.get(self.url, headers = self.headers)
				return response
			except:
				cnt_res += 1
				continue
		raise Exception #如果链接失败，则抛出异常，被调用函数捕获
	
	def _getDblp(self, li):
		try:
			cur_title = li.find('span', attrs={'class':'title', 'itemprop':'name'}).text
		except:
			print "NO NAME???"
			raise Exception
		#末尾都加上.
		if cur_title[-1] != '.':
			cur_title += '.'
		paper_title = self.paper_title
		if paper_title[-1] != '.':
			paper_title += '.'
		#去掉所有空格并转为小写字母，比较两个题目是否完全相同
		cur_title_temp = cur_title.replace(" ","").lower()
		paper_title_temp = paper_title.replace(" ", "").lower()
		if cur_title_temp != paper_title_temp:
			warnInfo("The two papers are different!\nCurrent: '%s'\nOrigin: '%s'\n"%(cur_title, paper_title))
			raise Exception
		else:
			#匹配成功
			try:
				dblpname = li.find('span', attrs={'itemprop':'isPartOf'}).text
			except:
				print "NO isPartOf???"
				raise Exception
		return dblpname


	def _parse(self, response):
		assert type(response) == requests.models.Response #判断response类型
		soup = BeautifulSoup(response.text)
		try:
			#判断是否可以匹配到
			match = soup.find(id='completesearch-info-matches').text
		except:
			warnInfo("Matches FAILED!")
			raise Exception

		if ((match != "found one match") && (match != "found 1 match")):
			warnInfo(match)
			raise Exception
		else:
			#只有一个匹配
			ul = soup.find('ul', attrs={'class':'publ-list'})
			try:
				li = ul.find('li', attrs={'class':'entry article'})			
				if type(li) == 'NoneType':
					#说明不是期刊论文
					li = ul.find('li', attrs={'class':'entry inproceedings'})			
					if type(li) == 'NoneType':
						#说明不是会议论文
						raise Exception
					else:
						#是会议论文
						dblpname = _getDblp(li)
				else:
					dblpname = _getDblp(li)
			except:
				warnInfo("Get dblpname FAILED!")
				raise Exception
					

	def crawlWeb(self):
		try:
			response = _requestWeb()
		except:
			warnInfo("Connection FAILED! The url is: " + self.url)
			raise Exception
		try:
			#获取网页成功
			dblpname = _parse(self, response)	
		except:
			#获取网页失败
			warnInfo("Parser is FAILED! The url is: " + self.url)
			raise Exception #
		return dblpname #返回dblpname值

sql_ip = "192.168.1.198"
#sql_ip = "127.0.0.1"
db = MySQLdb.connect(host=sql_ip, user='jingfei', passwd='hanjingfei007', db='citation', charset='utf8')
cursor = db.cursor()

# Make a headers

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

sql_select_venue = "SELECT COUNT(*) FROM venue" #The number of Venues
nb_venue = 0


try:
	cursor.execute(sql_select_venue)
	nb_venue = cursor.fetchone()[0]
except:
	sys.exit("ERROR: SELECT the TABLE venue failed!")

sql_select_dblp_notnull = "SELECT * FROM venue WHERE venue_dblpname IS NOT NULL ORDER BY venue_id DESC"
try:
	cursor.execute(sql_select_dblp_notnull)
	cur_venue_id = cursor.fetchone()[0]
	cur_venue_id += 1
except:
	sys.exit("ERROR: SELECT the TABLE venue failed!")	

#cur_venue_id = 32
sleep_interval = 0; # When greater than 10, we need sleep.
while(cur_venue_id <= nb_venue):
	sql_select_paper = "SELECT paper_title FROM paper WHERE venue_venue_id='%d' ORDER BY paper_publicationYear DESC" %cur_venue_id
	try:
		cursor.execute(sql_select_paper)
		paper_titles = cursor.fetchall() #Find all papers from citation1.paper, where venue_venue_id is a particular value.
	except:
		sys.exit("ERROR: SELECT the TABLE paper failed!")

	no_match = 0 #Record the time of no match.

	for paper_title_tuple in paper_titles:
		
		#Search teh paper_title from dblp
		paper_title = paper_title_tuple[0]
		if paper_title[-1] != '.':
			paper_title += '.'
		line = paper_title.replace("%","%25").replace(" ", "%20").replace(",", "%2C").replace(":", "%3A").replace("?", "%3F").replace("&", "%26").replace("'","%27")
		url = "http://dblp.uni-trier.de/search?q=" + line

		cur_extract = extractPaper(url, headers)
		try:
			dblpname = cur_extract.crawlWeb()
		except:
			no_match += 1
			if no_match >=5:
				warnInfo("The %dth venue is not in DBLP!" %cur_venue_id)
				break
			continue
		sql_update = "UPDATE venue SET venue_dblpname='%s' WHERE venue_id='%d'" %(dblp_name, cur_venue_id)
		try:
			cursor.execute(sql_update)
			db.commit()
			print "The venue %d dblpname is update SUCCESSFULLY!" %cur_venue_id
			break;
		except:
			sys.exit("This sql sentence : "  + sql_update +"  FAILED!")

	cur_venue_id += 1

print "All venues' dblpname are inserted SUCCESSFULLY!"

