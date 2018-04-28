#!python2
import thread
import time
import SocketServer
import socket
import sys
import PCF8591 as ADC
import RPi.GPIO as GPIO


outlum = 0


'''
TCP Socket with Server and Client
'''
'''
def TCP(sock, addr): 
	while True:
		data = sock.recv(1024) 
		time.sleep(1) 
		if not data or data.decode() == '-quit-': 
			break
		print data

	sock.close() 

# Define the server function for the thread
def server_thread(HOST, PORT):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(1) 
	print('\nServer is running...\n')
	sock, addr = s.accept()
	print('Accept new connection from %s.' %addr[0])
	while True:
		sock, addr = s.accept()
		TCP(sock, addr)

'''

# Define the client function for the thread
def client_thread( HOST, PORT):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	addr = (HOST, PORT)
	
	while True:
		data = 'outdoorIllum:'+ str(outlum) +';'
		s.sendto(data, addr)
		print data
		time.sleep(3)
	sock.close()
			
		
'''Outdoorphotoresistor'''
def outlumsetup():
	ADC.setup(0x48)
def outlumloop():
	while True:
		global outlum
		outlum = ADC.read(3)
		#print 'outValue: ', ADC.read(3)
		
		time.sleep(3)
		
def outlumsensor():
	try:
		outlumsetup()
		outlumloop()
		
	except KeyboardInterrupt: 
		pass





'''MAIN'''
HOST = ''
PORT = 8888
if len(sys.argv) != 2:
	print "Usage: python PiChat <Destination IP"
	exit(0)
try:
	#thread.start_new_thread( server_thread, (HOST, PORT, ) )
	thread.start_new_thread( client_thread, (sys.argv[1], PORT, ) )
	thread.start_new_thread( outlumsensor, () )
except:
	print "Error: unable to start thread"

while 1:
	pass
