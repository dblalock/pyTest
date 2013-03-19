#!/bin/python

import random as r

P_ERROR = .1
BUFFER_LEN = 5;	# for testing, needs to be less than the congestion window

class SerialInterface:

	def __init__(self, rx_callback):
		self._rx_callback = rx_callback
		self._buffer_idx = 0
		
		# initialize buffer to length BUFFER_LEN; this way we can avoid
		# checking whether it's big enough the first time through
		self._buff = [0]*BUFFER_LEN
		
	def tx(self,data):
		"""send an arbitrary string of data"""
		# simulate random errors; either send a plausible number to try
		# to trick it, or just send complete garbage
		if (r.random() < P_ERROR):
			data = r.choice( (r.randint(data-5,data+5), r.getrandbits(32)) )
		# loopback in sw for now
		self._rx(data)

	def _rx(self,data):
		"""try to receive serial data"""
		if (data and self._rx_callback):
			# if we're buffering input, store it in the buffer for a while
			# before flushing it all at once
			if (BUFFER_LEN):
				self._buff[self._buffer_idx] = data
				if (self._buffer_idx == BUFFER_LEN -1):
					self._buffer_idx = 0
					for data in self._buff:
						self._rx_callback(data)
				else:
					self._buffer_idx += 1
			# otherwise, just send each piece of data as we get it
			else:
				self._rx_callback(data)