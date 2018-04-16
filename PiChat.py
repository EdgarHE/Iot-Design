#!python2
import thread
import time
import SocketServer
import socket
import sys


class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print '{} :{}'.format(self.client_address[0], self.data)


# Define the server function for the thread
def server_thread(HOST, PORT):
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    print "The server start at port %s" % ( PORT )
    server.serve_forever()

# Define the client function for the thread
def client_thread( HOST, PORT):
    # Create a socket (SOCK_STREAM means a TCP socket)
	print 'Ready to connect to %s' % (HOST)
	raw_input("Press enter to begin connection")
	while True:
		data = user_input = raw_input()
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			# Connect to server and send data
			sock.connect((HOST, PORT))
			sock.sendall(data + "\n")

			# Receive data from the server and shut down
			#received = sock.recv(1024)
		finally:
			sock.close()

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
