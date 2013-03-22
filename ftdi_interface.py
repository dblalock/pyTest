
import random as r
import sys, ftdi3

DEBUG = 1

ENDIANNESS = "big"
BYTE_SIZE = ftdi3.FT_BITS_8
PARITY = ftdi3.FT_PARITY_NONE
STOP_BITS = ftdi3.FT_STOP_BITS_1
DEFAULT_BAUD_RATE = 19200
TX_LEN_BYTES = 2
RX_LEN_BYTES = 2

SLEEP_INTERVAL = .001
TIMEOUT = 5

P_ERROR = .1
BUFFER_LEN = 0; # for testing; needs to be less than the congestion window

class SerialInterface:

    def __init__(self, rx_callback, baudrate=DEFAULT_BAUD_RATE):
        self._rx_callback = rx_callback
        self._baud_rate = baudrate
        self._dev = self._open_device()
        
        # initialize buffer to length BUFFER_LEN; this way we can avoid
        # checking whether it's big enough the first time through
        self._buffer_idx = 0
        self._buff = [0]*BUFFER_LEN
        
    def tx(self,data):
        """send an arbitrary string of data"""
        # simulate random errors; either send a plausible number to try
        # to trick it, or just send complete garbage
        if DEBUG and (r.random() < P_ERROR):
            data = r.choice( (r.randint(data-5,data+5), r.getrandbits(32)) )
        else:
            self._dev.write( data.to_bytes(TX_LEN_BYTES, ENDIANNESS) )
        
        #block until answer
        self._rx(data)

    def set_rx_callback(self, f):
        """sets the callback to be invoked when the interface
        receives data (TODO: nail down exact trigger for this)"""
        valid = f is not None
        if valid:
            self._rx_callback = f
        return valid

    def get_baud_rate(self):
        return self._baud_rate

    def set_baud_rate(self, baud_rate):
        self._baud_rate = baud_rate

    def _rx(self,data=None):
        """try to receive serial data (or just use the test data
        supplied as the first arg). If not using test data,
        this method will block for up to TIMEOUT seconds"""
        if not data:
            for i in range(SLEEP_INTERVAL / TIMEOUT):
                if self._dev.get_queue_status() > RX_LEN_BYTES:
                    break;
                time.sleep(SLEEP_INTERVAL)
            data = self._dev.read(RX_LEN_BYTES)
        #if we were given test data
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

    def _open_device(self):
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
            print('Device not already open. Hooray!')
            try:
                device = ftdi3.open_ex(info['SerialNumber'])
            except ftdi3.FTDeviceError:
                # device var not assigned
                print('Ftdi device error while attempting to open device')
                return None
            try:
                device.reset_device()
                device.set_baud_rate(self._baud_rate)
                device.set_data_characteristics(BYTE_SIZE,
                                                STOP_BITS, 
                                                PARITY)
                device.set_flow_control(ftdi3.FT_FLOW_NONE, 0, 0)
                device.purge(to_purge='TXRX')
            except (ftdi3.FTDeviceError):
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
