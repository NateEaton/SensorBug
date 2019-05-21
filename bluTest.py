#!/usr/bin/env python3

from bluepy import btle
from struct import *

print ("connecting...")
dev = btle.Peripheral("EC:FE:7E:10:92:09")

print ("Services...")
for svc in dev.services:
    print (str(svc))

#print ("Services Method..")
#services=dev.getServices()
#for service in services:
#    print (str(service))

#char = dev.getCharacteristics(40,44)

#for c in char:
#    if c.supportsRead():
#        print (str(c.read()))
#    else:
#        print(str(c.uuid) + " does not support reading")
val = dev.readCharacteristic(42)
#i = int.from_bytes(val, byteorder='little')
print (val.hex())
