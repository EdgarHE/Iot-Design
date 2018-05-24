#!python2
import thread
import threading
import time
import socket
import sys
import math
import struct
import fcntl

def getip(ethname):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0X8915, struct.pack('256s', ethname[:15]))[20:24])


alpha = 1
beta = 0.005
gamma = 1

routingTable = {}
inNI = {} # In region node info
seqT = {} #Sequence number
ipTable = {}
nodeMap = {} #'A':coord_A  coord_A = Coord(1,1)
radius = 5
currNode = 'A' # Current Node
currX = 0
currY = 0
currSeq = 0
currEnergy = 100
currIP = getip('eth0')
print currIP

send_state = threading.Lock()
storeNI_state = threading.Lock()
storeRT_state = threading.Lock()
pktRecv_state = threading.Lock()


class Coord:
    def __init__(self, coordx, coordy):
        self.x = coordx
        self.y = coordy
        
def sendHello(PORT):
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	while True:
		data = ''
		network = '<broadcast>'
		addr = (network, PORT)
		data = genHelloMsg()
		s.sendto(data, addr)
		storeNI_state.acquire()
		print 'send: ' + data
		storeNI_state.release()
		time.sleep(1)
		
	s.close()   
	
def recvHello(PORT):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
	
	s.bind(('', PORT))
	
	while True:
		data, addr = s.recvfrom(100)
		storeNI_state.acquire()
		storeReceiveMsg(data)
		print routingTable
		storeNI_state.release()
		
		

def storeReceiveMsg(recvData):
	# Global Parameters
	# 
	data = recvData
	blockNum = len(data.split(';'))
	#print ("bnum%d"%blockNum)
	if data.split(';')[0] == 'Hello':
		seqNum = data.split(';')[1]

		sourceNodeStr = data.split(';')[2]
		node = data.split(';')[2].split(',')[0]
		
		if node == currNode:
			return
		print 'data   ' + data
		nodeCoord = data.split(';')[2].split(',')[1]
		nodeIP = data.split(';')[2].split(',')[2]
		if blockNum == 3:
			addToInNI(node, seqNum, nodeCoord, nodeIP)

		elif blockNum > 3:
			inNeighborStr = data.split(';')[3]
			nodeInfo = nodeCoord + ';' + inNeighborStr
			addToInNI(node, seqNum, nodeInfo, nodeIP)
			


			
def findNodeInfo(node, num): # 0:Coord, 1:cost, 2:Path
	nodeInfo = rT.get(node)
	if nodeInfo != none:
		infoStr = rT[nodeInfo].split(';')
		return infoStr[num]

def addSeqNum(node, seq):
	global seqT
	if seqT.get(node, 'None') != 'None':
		if int(seqT[node].split(' ')[0]) < seq:
			seqT[node] = str(seq) + ' ' + str(currSeq)
	else :
		seqT[node] = str(seq) + ' ' + str(currSeq)
	

def addToInNI(node, seqTime, info, nodeIP):
	global inNI
	seq = int(seqTime.split(',')[0])
	time = seqTime.split(',')[1]
	coord = info.split(';')[0]
	x = int(coord.split(' ')[0])
	y = int(coord.split(' ')[1])
	dist = math.sqrt((x - currX)**2 + (y - currY)**2)
	if dist <= radius:
		if inNI.get(node, 'None') != 'None':
			nodeSeq = int(seqT[node].split(' ')[0])
			if seq > nodeSeq:
				inNI[node] = time + ";" + info
				addSeqNum(node, seq)
				addIP(node, nodeIP)
			
		else:
			inNI[node] = time + ";" + info
			addSeqNum(node, seq)
			addIP(node, nodeIP)
		
def addIP(node, nodeIP):
	global ipTable
	ipTable[node] = nodeIP



def updateRoutingTable():
	global inNI
	
	while True:
		storeNI_state.acquire()
		
		tmp = []
		for key in inNI:
			tmp.append(key)
		
		for key2 in tmp:
		
			dealInNIMsg(key2)
			inNI.pop(key2)
		scanSeq()
		storeNI_state.release()
		time.sleep(1)
		


