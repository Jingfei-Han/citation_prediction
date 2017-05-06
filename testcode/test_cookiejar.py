#encoding:utf-8
import requests
"""
#xichuan代理
cookie = 'NID=102=hshiZszo9xpaB2qRfKbePWOtYIznBELy7bipzmm1M9iTEwqqqBQyWHoswI5hkVecauhlGGlFpdX1XPdmPFE5vcY5ziwmbKeQ3e0DbPLzf5MGYNvJ1t7xD1SaQmlWnpmN; GSP=NW=1:LM=1494048602:S=dpGDLLJdWPVVc5Nf'
#cookie = 'NID=102=L_uc26dsyz4fa875NA12TKfXwaF0EYPCiV1fgsKXmV0dESpB-4TSRmk3jkTyEp255IQL9SgPwv69y1NmTZHCKkpfiL3WG-sv-X1P7lbM4F1ak3nGDLxBzYgiom3WFDV6; GSP=LM=1494034043:NW=1:S=9dsbqjAGHJg3qdbr'
headers = {
	'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, sdch, br',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
	'Connection':'keep-alive',
	'Host':'www.xichuan.pub',
	'Referer':'https://www.xichuan.pub/scholar',
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
	#'Cache-Control':'max-age=0',
	'Cookie': cookie,
	#'Upgrade-Insecure-Requests':'1',
}
url = "https://www.xichuan.pub/scholar"
"""
#e.ggkai.men
headers = {
	'accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate, sdch, br',
	'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
	'Connection':'keep-alive',
	'Host':'e.ggkai.men',
	'Referer':'https://e.ggkai.men/extdomains/scholar.google.com/schhp?hl=en&num=20&as_sdt=0',
	'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
	#'Cache-Control':'max-age=0',
	#'Cookie': cookie,
	#'Upgrade-Insecure-Requests':'1',
}
url = "https://e.ggkai.men/extdomains/scholar.google.com/scholar?hl=en&q=recurrent+neural+network&as_sdt=1%2C5&as_sdtp=&oq=recurrent"

#url = "https://www.baidu.com"
res = requests.get(url, headers=headers)
print res.status_code
print res.cookies