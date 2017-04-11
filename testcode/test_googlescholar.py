#测试谷歌学术爬虫demo
import requests
from bs4 import BeautifulSoup
from time import sleep

#主题集合，不断搜索
topic_set = [
	"Recurrent neural network",
	"Computer network",
	"Machine learning",
	"Yoshua Bengio"
]

#记录headers
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

cur_index = 1 #当前访问论文个数
succ_cnt = 0 #成功访问链接个数
fail_cnt = 0 #失败访问链接个数

while True:
	paper_title = topic_set[cur_index%4]
	line = paper_title.replace(" ", "+")
	url = "https://scholar.google.com/scholar?hl=en&q="+line+"&btnG=&as_sdt=1%2C2"
	flag_jump = 0 #记录访问失效次数，达到上限就访问失败
	
	while True:
		try:
			response = requests.get(url, headers = headers, timeout = 15)
			
			#更换Cookie，重置headers
			cookie_dic = requests.utils.dict_from_cookiejar(response.cookies) #为cookie属性与值的字典
			cookie = "NID=" + cookie_dic['NID'] + "; GSP=" + cookie_dic['GSP']
			headers['Cookie'] = cookie
			print "CURRENT COOKIE: " + cookie 
			break
		except:
			print "Connection Failed! 5 seconds break."
			flag_jump += 1
			if flag_jump > 5:
				print "This url FAILED! we must be change the next url."
				break
			sleep(5)

		if flag_jump > 5:
			fail_cnt += 1
			print "Current statistic: SUCESSED: %5d, FAILED: %5d" %(succ_cnt, fail_cnt)
			continue
		
		soup = BeautifulSoup(response.text)
		succ_cnt += 1
		print "This url SUCCESSED!"
		print "Current statistic: SUCESSED: %5d, FAILED: %5d" %(succ_cnt, fail_cnt)

		cur_index += 1
