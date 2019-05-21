#!/usr/bin/python

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import time
import sys
import datetime
import logging
from Adafruit_IO import *

__all__ = ['writetoMQTT', '__all__']

mqttLogger = logging.getLogger('__main__')

def connected(client):
	mqttLogger.info('Connected to Adafruit IO!')


mqtt = MQTTClient('tlbradshaw','4551326023d44215bc73c6367ad1b8f0')
#aio = Client('tlbradshaw','4551326023d44215bc73c6367ad1b8f0')

mqtt.on_connect = connected

mqtt.connect()
mqtt.loop_background()


def writetoMQTT(data):
#	for k,v in data.items():
#		print (k + ': ' +str(v))
#	mqttLogger.debug(data)
	try:
		if data['temperature'] != -99:
			mqtt.publish('home-garage-temperature',round(data['temperature']*1.8 + 32,1))
#			mqtt.publish('home-temperature', data['temperature']) 
#			aio.send('home-garage-temperature', round(data['temperature']*1.8 +32, 1))
			mqttLogger.debug('Message posted to MQTT.')
		if data['light'] != -99:
			mqtt.publish('home-garage-light', data['light'])
#			aio.send('home-garage-light',data['light'])
	except:
		pass
	try:
		if data['position'] != -99:
			mqtt.publish('home-garage-position',data['position'])
		if data['battery'] != -99:
			mqtt.publish('home-garage-battery',data['battery'])
		if data['RSSI'] != -99:
			mqtt.publish('home-garage-signal',data['RSSI'])
#			aio.send('home-garage-position', data['position'])
	except:
		pass

		#python3 aws-iot-device-sdk-python/samples/basicPubSub/basicPubSub.py -e a994nyueonve9-ats.iot.us-east-1.amazonaws.com -r root-CA.crt -c Garage_Pi.cert.pem -k Garage_Pi.private.key
