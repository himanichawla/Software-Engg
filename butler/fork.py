#-*- coding:utf-8 -*-
import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
from Queue import Queue
import mraa
# Deal with control-c







class Fork():
	def __init__(self,code):
		self.code = code
		self.mqtt_topic = 'cis650/winterfell/fork:'+code  # don't change this or you will screw it up for others
		self.mqtt_client = self.setup_mqtt()
		self.led = self.get_led(self.code)
		self.passenger = 0
		self.queue = Queue()
		self.FullFlag = False
		self.CarIn = [True,True]
		self.maxpassengernumber = 3
		self.MsgHead = "Fork:"+self.code+":"
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

		mqtt_client.will_set(self.mqtt_topic, '______________Will of The Winterfell Monitor _________________\n\n', 0, False)
		broker = 'sansa.cs.uoregon.edu'  # Boyana's server
		mqtt_client.connect(broker, '1883')
		mqtt_client.subscribe(self.mqtt_topic) #subscribe to all students in class
		mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive
		return mqtt_client


	def get_led(self,argv):
		i = ord(argv) - ord('a') +2
                led = mraa.Gpio(i)
		led.dir(mraa.DIR_OUT)
		return led
		



	def publish_msg(self,msg):
		self.mqtt_client.publish(self.mqtt_topic, self.MsgHead+msg)

	def processmessage(self,msg):
		# when get the passenger arrive information
		
		msgs = msg.split(':')
		if msgs[2] == "RequestFork": #this is request pick up
			if not self.pickedup:
				self.publish_msg( "PickedUpByPhil:" +  msgs[1])
				self.pickedup = True
                                self.led.write(0)
			else:
				self.halt.append(msg)
		elif msgs[2] == "ReleaseFork": # this is dropdown
			if self.pickedup:
				self.publish_msg("SettledDownByPhil:" +  msgs[1])

				self.publish_msg( "SettledDownByPhil:" +  msgs[1])

				while self.halt != []:
					self.queue.put(self.halt.pop())
				self.pickedup = False
                                self.led.write(1)
		else:
			#print "cannot recognize this!"
                        return 


	def run(self):
		self.led.write(1)
		while True:
			if self.queue.qsize():
				self.processmessage(self.queue.get())


def main(code):
	Fork(code).run()



if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "wrong arguments!"
		sys.exit(-1)
	code = sys.argv[1]
	main(code)