def dealInNIMsg(node):
	global routingTable
	nodeName = node
	nodeInfo = inNI[node]
	nodeCoord = inNI[node].split(';')[1]
	nodeTime = int(inNI[node].split(';')[0])
	nodeCost = calCost(nodeCoord, nodeTime)
	nodePath = nodeName
	updateNodeInfo(nodeName, nodeCoord, nodeCost, nodePath)
	#print (inNI[node])
	if len(inNI[node].split(';'))>2:
		nodeNum = len(inNI[node].split(';')[2].split('/'))
		#print (nodeNum)
		for i in range(0, nodeNum):
			currNodeInfo = inNI[node].split(';')[2].split('/')[i]
			currNodeName = currNodeInfo.split(',')[0]
			
			if currNodeName != currNode:
				currCoord = currNodeInfo.split(',')[1]
				currNodeX = int(currCoord.split(' ')[0])
				currNodeY = int(currCoord.split(' ')[1])
				dist = math.sqrt((currNodeX - currX)**2 + (currNodeY - currY)**2)
				
				#print dist
				if dist <= radius:
					nodeInRTInfo = routingTable.get(nodeName, 'None')
					if nodeInRTInfo!='None':
						currCost = int(currNodeInfo.split(',')[2]) + int(nodeInRTInfo.split(';')[1])
						currPath = nodeName + currNodeInfo.split(',')[3]
						updateNodeInfo(currNodeName, currCoord, currCost, currPath)
	#return


def calCost(coord, nodeTime):
	coordX = int(coord.split(' ')[0])
	coordY = int(coord.split(' ')[1])
	timehr = time.localtime(time.time()).tm_hour 
	timemin = time.localtime(time.time()).tm_min
	timesec = time.localtime(time.time()).tm_sec
	currTime = 3600*timehr + 60*timemin + timesec
	dTime = currTime - nodeTime
	cost = int(alpha * (2**(math.sqrt((coordX - currX)**2) + (coordY - currY)**2)) + beta * dTime)
	return cost


def updateNodeInfo(node, coord, cost, path):
	global routingTable
	isInRT = routingTable.get(node, 'None')
	if isInRT == 'None':
		routingTable[node] = coord + ';' + str(cost) + ';' + path
	else:
		routingCost = int(isInRT.split(';')[1])
		routingCoord = isInRT.split(';')[0]
		# print('cost:' + str(cost))
		# print('routingCost:' + path + str(routingCost))
		if routingCoord != coord:

			routingTable[node] = coord + ';' + str(cost) + ';' + path
		if routingCost > cost:
			routingTable[node] = coord + ';' + str(cost) + ';' + path

	return 

def genHelloMsg():
	global currSeq
	timehr = time.localtime(time.time()).tm_hour 
	timemin = time.localtime(time.time()).tm_min
	timesec = time.localtime(time.time()).tm_sec
	currTime = 3600*timehr + 60*timemin + timesec
	currSeq += 1
	data = "Hello;" + str(currSeq) +',' + str(currTime) + ';' + currNode + ',' + str(currX) + ' ' + str(currY) + ',' + currIP
	if len(routingTable)>0:
		data = data + ';'
	for key in routingTable:
		coord = routingTable[key].split(';')[0]
		cost = routingTable[key].split(';')[1]
		path = routingTable[key].split(';')[2]
		data = data + key + ',' + coord + ',' + cost + ',' + path + '/'
	data = data.rstrip('/')
	return data

def scanSeq():
	global routingTable
	global ipTable
	for key in seqT:
		nodes = []
		if (currSeq - int(seqT[key].split(' ')[1])) > 5:
			for node in routingTable:
				if routingTable[node].find(key) != -1:
					nodes.append(node)
			for element in nodes:
				if routingTable.get(element, 'None') != 'None':
					routingTable.pop(element)
					ipTable.pop(element)
			seqT[key] = str(0) + ' ' + str(currSeq)
			


