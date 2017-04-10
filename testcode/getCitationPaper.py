# encoding: utf-8
#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import re
from collections import deque
from random import randint
from time import sleep
import mysql.connector
import json
import sys
import os
from time import strftime
# from paraTest import *

cookie_list = [
"NID=71=zUva9PVEC4n_0cmimy_4Vdw880wZb1Px1H0tcUMvNSToVtjHTqPguZjThlQo1RqTOK3tfQB5Fnspne6iQUb1JORjgQ3t11oswXVYZ8RucBfP_4szDHcPfTCxyMhRg3eI; GSP=A=-a1ZFg:CPTS=1442219282:LM=1442219282:S=iRrz4tR5qCLc7eus",
]



cookie_listFail = []
cookie_index = -1

db = mysql.connector.connect(host="localhost",user="root",passwd="hanjingfei007",db="citation1",charset="utf8" )
cursor = db.cursor()

year = sys.argv[1]
ccfClass = sys.argv[2]
category = sys.argv[3]
venueType = sys.argv[4]
nbciteBegin = sys.argv[5]
nbciteEnd = sys.argv[6]

timeWait = 0
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

queueLink = deque()
queueArticle = deque()
fileW = open('paper_title_wrong.txt', 'a')
sql1 = "SELECT paper_citationLink, paper_nbCitation, paper_id FROM citation1.paper \
         WHERE paper_publicationYear = '%d' AND paper_venue_id in(SELECT venue_id FROM citation1.venue WHERE venue_CCF_classification like '%s' AND venue_computerCategory_id = '%d' AND venue_type like '%s')\
         AND paper_citationLink IS NOT NULL AND paper_nbCitation>'%d' AND paper_nbCitation <= '%d' ORDER BY paper_nbCitation ASC" %(int(year),str(ccfClass),int(category),str(venueType),int(nbciteBegin),int(nbciteEnd))
cursor.execute(sql1)
results1 = cursor.fetchall()

for row0 in results1:
    var = var + 1

