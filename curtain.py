import time
import sys
import socket
import thread

temp = 0
curtainStatus = -1

bar_length=50

def client_thread(HOST, PORT):
	global curtainStatus
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	s.bind((HOST, PORT))

	#print('Bound UDP on %d...'%PORT)

	while True:                                          
		data, addr = s.recvfrom(1024)
		#print data
		
		length = len(data.split(';'))-1
		for i in range(0, length):
			if  data.split(';')[i].split(':')[0] == 'curtainStatus':
				tempstatus = float(data.split(';')[i].split(':')[1])
				#print tempstatus
				if tempstatus > -1:
					curtainStatus = int(100 * tempstatus)

		#print 'curtainStatus %d'%curtainStatus


def progress(x):
	global temp
	if temp < x:
		while temp < x:
			temp = temp + 1
			hashes = '=' * int((temp)/100.0 * bar_length)
			spaces = ' ' * (bar_length - len(hashes))
			sys.stdout.write("\rCurtain: [%s] %d%% "%(hashes + spaces, temp))
			sys.stdout.flush()
			time.sleep(0.05)
	elif temp > x:
		while temp > x:
			temp = temp - 1
			hashes = '=' * int((temp)/100.0 * bar_length)
			spaces = ' ' * (bar_length - len(hashes))
			sys.stdout.write("\rCurtain: [%s] %d%% "%(hashes + spaces, temp))
			sys.stdout.flush()  
			time.sleep(0.05)
		

def runcurtain():
	try:
		hashes = '=' * int((temp)/100.0 * bar_length)
		spaces = ' ' * (bar_length - len(hashes))
		sys.stdout.write("\rCurtain: [%s] %d%% "%(hashes + spaces, temp))
		sys.stdout.flush()
		while True:
			if curtainStatus != -1:
					progress(curtainStatus)
					
	except KeyboardInterrupt, e: 
		pass


HOST = ''
PORT = 8888
PORTcurt = 8989
try:
	print ''
	print "---------------------------- CURTAIN ----------------------------"
	thread.start_new_thread( client_thread, (HOST, PORTcurt, ) )
	thread.start_new_thread( runcurtain, () )
except:
	print "Error: unable to start thread"

while 1:
	pass
