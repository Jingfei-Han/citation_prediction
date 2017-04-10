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

db = mysql.connector.connect(host="localhost",user="root",passwd="",db="paper",charset="utf8" )
cursor = db.cursor()

sql1="select * from papernew.paper LIMIT 0,500 "
cursor.execute(sql1)
results1 = cursor.fetchall()


for row in results1:
    papername=row[1]
    print papername
    papername=papername.replace(" ", "+")
    link="https://google.gg-g.org/scholar?q="+papername+"&btnG=&hl=zh-CN&as_sdt=0%2C5"
    headers = {
        'Host': 'google.gg-g.org',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Referer': 'https://google.gg-g.org/',
        'Cookie': 'NID=99=dzMcu-mA4Xd8zmQ0YNmPqoqE-OatqdZ6MZrB-HUNKJxznZqoGJa-ZkK5MGTyikz3w2aAgmM8-lD5UthI6lBi69AnTUYqjeKyML6nDC3KmV46i6ty3vEqQu5yH0zYwYHrgEC5CB-67lmP566BlA; UM_distinctid=15ae5ac0d5a4b-0f36f9cfce36cc-5e4f2b18-100200-15ae5ac0d5b1a6; GSP=NW=1:LM=1490003945:S=DpH3L7IIKtO5LTDP; CNZZDATA1257357503=1130527629-1489906855-null%7C1490001144',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0', }
    Response = requests.get(link, headers=headers, proxies=None, timeout=60)
    Soup = BeautifulSoup(Response.text, "html.parser")
    for src in Soup.find_all("div", {"class": "gs_fl"}):
        texts=[]
        texts=src.get_text().split(" ")
        if (texts[0]!="[PDF]"):
            print texts[0]