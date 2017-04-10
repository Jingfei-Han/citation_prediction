import MySQLdb
import MySQLdb.cursors
import sys
import pandas as pd
import numpy as np


db = MySQLdb.connect(host='localhost', user='root', passwd='hanjingfei007', db='citation1', charset='utf8')
cursor = db.cursor()

journal_index = 3000 #journal's CORE_id > 3000

dic = {
	'CORE_id' : '0',
	'CORE_name' : '0',
	'CORE_type' : 'conference',
	'CORE_classification' : ''
}

f = pd.read_csv('CORE_journals.csv')
data = f.values

m = data.shape[0]
i = 0
while i<m:
	# In data, if an element is empty, its type is float
	if str(data[i][2]) == 'nan':
		data[i][2] = ''
	dic['CORE_id'] = int(data[i][0]) + journal_index
	dic['CORE_name'] = data[i][1].strip().replace('\'', '\\\'')
	dic['CORE_type'] = 'journal'
	dic['CORE_classification'] = data[i][2].strip().replace('\'', '\\\'')

	sql = "INSERT INTO citation1.CORE(CORE_id, CORE_name, CORE_type, CORE_classification) \
			VALUES('%d', '%s', '%s', '%s')" %(dic['CORE_id'], dic['CORE_name'], dic['CORE_type'], dic['CORE_classification'])
	try:
		cursor.execute(sql)
		db.commit()
		if i%10 == 0:
			print "The %dth is INSERTED successfuly!" %(i+1)
	except:
		sys.exit("ERROR when %dth is INSERTED!" %(i+1))

	i += 1


print "%d journals are INSERTED SUCCESSFULLY!" %i

sql2 = "INSERT INTO citation1.CORE(CORE_id, CORE_name) VALUES('9999', 'NOCORE')"
try:
	cursor.execute(sql2)
	db.commit()
except:
	sys.exit("ERROR when NOCORE is INSERTED!")

