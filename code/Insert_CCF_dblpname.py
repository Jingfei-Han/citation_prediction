import requests
from bs4 import BeautifulSoup
from time import sleep
import MySQLdb
import MySQLdb.cursors
import sys
import requests
from bs4 import BeautifulSoup
from time import sleep

db = MySQLdb.connect(host='localhost', user='root', passwd='hanjingfei007', db='citation', charset='utf8')
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




sql_select = "SELECT CCF_id, CCF_name, CCF_abbreviation, CCF_type FROM citation.ccf WHERE CCF_id<10000000 AND CCF_dblpname IS NULL"
try:
	#Record the number of items of table dblp
	cursor.execute(sql_select)
	ccf_set = cursor.fetchall()
except:
	sys.exit("ERROR: SELECT the TABLE ccf failed!")

for row_tuple in ccf_set:

	CCF_id = row_tuple[0]
	CCF_name = row_tuple[1]
	CCF_abbreviation = row_tuple[2]
	CCF_type = row_tuple[3]
	if CCF_type == 'conference':
		if CCF_abbreviation != '':
			sql_update = "UPDATE citation.ccf SET CCF_dblpname = '%s' WHERE CCF_id = '%d' " %(CCF_abbreviation, CCF_id)
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
		line = CCF_name.replace("%","%25").replace(" ", "%20").replace(",", "%2C").replace(":", "%3A").replace("?", "%3F").replace("&", "%26").replace("'","%27")
		url = "http://dblp.uni-trier.de/search?q=" + line
		#url = 'http://dblp.uni-trier.de/search?q=Cybernetics%20and%20Systems'
		if CCF_type != 'journal':
			sys.exit("Current venue is '%s'") %CCF_type

		flag_jump = 0
		while(True):
			try:
				r = requests.get(url, headers = headers, timeout=15)#, proxies=proxies)
				break
			except:
				print "Connection FAILED! We need have a 5 seconds break."
				flag_jump += 1
				if flag_jump > 10:
					print "This venue can't be connected! We must change the next venue."
					break
				sleep(5)
		if (flag_jump > 10):
			continue

		soup1 = BeautifulSoup(r.text)

		exact_match = ''
		exact_match = soup1.find(text="Exact matches")
		if exact_match:
			#We can get the venue
			tag = soup1.find('mark').parent

			link = tag['href']

			flag_jump = 0
			while(True):
				try:
					r2 = requests.get(link, headers = headers, timeout=15)#, proxies=proxies)
					break
				except:
					print "Connection FAILED! We need have a 5 seconds break."
					flag_jump += 1
					if flag_jump > 10:
						print "This venue can't be connected! We must change the next venue."
						break
					sleep(5)
			if (flag_jump > 10):
				continue

			soup2 = BeautifulSoup(r2.text)
			
			main = soup2.find('div', id='main')
			ul = main.find('ul', recursive=False)

			if ul:
			
				link3 = ul.find('a')['href'] 

				flag_jump = 0
				while(True):
					try:
						r3 = requests.get(link3, headers = headers, timeout=15)#, proxies=proxies)
						break
					except:
						print "Connection FAILED! We need have a 5 seconds break."
						flag_jump += 1
						if flag_jump > 10:
							print "This venue can't be connected! We must change the next venue."
							break
						sleep(5)
				if (flag_jump > 10):
					continue

				soup3 = BeautifulSoup(r3.text)

				paper_set = soup3.find_all('span', attrs={'class':'title'})
				for row in paper_set:
					one_paper = row.text
					#one_paper = soup3.find('span', attrs={'class':'title'}).text
					line = one_paper.replace("%","%25").replace(" ","%20").replace(",", "%2C").replace(":", "%3A").replace("?", "%3F").replace("&", "%26").replace("'", "%27")

					url = "http://dblp.uni-trier.de/search?q=" + line

					flag_jump = 0
					while(True):
						try:
							response = requests.get(url, headers = headers, timeout=15)#, proxies=proxies)
							break
						except:
							print "Connection FAILED! We need have a 5 seconds break."
							flag_jump += 1
							if flag_jump > 10:
								print "This venue can't be connected! We must change the next venue."
								break
							sleep(5)
					if (flag_jump > 10):
						continue

					soup = BeautifulSoup(response.text)

					try:
						match = soup.find(id='completesearch-info-matches').text
						if match == "found 1 match" or match == "found one match":
							print "Search successfully!"
						else:
							print "The paper is not the only one."
							continue
					except:
						print "ERROR: Match FAILED!"
						continue
					try:
						li = soup.find('li', attrs={'class':'entry article'})
						span = li.find('span',attrs={'itemprop':'isPartOf'})
					except:
						try:
							li = soup.find('li', attrs={'class':'entry inproceedings'})
							span = li.find('span',attrs={'itemprop':'isPartOf'})
						except:
							try:
								li = soup.find('li', attrs={'class':'entry informal'})
								span = li.find('span',attrs={'itemprop':'isPartOf'})
							except:
								print "DBLP FAILED!"
								continue

					dblp_name = span.text
					if dblp_name:
						break
					#print dblp_name
					#return dblp_name
				else:
					#Not Found
					print "The venue %s NOT FOUND in DBLP" %CCF_name
					break
		else :
			print "No exact matches."
			#No exact matches , but we can check whether only one likely matches

			likely_matches = ''
			likely_matches = soup1.find(text='Likely matches')
			if likely_matches:
				#We consider this is the venue's dblpname when only one likely matches
				div_likely = soup1.find(id = 'completesearch-venues')
				div_likely2 = div_likely.find('div', attrs={'class':'body hide-body'})
				ul_likely = div_likely2.find('ul',recursive=False)
				lis_likely = ul_likely.find_all('li')
				cnt_likely = 0
				for li_likely in lis_likely:
					cnt_likely += 1

				if cnt_likely == 1:
					print "Only 1 likely matches!"

					tag = soup1.find('mark').parent

					link = tag['href']

					flag_jump = 0
					while(True):
						try:
							r2 = requests.get(link, headers = headers, timeout=15)#, proxies=proxies)
							break
						except:
							print "Connection FAILED! We need have a 5 seconds break."
							flag_jump += 1
							if flag_jump > 10:
								print "This venue can't be connected! We must change the next venue."
								break
							sleep(5)
					if (flag_jump > 10):
						continue

					soup2 = BeautifulSoup(r2.text)
					
					main = soup2.find('div', id='main')
					ul = main.find('ul', recursive=False)

					if ul:
					
						link3 = ul.find('a')['href'] 

						flag_jump = 0
						while(True):
							try:
								r3 = requests.get(link3, headers = headers, timeout=15)#, proxies=proxies)
								break
							except:
								print "Connection FAILED! We need have a 5 seconds break."
								flag_jump += 1
								if flag_jump > 10:
									print "This venue can't be connected! We must change the next venue."
									break
								sleep(5)
						if (flag_jump > 10):
							continue

						soup3 = BeautifulSoup(r3.text)

						paper_set = soup3.find_all('span', attrs={'class':'title'})
						for row in paper_set:
							one_paper = row.text
							#one_paper = soup3.find('span', attrs={'class':'title'}).text
							line = one_paper.replace("%","%25").replace(" ","%20").replace(",", "%2C").replace(":", "%3A").replace("?", "%3F").replace("&", "%26").replace("'", "%27")

							url = "http://dblp.uni-trier.de/search?q=" + line

							flag_jump = 0
							while(True):
								try:
									response = requests.get(url, headers = headers, timeout=15)#, proxies=proxies)
									break
								except:
									print "Connection FAILED! We need have a 5 seconds break."
									flag_jump += 1
									if flag_jump > 10:
										print "This venue can't be connected! We must change the next venue."
										break
									sleep(5)
							if (flag_jump > 10):
								continue

							soup = BeautifulSoup(response.text)

							try:
								match = soup.find(id='completesearch-info-matches').text
								if match == "found 1 match" or match == "found one match":
									print "Search successfully!"
								else:
									print "The paper is not the only one."
									continue
							except:
								print "ERROR: Match FAILED!"
								continue
							try:
								li = soup.find('li', attrs={'class':'entry article'})
								span = li.find('span',attrs={'itemprop':'isPartOf'})
							except:
								try:
									li = soup.find('li', attrs={'class':'entry inproceedings'})
									span = li.find('span',attrs={'itemprop':'isPartOf'})
								except:
									try:
										li = soup.find('li', attrs={'class':'entry informal'})
										span = li.find('span',attrs={'itemprop':'isPartOf'})
									except:
										print "DBLP FAILED!"
										continue

							dblp_name = span.text
							if dblp_name:
								break
							#print dblp_name
							#return dblp_name
					else:
						#Not Found
						print "The venue %s NOT FOUND in DBLP" %CCF_name
						break
				else:
					continue
			else:
				continue
		try:
			print "The venue :'%s' DBLP name is: '%s'" %(CCF_name, dblp_name)
			sql_update = "UPDATE citation.ccf SET CCF_dblpname = '%s' WHERE CCF_id = '%d'" %(dblp_name, CCF_id)
			try:
				cursor.execute(sql_update)
				db.commit()
				print "%dth ccf venue's dblpname is updated successfully!" %CCF_id
			except:
				sys.exit("ERROR: Update the TABLE ccf failed!")
			del dblp_name #Delete last variable
		except :
			print "Not found the venue: '%s' IN DBLP" %CCF_name


