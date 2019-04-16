from machinaRobot import *
from machinaMonitor import *
from multiprocessing import Queue
import os, time, copy, threading

class Robot(object):

	def __init__(self, TP=None, ptPerLayer=100, printSpeed=25, travelSpeed = 100):
		self.robot = MachinaRobot()
		self.monitor = MachinaMonitor()
		self.isRunning = True
		self.master = True

		self.printSpeed = printSpeed
		self.travelSpeed = travelSpeed
		self.ptPerLayer = ptPerLayer

		self.TP = TP
		self.layerCount = 0
		self.robotSetup()

	def robotSetup(self):
		self.robot.queueSpeedTo(25)
		self.robot.queueAccelerationTo(100)
		self.robot.queuePrecisionTo(.1)
		self.robot.queueMotionMode("joint")
		self.robot.queueDefineTool("clayExtruder",-380.474,-211.024,219.652,0,0,1,0,1,0,1,1,1,1)
		self.robot.queueAttachTool("clayExtruder")
		self.robot.runQueuedCommands()

	def initTP(self, TP):
		self.TP = TP

	def resetTP(self):
		self.TP = None

	def runTP(self):
		assert(self.TP != None)
		self.isRunning = True
		self.master = True

		hoverPt = copy.deepcopy(self.TP[0])
		hoverPt[2] += 200
		
		# House Keeping Start
		self.robot.queueSpeedTo(self.travelSpeed)
		self.robot.queueMoveTo(hoverPt[0], hoverPt[1], hoverPt[2])
		self.robot.queueMoveTo(self.TP[0][0],self.TP[0][1],self.TP[0][2])
		self.robot.queueSpeedTo(self.printSpeed)

		self.robot.runQueuedCommands()
		time.sleep(1)

		returnQueue = Queue(1)

		# Push targets layer by layer.
		while self.isRunning and self.master:
			print("Layer: ", self.layerCount)
			print(self.isRunning, self.master)
			if len(self.TP) < 100:
				break
			layerTarget = self.TP[:self.ptPerLayer][-1]
			for i in range(self.ptPerLayer):
				curTarget = self.TP.pop(0)
				self.robot.queueMoveTo(curTarget[0], curTarget[1], curTarget[2])

			threading.Thread(target=self.robot.runQueuedCommands()).start()
			threading.Thread(target=self.monitor.monitorLayer(layerTarget, returnQueue)).start()
			while returnQueue.empty():
				print(returnQueue.qsize())
				time.sleep(.1)
			self.isRunning = returnQueue.get()
			self.layerCount += 1
		#################################### add DO OFF

		#House Keeping End
		self.robot.queueSpeedTo(self.travelSpeed)
		self.robot.queueMove(0,0,200)
		# self.robot.queueMove(-500,0,0)
		self.robot.queueSpeedTo(self.printSpeed)
		self.robot.runQueuedCommands()

# def import_TP():
# 	filepath ="C:\\Users\\Ozguc Capunaman\\Documents\\GitHub\\InteractiveDigitalFabrication\\sessions\\20190408-1117\\20190408-1117-tp0.xyz"
# 	if(os.path.exists(filepath)):
# 		result = []
# 		with open(filepath) as fp:  
# 			line = fp.readline()
# 			while line:
# 				curLine = line.strip()
# 				coord = curLine.split()
# 				if len(coord) == 3:
# 					for i in range(len(coord)):
# 						if coord[i] == "0.0":
# 							coord[i] = 0.0
# 						else:
# 							coord[i] = float(coord[i])
# 					result.append(coord)
# 				line = fp.readline()
# 		return result

# def add(coord):
# 	for c in coord:
# 		c[0] = c[0]*10 + 2000
# 		c[1] = c[1]*10 + 100
# 		c[2] = c[2]*10 + 750
# 	return coord
# TP = add(import_TP())

# robot = Robot(TP)
# robot.runTP()