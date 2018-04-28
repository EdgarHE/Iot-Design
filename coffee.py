import time
import sys
import socket
import thread

temp = 0
coffeeStatus = 0 #-1:question 0:nothing 1:hot 2:cold


def client_thread(HOST, PORT):
	global coffeeStatus
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	s.bind((HOST, PORT))

	#print('Bound UDP on %d...'%PORT)

	while True:                                          
		data, addr = s.recvfrom(1024)
		#print data
		
		length = len(data.split(';'))-1
		for i in range(0, length):
			if data.split(';')[i].split(':')[0] == 'coffeeStatus':
				coffeeStatus = int(data.split(';')[i].split(':')[1])


		#print 'coffeeStatus %d'%coffeeStatus

def cmd_coffee(x): # x=1 / 2
	thr = time.localtime(time.time()).tm_hour 
	tmin = time.localtime(time.time()).tm_min
	tsec = time.localtime(time.time()).tm_sec
	
	if thr < 10:
		timehr = '0' + str(thr)
	else:
		timehr = str(thr)
	if tmin < 10:
		timemin = '0' + str(tmin)
	else:
		timemin = str(tmin)
	if tsec < 10:
		timesec = '0' + str(tsec)
	else:
		timesec = str(tsec)
	
	if x == -1:
		sys.stdout.write("\r%s:%s:%s Do you want a cup of coffee?"%(timehr,timemin,timesec))
		sys.stdout.flush()
	elif x==0:
		sys.stdout.write("\r%s:%s:%s Waiting for command...      "%(timehr,timemin,timesec))
		sys.stdout.flush()
	elif x==1:
		print '' 
		print "%s:%s:%s Preparing coffee..."%(timehr,timemin,timesec)
		print ''
		print ''
		print "             *  *  *"
		time.sleep(0.1)
		print "             *  *  *"
		time.sleep(0.1)
		print "            *  *  *"
		time.sleep(0.1)
		print "            *  *  *"
		time.sleep(0.1)
		print "         ------------"
		time.sleep(0.1)
		print "        /            \\"
		time.sleep(0.1)
		print "       |  **********  |--"
		time.sleep(0.1)
		print "       |  SMARTHOUSE  |  \\"
		time.sleep(0.1)
		print "       |    KEEPER    |  /"
		time.sleep(0.1)
		print "       |    COFFEE    |--"
		time.sleep(0.1)
		print "        \            /"
		time.sleep(0.1)
		print "         ============"
		time.sleep(0.1)
		print "     ********************"
		print ''
		

def runcoffee():
	try:
		while True:
			cmd_coffee(coffeeStatus)
			time.sleep(1)
					
	except KeyboardInterrupt, e: 
		pass
		

HOST = ''
PORT = 8888
PORTcoff = 9999
try:
	print ''
	print "----------- COFFEE MACHINE -----------"
	thread.start_new_thread( client_thread, (HOST, PORTcoff, ) )
	thread.start_new_thread( runcoffee, () )
except:
	print "Error: unable to start thread"

while 1:
	pass
