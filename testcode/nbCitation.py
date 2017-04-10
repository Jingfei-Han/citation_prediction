# encoding: utf-8
#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import re
from collections import deque
from random import randint
from time import sleep
import mysql.connector
import urllib
import urllib.request
import json
import sys
from time import strftime
# from para0802soir import *

cookie_list = [
"NID=71=dny0UkynXb5UOtiGE-KRlkkLRlAvJUc2RaMUyPBCUEvBmyXmRki7EAQcy7rT2oSJI6emyqnl1OFEA7STa85VU0Ku3DWOGVEm1QNxHL3JxZ6hmmkfDe6mpBpIioayY4_5; GOOGLE_ABUSE_EXEMPTION=ID=d1db736f083cd4c2:TM=1441701531:C=c:IP=45.74.41.97-:S=APGng0sP5mXbLTVhDth0XGaR8md5pTnOHg; GSP=A=qbAwEQ:CPTS=1441701536:LM=1441701536:S=LN9eRhP0PWm-tZSW",
                ]

cookie_index = -1


db = mysql.connector.connect(host="localhost",user="root",db="citation1",charset="utf8" )

cursor = db.cursor()

nbRequestTotal = 0
nbRequestError = 0 
nbRequestEscaped = 0
nbRequestWorks = 0
beginTime = strftime("%Y-%m-%d %H:%M:%S")
print("Begin Time: " + beginTime)
finishTime = ""
num =1
count = 1
var = 0
linkCitation = ''
dormir = 1
notFound = 0
year = sys.argv[1]
ccfClass = sys.argv[2]
category = sys.argv[3]
venueType = sys.argv[4]

paperIdBegin = sys.argv[5]
paperIdEnd = sys.argv[6]

sql1 =  "SELECT paper_title, paper_publicationYear, paper_id FROM citation1.paper \
         WHERE paper_publicationYear = '%d' AND paper_venue_id in(SELECT venue_id FROM citation1.venue WHERE venue_CCF_classification like '%s' and venue_computerCategory_id = '%d' and venue_type like '%s') \
         AND paper_nbCitation is NULL AND paper_venue_name like 'Bioinformatics' AND paper_id > '%d' AND paper_id <= '%d' ORDER BY paper_id ASC" %(int(year),str(ccfClass),int(category),str(venueType),int(paperIdBegin),int(paperIdEnd))
cursor.execute(sql1)
results1 = cursor.fetchall()

for row0 in results1:
    var = var + 1

