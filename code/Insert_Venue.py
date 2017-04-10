#Crawl the venue's dblp name from dblp website
import MySQLdb
import MySQLdb.cursors
import sys
import requests
from bs4 import BeautifulSoup
from time import sleep

db = MySQLdb.connect(host='localhost', user='root', passwd='hanjingfei007', db='citation1', charset='utf8')
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

ipHttps = "http://182.88.88.109:8123"

proxies = { 
"http": ipHttps,
}

sql_select_venue = "SELECT COUNT(*) FROM citation1.venue" #The number of Venues
nb_venue = 0


try:
	cursor.execute(sql_select_venue)
	nb_venue = cursor.fetchone()[0]
except:
	sys.exit("ERROR: SELECT the TABLE venue failed!")

sql_select_dblp_notnull = "SELECT * FROM citation1.venue WHERE venue_dblpname IS NOT NULL ORDER BY venue_id DESC"
try:
	cursor.execute(sql_select_dblp_notnull)
	cur_venue_id = cursor.fetchone()[0]
	cur_venue_id += 1
except:
	sys.exit("ERROR: SELECT the TABLE venue failed!")	

#cur_venue_id = 32
sleep_interval = 0; # When greater than 10, we need sleep.
while(cur_venue_id <= nb_venue):
	# sql_select_dblpname = "SELECT venue_dblpname FROM citation1.venue WHERE venue_id='%d' " %cur_venue_id
	# try:
	# 	cursor.execute(sql_select_dblpname)
	# 	cur_dblpname = cursor.fetchone()[0]
	# 	if cur_dblpname != "NULL": #Current dblpname was inserted!
	# 		cur_venue_id += 1
	# 		continue
	# except:
	# 	sys.exit("ERROR: SELECT the TABLE venue failed!")
	sql_select_paper = "SELECT paper_title FROM citation1.paper WHERE venue_venue_id='%d' ORDER BY paper_publicationYear DESC" %cur_venue_id
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
		line = paper_title.replace("Fast track article: ","").replace("Research Article: ","").replace("Guest editorial: ","").replace("Letters: ","").replace("Editorial: ","").replace("Chaos and Graphics: ","").replace("Review: ","").replace("Education: ","").replace("Computer Graphics in Spain: ","").replace("Graphics for Serious Games: ","").replace("Short Survey: ","").replace("Brief paper: ","").replace("Original Research Paper: ","").replace("Review: ","").replace("Poster abstract: ","").replace("Erratum to: ","").replace("Review: ","").replace("Guest Editorial: ","").replace("Review article: ","").replace("Editorial: ","").replace("Short Communication: ","").replace("Invited paper: ","").replace("Book review: ","").replace("Technical Section: ","").replace("Fast communication: ","").replace("Note: ","").replace("Introduction: ","")
		line = line.replace("%","%25").replace(" ", "%20").replace(",", "%2C").replace(":", "%3A").replace("?", "%3F").replace("&", "%26").replace("'","%27")
		url = "http://dblp.uni-trier.de/search?q=" + line
		flag_jump = 0
		while(True):
			try:
				response = requests.get(url, headers = headers, timeout=15)#, proxies=proxies)
				break
			except:
				print "Connection FAILED! We need have a 5 seconds break."
				flag_jump += 1
				if flag_jump > 5:
					print "This paper can't be connected! We must change the next paper."
					break
				sleep(5)
		if (flag_jump > 5):
			continue
		#print "The %d Connection successfully!" %cur_venue_id
		#http://dblp.uni-trier.de/search?q=Formal%20validation%20of%20fault%20management%20design%20solutions
		# if sleep_interval > 10:
		# 	sleep_interval = 0
		# 	print "Have a 10 seconds break."
		# 	sleep(10)
		# else :
		# 	sleep_interval += 1

		soup = BeautifulSoup(response.text)
		try:
			match =  soup.find(id='completesearch-info-matches').text #Information about whether matches a dblp record.
		except:
			print "ERROR: Match FAILED!"
			#print "Current url is :"+ url 
			continue
		if match == "no matches":
			#No matches in DBLP
			print "no matches"
			no_match += 1
			if(no_match > 5):
				print "The venue %d can't be searched in DBLP." %cur_venue_id
				break
			continue
		else :
			#match a dblp record successfully!
			#unavail = soup.find(text = "service temporarily not available")
			#if unavail:
			#	print "ERROR: service temporarily not available"
			#	sleep(3) # Sleep 3 seconds
			#	continue
			try:
				li = soup.find('li', attrs={'class':'entry article'})
				if li:
					cur_title = li.find('span', attrs={'class':'title', 'itemprop':'name'}).text
					if cur_title[-1] != '.':
						cur_title += '.'
					if cur_title.lower() != paper_title.lower():
						no_match +=1
						print "current title is : " + cur_title
						print "our taget paper title is : " + paper_title
						print "They are not the same paper, so we jump this paper."
						continue
					span = li.find('span',attrs={'itemprop':'isPartOf'})
				else:
					li = soup.find('li', attrs={'class':'entry inproceedings'})
					if li:
						cur_title = li.find('span', attrs={'class':'title', 'itemprop':'name'}).text
						if cur_title != paper_title:
							no_match +=1
							continue
						span = li.find('span',attrs={'itemprop':'isPartOf'})
					else:
						li = soup.find('li', attrs={'class':'entry informal'})
						cur_title = li.find('span', attrs={'class':'title', 'itemprop':'name'})
						if cur_title != paper_title:
							no_match +=1
							continue
						span = li.find('span',attrs={'itemprop':'isPartOf'})
			except:
				print "DBLP FAILED!"
				continue
			dblp_name = span.text
			sql_update = "UPDATE citation1.venue SET venue_dblpname='%s' WHERE venue_id='%d'" %(dblp_name, cur_venue_id)
			try:
				cursor.execute(sql_update)
				db.commit()
				print "The venue %d dblpname is update SUCCESSFULLY!" %cur_venue_id
				break;
			except:
				sys.exit("This sql sentence : "  + sql_update +"  FAILED!")

	cur_venue_id += 1

print "All venues' dblpname are inserted SUCCESSFULLY!"

