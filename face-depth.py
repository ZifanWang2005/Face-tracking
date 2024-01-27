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
minSpeed = 1
prev = [0, 0, 0]
speed = 0
cushion = 0.5

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

        # finding focal length
        w, _ = detector.findDistance(pointLeft, pointRight)  # dist in pixels
        W = 6.4
        # d = 40
        # f = (w*d)/W

        # finding distance in cm
        f = 1510
        d = ((W*f)/w)

        # X, Y distance from center of the screen
        xDist, yDist = (eyeCenter[0]-center[0])*d/f, (center[1]-(eyeCenter[1]))*d/f

        vector = [xDist, yDist, d]

        if not times:
            times.append(time.time())
            pastLocations.append(vector)
        elif len(times) == 1 and time.time()-times[0] >= timeInterval:
            pastLocations.append(vector)

        if len(pastLocations) == 2:
            speed = ((pastLocations[0][0]-pastLocations[1][0])**2+(pastLocations[0][1]-pastLocations[1][1])**2 + (
                    pastLocations[0][2]-pastLocations[1][2])**2)**0.5
            times = []
            pastLocations = []

        for i in range(3):
            if abs(vector[i]-prev[i]) < cushion and speed < minSpeed:
                vector[i] = prev[i]
            else:
                prev[i] = vector[i]

        roundedVector = [round(vector[0]/100, 4), round(vector[1]/100, 4), round(vector[2]/100, 4)]
        sock.sendto(str.encode(str(roundedVector)), serverAddressPort)
        # cv2.circle(img, [int(vector[0]*f/d+center[0]), int(vector[1]*f/d+center[1])], 5, (255, 0, 255), cv2.FILLED)

        cvzone.putTextRect(img, f'X,Y,Z: {roundedVector}',
                           (face[10][0]-75, face[10][1]-100),
                           scale=2)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
