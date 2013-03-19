#!/usr/local/bin/python3.2

import ftdi3
import sys

_BAUD_RATE = 9600

def open_device():
	"""Opens and returns a pointer to the ftdi device"""

	try:
		dev_infos = ftdi3.get_device_info_list()
	except ftdi3.FTDeviceError:
		print('Error getting device info list.')
		return None
    
	if len(dev_infos) < 1:
    		print('No device infos found.')
    		return None
	elif len(dev_infos) > 1:
    		print('Warning: More than one device info found; opening the first')
    		return None
    
	info = dev_infos[0];
	print(info)
	
	device = None
	if not (info['Flags'] & ftdi3.FT_FLAGS_OPENED):
#	if (1):
		print('device not open')
		try:
			device = ftdi3.open_ex(info['SerialNumber'])
		except ftdi3.FTDeviceError:
			# device var not assigned
			print('Ftdi device error while attempting to open device')
			return None
    
		try:
			device.reset_device()
			device.set_baud_rate(_BAUD_RATE)
			device.set_data_characteristics(ftdi3.FT_BITS_8,
	                	                    ftdi3.FT_STOP_BITS_1, 
	                        	            ftdi3.FT_PARITY_NONE)
			device.set_flow_control(ftdi3.FT_FLOW_NONE, 0, 0)
			device.purge(to_purge='TXRX')
		except (ftdi3.FTDeviceError, CommError):
			device.close()
		except:
			device.close()
			raise
	else:
		print('device open…')
		serialNum = ftdi3.list_devices()[0]
		print(serialNum)
		device = ftdi3.open_ex(serialNum)
	
	print(device)
	return device


if __name__ == "__main__":
#	serialNum = ftdi3.list_devices()[0]
#	print(serialNum)
#	device = ftdi3.open_ex(serialNum)
#	print(device)
##	print(ftdi3.get_device_info_detail(0))
##	dev_infos = ftdi3.get_device_info_list()
##	print(dev_infos)
#	sys.exit(0)
#	serialNum = dev_info['SerialNumber']
#	print(serialNum)
#	print(ftdi3.list_devices()[0])
#	device = ftdi3.open_ex(serialNum)
#	print(device)
	
#	print(ftdi3.list_devices()[0].__class__)
	
	open_device()
