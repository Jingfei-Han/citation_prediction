#encoding:utf-8
import requests
from bs4 import BeautifulSoup
import re
import subprocess
import shlex

headers = {
	
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'CNZZDATA1256960793=1695989835-1488850966-null%7C1488850966; _free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJWIyNDlhYWMwMjVkOGU3YjUzNjUxMTYyYTZkMTA3OTAwBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMUlQd2lpWlJFWWhXRFI1YU05Mys0ZEQ4RTcwV2IyR0lwMkdHdjl0bDRaOXc9BjsARg%3D%3D--33c0bc529c83ff4888878c67e92de3c0c36ef83c; Hm_lvt_0cf76c77469e965d2957f0553e6ecf59=1492239714; Hm_lpvt_0cf76c77469e965d2957f0553e6ecf59=1492240179',
'Host':'www.xicidaili.com',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',

}
url = "http://www.xicidaili.com/wn/"

#先爬1页的代理
output = open('proxies.txt', 'w')

def PING(ip):
	#cmd = "ping -c 1 "+ ip #linux
	cmd = "ping -n 1 " + ip #windows
	args = shlex.split(cmd)
	try:
		subprocess.check_call(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return True
	except:
		return False

output_index = 1
def crawlproxies(url, output, headers):

	response = requests.get(url, headers = headers)
	assert(response.status_code == requests.codes.ok) #判断是否获取网页成功 

	soup = BeautifulSoup(response.text)

	tag_div = soup.find(name="div", attrs={"id":"body", "class":"clearfix proxies"})
	tag_table = tag_div.find(name="table", attrs={"id":"ip_list"})
	tag_tr = tag_table.find_all("tr", attrs={"class":"odd"})

	regex_ip = "((?:(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d)))\.){3}(?:25[0-5]|2[0-4]\d|((1\d{2})|([1-9]?\d))))"
	for td in tag_tr:
		tag_ip = td.find("td", text=re.compile(regex_ip))
		tag_port = td.find("td", text = re.compile("^\d+$"))

		ip = tag_ip.text.strip()
		port = tag_port.text.strip()
		string = ip + ":" + port + "\n"
		if PING(ip):
			output.write(string)
			print "%3dth SUCESS!" %output_index
		else:
			print "%3dth FALSE!" %output_index
		
		global output_index
		output_index += 1

#爬n页的代理
def crawl(page=1):
	for index in range(1,page+1):
		cur_url = url + str(index)
		crawlproxies(cur_url, output, headers)

crawl(10)
output.close()


