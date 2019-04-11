from machinaRobot import *
from machinaMonitor import *
import os, time, copy

def import_TP():
	filepath ="C:\\Users\\Ozguc Capunaman\\Documents\\GitHub\\InteractiveDigitalFabrication\\sessions\\20190408-1117\\20190408-1117-tp0.xyz"
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
		return result

def add(coord):
	for c in coord:
		c[0] = c[0]*10 + 2000
		c[1] = c[1]*10 + 100
		c[2] = c[2]*10 + 750
	return coord

def push_TP(robot, monitor, TP, resolution = 100):
	isRunning = True
	layerCount = 0
	hoverPt = copy.deepcopy(TP[0])
	hoverPt[2] += 200
	robot.queueSpeedTo(100)
	robot.queueMoveTo(hoverPt[0], hoverPt[1], hoverPt[2])
	robot.queueSpeedTo(25)
	while isRunning:
		print("Layer: ", layerCount)
		if len(TP) < 100:
			break
		layerTarget = TP[:resolution][-25]
		for i in range(resolution):
			curTarget = TP.pop(0)
			robot.queueMoveTo(curTarget[0], curTarget[1], curTarget[2])
		threading.Thread(target=robot.runQueuedCommands()).start()
		threading.Thread(monitor.monitorLayer(layerTarget)).start()
		layerCount += 1
	# add DO OFF
	robot.queueSpeedTo(100)
	robot.queueMove(0,0,200)
	robot.queueSpeedTo(25)
	robot.runQueuedCommands()

def robotSetup(robot):
	robot.queueSpeedTo(25)
	robot.queueAccelerationTo(100)
	robot.queuePrecisionTo(.1)
	robot.queueMotionMode("joint")
	robot.queueDefineTool("clayExtruder",-380.474,-211.024,219.652,0,0,1,0,1,0,1,1,1,1)
	robot.queueAttachTool("clayExtruder")
	robot.runQueuedCommands()

TP = add(import_TP())

robot = MachinaRobot()
monitor = MachinaMonitor()

robotSetup(robot)
push_TP(robot, monitor, TP)