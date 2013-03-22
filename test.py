#!/bin/python

from ftdi_interface import SerialInterface
from datetime import datetime
import time

DEBUG = 1

CONGESTION_WINDOW_SZ = 8 # congestion window, so we send at the right rate
MAX_PACKET_ID = DEBUG and 1000 or 65535	# smaller runs for debugging
DEFAULT_SLEEP_DURATION = 0
MAX_SLEEP_DURATION = .01
BAUD_RATES_LIST = (38400,115200,230400,460800,921600)
LOG_FILE = "errLog.txt"
ERRORS_CSV_FILE = "errors.csv"

def printVar(varName):
	"""utility method for debugging"""
	print(varName + " = " + str(eval(varName)) )

class SerialTest:

	def __init__(self):
		self.ser = SerialInterface(self._receive_data)
		self.bauds2errors = {}
	
	def _receive_data(self,data):
		"""callback to be invoked when serial data is received"""
		# convert bytes to int
		data = int(data)
		
		# case 1: received the packet we were expecting; now wait for the next one
		if (data == self.expected_packet_id):
			self._logSuccess(self.expected_packet_id)
			self.unacked_packets -= 1
			self.expected_packet_id = self._nextPacketId(self.expected_packet_id)
		# case 2: received either garbage or a sensible but incorrect packet
		else:
			initial_expected_packet_id = self.expected_packet_id
			try:
				actual_packet_id = int(data)
				# if we received the id for some packet we actually sent,
				# assume previous packets just got dropped and set the
				# id we're expecting based on what we just got.
				# Note that this will get really confused if things are
				# frequently received out of order.
				#
				# Actually, this really screws up everything if the packet isn't actually lost,
				# so it's commented out for now. Might bring it back if completely
				# dropped packets turn out to be a problem.
				if (self.expected_packet_id < actual_packet_id < self.send_packet_id):
					raise ValueError("{}".format(actual_packet_id))
#					self.unacked_packets -= (actual_packet_id - self.expected_packet_id + 1)
#					self.expected_packet_id = actual_packet_id + 1
#					print("skipped some packets")
				else:
					raise ValueError("{}".format(actual_packet_id))
			# if we didn't received a valid acknowledgement for a packet,
			# the packet we got is probably just garbage, so hope the next
			# one works out better
			except Exception as e:
				self.unacked_packets -= 1
				self.expected_packet_id = self._nextPacketId(self.expected_packet_id)
				self._logError(initial_expected_packet_id, e)

	def test_baud_rate(self, baud_rate):
		self.unacked_packets = 0
		self.expected_packet_id = 1
		self.send_packet_id = 1
		self.ser.set_baud_rate(baud_rate)
		self.error_count = 0
		self._tx_next_packet()
		
		# if we haven't filled up congestion window, send another packet.
		# If we have, exponential backoff
		while(self.expected_packet_id < MAX_PACKET_ID):
			#time.sleep(.01)
			if (self.unacked_packets <= CONGESTION_WINDOW_SZ):
				self.sleep_duration = DEFAULT_SLEEP_DURATION;
				self._tx_next_packet()
			else:
				print("waiting for c_window to empty...")
				self.sleep_duration = min( \
					MAX_SLEEP_DURATION, self.sleep_duration*2)
				time.sleep(self.sleep_duration)
				
		#record how many errors we encountered at this baud rate
		self.bauds2errors[baud_rate] = self.error_count
		
	def _tx_next_packet(self):
		self.unacked_packets += 1
		self.ser.tx( self.send_packet_id )
		self.send_packet_id = self._nextPacketId(self.send_packet_id)
		
	def _logSuccess(self, packetId):
		print("sent and received packet: {0}".format(packetId) )
		
	def _logError(self,packetId, e=None):
		self.error_count += 1
		errStr = "Err: Expected {0}, Received {1}".format(packetId,e)
		print(errStr)
		with open(LOG_FILE, 'a') as f:
			f.write("{0} - {1} - {2}\n".format(
				str(datetime.now()),
				self.ser.get_baud_rate(),
				errStr ) )

	def _exportErrors(self):
		with open(ERRORS_CSV_FILE, 'w') as f:
			for key, value in self.bauds2errors.items():
				f.write("{0}, {1}\n".format(key,value) )
		
	
	def _nextPacketId(self,currentId):
		"""return the next id for a packet; either adds 1 or
		loops around to 1 if at the max value"""
		if (currentId < MAX_PACKET_ID):
			return currentId + 1
		else:
			return 1

	def start(self):
		for baud_rate in BAUD_RATES_LIST:
			self.test_baud_rate(baud_rate)
		self._exportErrors()

if __name__ == "__main__":
	SerialTest().start()
