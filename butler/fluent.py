#-*- coding:utf-8 -*-
import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
from Queue import Queue
import mraa
# Deal with control-c







class Fluent():
	def __init__(self,ID,lightID):
        	self.mqtt_topic = 'cis650/winterfell/' 
        	self.mqtt_client = self.setup_mqtt()
		#self.led = self.get_led()
		# self.passenger = 0
        	self.ID = ID
		self.lightID = lightID
        	self.eating = False
        	signal.signal(signal.SIGINT, self.control_c_handler)
        	self.led = self.get_led()

	def on_connect(self,client, userdata, flags, rc):
		print('connected')

	def on_message(self,client, userdata, msg):
		print('on_message')
		print(msg.topic)
		print(msg.payload)
		self.queue.put(msg.payload)
	
	def on_message_phil(self,client,userdata,msg):
		print(msg.payload)
		if not self.eating:
			vals = msg.payload
			if vals == "eating":
			  print "eating"
			  self.eating = True
			  self.led.write(0)

	def on_message_butler(self,client,userdata,msg):
		print(msg.payload)
		#if not self.getup:
		vals = msg.payload.split(":")
		if vals[2] == "GetUp" and vals[1]== self.ID:
		    print "not eating"
		    self.eating = False
                    self.led.write(1)


	def on_disconnect(self,client, userdata, rc):
		print("Disconnected in a normal way")
		#graceful so won't send will

	# Instantiate the MQTT client

	def control_c_handler(self,signum, frame):
		print('saw control-c')
		self.mqtt_client.disconnect()
		self.mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
		print "Now I am done."
		#self.led.write(1)
		sys.exit(0)
	# just loop forever (or until ctrl-c)

	def setup_mqtt(self):
		mqtt_client = paho.Client()

		# set up handlers
		mqtt_client.on_connect = self.on_connect
		mqtt_client.on_message = self.on_message
		mqtt_client.on_disconnect = self.on_disconnect
		mqtt_client.message_callback_add(self.mqtt_topic + "phil:" + ID, self.on_message_phil)
		mqtt_client.message_callback_add(self.mqtt_topic + "butler" , self.on_message_butler)

		mqtt_client.will_set(self.mqtt_topic, '______________Will of The Winterfell Monitor _________________\n\n', 0, False)
		broker = 'sansa.cs.uoregon.edu'  # Boyana's server
		mqtt_client.connect(broker, '1883')
		mqtt_client.subscribe(self.mqtt_topic + "phil:" + ID)
		mqtt_client.subscribe(self.mqtt_topic + "butler")
		
		
		mqtt_client.subscribe(self.mqtt_topic) #subscribe to all students in class
		mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive
		return mqtt_client
	def publish_msg(self,msg):
		self.mqtt_client.publish(self.mqtt_topic, self.MsgHead+msg)

	def publish_msg_to_topic(self,msg,topic):
		self.mqtt_client.publish(topic, msg)
	def run(self):
	  while True:
	    pass
	        #print "running"
	        #if self.eating == True:
	         #   print "True"
	        #self.led.write(0)
	        #if self.eating == False:
	         #   print "False"
    
          


	def get_led(self):
	    print self.lightID
	    led = mraa.Gpio(self.lightID+2)
	    led.dir(mraa.DIR_OUT)
	    led.write(1)
	    return led
		#i = ord(argv) - ord('a') +2
		# led = mraa.Gpio(i)
		# led.dir(mraa.DIR_OUT)
		



	
  

	
	        #self.led.write(1) 
	    
	    #if self.getup == True:
	        #self.led.write(1)
		 #self.led.write(1)
		 #while True:
			#if self.queue.qsize():
			#	self.processmessage(self.queue.get())
	#		print self.CurrentPeople


def main(ID,lightID):
	Fluent(ID,lightID).run()



if __name__ == "__main__":
	if len(sys.argv) != 3:
		print "wrong arguments!"
		sys.exit(-1)
	ID = sys.argv[1]
	lightID = int(sys.argv[2])
	main(ID,lightID)
