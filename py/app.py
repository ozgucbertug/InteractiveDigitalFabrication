from pynput.keyboard import Key, Listener
import threading
import time

from udpComm import UDP
import ply2xyz

class IDF(object):

	def __init__(self, sessionName):
		self._done = False
		self._stateList = ['handshake', 'initGeo']
		self._state = self._stateList[0]
		self._cycle = 0
		self._session = sessionName
		
		# UDP
		self.udp_out = UDP(mode = 'out')
		self.udp_in = UDP(PORT=5004, mode = 'in')

		# Print Settings
		self.layer_height = 1
		self.nozzle_width = 1
		self.resolution = 50

	def on_press(self, key):
		if key == Key.esc:
			self._done = True
			return False

# Collect events until released


	def UDP_send(self, msg):
		self.udp_out.send(msg)

	def UDP_receive(self, runtime = None):
		return self.udp_in.receive(runtime)

	def gh_py_handhake(self):
		print("Handshaking...", end='')
		self.UDP_send('+gh_handshake')
		ret = self.UDP_receive(5)
		if ret == '-gh_success':
			self._state = 'initGeo'
			print("Successful!")
		else:
			print(" Failed!")
			self._done = True


	def toolPathRequest(self, mode):
		if mode == "init":
			print("Requesting Initial Tool Path...", end='')
			filename = self._session + "-tp" + str(self._cycle)
			msg = '+gh_initGeo' + "_" + str(self.resolution) + "_" + str(self.layer_height) + "_" + str(filename)
			self.UDP_send(msg)
			ret = self.UDP_receive(20)
			if ret == '-gh_success':
				self._state = 'readyToPrint'
				print("Successful!")
			elif ret == '-gh_fail_noInitGeo':
				print(" Failed!")
				print("Initial Geometry Missing!")
				self._done = True
			else:
				print(" Failed!")
				self._done = True
		else:
			pass

	def runHorus(self):
		pass

	def run(self):
		# with Listener(on_press=self.on_press) as listener:
		while not self._done:
			###################################
			print("Running IDF")
			if self._state == 'handshake':
				self.gh_py_handhake()
				time.sleep(.1)
			if self._state == 'initGeo':
				self.toolPathRequest("init")
			if self._state == 'readyToPrint':
				break
			###################################
			# listener.join()

a = IDF('test')
a.run()