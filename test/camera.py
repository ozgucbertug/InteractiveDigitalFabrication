import cv2

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

class Camera(object):

	def __init__(self, camera_id=1):
		self.cam = cv2.VideoCapture(camera_id)
		self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
		self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
		self.cam.set(cv2.CAP_PROP_FPS, 60)

	def captureImage(self):
		ret, im = self.cam.read()
		return im

	def videoStream(self):
		while True:
			cv2.imshow("Video Stream", self.captureImage())

			key = cv2.waitKey(1) & 0xFF
			if key == ord("q"):
				break

	def exit(self):
		self.cam.release()
		cv2.destroyAllWindows()


def main():
	cam = Camera()
	cam.videoStream()
	cam.exit()
main()