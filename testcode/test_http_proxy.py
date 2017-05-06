#encoding:utf-8
import requests

headers = {
	'Accept':'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
	'Accept-Encoding':'gzip, deflate, sdch',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
	'Connection':'keep-alive',
	'Host':'dblp.uni-trier.de',
	'Referer':'http://dblp.uni-trier.de/db/',
	'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
}
url = "http://dblp.uni-trier.de/db/"
proxies = {"http":"http://116.199.115.78:80",}

#url = "http://www.baidu.com"
res = requests.get(url, proxies = proxies)
print res.status_code
print res.cookies