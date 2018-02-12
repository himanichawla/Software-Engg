#-*- coding:utf-8 -*-
import time, socket, sys
from datetime import datetime as dt
import paho.mqtt.client as paho
import signal
from Queue import Queue
# import updatefsm
from PyQt4 import QtGui, QtCore,uic
from PyQt4.QtCore import  *
from PyQt4.QtGui import *
# from PyQt4.QtCore.form import  Ui
import os


Dict = {'set([0, 2])': (0,'s'),'set([0])':(0,'r'),'set([1, 3])':(1,'s'),'set([3])':(1,'r'),'set([0, 1])':(2,'s'),'set([1])':(2,'r'),'set([2, 3])':(3,'s'),'set([2])':(3,'r')}

LaneIndex = {0:1,1:14,2:7,3:8}
Inter2Lane = {1:0,14:1,7:2,8:3}
GridIndex = {0:5,1:6,2:9,3:10}

# }
# {0:([0,2],[0]),
#                 1: ([3, 1], [3]),
#
#                 2: ([1, 0], [1]),
#
#                 3: ([2, 3], [2]),
#                 }



class Vis(QtGui.QWidget):
	trigger = pyqtSignal()

	def __init__(self):
		super(Vis, self).__init__()
		self.__init__UI()

	def __init__UI(self):
		QObject.__init__(self)
		# QtGui.QWidget.__init__(self,parent=parent)
		# self.ui = Ui
		self.failState = False
		self.q = Queue()
		self.mqtt_topic = 'cis650/winterfell/VMEI:'
		self.mqtt_client = self.setup_mqtt()
		signal.signal(signal.SIGINT, self.control_c_handler)
		self.Inter = [[],[],[],[]]
		self.CarPos = {0:None,1:None,2:None,3:None}
		self.trigger.connect(self.Op)
		self.CarDir= {0:None,1:None,2:None,3:None}

	def on_connect(self,client, userdata, flags, rc):
		print('connected')

	def on_message(self, client, userdata, msg):
		# print('on_message')
		# print(msg.topic)
		# print(msg.payload)
		self.q.put(msg.payload)
		# self.trigger.emit()



	def on_disconnect(self,client, userdata, rc):
		print("Disconnected in a normal way")

	def control_c_handler(self,signum, frame):
		print('saw control-c')
		self.mqtt_client.disconnect()
		self.mqtt_client.loop_stop()
		print "Now I am done."
		sys.exit(0)

	@pyqtSlot()
	def quit(self):
		self.mqtt_client.disconnect()
		self.mqtt_client.loop_stop()

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
	# @pyqtSlot()
	# def reloadimage(self):
	# 	pixmap = QPixmap("partb.png")
	# 	self.label.setPixmap(pixmap)
	# 	self.w.resize(pixmap.width(), pixmap.height())
	# def paintEvent(self, e):
	#
	# 	qp = QtGui.QPainter()
	# 	qp.begin(self)
	# 	self.drawLines(qp)
	# 	qp.end()
	#
	#
	# def drawLines(self,qp):
	# 	pass
	# 	# size = self.box
	# 	# qp.setPen(QtCore.Qt.black)
	# 	# for i in range(1,4,1):
	# 	# 	qp.drawLine(0,size.height()/4*i,size.width(),size.height()/4*i)
	# 	# 	qp.drawLine(size.width()/4*i, 0 ,size.width()/4*i,size.height())

	def MoveOfCar(self,CarID,src,dst):
		now = self.carpos[CarID]
		if now != src:
			print "wrong pos!"
			sys.exit(-1)
		self.labels[now].setStyleSheet("QLabel { background-color : black; color : blue; }")
		self.labels[now].setText("")
		self.labels[dst].setStyleSheet("QLabel { background-color : red; color : blue; }")
		self.labels[dst].setText(CarID)
		self.carpos[CarID] = dst

	def aaa(self,labels):
		self.labels[8].setStyleSheet("QLabel { background-color : black; color : blue; }")
		self.labels[9].setStyleSheet("QLabel { background-color : red; color : blue; }")

	def Init_variables(self):
		# self.carpos = {"0":1,"1":7,"2":8,"3":14}
		self.poses = [(i,j) for i in range(4) for j in range(4)]
		f = QLabel
		self.labels = [f() for i in xrange(16)]
		for pos,label in zip(self.poses,self.labels):
			self.grid.addWidget(label,*pos)
		qf = QtGui.QFont("Times", 24, QtGui.QFont.Bold)
		# count = 0
		for i in self.labels:
			i.setStyleSheet("QLabel { background-color : black; color : blue; }")
			i.setAlignment(QtCore.Qt.AlignCenter)
			i.setFont(qf)
			# i.setText("")
			# count += 1
		self.Boards = [f() for i in xrange(16)]
		for pos,Board in zip(self.poses,self.Boards):
			self.BoardLayout[pos[0]].addWidget(Board)
			for i in self.Boards:
				i.setStyleSheet("QLabel { background-color : Green; color : blue; }")
				i.setAlignment(QtCore.Qt.AlignCenter)
				i.resize(i.width(),10)
				i.setFont(qf)
			for i in [0,4,8,12]:
				self.Boards[i].setText(str(i/4))
				self.Boards[i].setStyleSheet("QLabel { background-color : pink; color : blue; }")
			for i in range(4):
				c = [j for j in range(4) if j!= i]
				for k in range(1,4):
					self.Boards[i*4+k].setText(str(c[k-1]))
	@pyqtSlot()
	def Op(self):
		if self.q.qsize():
			msg =  self.q.get()
			self.processmsg(msg)
	def processmsg(self,msg):
		print msg
		if "request" in msg:
			msgs = msg.split('|')
			ID = int(msgs[0])
			pos = LaneIndex[Dict[msgs[3]][0]]
			self.CarPos[ID] = pos
			self.CarDir[ID] = Dict[msgs[3]][1]
			self.Inter[Dict[msgs[3]][0]].append(ID)
			s = ";".join([str(i)+self.CarDir[i] for i in self.Inter[Inter2Lane[pos]]])
			self.labels[pos].setText(s)
			self.labels[pos].setStyleSheet("QLabel { background-color : red; color : blue; }")

		elif "Grid" in msg:
			ID = int(msg[0])
			# for i in self.Inter:
			# 	if ID in i:
			# 		i.remove(ID)
			# 		pos_lane = LaneIndex[self.Inter.index(i)]
			# 		self.labels[pos_lane].setText(";".join([str(j) for j in i]))
			# 		if len(i) == 0:
			# 			self.labels[pos_lane].setStyleSheet("QLabel { background-color : black; color : blue; }")
			# 		break
			pos_old = self.CarPos[ID]
			pos_new = GridIndex[int(msg.split("|")[1])]
			if pos_old in [1, 7, 8, 14]:
				InterInd = Inter2Lane[pos_old]
				i = self.Inter[InterInd]
				i.remove(ID)
				pos_lane = LaneIndex[InterInd]
				self.labels[pos_lane].setText(";".join([str(j)+self.CarDir[j] for j in i]))
				if len(i) == 0:
					self.labels[pos_lane].setStyleSheet("QLabel { background-color : black; color : blue; }")
				self.labels[pos_new].setText(str(ID) + self.CarDir[ID])
				self.labels[pos_new].setStyleSheet("QLabel { background-color : red; color : blue; }")
			elif pos_old in [5,6,9,10]:
				self.labels[pos_new].setText(str(ID) + self.CarDir[ID])
				self.labels[pos_new].setStyleSheet("QLabel { background-color : red; color : blue; }")
				self.labels[pos_old].setText("")
				self.labels[pos_old].setStyleSheet("QLabel { background-color : black; color : blue; }")
			self.CarPos[ID] = pos_new

		elif "Exit" in msg:
			ID = int(msg[0])
			pos_old = self.CarPos[ID]
			self.labels[pos_old].setText("")
			self.labels[pos_old].setStyleSheet("QLabel { background-color : black; color : blue; }")
			self.CarPos[ID] = None
			self.CarDir[ID] = None
			for i in range(ID*4+1 ,ID*4 + 4):
				self.Boards[i].setStyleSheet("QLabel { background-color : green; color : blue; }")
		elif "permission" in msg:
			sender =  int(msg.split('|')[0])
			receiver = int(msg.split('|')[1])
			ind = [i for i in xrange(4) if i != receiver].index(sender)
			self.Boards[4*receiver+ind+1].setStyleSheet("QLabel { background-color : yellow; color : blue; }")
		# elif "rejection" in msg:


	def run(self):
		# self.w = QWidget()
		self.resize(600,300)
		self.setWindowTitle("Vis")
		self.grid = QGridLayout()
		self.BoardLayouts = QVBoxLayout()
		self.BoardLayout = [QHBoxLayout(),QHBoxLayout(),QHBoxLayout(),QHBoxLayout()]
		for i in xrange(4):
			self.BoardLayouts.addLayout(self.BoardLayout[i])
		self.Init_variables()
		# for i in xrange(4):
		# 	self.HL0.addWidget(ff[4*i + 0])
		# 	self.HL1.addWidget(ff[4*i + 1])
		# 	self.HL2.addWidget(ff[4*i + 2])
		# 	self.HL3.addWidget(ff[4*i + 3])
		for i in [0,3,12,15]:
			self.labels[i].setStyleSheet("QLabel { background-color : white; color : blue; }")
			self.labels[i].setText("")
		for i in [2,4,11,13]:
			self.labels[i].setStyleSheet("QLabel { background-color : orange; color : blue; }")
			self.labels[i].setText("")
		self.all = QVBoxLayout()
		self.bt = QHBoxLayout()
		btn = QPushButton("Next")
		btn.clicked.connect(self.Op)
		self.bt.addWidget(btn)

		self.UP = QHBoxLayout()
		self.UP.addLayout(self.BoardLayouts)
		self.UP.addLayout(self.grid)
		self.all.addLayout(self.UP)
		self.all.addLayout(self.bt)
		self.setLayout(self.all)
		self.show()



if __name__ == "__main__":
	app = QtGui.QApplication(sys.argv)
	window = Vis()
	app.aboutToQuit.connect(window.quit)
	# window.show()
	window.run()
	# window.show()
	sys.exit(app.exec_())
