import socket
import time

class UDP():

	def __init__(self, IP="127.0.0.1", PORT=5005, mode = None):
		self.UDP_IP = IP
		self.UDP_PORT = PORT
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		if mode == 'in':
			self.socket.bind((self.UDP_IP, self.UDP_PORT))


	def b2str(self, b_msg):
		return b_msg.decode('ascii')


	def send(self, msg="-"):
			msg = msg.encode('ascii')
			self.socket.sendto(msg, (self.UDP_IP, self.UDP_PORT))
			time.sleep(.1)
			self.socket.sendto(b'', (self.UDP_IP, self.UDP_PORT))

	def receive(self, runtime):

		t0 = time.time()
		while True:
			data, addr = self.socket.recvfrom(1024)
			if data:
				data = self.b2str(data)
				# print("received: ", data)
				return data
				break
			elif runtime != None:
				t1 = time.time()
				if t1 - t0 > runtime:
					return None