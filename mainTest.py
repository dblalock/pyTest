#!/usr/local/bin/python3.2

import ftdi3
import sys, time

BAUD_RATE = 19200
BYTE_ORDER = "big"

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
#     if (1):
            print('Device not already open. Hooray!')
            try:
                  device = ftdi3.open_ex(info['SerialNumber'])
            except ftdi3.FTDeviceError:
                  # device var not assigned
                  print('Ftdi device error while attempting to open device')
                  return None
            try:
                  device.reset_device()
                  device.set_baud_rate(BAUD_RATE)
                  device.set_data_characteristics(ftdi3.FT_BITS_8,
                                          ftdi3.FT_STOP_BITS_1, 
                                          ftdi3.FT_PARITY_NONE)
                  device.set_flow_control(ftdi3.FT_FLOW_NONE, 0, 0)
                  device.purge(to_purge='TXRX')
            except (ftdi3.FTDeviceError, CommError):
                  device.close()
                  raise
            except:
                  device.close()
                  raise
      else:
            print('device open')
            serialNum = ftdi3.list_devices()[0]
            print(serialNum)
            device = ftdi3.open_ex(serialNum)
      
      print(device)
      return device


if __name__ == "__main__":
#     serialNum = ftdi3.list_devices()[0]
#     print(serialNum)
#     device = ftdi3.open_ex(serialNum)
#     print(device)
##    print(ftdi3.get_device_info_detail(0))
##    dev_infos = ftdi3.get_device_info_list()
##    print(dev_infos)
#     sys.exit(0)
#     serialNum = dev_info['SerialNumber']
#     print(serialNum)
#     print(ftdi3.list_devices()[0])
#     device = ftdi3.open_ex(serialNum)
#     print(device)
      
#     print(ftdi3.list_devices()[0].__class__)

      num_instrs = 10
      instr_len = 1
      ##msg = "ABCDEFGHIJ"## * num_instrs
      msg = bytes(255) + bytes(255)
      msg = (65535).to_bytes(2, "big")
      print(msg)
      dev = open_device()
      dev.write(msg)

      while not dev.get_queue_status():
            print("waiting for data...")

      time.sleep(.2)
      ##data_bytes = dev.read_available()
      data_bytes = dev.read(2)
      val = int.from_bytes(data_bytes, byteorder=BYTE_ORDER)
      print(val)
      #rxStr = data_bytes.decode()
      #print(rxStr)

      sys.exit(0)

##    time.sleep(.1)
##    data_bytes = dev.read_available(instr_len)
##    print(data_bytes)
      
      #wait for the rx buffer to get data
      ##while not data_bytes:
        ##    data_bytes = dev.read_available(instr_len)
      #read until the rx buffer is empty
      #i = 0
      for i in range(num_instrs):
                ##dev.write("B")
                while not dev.get_queue_status():
                        print("waiting for data...")
                        pass
                ##data_bytes = dev.read_available(instr_len)
                ##data_bytes = dev.read(instr_len)

            ##if not data_bytes:
            ##    print("reached end of rx buffer")
            ##    break
                val = int.from_bytes(data_bytes, byteorder=BYTE_ORDER)
                print("{0}, {1}".format(i,val))
            #i += 1

      # SELF: TODO is that every other byte being read back is
      # 0 for some reason. Reading + writing the right number of them
      # though.

      dev.close()
