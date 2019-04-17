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

	async def listen(self, q):
		isRunning = True
		async with websockets.connect(self.address) as websocket:
			while isRunning:
				feedback = await websocket.recv()
				ind0 = feedback.find("\"pos\"")
				if ind0 == -1:
					pass#return None
				else:
					ind1 = feedback.find("\"ori\"")
					posStr = feedback[ind0+7:ind1-2]
					pos = []
					for tmp in posStr.split(","):
						pos.append(float(tmp))
					# print("curPos: ", pos, "/targetPos: ", self.targetPos, "/dist: ", self.eucDist(pos))
					if self.isLayerComplete(pos):
						q.put(1)
						return# True

	def eucDist(self, pt):
		sqSum = 0
		for i in range(3):
			sqSum += (self.targetPos[i]-pt[i])**2
		return math.sqrt(sqSum)

	def isLayerComplete(self, curPos):
		if self.eucDist(curPos) > .5:
			return False
		else:
			self.layerCount += 1
			return True


	def monitorLayer(self, target, q):
		assert(target != None)
		self.layerCount = 0
		self.isMonitoring = True
		self.targetPos = target
		return self.monitor(q)

	def monitor(self, q):
		return asyncio.new_event_loop().run_until_complete(self.listen(q))