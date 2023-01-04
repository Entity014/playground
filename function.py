import cv2
import mediapipe as mp
import numpy as np
import time
import math
import pyfirmata

def ard(finger, arr):
    arr1 = np.zeros(5)
    arr2 = np.zeros(5)
    for i, j in enumerate(finger):
        if j == f'{int(j[0])}R':
            arr1[int(j[0])] = 1
        elif j == f'{int(j[0])}L':
            arr2[int(j[0])] = 1
        else:
            arr1[int(j[0])] = 0
            arr2[int(j[0])] = 0
    for i, j in enumerate(arr1):
        arr[i].write(j)
    print(arr1, arr2)

def handCheck(direct, finger, side : str):
    for i in range(4, 21, 4):
        x1, y1 = np.subtract(direct[i], direct[0])
        x2, y2 = np.subtract(direct[4], direct[17])
        x3, y3 = np.subtract(direct[9], direct[5])
        z1, z2, z3= math.sqrt(pow(x1, 2) + pow(y1, 2)), math.sqrt(pow(x2, 2) + pow(y2, 2)), math.sqrt(pow(x3, 2) + pow(y3, 2))
        if (z3 != 0) & (i > 4):
            if (z1/z3) * 20 > 100:
                finger.append(f"{int(i/4) - 1}{side}")
        if (z3 != 0) & (i == 4):
            if (z2/z3) * 20 > 100:
                finger.append(f"{int(i/4) - 1}{side}")

def detectHand2():
    cap = cv2.VideoCapture(0)
    
    arr = np.zeros((21, 2))
    
    mpHands = mp.solutions.hands
    hands = mpHands.Hands()
    mpDraw = mp.solutions.drawing_utils
    
    board = pyfirmata.Arduino("COM5")
    led_1 = board.get_pin('d:13:o')
    led_2 = board.get_pin('d:12:o')
    led_3 = board.get_pin('d:11:o')
    led_4 = board.get_pin('d:10:o')
    led_5 = board.get_pin('d:9:o')
    
    arr_a = [led_1, led_2, led_3, led_4, led_5]
    
    while cap.isOpened():
        finger = []
        check, frame = cap.read()
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    arr[id] = [cx, -cy]
                mpDraw.draw_landmarks(frame, handLms, mpHands.HAND_CONNECTIONS)
                if np.cross(np.subtract(arr[5], arr[0]), np.subtract(arr[17], arr[5])) > 0: 
                    handCheck(arr, finger, "R")
                else:
                    handCheck(arr, finger, "L")
        ard(finger, arr_a)
        
        cv2.putText(frame, "Finger : ", (10, 70), cv2.FONT_HERSHEY_PLAIN, 1, (218, 224, 159), 2)
        cv2.putText(frame, f"Finger Count: ", (10, 40), cv2.FONT_HERSHEY_PLAIN, 2, (218, 224, 159), 3)
        if len(finger) != 0:
            cv2.putText(frame, f"{' '.join(finger)}", (85, 70), cv2.FONT_HERSHEY_PLAIN, 1, (47, 209, 29), 2)
            cv2.putText(frame, f"{str(len(finger))}", (245, 40), cv2.FONT_HERSHEY_PLAIN, 2, (47, 209, 29), 3)
        else:
            cv2.putText(frame, "None", (85, 70), cv2.FONT_HERSHEY_PLAIN, 1, (57, 130, 247), 2)
            cv2.putText(frame, f"{str(len(finger))}", (245, 40), cv2.FONT_HERSHEY_PLAIN, 2, (57, 130, 247), 3)
        if check == True:
            cv2.imshow("Video", frame)
            if cv2.waitKey(1) & 0xFF == ord('e'):
                break
        else:
            break