#!/usr/bin/env python
import sys
import struct
import socket
import time
import random

# Socket program configuration
TCP_IP = '137.110.90.84'#127.0.0.1'
TCP_PORT = 3000
FILE_LEN_BUFFER_SIZE = 4 # 32-bit long = 4 bytes

MAX_ITERATION = 100

# generate a sample xml file
def gen_xml_file(ID, iteration):
	string = "<tritoneye>\n"
	string += "<cameraid>" + ID + "</cameraid>\n"
	string += "<carcnt>" + str(iteration) + "</carcnt>\n"
	string += "</tritoneye>"
	return string

def gen_line(ID, iteration):
	return ID + "," + str(iteration) + "\n"

def gen_random():
	floor = random.randint(1,4)
	capacity = random.randint(0,40)
	inout = random.randint(0,1)
	return str(floor) + "," + str(capacity) + "," + str(inout) + "\n"

# BODY =================================================================
# Program argument
# Example: python client.py ID_03
ID = "ID_00_FROM_PY"
if len(sys.argv) == 2:
	ID = sys.argv[1]

# Create socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

# For each iteration (2 second interval),
# 1) generate a sample xml file
# 2) send the file length in 32-bit byte array (so server knows if the file is completely received.)
# 3) send the file content
for i in range(MAX_ITERATION):
	#filecontent = gen_xml_file(ID, i)
	#file_length = len(filecontent)
	#file_length_in_bytearray = struct.pack("<l", file_length)

	#if len(file_length_in_bytearray) != FILE_LEN_BUFFER_SIZE:
	#	sys.exit("ASSERTION. The file length is not 32-bit long.")

	#s.send(file_length_in_bytearray)
	filecontent = gen_random()
	print(filecontent)
	s.send(filecontent)

	time.sleep(2)

s.close()
