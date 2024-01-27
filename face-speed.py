import cv2
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
import socket
import time

cap = cv2.VideoCapture(0)
detector = FaceMeshDetector(maxFaces=1)

_, screenMeasure = cap.read()
(height, width) = screenMeasure.shape[:2]

# Communications
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serverAddressPort = ("127.0.0.1", 9000)
pastLocation = False

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img, faces = detector.findFaceMesh(img, draw=False)

    if faces:
        start = time.time()
        time.sleep(0.02)

        face = faces[0]
        pointLeft = face[145]
        pointRight = face[374]
        eyeCenter = [(int((pointRight[0] + pointLeft[0]) / 2)), (int((pointRight[1] + pointLeft[1]) / 2))]
        center = [int(width/2), int(height/2)]

        # cv2.line(img, pointLeft, pointRight, (0, 200, 0), 3)
        # cv2.circle(img, pointLeft, 5, (255, 0, 255), cv2.FILLED)
        # cv2.circle(img, pointRight, 5, (255, 0, 255), cv2.FILLED)
        # cv2.circle(img, eyeCenter, 5, (255, 0, 255), cv2.FILLED)

        # finding focal length
        w, _ = detector.findDistance(pointLeft, pointRight)  # dist in pixels
        W = 6.4
        # d = 40
        # f = (w*d)/W

        # finding distance in cm
        f = 1510
        d = round(((W*f)/w), 2)

        # X, Y distance from center of the screen
        xDist, yDist = round(((eyeCenter[0])-center[0])*d/f, 2), round((center[1]-(eyeCenter[1]))*d/f, 2)

        # cvzone.putTextRect(img, f'Depth: {int(d)}cm',
        #                    (face[10][0]-75, face[10][1]-50),
        #                    scale=2)
        # cvzone.putTextRect(img, f'X,Y: {int(xDist),int(yDist)}cm',
        #                    (face[10][0]-75, face[10][1]-100),
        #                    scale=2)

        if pastLocation:

            end = time.time()
            elapsed = (end-start)

            xSpeed = int(round(xDist-pastLocation[0], 2)/elapsed)
            ySpeed = int(round(yDist-pastLocation[1], 2)/elapsed)
            zSpeed = int(round(d-pastLocation[2], 2)/elapsed)

            if abs(d-pastLocation[2]) <= 0.25:
                zSpeed = 0

            speeds = [xSpeed, ySpeed, zSpeed]

            for i in range(len(speeds)):
                if abs(speeds[i]) <= 3:
                    speeds[i] = 0

            # cvzone.putTextRect(img, f'speed: {speeds}cm/s', (face[10][0]-75, face[10][1]-50), scale=2)

            sock.sendto(str.encode(str(speeds)), serverAddressPort)

        pastLocation = [xDist, yDist, d]

    else:
        pastLocation = False

    # cv2.imshow("Image", img)
    cv2.waitKey(1)
