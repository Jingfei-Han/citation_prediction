#encoding:utf-8
import os, time, sched
import multiprocessing

schedule = sched.scheduler(time.time, time.sleep)

cmd = '''kill -9 `ps -aux|grep 'python Crawl_paper.py'|awk '{print $2}'`
'''
cmd2 = 'python Crawl_paper.py '


def start_test(c2):
	os.system(c2)
	#print time.ctime(),'test running'

def recycle_eval(c1, c2, inc):
	schedule.enter(inc, 0, recycle_eval, (c1, c2, inc))
	os.system(c1)
	
	#print time.ctime(),'test killed'
	p = multiprocessing.Process(target=start_test, args=(c2+'C Conference',))
	p.start()
	p1 = multiprocessing.Process(target=start_test, args=(c2+'C Journal',))
	p1.start()
	
	
	
	


if __name__ == '__main__':
	inc = 20   #多久重启一次
	p = multiprocessing.Process(target=start_test, args=(cmd2+'C Conference',))
	p.start()
	p1 = multiprocessing.Process(target=start_test, args=(cmd2+'C Journal',))
	p1.start()
	
	schedule.enter(inc, 0, recycle_eval, (cmd, cmd2, inc))
	schedule.run()
