import sys
import struct
import socket
import time
import communication.comm_conf as conf

# get time in milliseconds
def get_milli_time():
	return int(round(time.time() * 1000))

# generate a xml-style lines
def gen_xml_file(ID, car_in, car_out):
	string = "<tritoneye>\n"
	string += "<cameraid>" + ID + "</cameraid>\n"
	string += "<carin>" + str(car_in) + "</carin>\n"
	string += "<carout>" + str(car_out) + "</carout>\n"
	string += "</tritoneye>"
	return string

# generate a csv-style single line
def gen_text_line(ID, car_in, car_out):
	return ID + "," + str(car_in) + "," + str(car_out) + "\n"

# Communication class
class TCPIPInterface:
	def __init__(self):
		self.s = None
		self.out_logfile = None
		self.log_start_time = None
		self.device_id = conf.DEVICE_ID

	# Set deviceID that will be sent
	def set_device_id(self, device_id):
		self.device_id = device_id

	# Establish connection
	def connect(self, ipaddr=conf.TCP_IP, port=conf.TCP_PORT):
		self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.s.connect((ipaddr, port))

	# Close connection and log
	def close(self):
		self.s.close()
		self.s = None
		self.close_log()

	# Set and open a log file
	def set_log(self, filename):
		if filename is None:
			self.close_log()
			return

		self.out_logfile = open(filename, 'w')
		self.log_start_time = get_milli_time()

	# Close log file
	def close_log(self):
		if self.out_logfile is not None:
			self.out_logfile.close()
			self.out_logfile = None

	# Send information over connection
	def send_info(self, car_in, car_out, verbose = False):
		filecontent = gen_text_line(self.device_id, car_in, car_out)

		if verbose:
			print(filecontent.strip())

		self._send(filecontent)

		# Write log file if given
		if self.out_logfile is not None:
			elapsed_time = get_milli_time() - self.log_start_time
			self.out_logfile.write(str(elapsed_time) + "\t")
			self.out_logfile.write(filecontent)

	# Simulate log file
	def simulate_logfile(self, filename, simulation_speed):
		print("Simulation Start: " + filename)
		prev_time = 0
		with open(filename, 'r') as f:
			for line in f:
				ll = line.split('\t')
				cur_time = int(ll[0])
				filecontent = ll[1]
				old_device_id = filecontent.split(',')[0]
				filecontent = filecontent.replace(old_device_id, self.device_id)

				sleep_time = cur_time-prev_time

				print("LINE:\t" + line.strip())
				print("PACK:\t" + filecontent.strip())
				print("SLEEP:\t" + str(sleep_time))

				time.sleep(float(sleep_time) / 1000 / simulation_speed)
				self._send(filecontent)
				prev_time = cur_time

	# Internal use: transmit the packet
	def _send(self, v):
		if self.s is None:
			print("Warning: connection is not established. No packet sent.")
		else:
			self.s.send(v)

