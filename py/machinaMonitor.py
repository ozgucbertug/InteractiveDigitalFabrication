from ast import literal_eval
import asyncio
import websockets
import math

class MachinaMonitor(object):

	def __init__(self, address = "ws://127.0.0.1:6999/Bridge"):
		self.address = address
		self.isMonitoring = False
		self.layerCount = 0
		
		self.targetPos = None

	async def listen(self):
		async with websockets.connect(self.address) as websocket:
			feedback = await websocket.recv()
			ind0 = feedback.find("\"pos\"")
			if ind0 == -1:
				return None
			else:
				ind1 = feedback.find("\"ori\"")
				posStr = feedback[ind0+7:ind1-2]
				pos = []
				for tmp in posStr.split(","):
					pos.append(float(tmp))
				return pos

	def eucDist(self, pt):
		sqSum = 0
		for i in range(3):
			sqSum += (self.targetPos[i]-pt[i])**2
		return math.sqrt(sqSum)

	def isLayerComplete(self, curPos):
		if self.eucDist(curPos) > .1:
			return False
		else:
			self.layerCount += 1
			return True


	def monitorLayer(self, target):
		assert(target != None)
		self.layerCount = 0
		self.isMonitoring = True
		self.targetPos = target
		return self.monitor()

	def monitor(self):
		while self.isMonitoring:
			curPos = asyncio.get_event_loop().run_until_complete(self.listen())
			print("curPos: ", curPos, "/targetPos: ", self.targetPos, "/dist: ", self.eucDist(curPos))
			if curPos != None and self.isLayerComplete(curPos):
				self.isMonitoring = False
				return True