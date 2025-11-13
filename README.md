# modbus-server
A simple Modbus TCP server that acts as a gateway for serial data.

Every 5 bytes read from the serial port are sent to 5 one-byte holding registers on the Modbus server.
