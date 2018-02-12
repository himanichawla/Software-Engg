# -*- coding:utf-8 -*-
import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
from Queue import Queue
import mraa


# Deal with control-c







class Node():
	def __init__(self, ID,NID):
		self.ID = int(ID)
		self.NID = int(NID)
		self.mqtt_topic_self = 'cis650/winterfell/ring/node:' + str(self.ID)  # don't change this or you will screw it up for others
		self.mqtt_topic_next = 'cis650/winterfell/ring/node:' + str(self.NID)
		self.mqtt_client = self.setup_mqtt()
		self.leds = self.get_led()
	# self.queue = Queue()
		self.OutofContention = False
		signal.signal(signal.SIGINT, self.control_c_handler)

	def on_connect(self, client, userdata, flags, rc):
		print('connected')

	def on_message(self, client, userdata, msg):
		print('on_message')
		print(msg.topic)
		print(msg.payload)
		# self.queue.put(msg.payload)
		self.processmessage(msg.payload)
	def on_disconnect(self, client, userdata, rc):
		print("Disconnected in a normal way")

	# graceful so won't send will

	# Instantiate the MQTT client

	def control_c_handler(self, signum, frame):
		print('saw control-c')
		self.mqtt_client.disconnect()
		self.mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
		print "Now I am done."

		[i.write(1) for i in self.leds]
		sys.exit(0)
	# just loop forever (or until ctrl-c)

	def setup_mqtt(self):
		mqtt_client = paho.Client()

		# set up handlers
		mqtt_client.on_connect = self.on_connect
		# mqtt_client.on_message = self.on_message
		mqtt_client.message_callback_add(self.mqtt_topic_self , self.on_message)
		mqtt_client.on_disconnect = self.on_disconnect

		mqtt_client.will_set(self.mqtt_topic_self, '______________Will of The Winterfell Monitor _________________\n\n', 0,
		                     False)
		broker = 'sansa.cs.uoregon.edu'  # Boyana's server
		mqtt_client.connect(broker, '1883')
		mqtt_client.subscribe(self.mqtt_topic_self)  # subscribe to all students in class
		mqtt_client.subscribe(self.mqtt_topic_next)
		mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive
		return mqtt_client

	def get_led(self):
		leds = []
		for i in range(2,5):
			led = mraa.Gpio(i)
			led.dir(mraa.DIR_OUT)
			led.write(1)
			leds.append(led)
		return leds

	# def publish_msg(self, msg):
	# 	self.mqtt_client.publish(self.mqtt_topic, self.MsgHead + msg)

	def pulish_msg(self,topic,msg):
		self.mqtt_client.publish(topic,msg)

	def processmessage(self, msg):
		# when get the passenger arrive information
        # format will be "ID:1" and "Leader:1"
		msgs = msg.split(':')
		# print msg[1]
		if msgs[0] == "ID" :
			if int(msgs[1]) == self.ID:
				print "I am the leader!"
				self.pulish_msg(self.mqtt_topic_next,"Leader:" + str(self.ID))
				# self.OutofContention = False

				self.OutofContention = True

			else:
				m = max(self.ID,int(msgs[1]))
				self.pulish_msg(self.mqtt_topic_next, "ID:" + str(m))
				if m > self.ID:
					self.OutofContention = True
					for i in self.leds:
						i.write(1)
					self.leds[1].write(0)

		elif msgs[0] == "Leader":
			if int(msgs[1]) == self.ID:
				# self.pulish_msg(self.mqtt_topic_next,"Leader:" + str(self.ID))
				# self.GotLeader = True
				self.OutofContention = True
				for i in self.leds:
					i.write(1)
				self.leds[2].write(0)
				pass
			else:
				self.pulish_msg(self.mqtt_topic_next, msg)
				# self.G = True
				self.OutofContention = True
				for i in self.leds:
					i.write(1)
				self.leds[1].write(0)
		else:
			pass

		# if msgs[2] == "RequestFork":  # this is request pick up
		# 	if not self.pickedup:
		# 		self.publish_msg("PickedUpByPhil:" + msgs[1])
		# 		self.pickedup = True
		# 		self.led.write(0)
		# 	else:
		# 		self.halt.append(msg)
		# elif msgs[2] == "ReleaseFork":  # this is dropdown
		# 	if self.pickedup:
		# 		self.publish_msg("SettledDownByPhil:" + msgs[1])
		#
		# 		self.publish_msg("SettledDownByPhil:" + msgs[1])
		#
		# 		while self.halt != []:
		# 			self.queue.put(self.halt.pop())
		# 		self.pickedup = False
		# 		self.led.write(1)
		# else:
		# 	# print "cannot recognize this!"
		# 	return

	def run(self):
		# self.led.write(1)
		self.leds[0].write(0) # means no leader formed
		while True:

			# if self.queue.qsize():
			# 	self.processmessage(self.queue.get())
			time.sleep(4)
			if not self.OutofContention:
				self.pulish_msg(self.mqtt_topic_next,"ID:"+ str(self.ID))

def main(ID,NID):
	Node(ID,NID).run()


if __name__ == "__main__":
	if len(sys.argv) != 3:
		print "Arguements are not correct!"
		sys.exit(-1)
	ID,NID = sys.argv[1],sys.argv[2]
	main(ID,NID)
