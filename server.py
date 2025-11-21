#!/usr/bin/env python3

import argparse
import logging
import queue
import struct
from datetime import datetime

# need sudo pip install pyserial==3.4
import serial

from pyModbusTCP.server import DataBank, ModbusServer

class MyDataBank(DataBank):
    """A custom ModbusServerDataBank for override get_holding_registers method."""

    def __init__(self, port):
        # turn off allocation of memory for standard modbus object types
        # only "holding registers" space will be replaced by
        # dynamic build values.
        self.serial_port = port
        super().__init__(virtual_mode=True)

    def get_holding_registers(self, address, number=1, srv_info=None):
        """Get virtual holding registers."""
        # populate virtual registers dict with bytes read from serial port
        now = datetime.now()

        rx = self.serial_port.read_data(3)
        if rx:
            print(f"Received: {rx.decode('utf-8')}") # Decode bytes to string
            if len(rx) == 1:
                v_regs_d = {0: rx[0], 1: 0, 2: 0}
            elif len(rx) == 2:
                v_regs_d = {0: rx[0], 1: rx[1], 2: 0}
            else:
                v_regs_d = {0: rx[0], 1: rx[1], 2: rx[2]}
        else:
            print("No data received or error occurred.")
            v_regs_d = {0: 0, 1: 0, 2: 0}

        # build a list of virtual regs to return to server data handler
        # return None if any of virtual registers is missing
        try:
            return [v_regs_d[a] for a in range(address, address+number)]
        except KeyError:
            return

class MySerialDevice:
    def __init__(self, port, baudrate):
        self.serial_port = serial.Serial(port, baudrate, timeout=1) # Timeout of 1 second

    def read_data(self, num_bytes):
        try:
            data = self.serial_port.read(num_bytes)
            return data
        except serial.SerialException as e:
            print(f"Serial error: {e}")
            return b""

    def close(self):
        self.serial_port.close()


if __name__ == '__main__':
    # parse args
    parser = argparse.ArgumentParser()
    parser.add_argument('device', type=str, help='serial device (like /dev/ttyUSB0)')
    parser.add_argument('-H', '--host', type=str, default='localhost', help='host (default: localhost)')
    parser.add_argument('-p', '--port', type=int, default=502, help='TCP port (default: 502)')
    parser.add_argument('-b', '--baudrate', type=int, default=1200, help='serial rate (default is 1200)')
    parser.add_argument('-t', '--timeout', type=float, default=1.0, help='timeout delay (default is 1.0 s)')
    parser.add_argument('-e', '--eof', type=float, default=0.05, help='end of frame delay (default is 0.05 s)')
    parser.add_argument('-d', '--debug', action='store_true', help='set debug mode')
    args = parser.parse_args()
    # init logging
    logging.basicConfig(level=logging.DEBUG if args.debug else None)
    logger = logging.getLogger(__name__)
    try:
        # init serial port
        logger.debug('Open serial port %s at %d bauds', args.device, args.baudrate)
        serial_port = MySerialDevice(port=args.device, baudrate=args.baudrate)
        # start modbus server with custom engine
        logger.debug('Start modbus server (%s, %d)', args.host, args.port)
        srv = ModbusServer(host=args.host, port=args.port, data_bank=MyDataBank(serial_port))
        srv.start()
    except ModbusServer.Error as e:
        logger.critical('Modbus server error: %r', e)
        exit(2)
