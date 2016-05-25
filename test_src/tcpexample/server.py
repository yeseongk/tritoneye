#!/usr/bin/env python
import sys, signal
import struct
import socket
from thread import start_new_thread

# Socket program configuration
TCP_IP = '127.0.0.1'
TCP_PORT = 12222
FILE_LEN_BUFFER_SIZE = 4 # 32-bit long = 4 bytes

# For each client, this function is handling the received packet
def client_handling_thread(conn):
	while True:
		# 1) receive file length
		data = conn.recv(FILE_LEN_BUFFER_SIZE)
		if not data: break # disconnected
		file_length_in_bytearray = bytearray(data)
		file_length = struct.unpack("<l", file_length_in_bytearray)[0]

		# 2) get file content
		filecontent = conn.recv(file_length)
		if not filecontent: break # disconnected
		print(filecontent)

	conn.close()

# SIGINT(Control+C) hanling
def signal_handler(signal, frame):
	global s
	print("Pressed Ctrl+C")
	print("Socket closed")
	s.close()
	sys.exit(0)

# BODY =================================================================
signal.signal(signal.SIGINT, signal_handler) # register signal handler

# Create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

print('Server starting')
while True:
	# Accept multiple clients
	conn, addr = s.accept()
	print('Connection address:' + str(addr))
	start_new_thread(client_handling_thread, (conn,))


s.close()
