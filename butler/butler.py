#-*- coding:utf-8 -*-
import time, socket, sys, mraa
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
from Queue import Queue
# Deal with control-c

class Butler():
	def __init__(self,num):
		self.MaxPeople = num
		self.CurrentPeople  = 0;
		self.mqtt_topic = 'cis650/winterfell/butler'  # don't change this or you will screw it up for others
		self.mqtt_client = self.setup_mqtt()
		self.led = self.get_led(7)
		self.queue = Queue()
		self.WaitingList = Queue()
		self.FullFlag = False
		self.maxpassengernumber = 3
		self.pickedup = False
		self.halt = []
		signal.signal(signal.SIGINT, self.control_c_handler)

	def on_connect(self,client, userdata, flags, rc):
		print('connected')

	def on_message(self,client, userdata, msg):
		print('on_message')
		print(msg.topic)
		print(msg.payload)
		self.queue.put(msg.payload)


	def on_disconnect(self,client, userdata, rc):
		print("Disconnected in a normal way")
		#graceful so won't send will

	# Instantiate the MQTT client

	def control_c_handler(self,signum, frame):
		print('saw control-c')
		self.mqtt_client.disconnect()
		self.mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
		print "Now I am done."
		self.led.write(1)
		sys.exit(0)
	# just loop forever (or until ctrl-c)

	def setup_mqtt(self):
		mqtt_client = paho.Client()

		# set up handlers
		mqtt_client.on_connect = self.on_connect
		mqtt_client.on_message = self.on_message
		mqtt_client.on_disconnect = self.on_disconnect

		mqtt_client.will_set(self.mqtt_topic, '______________Will of The Winterfell Butler _________________\n\n', 0, False)
		broker = 'sansa.cs.uoregon.edu'  # Boyana's server
		mqtt_client.connect(broker, '1883')
		mqtt_client.subscribe(self.mqtt_topic) #subscribe to all students in class
		mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive
		return mqtt_client


	def get_led(self,index):
		led = mraa.Gpio(index+2)
		led.dir(mraa.DIR_OUT)
		led.write(1)
		return led

	def publish_msg(self,msg):
		self.mqtt_client.publish(self.mqtt_topic, self.MsgHead+msg)

	def publish_msg_to_topic(self,topic, msg):
		self.mqtt_client.publish(topic, msg)

	def processmessage(self,msg):
		# when get the passenger arrive information
		print msg
		msgs = msg.split(':')
		if msgs[2] == "RequestSitdown": #this is request sitdown
			if not self.FullFlag:
				self.publish_msg_to_topic('cis650/winterfell/phil:' + msgs[1],"SitdownGranted")
				self.CurrentPeople += 1
				if self.CurrentPeople >= self.MaxPeople:
					self.FullFlag = True
			else:
				self.WaitingList.put(msgs[1])
		elif msgs[2] == "GetUp": # this is dropdown
			self.CurrentPeople -= 1
			if self.WaitingList.qsize():
				phil_num = self.WaitingList.get()
				self.publish_msg_to_topic('cis650/winterfell/phil:' + phil_num, "SitdownGranted")
				self.CurrentPeople += 1
			self.FullFlag = (self.CurrentPeople >= self.MaxPeople)

		else:
			print "cannot recognize this!"

		if self.FullFlag:
			self.led.write(0)
		else:
			self.led.write(1)


	def run(self):
		while True:
			if self.queue.qsize():
				self.processmessage(self.queue.get())

def main(code):
	Butler(code).run()



if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "wrong arguments!"
		sys.exit(-1)
	code = int(sys.argv[1])
	main(code)
