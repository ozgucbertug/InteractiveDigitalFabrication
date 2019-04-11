from pynput.keyboard import Key, KeyCode, Listener
import threading, time, datetime, os
import open3d

from machinaRobot import *
from udpComm import UDP
from scanner import Scanner

class IDF(object):

	def __init__(self):
		self._done = False
		self._state = 'handshake'
		self._cycle = 0
		self._session = None
		self._mainDIR = "C:\\Users\\Ozguc Capunaman\\Documents\\GitHub\\InteractiveDigitalFabrication\\sessions\\"
		
		# UDP
		self.udp_out = UDP(mode = 'out')
		self.udp_in = UDP(PORT=5004, mode = 'in')

		# Print Settings
		self.nozzle_width = 10
		self.layer_height = self.nozzle_width/4
		self.resolution = 100

		self.listener = None

		# Machina
		# self.DO = ""
		self.machinaRobot = MachinaRobot()
		self.machinaRobot.speedTo(25)
		# self.machinaRobot.MoveTo()

		self.TP = None

		self.create_session()
		self.scanner = None

	### KEYBOARD ###

	def keyboard_listener(self):
		with Listener(on_press=self.on_press) as self.listener:
			self.listener.join()

	def on_press(self, key):
		print(key)
		if self._done:
			return False
		if key == Key.esc:
			self._done = True
			return False
		elif key == Key.end and self._state == 'readyToPrint' and self.TP != None:
			self._state = 'printing'
		elif key == Key.down and self._state == 'printing':
			self._state = 'readyToPrint'

	### HORUS ###
	
	def init_horus(self):
		self.scanner = Scanner(self._session)

	def run_horus(self):
		self.scanner.run(self._session + "-scan" + str(self._cycle))


	### UDP ###

	def UDP_send(self, msg):
		self.udp_out.send(msg)

	def UDP_receive(self, runtime = None):
		return self.udp_in.receive(runtime)
	
	### FUNCTIONS ###

	def create_session(self):
		now = datetime.datetime.now()
		self._session = now.strftime("%Y%m%d-%H%M")
		folder = "../sessions/" + self._session
		if not os.path.isdir(folder):
			os.mkdir(folder)


	### STATES ###

	def gh_py_handhake(self):
		print("Handshaking...", end='')
		self.UDP_send('+gh_handshake' + "_" + self._session + "_" + str(self.resolution) + "_" + str(self.layer_height))
		ret = self.UDP_receive(5)
		if ret == '-gh_success':
			self._state = 'initGeo'
			print("Successful!")
		else:
			print(" Failed!")
			self._done = True

	def request_toolpath(self, mode=None):
		if mode == "init":
			print("Requesting Initial Tool Path...", end='')
			filename = self._session + "-tp" + str(self._cycle)
			msg = '+gh_initGeo' + "_" + str(filename)
			self.UDP_send(msg)
			ret = self.UDP_receive(20)
			self.import_TP(filename)
		# else:
		# 	print("Requesting Tool Path for Cycle %d..." %self._cycle, end='')
		# 	filename = self._session + "-tp" + str(self._cycle)
		# 	msg = '+gh_cycleGeo' + "_" + str(filename)
		# 	self.UDP_send(msg)
		# 	ret = self.UDP_receive(20)

		if ret == '-gh_success':
			self._state = 'readyToPrint'
			print("Successful!")
		else:
			print(" Failed!")
			self._done = True
	
	def request_read(self):
		print("Requesting Point Cloud Read...", end='')
		filename = self._session + "-scan" + str(self._cycle-1)
		filename2 = self._session + "-tp" + str(self._cycle)
		msg = '+gh_readScan' + "_" + str(filename) + "_" + str(filename2)
		self.UDP_send(msg)
		ret = self.UDP_receive(20)
		if ret == '-gh_success':
			self._state = 'readyToPrint'
			print("Successful!")
			self.import_TP(filename2)
		else:
			print(" Failed!")
			self._done = True

	def import_TP(self, FN):
		filepath = self._mainDIR+self._session+"\\"+FN+".xyz"
		if(os.path.exists(filepath)):
			result = []
			with open(filepath) as fp:  
			   line = fp.readline()
			   while line:
				   curLine = line.strip()
				   coord = curLine.split(' ')
				   for i in range(len(coord)):
					   coord[i] = float(coord[i])
				   result.append(coord)
				   line = fp.readline()
		self.TP =  result

		#################### DEV #######################
	def push_TP(self)
		for i in range(len(self.TP)):
			curTarget = self.TP.pop(0)
			self.machinaRobot.MoveTo(curTarget[0], curTarget[1], curTarget[2])

	def ready_to_print(self):
		print("Ready to start printing.\nPress [P] to proceed.")
		while not self._done:
			time.sleep(.1)
			if self._state == 'printing':
				break

	def printing(self):
		self._state = 'scanning'

	def scan(self):
		if self.scanner == None:
			self.init_horus()
		self.run_horus()
		time.sleep(1)
		self._cycle += 1
		self.request_read()


	def main(self):
		print("Running IDF")
		while not self._done:
			###################################
			if self._state == 'handshake':
				self.gh_py_handhake()
				time.sleep(.25)
			if self._state == 'initGeo':
				self.request_toolpath("init")
				time.sleep(.25)
			if self._state == 'readyToPrint':
				self.ready_to_print()
				time.sleep(.25)
			if self._state == 'printing':
				self.printing()
				time.sleep(.25)
			if self._state == 'scanning':
				self.scan()
				time.sleep(.25)
			###################################
		self.listener.stop()
	def run(self):
		threading.Thread(target=self.keyboard_listener).start()
		threading.Thread(target=self.main).start()
		

a = IDF()
a.run()