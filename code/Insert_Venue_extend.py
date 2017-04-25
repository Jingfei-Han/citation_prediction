#encoding:utf-8
#Crawl the venue's dblp name from dblp website
import MySQLdb
import MySQLdb.cursors
import sys
import requests
from bs4 import BeautifulSoup
from time import sleep
import sys
import threading

def warnInfo(string):
	#with open("venue_log.txt","a") as fp:
	#	fp.write(string+'\n')
	print string


class extractPaper(object):
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
				return response
			except:
				cnt_res += 1
				continue
		raise Exception #如果链接失败，则抛出异常，被调用函数捕获
	
	def _getDblp(self, li):
		#print "_getDblp"
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
		#print "_parse"
		assert type(response) == requests.models.Response #判断response类型
		soup = BeautifulSoup(response.text)
		try:
			#判断是否可以匹配到
			match = soup.find(id='completesearch-info-matches').text
		except:
			warnInfo("Matches FAILED!")
			raise Exception

		if ((match != "found one match") and (match != "found 1 match")):
			warnInfo(match)
			raise Exception
		else:
			#只有一个匹配
			ul = soup.find('ul', attrs={'class':'publ-list'})
			try:
				li = ul.find('li', attrs={'class':'entry article'})			
				if li is None:
					#说明不是期刊论文
					li = ul.find('li', attrs={'class':'entry inproceedings'})			
					if li is None:
						#说明不是会议论文
						li = ul.find('li', attrs={'class':'entry informal'})
						if li is None:
							li = ul.find('li', attrs={'class':'entry book'})
							if li is None:
								raise Exception
							else:
								#是书或者毕业论文
								dblpname = self._getDblp(li)
						else:
							#非正式
							dblpname = self._getDblp(li)
					else:
						#是会议论文
						dblpname = self._getDblp(li)
				else:
					#期刊论文
					dblpname = self._getDblp(li)
			except:
				warnInfo("Get dblpname FAILED!")
				raise Exception
		return dblpname

	def crawlWeb(self):
		#print "crawlWeb"
		try:
			response = self._requestWeb()
		except:
			warnInfo("Connection FAILED! The url is: " + self.url)
			raise Exception
		try:
			#获取网页成功
			dblpname = self._parse(response)	
		except:
			#获取网页失败
			warnInfo("Parser is FAILED! The url is: " + self.url)
			raise Exception #
		return dblpname #返回dblpname值

def SQL_Operation(cur_venue_id, nb_venue, headers):

	sql_ip = "192.168.1.198"
	#sql_ip = "127.0.0.1"
	db = MySQLdb.connect(host=sql_ip, user='jingfei', passwd='hanjingfei007', db='citation', charset='utf8')
	cursor = db.cursor()

	while(cur_venue_id <= nb_venue):
		warnInfo("*********************%d HAHA*******************" %cur_venue_id)
		#print "*********************%d HAHA*******************" %cur_venue_id
		sql_select_paper = "SELECT paper_title FROM paper WHERE venue_venue_id='%d' ORDER BY paper_publicationYear DESC" %cur_venue_id
		try:
			cursor.execute(sql_select_paper)
			paper_titles = cursor.fetchall() #Find all papers from citation1.paper, where venue_venue_id is a particular value.
		except:
			sys.exit("ERROR: SELECT the TABLE paper failed!")

		no_match = 0 #Record the time of no match.

		for paper_title_tuple in paper_titles:
			#print "-------------------------------------------"
			#Search teh paper_title from dblp
			paper_title = paper_title_tuple[0]
			if paper_title[-1] != '.':
				paper_title += '.'
			line = paper_title.replace("%","%25").replace(" ", "%20").replace(",", "%2C").replace(":", "%3A").replace("?", "%3F").replace("&", "%26").replace("'","%27")
			url = "http://dblp.uni-trier.de/search?q=" + line

			cur_extract = extractPaper(url, headers, paper_title)
			try:
				dblpname = cur_extract.crawlWeb()
			except:
				no_match += 1
				if no_match >=5:
					warnInfo("The %dth venue is not in DBLP!" %cur_venue_id)
					dblpname = "NOT IN DBLP"
					#break
				else:
					#sleep(2)
					continue
				
			sql_update = "UPDATE venue SET venue_dblpname='%s' WHERE venue_id='%d'" %(dblpname, cur_venue_id)
			try:
				cursor.execute(sql_update)
				db.commit()
				print "The venue %d dblpname is update SUCCESSFULLY!" %cur_venue_id
				break;
			except:
				sys.exit("This sql sentence : "  + sql_update +"  FAILED!")

		cur_venue_id += 1

if __name__ == "__main__":

	start_paper = int(sys.argv[1])
	end_paper = int(sys.argv[2])

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

	# sql_select_venue = "SELECT COUNT(*) FROM venue" #The number of Venues
	# nb_venue = 0


	# try:
	# 	cursor.execute(sql_select_venue)
	# 	nb_venue = cursor.fetchone()[0]
	# except:
	# 	sys.exit("ERROR: SELECT the TABLE venue failed!")

	sql_select_dblp_null = "SELECT * FROM venue WHERE venue_dblpname IS NULL AND venue_id>='%d' AND venue_id<='%d'" %(start_paper, end_paper)
	try:
		cursor.execute(sql_select_dblp_null)
		cur_venue_id = cursor.fetchone()[0]
	except:
		sys.exit("ERROR: SELECT the TABLE venue failed!")	

	interval = (end_paper - cur_venue_id + 1) / 4
	t = []
	for i in range(3):
		tmp = threading.Thread(target=SQL_Operation, args=(cur_venue_id+i*interval, cur_venue_id+(i+1)*interval-1, headers))
		t.append(tmp)
		t[i].start()

	tmp3 = threading.Thread(target=SQL_Operation, args=(cur_venue_id+3*interval, end_paper, headers))
	tmp3.start()
	#SQL_Operation(cur_venue_id, nb_venue, cursor, headers)


	print "All venues' dblpname are inserted SUCCESSFULLY!"

