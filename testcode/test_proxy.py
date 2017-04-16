import requests
from bs4 import BeautifulSoup

headers_xici = {
	
'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Encoding':'gzip, deflate, sdch',
'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
'Cache-Control':'max-age=0',
'Connection':'keep-alive',
'Cookie':'CNZZDATA1256960793=1695989835-1488850966-null%7C1488850966; _free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJWIyNDlhYWMwMjVkOGU3YjUzNjUxMTYyYTZkMTA3OTAwBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMUlQd2lpWlJFWWhXRFI1YU05Mys0ZEQ4RTcwV2IyR0lwMkdHdjl0bDRaOXc9BjsARg%3D%3D--33c0bc529c83ff4888878c67e92de3c0c36ef83c; Hm_lvt_0cf76c77469e965d2957f0553e6ecf59=1492239714; Hm_lpvt_0cf76c77469e965d2957f0553e6ecf59=1492240179',
'Host':'www.xicidaili.com',
'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',

}
url1 = "http://www.xicidaili.com/wn/"

headers_baike = {
	'Accept':'image/webp,image/*,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, sdch',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
	'Connection':'keep-alive',
	'Cookie':'BAIDUID=D116B9047C1FFCCE2C8B83D0D8700049:FG=1; PSTM=1492342546; BIDUPSID=BA896EF5860A3BFD7EF3A0383D3EBC21; PSINO=1; H_PS_PSSID=22584_1440_21086_22073; BDORZ=FFFB88E999055A3F8A630C64834BD6D0',
	'Host':'gsp0.baidu.com',
	'Referer':'https://baike.baidu.com/',
	'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
}
url2 = "https://baike.baidu.com/"

proxies = {"http":"http://119.5.1.26:808", "https" : "https://60.183.218.131:808",}

#res11 = requests.get(url1, headers = headers_xici)
#res12 = requests.get(url1, headers = headers_xici, proxies = proxies)

res21 = requests.get(url2, headers = headers_baike)
res22 = requests.get(url2, headers = headers_baike, proxies = proxies)
