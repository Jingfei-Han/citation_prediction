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