for row1 in results1:
    print('**********************'+'  num: ' + str(num))
    print('paper left: ' + str(var))
    print ("nb cookie left: " + str(len(cookie_list)))
    row1Title = row1[0].decode("utf-8")
    row1Year = row1[1].decode("utf-8")
    row1PaperId = row1[2]
    print ('PaperId ' + str(row1PaperId))

    cookie_index+=1
    cookie_index%=len(cookie_list)
    cookie = cookie_list[cookie_index]
    headers = { 
                    'Host':'scholar.google.fr',
                    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36',
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language':'zh-CN,en-US;q=0.8,zh;q=0.5,en;q=0.3',
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Referer':'https://www.google.fr',
                    'Cookie': cookie,
                    'Connection':'keep-alive',
                    'Cache-Control':'max-age=0',}


    ipHttps = "https://222.124.219.215:3128"

    proxies1 = { 
    "https": ipHttps,
    }

    urlTitle = "https://scholar.google.fr/scholar?as_q=&as_epq="  +  str(row1Title.replace("+","%2B").replace("Fast track article: ","").replace("Research Article: ","").replace("Guest editorial: ","").replace("Letters: ","").replace("Editorial: ","").replace("Chaos and Graphics: ","").replace("Review: ","").replace("Education: ","").replace("Computer Graphics in Spain: ","").replace("Graphics for Serious Games: ","").replace("Short Survey: ","").replace("Brief paper: ","").replace("Original Research Paper: ","").replace("Review: ","").replace("Poster abstract: ","").replace("Erratum to: ","").replace("Review: ","").replace("Guest Editorial: ","").replace("Review article: ","").replace("Editorial: ","").replace("Short Communication: ","").replace("Invited paper: ","").replace("Book review: ","").replace("Technical Section: ","").replace("Fast communication: ","").replace("Note: ","").replace("Introduction: ","").replace(":","%3A").replace("'","%27").replace("&","%26").replace("(","%28").replace(")","%29").replace("/","%2F").replace(" ","+")) + '+' + '&as_oq=&as_eq=&as_occt=title&as_sauthors=&as_publication=Bioinformatics&as_ylo=2009&as_yhi=2009&btnG=&hl=en&num=20&as_sdt=0%2C5'
    # print(urlTitle)
    while True:
        if(len(cookie_list)==0):
            while True:
                    timeWait = randint(2000,4000)
                    print ("timeWait: " + str(timeWait))
                    sleep(timeWait)
        try:
            headers = { 
                    'Host':'scholar.google.fr',
                    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36',
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language':'zh-CN,en-US;q=0.8,zh;q=0.5,en;q=0.3',
                    'Accept-Encoding':'gzip, deflate, sdch',
                    'Referer':'https://www.google.fr',
                    'Cookie': cookie,
                    'Connection':'keep-alive',
                    'Cache-Control':'max-age=0',}
            print("trying cookie: " + str(cookie))
            nbRequestTotal = nbRequestTotal + 1
            response = requests.get(urlTitle,headers=headers,proxies=None,timeout=45)
            soup = BeautifulSoup(response.text)
            try:
                soup.find("a",text=re.compile("Try your query on the entire web")).get_text()
                print("ip success")
                print("NOT FOUND IN SCHLOAR")
                nbRequestWorks = nbRequestWorks + 1
                notFound = 1
                break
            except:
                try:
                    linkInfo = soup.find("div",{ "class" : "gs_a"}).get_text()
                    print("ip success")
                    nbRequestWorks = nbRequestWorks + 1
                    print("FOUND IN SCHLOAR")
                    break
                except:
                    print("ip escaped")
                    cookie_list.remove(cookie)
                    if(len(cookie_list)==0):
                        while True:
                                timeWait = randint(2000,4000)
                                print ("timeWait: " + str(timeWait))
                                sleep(timeWait)
                    cookie_index%=len(cookie_list)
                    cookie=cookie_list[cookie_index]
                    nbRequestEscaped = nbRequestEscaped + 1
                    nbRequestEscaped = nbRequestEscaped + 1
        except:
            print("connect fail")
            nbRequestError = nbRequestError + 1
    try:
        link = soup.find("a", text=re.compile("Cited"))
        nbCitation = int(link.get_text().strip('Cited by'))
        arct = soup.find("h3")
        # print (arct)
        try:
            typespan = arct.find("span",{ "class" : "gs_ct1"}).get_text()
            arct.span.extract()
            targetPaperTitle = arct.get_text()[1:]
        except:
            typespan = 'NormalType'
            targetPaperTitle = arct.find("a").get_text()
            # print("targetPaperTitle: " + str(targetPaperTitle))
        try:
            sql2 = "UPDATE citation1.paper SET paper_nbCitation = '%d', paper_citationLink = '%s', paper_CitationFoundName = '%s' WHERE paper_id = '%d'"  % (int(link.get_text().strip('Cited by')),str("http://scholar.google.com"+ str(link.get('href'))),str(targetPaperTitle.replace("'","''")),int(row1PaperId))
        except:
            sql2 = "UPDATE citation1.paper SET paper_nbCitation = '%d', paper_citationLink = '%s' WHERE paper_id = '%d'"  % (int(link.get_text().strip('Cited by')),str("http://scholar.google.com"+ str(link.get('href'))),int(row1PaperId))
    except:
        if(notFound == 1):
            nbCitation = -1
        else:
            print("BUT NO CITATION")
            nbCitation = 0
        sql2 = "UPDATE citation1.paper SET paper_nbCitation = '%d' WHERE paper_id = '%d'"  % (int(nbCitation),int(row1PaperId))
    
    print (nbCitation)
    cursor.execute(sql2)
    db.commit()
    # dormir = randint(1,2)
    # print ('sleep .....' + str(dormir))
    # sleep(dormir)
    # print ('wake .....')
    num = num + 1
    var = var - 1
    targetPaperTitle = ''
    notFound = 0
    print ("nbRequestTotal: " + str(nbRequestTotal))
    print("nbRequestWorks: " + str(nbRequestWorks))
    print("nbRequestError: " + str(nbRequestError))
    print("nbRequestEscaped: " + str(nbRequestEscaped))
    if(nbRequestTotal != 0):
        print("Works rate: " + str((nbRequestWorks/nbRequestTotal)*100) +"%")
finishTime = strftime("%Y-%m-%d %H:%M:%S")
print ("Between " + str(paperIdBegin) + " AND " + str(paperIdEnd) + " Finished")
print("Begin Time: " + beginTime)
print("Finish Time:" + finishTime)





















