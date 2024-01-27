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

pastLocations = []
times = []
timeInterval = 0.5
minSpeed = 100
prev = [0, 0]
speed = 0
cushion = 20

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    img, faces = detector.findFaceMesh(img, draw=False)

    if faces:

        face = faces[0]
        pointLeft = face[145]
        pointRight = face[374]
        eyeCenter = [(int((pointRight[0] + pointLeft[0]) / 2)), (int((pointRight[1] + pointLeft[1]) / 2))]
        center = [int(width/2), int(height/2)]

        # cv2.line(img, pointLeft, pointRight, (0, 200, 0), 3)
        # cv2.circle(img, pointLeft, 5, (255, 0, 255), cv2.FILLED)
        # cv2.circle(img, pointRight, 5, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, eyeCenter, 5, (255, 0, 255), cv2.FILLED)

        # X, Y distance from center of the screen
        xDist, yDist = (eyeCenter[0]-center[0]), (center[1]-(eyeCenter[1]))

        coord = [xDist, yDist]

        if not times:
            times.append(time.time())
            pastLocations.append(coord)
        elif len(times) == 1 and time.time()-times[0] >= timeInterval:
            pastLocations.append(coord)

        if len(pastLocations) == 2:
            speed = ((pastLocations[0][0]-pastLocations[1][0])**2+(pastLocations[0][1]-pastLocations[1][1])**2)**0.5
            times = []
            pastLocations = []

        for i in range(2):
            if abs(coord[i]-prev[i]) < cushion and speed < minSpeed:
                coord[i] = prev[i]
            else:
                prev[i] = coord[i]

        sock.sendto(str.encode(str(coord)), serverAddressPort)
        # cv2.circle(img, [int(vector[0]*f/d+center[0]), int(vector[1]*f/d+center[1])], 5, (255, 0, 255), cv2.FILLED)

        cvzone.putTextRect(img, f'X,Y,Z: {coord}',
                           (face[10][0]-75, face[10][1]-100),
                           scale=2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