def getEdge(source, destination): # destination_node is a node outside the range (i.e. final destination)
	#global routingTable
	vector1X = nodeMap[destination].x - nodeMap[source].x  # vector_X from source to destination
	vector1Y = nodeMap[destination].y - nodeMap[source].y  # vector_Y from source to destination
	product = -10000  # means negative infinity
	if len(routingTable) > 0:
		for node in routingTable:
			location = routingTable[node].split(';')[0]
			locationX = float(location.split(' ')[0])
			locationY = float(location.split(' ')[1])
			vector2X = locationX - nodeMap[source].x  # vector_X from source to neighbor
			vector2Y = locationY - nodeMap[source].y  # vector_Y from source to neighbor
			newproduct = vector1X * vector2X + vector1Y * vector2Y
			if newproduct > product:  # record the max_product
				product = newproduct
				edge = node
		return edge
	else:
		return 'None'

def createPath(destination): # destination_node is a node in the range (i.e. edge node)
	storeNI_state.acquire()
	path_string = routingTable[destination].split(';')[2]
	storeNI_state.release()
	count = len(path_string) - 1
	path = []
	while count >= 0:
		path.append(path_string[count])
		count = count - 1
	return path
	
def genPkt(source_node, destination_node, current_node): # destination_node is a node outside the range (i.e. final destination)
	packet = {}
	packet.update(source = source_node)
	packet.update(destination = destination_node)
	packet.update(edge = getEdge(current_node, destination_node)) # Edge is a node at the edge of the range
	packet.update(content = "I am a cute packet from " + source_node + " to " + destination_node)
	packet.update(pathToEdge = createPath(destination_node))
	return packet
	
def recvAndTreatPkt(): # receive, check, print or route/send the packet

	HOST = ipTable[currNode]
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.bind((HOST, PORT_RECV))
	#s.listen(1)
	while True:
		#conn, addr = s.accept()
		#print'Connected by', addr
		data= s.recv(10024)
		#if len(data.strip()) == 0:
			#conn.sendall('Done.')
		#else:
		packet = eval(data) # retrive the dictionary from string, packet is a dictionary
		if currNode == packet['destination']: # current node is the destination, print the detail about the packet
			print("I received a packet from " + packet['source'])
			print("Packet contains:")
			print(packet['content'])
		elif currNode == packet['edge']: # current node is the edge so calculate new route path in the range
			newpacket = genPkt(packet['source'],packet['destination'], currNode)
			nextHop = packet['pathToEdge'].pop()
			sendPkt(nextHop, packet)
		else: # current is a node in the range, route the packet to the next hop
			try:
				nextHop = packet['pathToEdge'].pop()
			except:
				print("The pathToEdge term is empty, nothing to be popped")
			sendPkt(nextHop, packet)

	s.close()

def sendPkt(destination, packet): # send packet to the next hop, packet is a dictionary
	global currNode
	global ipTable
	global PORT_SEND
	HOST = ipTable[destination]
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	addr = (HOST, PORT_SEND)
	#s.connect((HOST, PORT_SEND))
	s.sendto(repr(packet),addr)
	s.close()
    


def changeVariable():
	global currX, currY
	while True:
		data = raw_input()
		if data.find('coord:') != -1:
			coord = data.split(':')[1]
			if coord.find(' ') != -1:
				x = coord.split(' ')[0]
				y = coord.split(' ')[1]
				if x.isdigit() and y.isdigit() :
					currX = int(x)
					currY = int(y)
				else:
					print 'Invalid Input'
			else:
				print 'Invalid Input'
		else:
			print 'Invalid Input'
			
def testSendPkt():
	time.sleep(3)
	coord_A = Coord(0,0)
	coord_B = Coord(2,0)
	nodeMap['A'] = coord_A
	nodeMap['B'] = coord_B
	pkt = genPkt('A', 'B', 'A')
	sendPkt('B', pkt)
	print 'SENDPKT#######################'
	
	
	

'''MAIN'''

HOST = ''
PORT = 8888 #routing table

PORT_SEND = 23333 #packet
PORT_RECV = 23334

ipTable[currNode] = currIP
try:
	thread.start_new_thread( sendHello, (PORT, ) )
	thread.start_new_thread( recvHello, (PORT, ) )
	thread.start_new_thread( updateRoutingTable, ( ) )
	thread.start_new_thread( changeVariable, ( ) )
	thread.start_new_thread( testSendPkt, ( ) )
	thread.start_new_thread( recvAndTreatPkt, ( ) )
except:
	print "Error: unable to start thread"
while 1:
	pass

