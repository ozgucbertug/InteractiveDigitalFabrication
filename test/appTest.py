import cv2

cap = cv2.VideoCapture(1)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

while True:

	ret, im = cap.read()
	cv2.imshow("im", im)

	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break