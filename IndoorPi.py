import time
import sys
import socket
import thread
import threading

temp = 0
joystatus = 0

bar_length=50

def TCP(sock, addr): 
	while True:
		global joystatus
		data = sock.recv(1024) 
		time.sleep(0.1)
		if not data: 
			break
		#print data
		joystatus = int(data)

	sock.close() 

# Define the server function for the thread
def server_thread(HOST, PORT):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.bind((HOST, PORT))
	s.listen(1) 
	#print('\nServer is running...\n')
	sock, addr = s.accept()
	#print('Accept new connection from %s.' %addr[0])
	while True:
		sock, addr = s.accept()
		TCP(sock, addr)
		
		
def progress_right(x):
    global temp
    while temp < x:
        temp = temp + 1
        hashes = '=' * int((temp)/100.0 * bar_length)
        spaces = ' ' * (bar_length - len(hashes))
        sys.stdout.write("\rPercent: [%s] %d%% "%(hashes + spaces, temp))
        sys.stdout.flush()
        time.sleep(0.01)
        
    
def progress_left(x):
    global temp
    while temp > x:
        temp = temp - 1
        hashes = '=' * int((temp)/100.0 * bar_length)
        spaces = ' ' * (bar_length - len(hashes))
        sys.stdout.write("\rPercent: [%s] %d%% "%(hashes + spaces, temp))
        sys.stdout.flush()
        
        time.sleep(0.01)
    #temp = x

def runcurtain():
	try:
                hashes = '=' * int((temp)/100.0 * bar_length)
                spaces = ' ' * (bar_length - len(hashes))
                sys.stdout.write("\rPercent: [%s] %d%% "%(hashes + spaces, temp))
                sys.stdout.flush()
		while True:
			if joystatus == 1 and temp > 1:
				progress_left(temp-2)
			elif joystatus == 2 and temp < 100:
				progress_right(temp+2)
	except KeyboardInterrupt, e: 
		pass


HOST = ''
PORT = 8888
try:
	thread.start_new_thread( server_thread, (HOST, PORT, ) )
	thread.start_new_thread( runcurtain, () )
except:
	print "Error: unable to start thread"

while 1:
	pass

