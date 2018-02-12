# -*- coding:utf-8 -*-
import time, sys
import paho.mqtt.client as paho
import signal
from Queue import Queue


class Message():
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload

    def getPayload(self):
        return self.payload

    def getTopic(self):
        return self.topic


class NodeCheatDetector():
    def __init__(self, maxNodes):
        self.maxNodes = maxNodes
        self.mqtt_topic_base = 'cis650/winterfell/ring/node:'
        self.mqtt_client = self.setup_mqtt()
        self.cheaterDetected = False
        self.maxReceived = [x for x in range(0, self.maxNodes)]
        self.messageQueue = Queue()
        signal.signal(signal.SIGINT, self.control_c_handler)

    def on_connect(self, client, userdata, flags, rc):
        print('connected')

    def on_message(self, client, userdata, msg):
        if not self.cheaterDetected:
            print('on_message')
            print(msg.topic)
            print(msg.payload)
            self.messageQueue.put(Message(msg.topic, msg.payload))

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected in a normal way")

    def control_c_handler(self, signum, frame):
        print('saw control-c')
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
        # subscribe to all topics
        for i in range(0, self.maxNodes):
            mqtt_client.subscribe(self.mqtt_topic_base + str(i))

        mqtt_client.loop_start()  # just in case - starts a loop that listens for incoming data and keeps client alive
        return mqtt_client

    def publish_msg(self, topic, msg):
        self.mqtt_client.publish(topic, msg)

    def processmessage(self, msg):
        # when get the passenger arrive information
        # format will be "ID:1" and "Leader:1"
        msgs = msg.getPayload().split(':')
        recID = int(msg.getTopic().split(':')[1])
        senderBestID = int(msgs[1])
        senderID = (recID-1) % self.maxNodes

        if msgs[0] == "ID":
            self.maxReceived[recID] = max(self.maxReceived[recID], senderBestID)

            if self.maxReceived[senderID] > senderBestID:
                print "CHEATER"
                print "Probably Node:"+str(senderID)
                self.cheaterDetected = True


    def run(self):
        while True:
            if self.messageQueue.qsize():
                self.processmessage(self.messageQueue.get())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Arguments are not correct!"
        sys.exit(-1)
    maxNodes = int(sys.argv[1])
    NodeCheatDetector(maxNodes).run()
