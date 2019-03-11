import time

from horus.engine.scan.ciclop_scan import CiclopScan
# from horus.util import profile
# from horus.gui.workbench.calibration.main import CalibrationWorkbench

def tracefunc(frame, event, arg, indent=[0]):
      if event == "call":
          indent[0] += 2
          print ("-" * indent[0] + "> call function", frame.f_code.co_name)
      elif event == "return":
          print ("<" + "-" * indent[0], "exit function", frame.f_code.co_name)
          indent[0] -= 2
      return tracefunc

# #####TEST#####
def test():
	# print("Importing settings...", end='')
	# settings = Settings()
	# print("Done!")
	
	print("Setting up the scanner...", end='')
	scanner = CiclopScan()
	scanner.set_capture_texture(False)
	scanner.set_motor_step(20)
	print("Done!")

	print("Connecting to the scanner...", end='')
	scanner.driver.board.connect()
	print("Done!")

	print("Testing Lasers...", end='')
	scanner.driver.board.lasers_on()
	time.sleep(.5)
	scanner.driver.board.lasers_off()
	print("Done!")

	print("Testing the motor...", end='')
	scanner.driver.board.motor_enable()
	scanner.driver.board.motor_speed(200)
	scanner.driver.board.motor_move(100)
	time.sleep(.5)
	scanner.driver.board.motor_invert(True)
	scanner.driver.board.motor_move(100)
	scanner.driver.board.motor_disable()
	print("Done!")

	print("Disconnecting the scanner...", end='')
	scanner.driver.board.disconnect()
	print("Done!")

	# scanner.driver.camera.disconnect()
	# scanner.driver.camera.connect()
	# scanner.start()
	# scanner.stop()

import sys
# sys.settrace(tracefunc)

test()