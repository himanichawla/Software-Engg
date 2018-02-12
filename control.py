import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
from Queue import Queue
import mraa
# Deal with control-c







class Control():
	def __init__(self):
		self.mqtt_topic = 'cis650/winterfell'  # don't change this or you will screw it up for others
		self.mqtt_client = self.setup_mqtt()
		self.leds = self.get_leds()
		self.passenger = 0
		self.queue = Queue()
		self.FullFlag = False
		self.CarIn = [True,True]
		self.maxpassengernumber = 3
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
                for i in self.leds:
                    i.write(1)
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


	def get_leds(self):
		leds = []
		for i in range(2,10):
			led = mraa.Gpio(i)
			led.dir(mraa.DIR_OUT)
			leds.append(led)
		return leds


	def publish_msg(self,msg):
		self.mqtt_client.publish(self.mqtt_topic, msg)

	def processmessage(self,msg):
		if msg == "TERMINAL:Passenger arrives":   #when get the passenger arrive information
			if not self.FullFlag:
				self.passenger += 1
				if self.passenger >= self.maxpassengernumber:
					self.FullFlag = not self.FullFlag
					self.publish_msg("FULL")
					#if any(self.carIn):
					self.publish_msg("PickupReady")
				for i in self.leds[:self.passenger]:
					i.write(0)


		# when get the pickupinformation
		elif "RequestPickup" in msg:
			'''
			things to do:
			'''
			if self.FullFlag: #only when the passengers are full to pick up
				slices = msg.split(':')
				slices[-1] =  "PickupGranted"
				#self.CarIn[int(slices[1])] = False
				self.publish_msg(':'.join(slices))
				self.publish_msg("EMPTY")
				self.FullFlag = False
				self.passenger = 0
				for led in self.leds:
					led.write(1)
			# elif msg == "2":
			# 	print msg


		#when get the arrive information
		elif "Arrived" in msg:
                        #self.carIn(int(msg.split(':')[1])) = True
			if self.FullFlag:
				self.publish_msg("PickupReady")



	def run(self):
		for i in self.leds:
		 	i.write(1)
		while True:
			if self.queue.qsize():
				self.processmessage(self.queue.get())


def main():
	Control().run();



if __name__ == "__main__":
	main();
