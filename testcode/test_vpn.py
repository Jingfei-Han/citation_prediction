#encoding:utf-8
import requests


#scholar.google.com.hk
headers = {
	'Accept':'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
	'Accept-Encoding':'gzip, deflate, sdch',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
	'Connection':'keep-alive',
	'Host':'ga.shhr.online',
	'Referer':'https://ga.shhr.online/extdomains/scholar.google.com',
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
	'Cookie' : 'NID=103=gbCPErM0LV-e_Fmt62GDBERDlJe3qkXfNfthwvXX1lNAtGYq5hxvNWQr2RPKfIKTsbmAHESUGVhbqfv1JK44y8xwxHN52-5t6YZmsf7aqd8t-pd_DQkvy2i7tqNkzsIY; GSP=LM=1494311848:S=SYYUsD7oVa3HJKbG'
}
url = "https://ga.shhr.online/extdomains/scholar.google.com/scholar?q=Load-Balancing+Multipath+Switching+System+with+Flow+Slice+&btnG=&hl=en&as_sdt=0%2C5&as_ylo=2012&as_yhi=2012"

res = requests.get(url, headers=headers)
print res.status_code
print res.cookies