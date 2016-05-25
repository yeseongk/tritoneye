# Smaller version only for simulation (Dont need to use cv)
import sys, signal
import argparse
from communication.tcpclient_util import *

# cleanup communication 
def cleanup():
	global tcpinterface
	if tcpinterface is not None:
		tcpinterface.close()
	print("All cleaned up")

# SIGINT(Control+C) hanling
def signal_handler(signal, frame):
	print("Pressed Ctrl+C. Clean up")
	cleanup()
	sys.exit(0)

if __name__ == '__main__':
	# init global class
	tcpinterface = None
	signal.signal(signal.SIGINT, signal_handler) # register signal handler

	# construct the argument parse and parse the arguments
	ap = argparse.ArgumentParser()
	ap.add_argument("-sl", "--simulate_logfile", help="The log file to be simulated.", required=True)
	ap.add_argument("-ss", "--simulation_speed", help="simulation speed, optional. Default = 1", required=False)
	ap.add_argument("-l", "--loop_log", action='store_true',
		help="loop log, optional", required=False)
	ap.add_argument("-di", "--device_id", help="device id sent to server, optional", required=False)
		
	args = vars(ap.parse_args())
	loop_log = args.get("loop_log", False)
	simulation_speed = 1
	if args.get("simulation_speed", False):
		simulation_speed = float(args["simulation_speed"])

	# Setup communication
	tcpinterface = TCPIPInterface()
	tcpinterface.connect()
	if args.get("device_id", False):
		tcpinterface.set_device_id(args["device_id"])

	do_simulate = True
	while do_simulate:
		tcpinterface.simulate_logfile(args["simulate_logfile"], simulation_speed)
		do_simulate = loop_log

	cleanup()
