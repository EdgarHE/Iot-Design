import time
import sys
import socket
import thread

temp = 0
joystatus = -1

def TCP(sock, addr): 
	while True:
		global joystatus
		data = sock.recv(1024) 
		time.sleep(1) 
		joystatus = int(data)

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
		
		
def progress_test(x):
    bar_length=50
    global temp
    for percent in range(temp, x):
    	hhh = 100-percent
        hashes = '=' * int((100.0-percent)/100.0 * bar_length)
        spaces = ' ' * (bar_length - len(hashes))
        sys.stdout.write("\rPercent: [%s] %d%% "%(hashes + spaces, hhh))
        sys.stdout.flush()
        temp = x
        time.sleep(0.1)

def runcurtain():
	try:
		progress_test(1)
		while True:
			if joystatus == 1:
				progress_test(temp+2)
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

