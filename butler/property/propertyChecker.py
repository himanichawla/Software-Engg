#-*- coding:utf-8 -*-
import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
import updatefsm
from PyQt4 import QtGui, QtCore,uic
from PyQt4.QtCore import  *
from PyQt4.QtGui import *
# from PyQt4.QtCore.form import  Ui
import os

class Property(QObject):

	trigger = pyqtSignal()
	def __init__(self,parent = None):
		QObject.__init__(self)
		# QtGui.QWidget.__init__(self,parent=parent)
		# self.ui = Ui
		self.failState = False
		self.currentState = 0
		self.mqtt_topic = 'cis650/winterfell/'
		self.mqtt_client = self.setup_mqtt()
		self.trigger.connect(self.reloadimage)
		signal.signal(signal.SIGINT, self.control_c_handler)

	def on_connect(self,client, userdata, flags, rc):
		print('connected')

	def on_message_phil(self,client,userdata,msg):
		print(msg.payload)
		vals = msg.payload.split(":")
		if vals[0] == "SitdownGranted":
			print "-----------------sitdown------------------------"
			if not self.failState and self.currentState == 0:
				self.currentState = 1
			else:
				self.currentState = -1
				self.failState = True
			updatefsm.changepartbpng(self.currentState)
			# self.reloadimage()
			# self.w.update()
			self.trigger.emit()

	def on_message_butler(self,client,userdata,msg):
		print(msg.payload)
		vals = msg.payload.split(":")
		if vals[0] == "Phil" and vals[1] == "2" and vals[2] == "GetUp":
			print "-----------------phil1 get up----------------------"
			if not self.failState and self.currentState == 1:
				self.currentState = 0
			else:
				self.currentState = -1
				self.failState = True
			updatefsm.changepartbpng(self.currentState)
			# self.reloadimage()
			# self.w.update()
			self.trigger.emit()
	def on_disconnect(self,client, userdata, rc):
		print("Disconnected in a normal way")

	def control_c_handler(self,signum, frame):
		print('saw control-c')
		self.mqtt_client.disconnect()
		self.mqtt_client.loop_stop()
		print "Now I am done."
		sys.exit(0)

	def setup_mqtt(self):
		mqtt_client = paho.Client()

		# set up handlers
		mqtt_client.on_connect = self.on_connect
		mqtt_client.message_callback_add(self.mqtt_topic + "butler", self.on_message_butler)
		mqtt_client.message_callback_add(self.mqtt_topic + "phil:1", self.on_message_phil)
		mqtt_client.on_disconnect = self.on_disconnect

		mqtt_client.will_set(self.mqtt_topic, '______________Will of The Winterfell Philosopher _________________\n\n', 0, False)
		broker = 'sansa.cs.uoregon.edu'  # Boyana's server
		mqtt_client.connect(broker, '1883')
		mqtt_client.subscribe(self.mqtt_topic + "phil:1")
		mqtt_client.subscribe(self.mqtt_topic + "butler")
		mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive
		return mqtt_client
	@pyqtSlot()
	def reloadimage(self):
		pixmap = QPixmap("partb.png")
		self.label.setPixmap(pixmap)
		self.w.resize(pixmap.width(), pixmap.height())

	def run(self):
		# while True:
		# 	pass
		# app = QApplication(sys.argv)
		self.w = QWidget()
		self.w.setWindowTitle("PyQT4 Pixmap @ pythonspot.com ")

		# Create widget
		self.label = QLabel(self.w)
		pixmap = QPixmap("partb.png")
		self.label.setPixmap(pixmap)
		self.w.resize(pixmap.width(), pixmap.height())
		# Draw window
		self.w.show()



if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = Property()
	# window.show()
	window.run()
	# window.show()
	sys.exit(app.exec_())