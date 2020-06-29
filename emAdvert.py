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
from bluepy.btle import Scanner, DefaultDelegate
import time
#import pymysql
import struct
from mqtttest import writetoMQTT

hostname = 'localhost'
username = 'datasrc'
password = 'datasrc000'
database = 'bleSensor'

#Enter the MAC address of the sensor from the lescan
SENSOR_ADDRESS = ["b0:b4:48:dc:1f:9a"]
SENSOR_LOCATION = ["Elemental Machine"]
data = {'battery':-99,'RSSI':-99,'temperature':-99,'light':-99,'position':-99}

class DecodeErrorException(Exception):
     def __init__(self, value):
         self.value = value

     def __str__(self):
         return repr(self.value)

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        return
        if isNewDev:
            print ("Discovered device", dev.addr)
        elif isNewData:
            print ("Received new data from", dev.addr)

    def doQueryInsert (conn, addr, loc, temp, accero):

        #blesensor table is date, time, addr, location, temp, accero
#        cur = conn.cursor()
        dostr = 'INSERT INTO data VALUES (CURRENT_DATE(), NOW(), %s, %s, %s, %s);'
#6        cur.execute (dostr, (addr, loc, temp, accero))
#        conn.commit() 

scanner = Scanner().withDelegate(ScanDelegate()) 
#        myConnection = pymysql.connect (host=hostname, user=username, passwd=password, db=database) 
ManuDataHex = [] 
ReadLoop = True 
RetryCount = 0

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
#                    print ("Looking for %s, Found %s)" % (saddr, dev.addr))
                if (dev.addr == saddr):
                    print ("Found Sensor")
                    print ("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
                    CurrentDevAddr = saddr
                    CurrentDevLoc = SENSOR_LOCATION[entry-1]
                    data['RSSI'] = dev.rssi
                    for (adtype, desc, value) in dev.getScanData():
                        print (adtype)
                        print (" %s = %s" % (desc, value))
                        if (desc == "Manufacturer"):
                            ManuData = value
                    if (ManuData == ""):
                        print ("No data received, end decoding")

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
                        data['battery'] = BatteryLevel
                        ConfigCounter = ManuDataHex[6]
                    idx = 7

                    #print "TotalLen: " + str(len(ManuDataHex))
                    while (idx < len(ManuDataHex)):
                       # print ("Idx: " + str(idx))
                       # print ("Data: " + hex(ManuDataHex[idx]))
                        
                        if (ManuDataHex[idx] == 0x41):
                            #Accerometer data
                            idx += 1
                            AcceleroType = ManuDataHex[idx]
                            AcceleroData = ManuDataHex[idx+1]
#                            print (hex(AcceleroData))
                            if (AcceleroData == 0x20):
                                data['position'] = 'Open'
                            else:
                                data['position'] = 'Closed'
                            idx += 2
                        elif (ManuDataHex[idx] == 0x42):
                            #Light data
                            idx += 1
                            LightData = ManuDataHex[idx+1]
                            LightData += ManuDataHex[idx+2] * 0x100
                            LightData = LightData * (4000/4095)
                            data['light'] = round(LightData)
                            idx += 3
                        elif (ManuDataHex[idx] == 0x43):
                            #Temperature data
                            idx += 1
                            TempData = ManuDataHex[idx]
                            TempData += ManuDataHex[idx+1] * 0x100
                            TempData = TempData * 0.0625
                            data['temperature'] = round(TempData,1)
                            TempData = (TempData * 1.8) + 32
                            idx += 2
                        else:
                            idx += 1
                    #print ("Device Address: " + CurrentDevAddr)
                    #print ("Device Location: " + CurrentDevLoc)
                    #print ("Battery Level: " + str(BatteryLevel) + "%")
                    #print ("Config Counter: " + str(ConfigCounter))
                    #print ("Accelero Data: " + hex(AcceleroType) + " " + hex(AcceleroData))
                    #print ("Light Data: " + str(round(LightData)))
                    #print ("Temp Data: " + str(round(TempData,1)))
                    #writetoMQTT(data)
#                    doQueryInsert(myConnection, CurrentDevAddr, CurrentDevLoc, TempData, AcceleroData)
                    ReadLoop = False
            else:
               print ("btLE not found")
               RetryCount +=1
               if RetryCount > 3: ReadLoop = False
except DecodeErrorException:
    pass



