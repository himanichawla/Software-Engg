# -*- coding:utf-8 -*-
import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
import datetime
import random
import threading
from Queue import Queue
# import mraa


# Deal with control-c



#lanes : 0:0->2
         # 1:3->1
		# 2 :1->0
		# 3:2->3


################################### 0  1
################################### 2  3
# first straight and second is right
LaneDir2Grid = {0:([0,2],[0]),
                1: ([3, 1], [3]),

                2: ([1, 0], [1]),

                3: ([2, 3], [2]),
                }



class Car():
	def __init__(self, ID):
		self.ID = int(ID)
		self.mqtt_topic = 'cis650/winterfell/VMEI:'  # don't change this or you will screw it up for others
		self.mqtt_client = self.setup_mqtt()
		# self.OutofContention = False
		self.TimeStamp = None
		self.HighList = set()
		self.LowList = set()
		self.initLowList()
		self.Permission = set()
		self.grids = set()
		self.InContension = False
		signal.signal(signal.SIGINT, self.control_c_handler)

	def on_connect(self, client, userdata, flags, rc):
		print('connected')

	def on_message(self, client, userdata, msg):
		# print('on_message')
		# print(msg.topic)
		print(msg.payload)
		self.processmessage(msg.payload)


	def on_disconnect(self, client, userdata, rc):
		print("Disconnected in a normal way")

	# graceful so won't send will


	def control_c_handler(self, signum, frame):
		print('saw control-c')
		self.mqtt_client.disconnect()
		self.mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
		print "Now I am done."
		sys.exit(0)
	# just loop forever (or until ctrl-c)

	def setup_mqtt(self):
		mqtt_client = paho.Client()
		# set up handlers
		mqtt_client.on_connect = self.on_connect
		mqtt_client.on_message = self.on_message
		# mqtt_client.message_callback_add(self.mqtt_topic , self.on_message)
		mqtt_client.on_disconnect = self.on_disconnect
		mqtt_client.will_set(self.mqtt_topic, '______________Will of The Winterfell Monitor _________________\n\n', 0,False)
		broker = 'sansa.cs.uoregon.edu'  # Boyana's server
		mqtt_client.connect(broker, '1883')
		mqtt_client.subscribe(self.mqtt_topic)  # subscribe to all students in class
		mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive
		return mqtt_client


	def initLowList(self):
		for i in xrange(4):
			if i != self.ID:
				self.LowList.add(i)

	def pulish_msg(self,topic,msg):
		self.mqtt_client.publish(topic,msg)

	def processmessage(self, msg):
		msgs = msg.strip().split('|')
		if len(msgs) >= 3:
			if int(msgs[0]) != self.ID: #not going to process message from self
				if msgs[2] == "request":
					#get request
					if self.TimeStamp == None:
						#format "sender|receiver|permission"
						m = "%s|%s|permission"%(str(self.ID),msgs[0])
						self.pulish_msg(self.mqtt_topic,m)
					else:
						# no grids conflict
						if len(set(self.grids).intersection(eval(msgs[3]))) == 0:
							m = "%s|%s|permission" % (str(self.ID),msgs[0])
							self.pulish_msg(self.mqtt_topic, m)
						else:
							if str(self.TimeStamp) > msgs[1]: #late
								m = "%s|%s|permission" % (str(self.ID),msgs[0])
								self.pulish_msg(self.mqtt_topic, m)
							elif str(self.TimeStamp) == msgs[1]: #late
								if self.ID < int(msgs[0]):
									m = "%s|%s|permission" % (str(self.ID),msgs[0])
									self.pulish_msg(self.mqtt_topic, m)
								else:
									m = "%s|%s|rejection" % (str(self.ID),msgs[0])
									self.pulish_msg(self.mqtt_topic, m)
									self.HighList.add(int(msgs[0]))
							else:
								m = "%s|%s|rejection" % (str(self.ID),msgs[0])
								self.pulish_msg(self.mqtt_topic, m)
								self.HighList.add(int(msgs[0]))
				elif msgs[2] == "permission":
					# self.Permission.add(int(msgs[1]))
					# if len(self.Permission) == 3:
					# 	pass#go
					if msgs[1] == str(self.ID):
						self.LowList.remove(int(msgs[0]))
						if len(self.LowList) == 0:
							# self.enterIntersection()
							threading.Thread(target=self.enterIntersection).start()
				elif msgs[2] == "rejection":
					# self.LowList.add(int(msgs[1]))
					pass
		else:
			# print msg
			pass
	def enterIntersection(self):
		self.pulish_msg(self.mqtt_topic,str(self.ID)+"Entered|" + str(datetime.datetime.now()))
		for i in self.grids:
			self.pulish_msg(self.mqtt_topic, str(self.ID) + "Grid|" + str(i))
			time.sleep(5)

		self.cleanup()

	def cleanup(self):
		self.pulish_msg(self.mqtt_topic,str(self.ID) + "Exited|" + str(datetime.datetime.now()))
		for i in self.HighList:
			msg = "%s|%s|permission" % (str(self.ID),str(i))
			self.pulish_msg(self.mqtt_topic, msg)
		self.TimeStamp = None
		self.HighList = set()
		self.LowList = set()
		self.initLowList()
		self.Permission = set()
		self.grids = set()
		self.InContension= False

	def sendrequest(self):
		# format (ID|timestamp|request|grids)
		self.TimeStamp = datetime.datetime.now()
		msg = "%s|%s|request|%s"%(str(self.ID),str(self.TimeStamp),str(set(self.grids)))
		self.pulish_msg(self.mqtt_topic,msg)

	def run(self):
		# enter the intersection and wait until every one is already.
		time.sleep(4)
		while True:
			if not self.InContension:
				time.sleep(0.5)
				if random.randrange(0,10)>8:
					lane = random.randrange(0,4)
					# lane = 0
					direction = random.randrange(0,2)
					# direction = 0
					self.grids = LaneDir2Grid[lane][direction]
					self.InContension = True
					self.sendrequest()
			else:
				pass
def main(ID):
	Car(ID).run()


if __name__ == "__main__":
	if len(sys.argv) != 2:
		print "Arguements are not correct!"
		sys.exit(-1)
	ID = sys.argv[1]
	main(ID)