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
import csv
import psycopg2
from datetime import datetime
#import pymysql
#import struct
#from mqtttest import writetoMQTT

#hostname = 'localhost'
#username = 'datasrc'
#password = 'datasrc000'
#database = 'bleSensor'

#Enter the MAC address of the sensor from the lescan
SENSOR_ADDRESS = ["b0:b4:48:dc:1f:9a"]
SENSOR_LOCATION = ["Elemental Machine"]
#data = {'battery':-99,'RSSI':-99,'temperature':-99,'light':-99,'position':-99}

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
            pass
#            if (dev.addr == "b0:b4:48:dc:1f:9a"):
#                print ("Discovered device", dev.addr)
#                for (adtype, desc, value) in dev.getScanData():
#                    print (" %s = %s" % (desc, value))
#        elif isNewData:
#            if (dev.addr == "b0:b4:48:dc:1f:9a"):
#                for (adtype, desc, value) in dev.getScanData():
#                    print (" %s = %s" % (desc, value))
                #print ("Received new data from", dev.addr)

    def doQueryInsert (conn, addr, loc, temp, accero):

        #blesensor table is date, time, addr, location, temp, accero
        dostr = 'INSERT INTO data VALUES (CURRENT_DATE(), NOW(), %s, %s, %s, %s);'
#6        cur.execute (dostr, (addr, loc, temp, accero))
#        conn.commit() 

    def doQueryInsertPostgres():
        conn = psycopg2.connect(host="localhost",database="suppliers", user="postgres", password="postgres")

scanner = Scanner().withDelegate(ScanDelegate()) 

#scanner.start()

#        myConnection = pymysql.connect (host=hostname, user=username, passwd=password, db=database) 

#try:
#    while True:
#        print ("Still running")
#        scanner.process()




try:
    connection = psycopg2.connect(user = "piuser",
                                  password = "piuser4",
                                  host = "192.168.1.167",
                                  port = "5432",
                                  database = "piuser")
    cursor = connection.cursor()

    while True:
        devices = scanner.scan(2.0)
        ManuData = ""
        for dev in devices:
            entry = 0
            AcceleroData = 0
            AcceleroType = 0
            TempData = 0
            for saddr in SENSOR_ADDRESS:
                entry += 1
#                print ("Looking for %s, Found %s)" % (saddr, dev.addr))
            if (dev.addr == saddr):
                #print ("Found Sensor")
#                print ("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
                CurrentDevAddr = saddr
                CurrentDevLoc = SENSOR_LOCATION[entry-1]
#                data['RSSI'] = dev.rssi
                for (adtype, desc, value) in dev.getScanData():
#                    print (adtype)
#                    print (" %s  %s = %s" % (time.ctime(), desc, value))
                    if (desc == "Flags"):
                        postgres_insert_query = """ INSERT INTO "Element-Machine" ("time-stamp", raw, rssi) VALUES (%s,%s,%s)"""
                        record_to_insert = (datetime.now(tz=None), value, dev.rssi)
                        cursor.execute(postgres_insert_query, record_to_insert)

                        connection.commit()
                        print (" %s  %s = %s RSSI = %s" % (time.ctime(), desc, value, dev.rssi))
                        rows = [time.ctime(), desc, value, dev.rssi]
                        with open('output.txt', 'a', newline='') as csvfile: 
                            # creating a csv writer object 
                            csvwriter = csv.writer(csvfile) 

                            csvwriter.writerow(rows)
except DecodeErrorException:
    print ("Error in Code")
