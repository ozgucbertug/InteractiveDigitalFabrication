import socket

class Server():

	def __init__(self):
		self.TCP_IP = '127.0.0.5'
		self.TCP_PORT = 5005
		self.BUFFER_SIZE = 20
		self.conn = None

	def start(self, retMsg="received"):
		print("Starting server...", end="")
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind((self.TCP_IP, self.TCP_PORT))
		self.server.listen(1)

		self.conn, addr = self.server.accept()
		print("Done!")
		print ('Connection address:', addr)

		while True:
			print("!!!!")
			data = self.conn.recv(BUFFER_SIZE)
			if not data: break
			print ("received data:", data)
			self.conn.send(retMsg)  # echo

	def stop(self):
		self.conn.close()