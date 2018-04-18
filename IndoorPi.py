#!python2
import thread
import time
import SocketServer
import socket
import sys
import PCF8591 as ADC
import RPi.GPIO as GPIO

inlum = 0
#outlum = 0
intemp = 0
inhumid = 0
currtime = '----'
sleepstatus = 0
joystatus = 'home'

ledStatus = 0
coffeeStatus = -1
curtainStatus = -1
aircondition = -1


BTNPIN = 16
DHTPIN = 17
RPIN = 18
GPIN = 19
BPIN = 20

MAX_UNCHANGE_COUNT = 100

STATE_INIT_PULL_DOWN = 1
STATE_INIT_PULL_UP = 2
STATE_DATA_FIRST_PULL_DOWN = 3
STATE_DATA_PULL_UP = 4
STATE_DATA_PULL_DOWN = 5

'''
TCP Socket with Server and Client
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

# Define the client function for the thread
def client_thread( HOST, PORT):
    # Create a socket (SOCK_STREAM means a TCP socket)
	print 'Ready to connect to %s' % (HOST)
	raw_input("Press enter to begin connection")
	while True:
		hour = time.localtime(time.time()).tm_hour 
		minute = time.localtime(time.time()).tm_min
		timehr = ''
		timemin = ''
		if hour < 10:
			timehr = '0' + str(hour)
		else:
			timehr = str(hour)
		if hour < 10:
			timemin = '0' + str(minute)
		else:
			timemin = str(minute)
			
		currtime = timehr + timemin
		
		data = 'indoorTemp:' +  str(intemp) +';'
		data = data + 'indoorHumid:'+ str(inhumid) +';'
		data = data + 'indoorIllum:'+ str(inlum) +';'
		data = data + 'currentTime:'+ str(currtime) +';'
		data = data + 'sleepStatus:'+ str(sleepstatus) +';'
		data = data + 'joyStatus:'+ str(joystatus) +';'
		
		print data
		
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			# Connect to server and send data
			sock.connect((HOST, PORT))
			sock.sendall(data)
			time.sleep(1)

		finally:
			sock.close()



'''Indoorphotoresistor'''
def inlumsetup():
	ADC.setup(0x48)

def inlumloop():
	#status = 1
	while True:
		global inlum
		inlum = ADC.read(0)
		#print 'inValue: ', ADC.read(0)
		#print 'outValue: ', ADC.read(2)
		
		time.sleep(1)
		
def inlumsensor():
	try:
		#inlumsetup()
		inlumloop()
		
	except KeyboardInterrupt: 
		pass
		
'''Outdoorphotoresistor'''
'''
def outlumsetup():
	ADC.setup(0x48)

def outlumloop():
	#status = 1
	while True:
		global outlum
		outlum = ADC.read(1)
		print 'outValue: ', ADC.read(1)
		
		time.sleep(1)
		
def outlumsensor():
	try:
		#outlumsetup()
		outlumloop()
		
	except KeyboardInterrupt: 
		pass
