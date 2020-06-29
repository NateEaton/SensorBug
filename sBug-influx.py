# This program is free software: you can redistribute it and/or 
# modify it under the terms of the GNU General Public License as 
# published by the Free Software Foundation, either version 3 of 
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program.  If not, see 
# <http://www.gnu.org/licenses/>. bscan.py - Simple bluetooth LE 
# scanner and data extractor
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import ASYNCHRONOUS
import os
from bluepy.btle import Scanner, DefaultDelegate
import time
import struct
import emailout
#from mqtttest import writetoMQTT

debug = False

#Setup default email content
sendTo = 'terrylbradshaw@gmail.com'
emailSubject = "Garage Alert"
emailContent = "Better Check the garage."
sender = emailout.Emailer()

#Enter the MAC address of the sensor from the lescan
SENSOR_ADDRESS = ["ec:fe:7e:10:92:09"]
SENSOR_LOCATION = ["Garage"]
data = {'Battery':-99,'RSSI':-99,'Temperature':-99,'Light':-99,'Position':-99, 'Position_Int':-99}

_url = "http://192.168.1.167:8086"

client = InfluxDBClient(url=_url, token="my-token", org="my-org")
write_api = client.write_api(write_options=ASYNCHRONOUS)

class DecodeErrorException(Exception):
     def __init__(self, value):
         self.value = value

     def __str__(self):
         return repr(self.value)

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
#            print ("Discovered device", dev.addr)
            return
        elif isNewData:
#            print ("Received new data from", dev.addr)
            return

scanner = Scanner().withDelegate(ScanDelegate()) 
ManuDataHex = [] 
ReadLoop = True 
RetryCount = 0
ctime = 0

try:
        while (ReadLoop):
            devices = scanner.scan(2.0)
            ManuData = ""
            for dev in devices:
                entry = 0
                AcceleroData = 0
                AcceleroType = 0
                TempData = 0
                for saddr in SENSOR_ADDRESS:
                    entry += 1
                if (dev.addr == saddr):
                    print (" ")
                    print ("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
                    CurrentDevAddr = saddr
                    CurrentDevLoc = SENSOR_LOCATION[entry-1]
                    data['RSSI'] = dev.rssi
                    for (adtype, desc, value) in dev.getScanData():
#                        print (adtype)
                        print (" %s = %s" % (desc, value))
                        if (desc == "Manufacturer"):
                            ManuData = value
                    if (ManuData == ""):
                        print ("No data received, end decoding")
                        continue
                    #print (ManuData)
                    
                    for i, j in zip (ManuData[::2], ManuData[1::2]):
                         ManuDataHex.append(int(i+j, 16))

                    #Start decoding the raw Manufacturer data
                    if ((ManuDataHex[0] == 0x85) and (ManuDataHex[1] == 0x00)):
                        print ("Header byte 0x0085 found")
                    else:
                        print ("Header byte 0x0085 not found, decoding stop")
                        continue
                    
                    id=0
#                    while (id < len(ManuDataHex)):
#                         print ("ID: "  + str(id))
#                         print ("Data: " + hex(ManuDataHex[id]))
#                         id += 1

                    #Skip Major/Minor Index 5 is 0x3c, indicate 
                    #battery level and config #
                    if (ManuDataHex[4] == 0x3c):
                        BatteryLevel = ManuDataHex[5]
                        data['Battery'] = BatteryLevel
                        ConfigCounter = ManuDataHex[6]
                    idx = 7

                    #print "TotalLen: " + str(len(ManuDataHex))
                    while (idx < len(ManuDataHex)):
                       # print ("Idx: " + str(idx))
                       # print ("Data: " + hex(ManuDataHex[idx]))
#                        LightData = 0
                        if (ManuDataHex[idx] == 0x41):
                            #Accerometer data
                            idx += 1
                            AcceleroType = ManuDataHex[idx]
                            AcceleroData = ManuDataHex[idx+1]
#                            print (hex(AcceleroData))
                            if (AcceleroData == 0x20):
                                data['Position'] = 'Open'
                                data['Position_Int'] = 1
                            else:
                                data['Position'] = 'Closed'
                                data['Position_Int'] = 0
                            idx += 2
                        elif (ManuDataHex[idx] == 0x42):
                            #Light data
                            idx += 1
                            LightData = ManuDataHex[idx+1]
                            LightData += ManuDataHex[idx+2] * 0x100
                            LightData = LightData * (4000/4095)
                            data['Light'] = round(LightData)
                            idx += 3
                        elif (ManuDataHex[idx] == 0x43):
                            #Temperature data
                            idx += 1
                            TempData = ManuDataHex[idx]
                            TempData += ManuDataHex[idx+1] * 0x100
                            TempData = TempData * 0.0625
                            data['Temperature'] = (round(TempData,1) * 1.8) + 32
                            TempData = (TempData * 1.8) + 32
                            idx += 2
                        else:
                            idx += 1
                    if debug == True:
                        print ("Device Address: " + CurrentDevAddr)
                        print ("Device Location: " + CurrentDevLoc)
                        print ("Battery Level: " + str(BatteryLevel) + "%")
                        print ("Config Counter: " + str(ConfigCounter))
                        print ("Accelero Data: " + hex(AcceleroType) + " " + hex(AcceleroData))
                        print ("Light Data: " + str(round(LightData)))
                        print ("Temp Data: " + str(round(TempData,1)))
                    if time.localtime()[3] >= 22 and data['Position'] == 'Open':
                        if ctime == 0 or ctime >= 30:
                            #Sends an email to the "sendTo" address with the specified "emailSubject" as the subject and "emailContent" as the email content.
                            emailContent = emailContent + "<br> <br>" + "Garage Door is: " + "<b>" + data['Position'] + "</b>"
                            sender.sendmail(sendTo, emailSubject, emailContent)
                            ctime = 0
                        ctime += 1
                    else:
                        ctime = 0
                    for item in data:
                        _point = Point("Enviro").tag("location", "Home").field(item, data[item])
                        async_result = write_api.write(bucket="iot_test", record=_point)
                        
#                    writetoMQTT(data)

#                    ReadLoop = False
                    time.sleep(60)
            else:
               continue
               print ("btLE not found")
               RetryCount +=1
               if RetryCount > 3: ReadLoop = False
except DecodeErrorException:
    pass




