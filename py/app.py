from pynput.keyboard import Key, KeyCode, Listener
import threading, time, datetime, os
import open3d

from robot import Robot
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
		self.minLayer = 0

		self.listener = None

		# Machina
		# self.DO = ""
		self.robot = Robot(ptPerLayer=self.resolution, printSpeed=100)

		self.TP = None

		self.create_session()
		self.scanner = None
		threading.Thread(target=self.init_horus).start()

	### KEYBOARD ###

	def keyboard_listener(self):
		with Listener(on_press=self.on_press) as self.listener:
			self.listener.join()

	def on_press(self, key):
		if self._done:
			return False
		if key == Key.esc:
			self._done = True
			return False
		elif key == KeyCode(char='+'):
			if self._state == "geoEdit":
				self.UDP_send("+gh_inc")
		elif key == KeyCode(char='-'):
			if self._state == "geoEdit":
				self.UDP_send("+gh_dec")
		elif key == KeyCode(char='1'):
			if self._state == 'ready' and len(self.TP) >= self.resolution:
				self._state = 'printing'
				print("Starting Fabrication...")
			if self._state == "geoEdit":
				self._state = 'printing'
		elif key == KeyCode(char='2') and self._state == 'printing' and self.robot.layerCount>=self.minLayer:
			self._state = 'ready'
			self.robot.master = False
			print("Stopping Fabrication")
		elif key == KeyCode(char='4') and self._state == 'ready':
			self._state = 'scanning'
		elif key == KeyCode(char='5') and self._state == 'geoEdit':
			self.request_ext_toolpath()
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

	def request_init_toolpath(self):
		print("Requesting Initial Tool Path...", end='')
		filename = self._session + "-tp" + str(self._cycle)
		msg = '+gh_initGeo' + "_" + str(filename)
		self.UDP_send(msg)
		ret = self.UDP_receive(20)
		self.import_TP(filename)

		if ret == '-gh_success':
			self._state = 'ready'
			print("Successful!")
		else:
			print(" Failed!")
			# self._done = True
	
	def request_read(self):
		print("Requesting Point Cloud Read...", end='')
		filename = self._session + "-scan" + str(self._cycle-1)
		msg = '+gh_extGeo' + "_" + str(filename)
		self.UDP_send(msg)
		ret = self.UDP_receive(20)
		if ret == '-gh_success':
			print("Successful!")
		else:
			print(" Failed!")
			# self._done = True

	def request_ext_toolpath(self):
		print("Requesting Extrapolated Toolpath...", end='')
		filename = self._session + "-scan" + str(self._cycle-1)
		filename2 = self._session + "-tp" + str(self._cycle)
		msg = '+gh_extTP' + "_" + str(filename) + "_" + str(filename2)
		self.UDP_send(msg)
		ret = self.UDP_receive(5)
		if ret == '-gh_success':
			print("Successful!")
			self.import_TP(filename2)
			if self.TP != None:
				self._state = 'ready'
		else:
			print(" Failed!")
			# self._done = True

	def import_TP(self, FN):
		filepath = self._mainDIR+self._session+"\\"+FN+".xyz"
		if(os.path.exists(filepath)):
			result = []
			with open(filepath) as fp:  
				line = fp.readline()
				while line:
					curLine = line.strip()
					coord = curLine.split()
					if len(coord) == 3:
						for i in range(len(coord)):
							if coord[i] == "0.0":
								coord[i] = 0.0
							else:
								coord[i] = float(coord[i])
						result.append(coord)
					line = fp.readline()
			self.TP = result

	def ready(self):
		if self._cycle == 0 and self.robot.layerCount == 0:
			print("Ready to start printing.\nPress [START PRINT] to proceed.")
			while not self._done:
				time.sleep(.1)
				if self._state == 'printing':
					break
		elif len(self.TP) >= self.resolution:
			print("Ready to scan or print.\nPress [START PRINT] to continue fabrication or [START SCANNING] to scan.")
			while not self._done:
				time.sleep(.1)
				if self._state == 'printing' or self._state == 'scanning':
					break
		else:
			print("Ready to start scanning.\nPress [START SCANNING] to proceed.")
			while not self._done:
				time.sleep(.1)
				if self._state == 'scanning':
					break

	def printing(self):
		assert(self.TP != None)
		self.robot.initTP(self.TP)
		self.robot.runTP()
		self._state = 'ready'


	def scan(self):
		if self.scanner == None:
			self.init_horus()
		self.run_horus()
		time.sleep(1)
		self._cycle += 1
		self.request_read()
		self._state = "geoEdit"
		self.TP = None

	def add(self,coord):
		for c in coord:
			c[0] = c[0] + 2000
			c[1] = c[1] + 100
			c[2] = c[2] + 750
		return coord


	def main(self):
		print("Running IDF")
		while not self._done:
			###################################
			if self._state == 'handshake':
				self.gh_py_handhake()
				time.sleep(.25)
			if self._state == 'initGeo':
				self.request_init_toolpath()
				time.sleep(.25)
			if self._state == 'ready':
				self.ready()
				time.sleep(.25)
			if self._state == 'printing':
				self.printing()
				time.sleep(.25)
			if self._state == 'scanning':
				self.scan()
				time.sleep(.25)
			if self._state == 'geoEdit':
				# self.geoEdit()
				time.sleep(.25)
			###################################
		self.listener.stop()
	def run(self):
		threading.Thread(target=self.main).start()
		threading.Thread(target=self.keyboard_listener).start()
		

a = IDF()
a.run()