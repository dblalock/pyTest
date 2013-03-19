#!/bin/python

from serialinterface_test import SerialInterface
#from serialinterface import SerialInterface
from datetime import datetime
import time

C_WINDOW_SZ = 8			# congestion window, so we send at the right rate
MAX_PACKET_ID = 65535
DEFAULT_SLEEP_DURATION = .001
MAX_SLEEP_DURATION = 2
LOG_FILE = "errLog.txt"

class SerialTest:

	def __init__(self):
		self.ser = SerialInterface(self._receive_data)
#		self.logFile = open(LOG_FILE, 'a')
	
	def _receive_data(self,data):
		"""callback to be invoked when serial data is received"""
		
		print("callback invoked")
		
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

	def start(self):
		self.unacked_packets = 0
		self.expected_packet_id = 1
		self.send_packet_id = 1
		self._tx_next_packet()
		
		# if we haven't filled up congestion window, send another packet.
		# If we have, exponential backoff
		while(1):
			time.sleep(.01)
			if (self.unacked_packets <= C_WINDOW_SZ):
				self.sleep_duration = DEFAULT_SLEEP_DURATION;
				self._tx_next_packet()
			else:
				print("waiting for c_window to empty...")
				self.sleep_duration = min( \
					MAX_SLEEP_DURATION, self.sleep_duration*2)
				time.sleep(self.sleep_duration)
		
	def _tx_next_packet(self):
		self.unacked_packets += 1
		print("sent packet: {0}".format(self.send_packet_id) )
		self.ser.tx( self.send_packet_id )
		self.send_packet_id = self._nextPacketId(self.send_packet_id)
		
	def _logSuccess(self, packetId):
		print("received packet: {0}".format(packetId) )
		
	def _logError(self,packetId, e=None):
		errStr = "Err: Expected value {0}, but received {1}".format(packetId,e)
		print(errStr)
		with open(LOG_FILE, 'a') as f:
			f.write("{} - ".format(str(datetime.now()) ) )
			f.write(errStr + "\n")
#		self.logFile.write(errStr)

	def _nextPacketId(self,currentId):
		"""return the next id for a packet; either adds 1 or
		loops around to 1 if at the max value"""
		if (currentId < MAX_PACKET_ID):
			return currentId + 1
		else:
			return 1

	def printVar(self,varName):
		print(varName + " = " + str(eval(varName)) )

if __name__ == "__main__":
	SerialTest().start()

