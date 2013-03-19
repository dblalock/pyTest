#!/bin/python

import random as r
import sys, subprocess, serial

BYTE_ORDER = "big"
BYTE_SIZE = serial.EIGHTBITS
PARITY = serial.PARITY_NONE
STOP_BITS = serial.STOPBITS_ONE

class SerialInterface:

	def __init__(self, rx_callback):
		self._rx_callback = rx_callback
		
		# figure out device file name #TODO generalize for other OSes (?)
		ports = runCmd('python3.2 -m serial.tools.list_ports').split()

		# figure out which of the ports is actaully associated with the
		# ftdi chip 	# TODO more direct method
		dev_file = ""
		for port in ports:
			if "serial" in port:
				dev_file = port
				break
		if dev_file == "":
			print("Device file not found. Exiting")
			sys.exit(1)
		
		print("Attempting to connect to device at:\n{0}".format(dev_file))
		
		# set up serial connection
		self._ser=serial.Serial(dev_file, baudrate = 19200, bytesize = 8, 
			parity = PARITY, stopbits = STOP_BITS, timeout = 1)
		
	def tx(self,data):
		"""Send an arbitrary integer. Will break for other data types."""
		bytes = (data).to_bytes(4, byteorder=BYTE_ORDER)
		# loopback for testing
		self._rx(bytes)

	def _rx(self,data):
		"""Try to receive serial data"""
		if (data and self._rx_callback):
			num = int.from_bytes(data, byteorder=BYTE_ORDER)
			self._rx_callback(num)
				
def runCmd(cmd):
	output = str(subprocess.check_output(cmd, shell=True))
	output = output.replace("\\n","\n")
	return str(output)[2:-2] 	# starts as b'<actual output>\n'
	
#def int2bytes(x):
#	"""convert an int to 4 bytes using py32's to_bytes() function"""
##	return eval("b'" + str(x) + "'")
#	return (x).to_bytes(4, byteorder=BYTE_ORDER)
#	
#def bytes2int(b):
#	"""convert 4 bytes to an int using py32's from_bytes() function"""
#	return int.from_bytes(data, byteorder=BYTE_ORDER)
