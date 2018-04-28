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
humid = 0
currtime = 0
sleepstatus = 0 # 1:sleep
joystatus = 0 #0:home 1:left 2:right

ledStatus = 1 # 0:light 1:no
coffeeStatus = 0 # -1:question 0:nothing 1:hot 2:cold
curtainStatus = -1 # 0: open 1: close
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
UDP Socket with Server
'''
def server_thread_coffee(HOST, PORT):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
 
	addr = (HOST, PORT)

	while True:
		dataudp = 'coffeeStatus:' +  str(coffeeStatus) +';'
		#dataudp = dataudp + 'curtainStatus:'+ str(curtainStatus) +';'
		
		s.sendto(dataudp, addr)
		time.sleep(1)
		#recvdata, addr = s.recvfrom(1024)
		#print(recvdata.decode('utf-8'))

	s.close()  
	
def server_thread_curt(HOST, PORT):
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
 
	addr = (HOST, PORT)

	while True:
		dataudp = 'curtainStatus:' +  str(curtainStatus) +';'
		#dataudp = dataudp + 'curtainStatus:'+ str(curtainStatus) +';'
		
		s.sendto(dataudp, addr)
		time.sleep(0.1)
		#recvdata, addr = s.recvfrom(1024)
		#print(recvdata.decode('utf-8'))

	s.close()  

'''
UDP Socket with Client
'''
def client_thread( HOST, PORT):
	global ledStatus
	global coffeeStatus
	global curtainStatus
	
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
	addr = (HOST, PORT)

	while True:
		timehr = time.localtime(time.time()).tm_hour 
		timemin = time.localtime(time.time()).tm_min
			
		currtime = 60*timehr + timemin
		
		data = 'indoorTemp:' +  str(intemp) +';'
		data = data + 'humidity:'+ str(humid) +';'
		data = data + 'indoorIllum:'+ str(inlum) +';'
		data = data + 'currentTime:'+ str(currtime) +';'
		data = data + 'sleepStatus:'+ str(sleepstatus) +';'
		data = data + 'joyStatus:'+ str(joystatus) +';'
		
		s.sendto(data, addr)
		#print data
		time.sleep(0.1)
		
		data1 = s.recv(1024)
			
		length = len(data1.split(';'))-1
		
		for i in range(0, length):
			if  data1.split(';')[i].split(':')[0] == 'ledStatus':
				ledStatus = int(data1.split(';')[i].split(':')[1])
			if  data1.split(';')[i].split(':')[0] == 'coffeeStatus':
				coffeeStatus = int(data1.split(';')[i].split(':')[1])
			if  data1.split(';')[i].split(':')[0] == 'curtainStatus':
				curtainStatus = float(data1.split(';')[i].split(':')[1])

		#print 'ledstatus %d'%ledStatus
		#print 'coffeeStatus %s'%coffeeStatus
		#print 'curtainStatus %f'%curtainStatus
		time.sleep(0.3)
		
	s.close()  
	


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
			global humid
			intemp = int(temperature)
			humid = int(humidity)
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
		ledout(ledStatus)
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
	
	if sleepstatus == 0:
		sleepstatus = 1
	
	else:
		sleepstatus = 0
	
def btnloop():
	while True:
		time.sleep(0.1)
		
def btnsensor():
	btnsetup()
	try:
		btnloop()
	except KeyboardInterrupt, e: 
		pass
		
'''Joystick'''
def joydirection():
	i = 0
	if ADC.read(1) <= 100:
		i = 1		#left
	if ADC.read(1) >= 150:
		i = 2		#right
	if ADC.read(1)  < 138 and ADC.read(1)  > 118:
		i = 0
	return i

def joyloop():
	global joystatus
	while True:
		tmp = joydirection()
		#print ADC.read(1)

		if tmp != None and tmp != joystatus:
			#print tmp
			joystatus = tmp
		time.sleep(0.02)

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
PORTcoff = 9999
PORTcurt = 8989
if len(sys.argv) != 2:
	print "Usage: python PiChat <Destination IP"
	exit(0)
try:
	lumsetup()
	thread.start_new_thread( server_thread_coffee, (HOST, PORTcoff, ) )
	thread.start_new_thread( server_thread_curt, (HOST, PORTcurt, ) )
	thread.start_new_thread( client_thread, (sys.argv[1], PORT, ) )
	thread.start_new_thread( inlumsensor, () )
	##thread.start_new_thread( outlumsensor, () )
	thread.start_new_thread( humituresensor, () )
	thread.start_new_thread( ledsensor, () )
	thread.start_new_thread( btnsensor, () )
	thread.start_new_thread( joysensor, () )
except:
	print "Error: unable to start thread"

while 1:
	pass
