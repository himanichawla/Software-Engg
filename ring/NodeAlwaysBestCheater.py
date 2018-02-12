# -*- coding:utf-8 -*-
import time, sys
import paho.mqtt.client as paho
import signal
import mraa


class Node():
    def __init__(self, ID, NID):
        self.ID = int(ID)
        self.NID = int(NID)
        self.mqtt_topic_self = 'cis650/winterfell/ring/node:' + str(
            self.ID)  # don't change this or you will screw it up for others
        self.mqtt_topic_next = 'cis650/winterfell/ring/node:' + str(self.NID)
        self.mqtt_client = self.setup_mqtt()
        self.leds = self.get_led()
        self.OutofContention = False
        signal.signal(signal.SIGINT, self.control_c_handler)

    def on_connect(self, client, userdata, flags, rc):
        print('connected')

    def on_message(self, client, userdata, msg):
        print('on_message')
        print(msg.topic)
        print(msg.payload)
        self.processmessage(msg.payload)

    def on_disconnect(self, client, userdata, rc):
        print("Disconnected in a normal way")

    def control_c_handler(self, signum, frame):
        print('saw control-c')
        self.mqtt_client.disconnect()
        self.mqtt_client.loop_stop()  # waits until DISCONNECT message is sent out
        print "Now I am done."

        [i.write(1) for i in self.leds]
        sys.exit(0)

    def setup_mqtt(self):
        mqtt_client = paho.Client()

        # set up handlers
        mqtt_client.on_connect = self.on_connect
        mqtt_client.message_callback_add(self.mqtt_topic_self, self.on_message)
        mqtt_client.on_disconnect = self.on_disconnect

        mqtt_client.will_set(self.mqtt_topic_self, '______________Will of The Winterfell Monitor _________________\n\n',
                             0,
                             False)
        broker = 'sansa.cs.uoregon.edu'
        mqtt_client.connect(broker, '1883')
        mqtt_client.subscribe(self.mqtt_topic_self)
        mqtt_client.subscribe(self.mqtt_topic_next)
        mqtt_client.loop_start()
        return mqtt_client

    def get_led(self):
        leds = []
        for i in range(2, 5):
            led = mraa.Gpio(i)
            led.dir(mraa.DIR_OUT)
            led.write(1)
            leds.append(led)
        return leds

    def pulish_msg(self, topic, msg):
        self.mqtt_client.publish(topic, msg)

    def processmessage(self, msg):
        # when get the passenger arrive information
        # format will be "ID:1" and "Leader:1"
        msgs = msg.split(':')

        if msgs[0] == "Leader":
            if int(msgs[1]) == self.ID:
                self.OutofContention = True
                for i in self.leds:
                    i.write(1)
                self.leds[2].write(0)
                pass
            else:
                self.pulish_msg(self.mqtt_topic_next, msg)
                self.OutofContention = True
                for i in self.leds:
                    i.write(1)
                self.leds[1].write(0)
        else:
            pass

    def run(self):
        # self.led.write(1)
        self.leds[0].write(0)  # means no leader formed
        while True:
            time.sleep(4)
            if not self.OutofContention:
                self.pulish_msg(self.mqtt_topic_next, "ID:" + str(self.ID))


def main(ID, NID):
    Node(ID, NID).run()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Arguements are not correct!"
        sys.exit(-1)
    ID, NID = sys.argv[1], sys.argv[2]
    main(ID, NID)
