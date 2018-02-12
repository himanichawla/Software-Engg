# -*- coding:utf-8 -*-
import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
from Queue import Queue
import mraa


# Deal with control-c
class Assert1():
	def __init__(self, ID,NID1,NID2):
		self.ID = int(ID)
		self.ID1 = int(NID1)
		self.ID2 = int(NID2)
		self.setFlag = False
		self.setFlag1 = False
		self.mqtt_topic_ID0 = 'cis650/winterfell/ring/node:' + str(self.ID)  # don't change this or you will screw it up for others
		self.mqtt_topic_ID1 = 'cis650/winterfell/ring/node:' + str(self.ID1)
		self.mqtt_topic_ID2 = 'cis650/winterfell/ring/node:' + str(self.ID2)
		self.mqtt_client = self.setup_mqtt()
		self.led = self.get_led()
	# self.queue = Queue()
		self.GotLeader = False
		signal.signal(signal.SIGINT, self.control_c_handler)

	def on_connect(self, client, userdata, flags, rc):
		print('connected')

	def on_message(self, client, userdata, msg):
		print('on_message')
		print(msg.topic)
		print(msg.payload)
		# self.queue.put(msg.payload)
		self.processmessage(msg.topic,msg.payload)
	def on_disconnect(self, client, userdata, rc):
		print("Disconnected in a normal way")

	# graceful so won't send will

	# Instantiate the MQTT client

	def control_c_handler(self, signum, frame):
		print('saw control-c')
		self.mqtt_client.disconnect()
		self.mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
		print "Now I am done."

		#[i.write(1) for i in self.led]
		sys.exit(0)
	# just loop forever (or until ctrl-c)

	def setup_mqtt(self):
		mqtt_client = paho.Client()

		# set up handlers
		mqtt_client.on_connect = self.on_connect
		# mqtt_client.on_message = self.on_message
		mqtt_client.message_callback_add(self.mqtt_topic_ID0 , self.on_message)
		mqtt_client.on_disconnect = self.on_disconnect

		mqtt_client.will_set(self.mqtt_topic_ID0, '______________Will of The Winterfell Monitor _________________\n\n', 0,
		                     False)
		broker = 'sansa.cs.uoregon.edu'  # Boyana's server
		mqtt_client.connect(broker, '1883')
		mqtt_client.subscribe(self.mqtt_topic_ID0)  # subscribe to all students in class
		mqtt_client.subscribe(self.mqtt_topic_ID1)
		mqtt_client.subscribe(self.mqtt_topic_ID2)
		mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive
		return mqtt_client

	def get_led(self):
		leds = []
		#for i in range(4,5):
		led = mraa.Gpio(8)
		led.dir(mraa.DIR_OUT)
		led.write(1)
		#leds.append(led)
	   	return led

	# def publish_msg(self, msg):
	# 	self.mqtt_client.publish(self.mqtt_topic, self.MsgHead + msg)

	def pulish_msg(self,topic,msg):
		self.mqtt_client.publish(topic,msg)

	def processmessage(self,topic, msg):
		# when get the passenger arrive information
        # format will be "ID:1" and "Leader:1"
       		topics = topic.split(':')
		msgs = msg.split(':')
		# print msg[1]
		if msgs[0] == "ID" and topics[1] == msgs[1]:
		    self.setFlag1=True
		 
		
		if msgs[0] == "Leader" and self.setFlag1== True:
		    leader_ID =  int(msgs[1])
		    if leader_ID < self.ID:
		        self.setFlag = True
		        self.led.write(0)
		        print "CHEATER"
	        #else:
			#pass
		elif msgs[0] == "Leader" and self.setFlag1== False:
		    print "Cheater"
		    self.setFlag = True
		    self.led.write(0)
	def run(self):
		while True:
			pass 



	
def main(ID,NID1,NID2):
	Assert1(ID,NID1,NID2).run()


if __name__ == "__main__":
	if len(sys.argv) != 4:
		print "Arguments are not correct!"
		sys.exit(-1)
	ID = sys.argv[1]

	NID1= sys.argv[2]
	NID2 =sys.argv[3]
	main(ID,NID1,NID2)
