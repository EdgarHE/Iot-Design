import socket
import time
import threading
import thread
import sys

def TCP(sock, addr): 
	while True:
		data = sock.recv(1024) 
		time.sleep(1) 
		if not data or data.decode() == '-quit-': 
			break
		print data
        #sock.send(data.decode('utf-8').upper().encode()) 

	sock.close() 
	#print('Connection from %s:%s closed.' %addr) 

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
		
def client_thread(HOST, PORT):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	
	while True:
		data = raw_input()
			
		try:
			s.connect((HOST, PORT))
			if data == '-quit-':
				s.send(b'-quit-')
				break
			s.send(data.encode())
		finally:
			s.close()
	
	s.close()
	
HOST = ''
PORT = 8888
if len(sys.argv) != 2:
	print "Usage: python PiChat <Destination IP"
	exit(0)
try:
	thread.start_new_thread( server_thread, (HOST, PORT, ) )
	thread.start_new_thread( client_thread, (sys.argv[1], PORT, ) )
except:
	print "Error: unable to start thread"
   
while 1:
	pass
		
		
	