for row1 in results1:
        queueLink = deque()
        queueArticle = deque()
        print('**********************'+'  num: ' + str(num) + '**********************')
        print('paper left: ' + str(var))
        print ("nb cookie left: " + str(len(cookie_list)))
        row1CitationLink = row1[0].decode("utf-8")
        row1NbCitation = row1[1]
        row1PaperId = row1[2]

        nbCitation = row1NbCitation
        print ('PaperId: ' + str(row1PaperId))
        print ('nbCitation: ' + str(nbCitation))

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

        # ipHttps = "https://222.124.219.215:3128"

        # proxies1 = { 
        # "https": ipHttps,
        # }

        sql0 = "SELECT COUNT(*) FROM citation1.targetpaper \
        WHERE targetPaper_CCFPaper_id = '%d'" % (int(row1PaperId))
        cursor.execute(sql0)
        results0 = cursor.fetchone()
        nbCiteFound = results0[0]
        print("nbCiteFound Begin: " + str(nbCiteFound))
        if(nbCitation>nbCiteFound):
            #访问已经下载好的引用链接
            print ('ADD CITATION LINK: ' + str(row1CitationLink))
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
                            subResponse = requests.get(str(row1CitationLink).replace("http","https").replace("httpss","https").replace(".fr",".fr").replace(".com",".fr")+'&num=20',headers=headers,proxies=None,timeout=60)
                            subSoup = BeautifulSoup(subResponse.text)
                            try:
                                    subSoup.find("div",{ "class" : "gs_a"}).get_text()
                                    # print ("ip success: " + str(ipHttps))
                                    print ("cookie success")
                                    nbRequestWorks = nbRequestWorks + 1
                                    break
                            except:
                                    print("Escaped by GOOGLE")
                                    # cookie_listFail.append(cookie_index)
                                    # print(subSoup.prettify())
                                    # while True:
                                    #     timeWait = randint(2000,4000)
                                    #     print ("timeWait: " + str(timeWait))
                                    #     sleep(timeWait)
                                    cookie_list.remove(cookie)
                                    if(len(cookie_list)==0):
                                        while True:
                                                timeWait = randint(2000,4000)
                                                print ("timeWait: " + str(timeWait))
                                                sleep(timeWait)
                                    # cookie_index+=1
                                    cookie_index%=len(cookie_list)
                                    cookie=cookie_list[cookie_index]
                                    nbRequestEscaped = nbRequestEscaped + 1
                    except:
                            print ("Connect error")
                            nbRequestError = nbRequestError + 1

            #如果数据库里还没有这篇文章的引文，那么先爬前20篇：
            if(nbCiteFound == 0):
                    #加入本页所有的引文信息
                    for src in subSoup.find_all("div",{ "class" : "gs_a"}):
                            queueArticle.append(src.get_text())
                    #加入本页文章的引文，以及加入该信息到数据库
                    for arct in subSoup.find_all("h3"):
                            try:
                                    targetPaperLink = arct.find("a").get('href')
                            except:
                                    targetPaperLink = 'noLink'
                            try:
                                    typespan = arct.find("span",{ "class" : "gs_ct1"}).get_text()
                                    arct.span.extract()
                                    targetPaperTitle = arct.get_text()[1:]

                            except:
                                    typespan = 'NormalType'
                                    targetPaperTitle = arct.find("a").get_text()

                            print ('targetPaperTitle: ' + targetPaperTitle)
                            targetPaperInfo = queueArticle.popleft()
                            try:
                                    nbCiteFound = nbCiteFound + 1
                                    sql3 = "INSERT INTO citation1.targetPaper(targetPaper_CCFPaper_id,targetPaper_scholarTitle,targetPaper_scholarInfo,targetPaper_scholarLink, targetPaper_scholarType) \
                                    VALUES ('%d','%s','%s','%s','%s') " % (int(row1PaperId),str(targetPaperTitle.replace("'","''")),str(targetPaperInfo.replace("'","''")),str(targetPaperLink.replace("'","''")),str(typespan))
                                    cursor.execute(sql3)
                                    db.commit()
                            except:
                                    fileW.write(str(row1PaperId)+'\n') 
                                    fileW.write(str(targetPaperTitle)+'\n'+'\n') 
                                    targetPaperTitle = ''

            if(nbCitation>20 and nbCitation<=200):
                    for page in subSoup.find_all("a",{ "class" : "gs_nma" }):
                            beginPageIndex = (nbCiteFound - 1) // 20 + 1
                            if (count >= beginPageIndex):
                                    linkCitation = "http://scholar.google.com"+str(page['href'])
                                    queueLink.append(linkCitation)
                                    print ('ADD CITATION LINK: ' + linkCitation)   
                            count = count + 1
                    count = 1

            if(nbCitation > 200):
                    if(nbCitation > 1000):
                            nbCitation = 1000
                    nbCachePage = ( (nbCitation -1 ) // 20 ) - 10 + 1
                    if(nbCiteFound <= 180):
                            beginPageIndex = (nbCiteFound - 1) // 20 + 1
                            for page in subSoup.find_all("a",{ "class" : "gs_nma" }):
                                    if(count >= beginPageIndex):
                                            linkCitation = "http://scholar.google.com"+str(page['href'])
                                            queueLink.append(linkCitation)
                                            print ('ADD CITATION LINK: ' + linkCitation)
                                    count = count + 1
                            count = 1

                            while (count <= nbCachePage):
                                    haha = ''.join(("start=",str(180 + 20*count)))
                                    if (count >= 1):               
                                            linkCitationN = linkCitation.replace("start=180",haha)
                                            print ('ADD CITATION LINK: ' + linkCitationN)
                                            queueLink.append(linkCitationN)
                                    count = count + 1
                            count = 1
                    if(nbCiteFound > 180 and nbCiteFound < 200):
                            nbCiteFound = 200
                    if(nbCiteFound >= 200):
                            beginPageIndex = (nbCiteFound - 1 - 200) // 20 + 2
                            for page in subSoup.find_all("a",{ "class" : "gs_nma" }):
                                    if(count >= 1):
                                            linkCitation = "http://scholar.google.com"+str(page['href'])
                                    count = count + 1
                            count = 1

                            while (count <= nbCachePage):
                                    haha = ''.join(("start=",str(180 + 20*count)))
                                    if (count >= beginPageIndex):               
                                            linkCitationN = linkCitation.replace("start=180",haha)
                                            print ('ADD CITATION LINK: ' + linkCitationN)
                                            queueLink.append(linkCitationN)
                                    count = count + 1
                            count = 1

            while queueLink:
                    print('paper left: ' + str(var))
                    print ("nb cookie left: " + str(len(cookie_list)))
                    if(len(cookie_list)==0):
                        while True:
                            timeWait = randint(2000,4000)
                            print ("timeWait: " + str(timeWait))
                            sleep(timeWait)
                    cookie_index+=1
                    cookie_index%=len(cookie_list)
                    cookie=cookie_list[cookie_index]

                    linkTemp = queueLink.popleft()
                    print ('\n'+str(linkTemp).replace("http","https").replace("httpss","https").replace(".fr",".fr").replace(".com",".fr")+'&num=20')
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
                                    subResponse = requests.get(str(linkTemp).replace("http","https").replace("httpss","https").replace(".fr",".fr").replace(".com",".fr")+'&num=20',headers=headers,proxies=None,timeout=60)                                        
                                    subSoup = BeautifulSoup(subResponse.text)
                                    try:
                                            subSoup.find("div",{ "class" : "gs_a"}).get_text()
                                            # print ("cookie success: " + str(ipHttps))
                                            print ("cookie success")
                                            nbRequestWorks = nbRequestWorks + 1
                                            break
                                    except:
                                            print("Escaped by GOOGLE")
                                            # print(subSoup.prettify())
                                            # while True:
                                            #     timeWait = randint(2000,4000)
                                            #     print ("timeWait: " + str(timeWait))
                                            #     sleep(timeWait)
                                            cookie_list.remove(cookie)
                                            if(len(cookie_list)==0):
                                                while True:
                                                        timeWait = randint(2000,4000)
                                                        print ("timeWait: " + str(timeWait))
                                                        sleep(timeWait)
                                            # cookie_index+=1
                                            cookie_index%=len(cookie_list)
                                            cookie=cookie_list[cookie_index]
                                            nbRequestEscaped = nbRequestEscaped + 1
                            except:
                                    print ("Connect error")
                                    nbRequestError = nbRequestError + 1

                    for src in subSoup.find_all("div",{ "class" : "gs_a"}):
                            queueArticle.append(src.get_text())

                    for arct in subSoup.find_all("h3"):
                            try:
                                    targetPaperLink = arct.find("a").get('href')
                            except:
                                    targetPaperLink = 'noLink'
                            try:
                                    typespan = arct.find("span",{ "class" : "gs_ct1"}).get_text()
                                    arct.span.extract()
                                    targetPaperTitle = arct.get_text()[1:]
                            except:
                                    typespan = 'NormalType'
                                    targetPaperTitle = arct.find("a").get_text()

                            print ('targetPaperTitle: ' + targetPaperTitle)
                            targetPaperInfo = queueArticle.popleft()
                            try:
                                    sql3 = "INSERT INTO citation1.targetPaper(targetPaper_CCFPaper_id,targetPaper_scholarTitle,targetPaper_scholarInfo,targetPaper_scholarLink, targetPaper_scholarType) \
                                    VALUES ('%d','%s','%s','%s','%s') " % (int(row1PaperId),str(targetPaperTitle.replace("'","''")),str(targetPaperInfo.replace("'","''")),str(targetPaperLink.replace("'","''")),str(typespan))
                                    cursor.execute(sql3)
                                    db.commit()
                            except:
                                    fileW.write(str(row1PaperId)+'\n') 
                                    fileW.write(str(targetPaperTitle)+'\n'+'\n') 
                            targetPaperTitle = ''
        cursor.execute(sql0)
        results0 = cursor.fetchone()
        nbCiteFound = results0[0]
        if((nbCiteFound>=nbCitation) or (nbCitation-nbCiteFound)<20):
            print("This paper's citation papers have been finshed, DELETE citationLink")
            sql4 = "UPDATE citation1.paper SET paper_citationLink = NULL WHERE paper_id = '%d'" %(int(row1PaperId))
            cursor.execute(sql4)
            db.commit()
        num = num + 1
        var = var - 1
        print ("nbRequestTotal: " + str(nbRequestTotal))
        print("nbRequestWorks: " + str(nbRequestWorks))
        print("nbRequestError: " + str(nbRequestError))
        print("nbRequestEscaped: " + str(nbRequestEscaped))
        if(nbRequestTotal != 0):
            print("Works rate: " + str((nbRequestWorks/nbRequestTotal)*100) +"%")
finishTime = strftime("%Y-%m-%d %H:%M:%S")

print ("Between " + str(nbciteBegin) + " AND " + str(nbciteEnd) + " Finished")
print("Begin Time: " + beginTime)
print("Finish Time:" + finishTime)






