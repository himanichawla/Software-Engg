#-*- coding:utf-8 -*-
import time, socket, sys, mraa, threading
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
from random import randint

class Philosopher():
	def __init__(self,philID,fork1,fork2,lightID):
		self.lightID = lightID
		self.hasFork1 = False
		self.hasFork2 = False
		self.isSitting = False
		self.philID = philID
		self.fork1 = fork1
		self.fork2 = fork2
		self.mqtt_topic = 'cis650/winterfell/'
		self.mqtt_client = self.setup_mqtt()
		self.led = self.get_led()
		signal.signal(signal.SIGINT, self.control_c_handler)
		self.publish_msg("butler", "Phil:"+philID + ":RequestSitdown")

	def on_connect(self,client, userdata, flags, rc):
		print('connected')

	def on_message_fork1(self,client,userdata,msg):
		#print(msg.payload)
		if not self.hasFork1:
			vals = msg.payload.split(":")
			if vals[2] == "PickedUpByPhil" and vals[3] == self.philID:
				self.hasFork1 = True

	def on_message_fork2(self,client,userdata,msg):
		#print(msg.payload)
		if not self.hasFork2:
			vals = msg.payload.split(":")
			if vals[2] == "PickedUpByPhil" and vals[3] == self.philID:
				self.hasFork2 = True

	def on_message_phil(self,client,userdata,msg):
		#print(msg.payload)
		vals = msg.payload.split(":")
		if vals[0] == "SitdownGranted":
			self.isSitting = True
			threading.Thread(target=self.request_forks).start()
			#self.publish_msg("fork:" + self.fork1, "Phil:"+philID +":RequestFork")
			#time.sleep(4)
			#self.publish_msg("fork:" + self.fork2, "Phil:"+philID +":RequestFork")

	def request_forks(self):
		self.publish_msg("fork:" + self.fork1, "Phil:"+philID +":RequestFork")
		time.sleep(4)
		self.publish_msg("fork:" + self.fork2, "Phil:"+philID +":RequestFork")

	def on_disconnect(self,client, userdata, rc):
		print("Disconnected in a normal way")

	def control_c_handler(self,signum, frame):
		print('saw control-c')
		self.mqtt_client.disconnect()
		self.mqtt_client.loop_stop()
		print "Now I am done."
		self.led.write(1)
		sys.exit(0)

	def setup_mqtt(self):
		mqtt_client = paho.Client()

		# set up handlers
		mqtt_client.on_connect = self.on_connect
		mqtt_client.message_callback_add(self.mqtt_topic + "fork:" + fork1, self.on_message_fork1)
		mqtt_client.message_callback_add(self.mqtt_topic + "fork:" + fork2, self.on_message_fork2)
		mqtt_client.message_callback_add(self.mqtt_topic + "phil:" + philID, self.on_message_phil)
		mqtt_client.on_disconnect = self.on_disconnect

		mqtt_client.will_set(self.mqtt_topic, '______________Will of The Winterfell Philosopher _________________\n\n', 0, False)
		broker = 'sansa.cs.uoregon.edu'  # Boyana's server
		mqtt_client.connect(broker, '1883')
		mqtt_client.subscribe(self.mqtt_topic + "fork:" + fork1)
		mqtt_client.subscribe(self.mqtt_topic + "fork:" + fork2)
		mqtt_client.subscribe(self.mqtt_topic + "phil:" + philID)
		mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive
		return mqtt_client


	def get_led(self):
		led = mraa.Gpio(self.lightID+2)
		led.dir(mraa.DIR_OUT)
		led.write(1)
		return led

	def publish_msg(self,subtopic,msg):
		self.mqtt_client.publish(self.mqtt_topic+subtopic, msg)

	def run(self):
		while True:
			if self.isSitting and self.hasFork1 and self.hasFork2:
				# Eat, release forks, get up, and request to sitdown again
				print("EATING")
				self.led.write(0)
				self.publish_msg("phil:" + philID, "eating")
				time.sleep(randint(2,5))
				self.publish_msg("fork:" + self.fork1, "Phil:" + philID + ":ReleaseFork")
				self.publish_msg("fork:" + self.fork2, "Phil:" + philID + ":ReleaseFork")
				self.hasFork1 = False
				self.hasFork2 = False
				self.publish_msg("butler", "Phil:" + philID + ":GetUp")
				self.isSitting = False
				self.led.write(1)
				time.sleep(randint(4,10))
				self.publish_msg("butler", "Phil:" + philID + ":RequestSitdown")


if __name__ == "__main__":
	if len(sys.argv) != 5:
		print "wrong arguments!"
		sys.exit(-1)
	philID = sys.argv[1]
	fork1 = sys.argv[2]
	fork2 = sys.argv[3]
	lightID = int(sys.argv[4])
	Philosopher(philID,fork1,fork2,lightID).run()
