# -*- coding:utf-8 -*-
import time, sys
import paho.mqtt.client as paho
import signal
import mraa
from Queue import Queue


class Detector():
	def __init__(self):
		self.mqtt_topic = 'cis650/winterfell/VMEI:'
		self.mqtt_client = self.setup_mqtt()
		self.collision = False
		self.usedGrids = {0:-1, 1:-1, 2:-1, 3:-1}
		self.messageQueue = Queue()
		self.leds = []
		self.setupLEDs()
		self.leds[0].write(0)
		signal.signal(signal.SIGINT, self.control_c_handler)

	def on_connect(self, client, userdata, flags, rc):
		print('connected')

	def on_message(self, client, userdata, msg):
		if not self.collision:
			print(msg.payload)
			self.messageQueue.put(msg.payload)

	def on_disconnect(self, client, userdata, rc):
		print("Disconnected in a normal way")

	def control_c_handler(self, signum, frame):
		print('saw control-c')
		for led in self.leds:
			led.write(1)
		self.mqtt_client.disconnect()
		self.mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
		print "Now I am done."
		sys.exit(0)

	def setup_mqtt(self):
		mqtt_client = paho.Client()
		# set up handlers
		mqtt_client.on_connect = self.on_connect
		# mqtt_client.on_message = self.on_message
		mqtt_client.on_message = self.on_message
		mqtt_client.on_disconnect = self.on_disconnect
		broker = 'sansa.cs.uoregon.edu'  # Boyana's server
		mqtt_client.connect(broker, '1883')
		mqtt_client.subscribe(self.mqtt_topic)
		mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive
		return mqtt_client

	def setupLEDs(self):
		for i in range(2,10):
			led = mraa.Gpio(i)
			led.dir(mraa.DIR_OUT)
			self.leds.append(led)
			led.write(1)

	def processmessage(self, msg):
    # when get the passenger arrive information
    # format will be "ID:1" and "Leader:1"
		msgs = msg.split('|')

		if "Grid" in msgs[0]:
			carIndex = int(msgs[0][0])
			gridIndex = int(msgs[1])

			for i in self.usedGrids:
				if self.usedGrids[i] == carIndex:
					self.usedGrids[i] = -1

				if self.usedGrids[gridIndex] != -1:
					self.leds[0].write(1)
					self.leds[len(self.leds)-1].write(0)
					print "COLLISION"
					self.collision = True
				else:
					print "NO COLLISION"

	def run(self):
		while True:
			if self.messageQueue.qsize():
				self.processmessage(self.messageQueue.get())


if __name__ == "__main__":
	Detector().run()
