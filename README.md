This project is applied for data crawler from google scholar. And the next time we will predict the number of paper's citation.

Fllowing is my work everytime.

----------------------------------2017.4.10------------------------------
使用谷歌学术镜像网站
https://a.ggkai.men/extdomains/scholar.google.com/
设置内容为英文显示，每次显示20行

给出两篇论文的url格式：
1: Blowing in the wind: unanchored patient information work during cancer care

url1: https://a.ggkai.men/extdomains/scholar.google.com/scholar?hl=en&q=Blowing+in+the+wind%3A+unanchored+patient+information+work+during+cancer+care&btnG=&as_sdt=1%2C5&as_sdtp= 

2: I don't mind being logged, but want to remain in control: a field study of mobile activity and context logging     
url2: https://a.ggkai.men/extdomains/scholar.google.com/scholar?hl=en&q=I+don%27t+mind+being+logged%2C+but+want+to+remain+in+control%3A+a+field+study+of+mobile+activity+and+context+logging&btnG=&as_sdt=1%2C5&as_sdtp=

可以发现假设论文名字为PAPER NAME, url格式为：
https://a.ggkai.men/extdomains/scholar.google.com/scholar?hl=en&q=PAPER+NAME&btnG=&as_sdt=1%2C5&as_sdtp=

一定会存在一些论文在google学术里面无法找到，因此需要抓住关键信息，判断是否可以在google学术中搜索到。
使用requests, BeautifulSoup进行测试，如下：
response = requests.get(url,headers=headers)
soup = BeautifulSoup(response.text)

linkinfo = soup.find("div", {"class":"gs_a"}).get_text()
可以得到linkinfo是google学术条目的作者信息那一行，我们可以使用作者信息判断该论文是否可以在谷歌学术中找到。

问题：作者名字存在法语或其他特殊字符
解决：目前不需要该作者信息

-----------------------------------2017.4.11---------------------------------
写一个小demo测试爬虫是否正确
镜像网站不稳定，因此使用vpn访问https://scholar.google.com
记录headers:

cookie = 'NID=101=SZYmK1bDCNI9YVEM-lBxM975ArpgyelHkwNMiiCJVjoY4sbhBGUWJ-zzrlo2_r1-8LeeeavR1hn8UxP2MuAM92L-uWOzdhExx-OIZZhuVlAGDS6P7XpR15PzPlcPSErq; GSP=IN=7e6cc990821af63:LD=en:NR=20:LM=1491915063:S=OmZJEGX4GZgsoDj5'
headers = {
	'Host': 'scholar.google.com',
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, sdch, br',
	'Accept-Language':'zh-CN,en-US;q=0.8,zh;q=0.5,en;q=0.3',
	'Cookie': cookie,
	'Referer':'https://www.google.com',
	'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
	'Cache-Control':'max-age=0',
}


问题：google学术使用requests.utils.dict_from_cookiejar(response.cookies)没有cookie返回。
待解决。

---------------------------------2017.04.13------------------------------------
首先测试两次无headers爬取google的cookie分别是什么？
第一次访问：
https://scholar.google.com/scholar?hl=en&q=Yoshua+Bengio&as_sdt=1%2C5&as_sdtp=&oq=
最终cookie为：
'GSP': 'LM=1492085690:S=MT2DJ2tBDnQA2lmr'
'NID': '101=fSdLNDYt8Adg6J2jqn2zV1FLD1VtFzPPA1tZM52d7DWDhMxo8M43HgTBZ6Uw-54Hn5el6rJmHrJPjHbCdzBo1B2PpDGHoB2zLaZ3uOrz7TvoCt8EY_rQGxgK6t9xNtsH'

第二次访问：
https://scholar.google.com/scholar?q=computer+network+security&hl=en&as_sdt=0%2C5&oq=
最终cookie为：
'GSP': 'LM=1492085859:S=R3n1bWo54jcZMaNf',
'NID': '101=GascO37p3VoBYkwSB43S9c-Vuoo2Q4MoMCGFeW5E8OdG3Fmxh1BYhvyGeF2a37om1B-DMhhRmVSrWq_AyF6vmcVSGjz9Av0SACHAVsIU4b1DQucOUXaxTPzl8aDpzyUw'