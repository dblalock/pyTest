#!/bin/python

import serial, time

BYTE_ORDER = "big"
BYTE_SIZE = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_ONE

dev_file = "/dev/tty.usbserial-A6007yZF"
ser = serial.Serial(dev_file, baudrate = 9600, bytesize = 8, 
			parity = PARITY, stopbits = STOP_BITS, timeout=2)
#ser.open()	# apparently already open…

def tx(data):
	"""Send an arbitrary integer. Will break for other data types."""
	bytes = (data).to_bytes(4, byteorder=BYTE_ORDER)
	ser.write(bytes)
	# loopback for testing
#	rx(bytes)

def rx():
	"""Try to receive serial data"""
	bytes = None
	while not bytes:
		bytes = ser.read(4)
		time.sleep(.01)
	
	print(bytes)
	num = int.from_bytes(data, byteorder=BYTE_ORDER)
	print(num)
#	if (data and self._rx_callback):
#		num = int.from_bytes(data, byteorder=BYTE_ORDER)
#		print(num)

#ser.write((54).to_bytes( ))

if __name__ == "__main__":
	while(1):
#		tx( (2**16 -1) - 2**14 - 2**12 - 2**10 - 2**8 )
#		tx(65535 - 32768 - 8192 - 1024 - 256)
		tx(85)
#		rx()
		time.sleep(.01)
	ser.close()

