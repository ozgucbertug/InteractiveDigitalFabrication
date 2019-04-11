from machinaRobot import *
from machinaMonitor import *
import os, time

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
	while isRunning:
		print("Layer: ", layerCount)
		layerTarget = TP[:resolution][-1]
		for i in range(resolution):#len(TP)):
			curTarget = TP.pop(0)
			robot.moveTo(curTarget[0], curTarget[1], curTarget[2])
		# add DOs
		isRunning = monitor.monitorLayer(layerTarget)
		layerCount += 1
	robot.move(0,0,200)
def robotSetup(robot):
	robot.speedTo(200)
	robot.accelerationTo(100)
	robot.precisionTo(.1)
	robot.motionMode("joint")
	robot.defineTool("clayExtruder",-380.474,-211.024,219.652,0,0,1,0,1,0,1,1,1,1)
	robot.attachTool("clayExtruder")

TP = add(import_TP())

robot = MachinaRobot()
monitor = MachinaMonitor()

robotSetup(robot)
push_TP(robot, monitor, TP)