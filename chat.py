import socket
import time
import threading
import thread
import sys

indoorillum = -1
indoortemp = -1
time_sleep = '----'
time_wake = '----'


def TCP(sock, addr): 
	while True:
		data = sock.recv(1024) 
		time.sleep(1) 
		if not data or data.decode() == '-quit-': 
			break

		print data

		length = len(data.split(';'))-1
		
		for i in range(0, length):
			if  data.split(';')[i].split(':')[0] == 'indoortemp':
				indoortemp = int(data.split(';')[i].split(':')[1])
			if  data.split(';')[i].split(':')[0] == 'indoorillum':
				indoorillum = int(data.split(';')[i].split(':')[1])
			if  data.split(';')[i].split(':')[0] == 'sleeptime':
				time_sleep = data.split(';')[i].split(':')[1]
			if  data.split(';')[i].split(':')[0] == 'wakeuptime':
				time_wake = data.split(';')[i].split(':')[1]	
		print 'indoortemp: %d' %indoortemp
		print 'indoorillum: %d' %indoorillum
		print 'sleeptime: %s' %time_sleep
		print 'wakeuptime: %s' %time_wake
		
        

	sock.close() 


def server_thread(HOST, PORT):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(1) 
	print('Server is running...')
	sock, addr = s.accept()
	print('Accept new connection from %s.' %addr[0])
	while True:
		sock, addr = s.accept()
		TCP(sock, addr)
		
def client_thread( HOST, PORT):
    # Create a socket (SOCK_STREAM means a TCP socket)
	print 'Ready to connect to %s' % (HOST)
	raw_input("Press enter to begin connection")
	#i = 1
	while True:
		temp = 20
		lum = 60
		dis = 5
		data = 'temp:' +  str(temp) +';'
		data = data + 'lum:'+ str(lum) +';'

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			# Connect to server and send data
			sock.connect((HOST, PORT))
			sock.sendall(data)
			time.sleep(1)

		finally:
			sock.close()

HOST = ''
PORT = 8888
if len(sys.argv) != 2:
	print "Usage: python PiChat <Destination IP"
	exit(0)
try:
	thread.start_new_thread( server_thread, (HOST, PORT, ) )
	#thread.start_new_thread( client_thread, (sys.argv[1], PORT, ) )
except:
	print "Error: unable to start thread"
   
while 1:
	pass
