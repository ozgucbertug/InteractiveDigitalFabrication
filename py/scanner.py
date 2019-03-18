import time
import subprocess, os
import win32gui, win32api, win32con, pyautogui
import open3d
import numpy as np

def windowEnumerationHandler(hwnd, top_windows):
	top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

class Scanner():

	def __init__(self, session):
		self._name = "Horus 0.2rc1"
		self._session = session
		self.cycle = 0

		self.workbench = None
		self.motorEnabled = False
		self.running = self.isRunning()

		self.initAll()

	def initAll(self):
		if not self.running:
			self.initHorus()
		self.enableMotors()
		self.goToScanningWorkbench()

	def isRunning(self):
		tmp = win32gui.FindWindow(None, self._name)
		return tmp != 0

	def bringToFront(self):
		if self.isRunning():
			top_windows = []
			win32gui.EnumWindows(windowEnumerationHandler, top_windows)
			for i in top_windows:
				if self._name.lower() in i[1].lower():
					win32gui.ShowWindow(i[0],5)
					win32gui.SetForegroundWindow(i[0])
					break
		else:
			print("App is not running...")

	def click(self, x, y):
		pyautogui.moveTo(x, y)
		pyautogui.click()
		# win32api.SetCursorPos((x,y))
		# win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
		# win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)
		time.sleep(.1)

	def runHorus(self):
		cmd = "C:/ProgramData/Microsoft/Windows/Start Menu/Programs/Horus/Horus.lnk"
		p = subprocess.Popen(cmd, shell=True)

	def initHorus(self):
		if not self.isRunning():
			self.runHorus()
			while not self.isRunning():
				time.sleep(.1)
			time.sleep(5)
			self.click(2262, 299) #maximize
			self.connectToScanner()
		else:
			self.bringToFront()

	def connectToScanner(self):
		self.bringToFront()
		self.click(30, 120) #connect
		time.sleep(5)

	def goToControlWorkbench(self):
		if self.workbench != "control":
			self.bringToFront()
			self.click(2840, 122)
			self.click(2840, 157)
			self.workbench = "control"

	def goToScanningWorkbench(self):
		self.bringToFront()
		self.click(2840, 122)
		self.click(2840, 234)
		self.workbench = "scanning"

	def enableMotors(self):
		if not self.motorEnabled:
			self.bringToFront()
			self.goToControlWorkbench()
			self.click(249,185)
			self.click(249,830)
			self.click(249,675)
			self.motorEnabled = not self.motorEnabled

	def disableMotors(self):
		if self.motorEnabled:
			self.bringToFront()
			self.goToControlWorkbench()
			self.click(249,185)
			self.click(249,830)
			self.click(249,675)
			self.motorEnabled = not self.motorEnabled

	def reEnableMotors(self):
		self.bringToFront()
		self.goToControlWorkbench()
		self.click(249,185)
		self.click(249,830)
		self.click(249,675)
		self.click(249,675)
		self.motorEnabled = True

	def scanDone(self):
		tmp = win32gui.FindWindow(None, "Scanning finished!")
		return tmp != 0

	def clearPtCloud(self):
		tmp = win32gui.FindWindow(None, "Clear point cloud")
		return tmp != 0

	def scan(self):
		print("Initiating Scan...", end="")
		if self.workbench != "scanning":
			self.goToScanningWorkbench()
		self.click(158,125) #start scan
		time.sleep(1)
		if self.clearPtCloud():
			self.click(1451,1010) #confirm clear point cloud
		while not self.scanDone():
			time.sleep(.1)
		time.sleep(1)
		self.click(1733,1010) #confirm scan done
		self.reEnableMotors()
		print("Done!")

	def exitHorus(self):
		self.click(2825,25)

	def ply2xyz(self, FN):
		fileDir = "../sessions/" + self._session
		srcDir = fileDir + "/" + FN + ".ply"
		ply = open3d.read_triangle_mesh(srcDir)
		xyz = open3d.PointCloud()
		srcDir = fileDir + "/" + FN

		xyz.points = ply.vertices
		targetDir = fileDir + "/" + FN + ".xyz"
		open3d.write_point_cloud(targetDir, xyz)


	def saveScan(self, FN):
		print("Saving Scan...", end="")
		if self.workbench != "scanning":
			self.goToScanningWorkbench()
		self.click(30,60) # ->File
		self.click(30,215) # ->Save Model

		self.click(855, 180) # ->File Directory
		fileDir = "C:\\Users\\Ozguc Capunaman\\Documents\\GitHub\\InteractiveDigitalFabrication\\sessions\\" + self._session
		pyautogui.typewrite(fileDir)
		pyautogui.press('enter')

		self.click(855,840) # ->Filename
		pyautogui.typewrite(FN)
		self.click(1100, 800)
		pyautogui.press('enter')
		print("Done!")

	def run(self, FN):
		self.scan()
		self.saveScan(FN)
		self.ply2xyz(FN)
		self.enableMotors()


# coord = pyautogui.position()
# print(coord)