'''


'''humiture sensor'''
def humituresetup():
	GPIO.setmode(GPIO.BCM)
	
def read_dht11_dat():
	GPIO.setup(DHTPIN, GPIO.OUT)
	GPIO.output(DHTPIN, GPIO.HIGH)
	time.sleep(0.05)
	GPIO.output(DHTPIN, GPIO.LOW)
	time.sleep(0.02)
	GPIO.setup(DHTPIN, GPIO.IN, GPIO.PUD_UP)

	unchanged_count = 0
	last = -1
	data = []
	while True:
		current = GPIO.input(DHTPIN)
		data.append(current)
		if last != current:
			unchanged_count = 0
			last = current
		else:
			unchanged_count += 1
			if unchanged_count > MAX_UNCHANGE_COUNT:
				break

	state = STATE_INIT_PULL_DOWN

	lengths = []
	current_length = 0

	for current in data:
		current_length += 1

		if state == STATE_INIT_PULL_DOWN:
			if current == GPIO.LOW:
				state = STATE_INIT_PULL_UP
			else:
				continue
		if state == STATE_INIT_PULL_UP:
			if current == GPIO.HIGH:
				state = STATE_DATA_FIRST_PULL_DOWN
			else:
				continue
		if state == STATE_DATA_FIRST_PULL_DOWN:
			if current == GPIO.LOW:
				state = STATE_DATA_PULL_UP
			else:
				continue
		if state == STATE_DATA_PULL_UP:
			if current == GPIO.HIGH:
				current_length = 0
				state = STATE_DATA_PULL_DOWN
			else:
				continue
		if state == STATE_DATA_PULL_DOWN:
			if current == GPIO.LOW:
				lengths.append(current_length)
				state = STATE_DATA_PULL_UP
			else:
				continue
	if len(lengths) != 40:
		#print "Data not good, skip"
		return False

	shortest_pull_up = min(lengths)
	longest_pull_up = max(lengths)
	halfway = (longest_pull_up + shortest_pull_up) / 2
	bits = []
	the_bytes = []
	byte = 0

	for length in lengths:
		bit = 0
		if length > halfway:
			bit = 1
		bits.append(bit)
	#print "bits: %s, length: %d" % (bits, len(bits))
	for i in range(0, len(bits)):
		byte = byte << 1
		if (bits[i]):
			byte = byte | 1
		else:
			byte = byte | 0
		if ((i + 1) % 8 == 0):
			the_bytes.append(byte)
			byte = 0
	#print the_bytes
	checksum = (the_bytes[0] + the_bytes[1] + the_bytes[2] + the_bytes[3]) & 0xFF
	if the_bytes[4] != checksum:
		#print "Data not good, skip"
		return False

	return the_bytes[0], the_bytes[2]
	
def humituredestroy():
	GPIO.cleanup()

def humituremain():
	#print "Raspberry Pi wiringPi DHT11 Temperature test program\n"
	while True:
		result = read_dht11_dat()
		if result:
			humidity, temperature = result
			global intemp
			global inhumid
			intemp = int(temperature)
			inhumid = int(humidity)
			#print "Temperature: %d C`" %intemp
			#print "humidity: %s %%,  Temperature: %s C`" % (humidity, temperature)
		time.sleep(1)	

def humituresensor():
	try:
		humituresetup()
		humituremain()
	except KeyboardInterrupt: 
		humituredestroy()

'''LED'''
def ledsetup():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(RPIN, GPIO.OUT)
	GPIO.setup(GPIN, GPIO.OUT)
	GPIO.setup(BPIN, GPIO.OUT)

def ledout(status):
	if status == 0:
		GPIO.output(RPIN, 1)
		GPIO.output(GPIN, 1)
		GPIO.output(BPIN, 1)
		
	else:
		GPIO.output(RPIN, 0)
		GPIO.output(GPIN, 0)
		GPIO.output(BPIN, 0)
		#print "sleep"
		
def ledmain():
	while True:
		ledout(sleepstatus)
		time.sleep(1)
	
def leddestroy():
	GPIO.output(RPIN, GPIO.HIGH) 
	GPIO.output(GPIN, GPIO.HIGH)
	GPIO.output(BPIN, GPIO.HIGH)
	GPIO.cleanup() 

def ledsensor():
	ledsetup()
	try:
		#leddestroy()
		ledmain()
	except KeyboardInterrupt, e: 
		leddestroy()

'''button'''
def btnsetup():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(BTNPIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	GPIO.add_event_detect(BTNPIN, GPIO.BOTH, callback=btndetect, bouncetime=200)

def btndetect(chn):
	global sleepstatus
	global time_sleep
	global time_wake
	
	if sleepstatus == 0:
		sleepstatus = 1
	
	else:
		sleepstatus = 0
	
def btnloop():
	while True:
		pass
		
def btnsensor():
	btnsetup()
	try:
		btnloop()
	except KeyboardInterrupt, e: 
		pass
		
'''Joystick'''
def joydirection():
	i = 0
	if ADC.read(1) <= 50:
		i = 1		#left
	if ADC.read(1) >= 200:
		i = 2		#right
	if ADC.read(0)  < 150 and ADC.read(0)  > 100	and ADC.read(1)  < 150 and ADC.read(1)  > 100:
		i = 0
	return i

def joyloop():
	global joystatus
	while True:
		tmp = joydirection()

		if tmp != None and tmp != joystatus:
			#print tmp
			joystatus = tmp
		time.sleep(0.05)

def joysensor():
	try:
		joyloop()
	except KeyboardInterrupt:
		destroy()
		
'''lumsetup'''
def lumsetup():
	ADC.setup(0x48)

'''MAIN'''
HOST = ''
PORT = 8888
if len(sys.argv) != 2:
	print "Usage: python PiChat <Destination IP"
	exit(0)
try:
	lumsetup()
	thread.start_new_thread( server_thread, (HOST, PORT, ) )
	thread.start_new_thread( client_thread, (sys.argv[1], PORT, ) )
	thread.start_new_thread( inlumsensor, () )
	#thread.start_new_thread( outlumsensor, () )
	thread.start_new_thread( humituresensor, () )
	thread.start_new_thread( ledsensor, () )
	thread.start_new_thread( btnsensor, () )
	thread.start_new_thread( joysensor, () )
except:
	print "Error: unable to start thread"

while 1:
	pass
