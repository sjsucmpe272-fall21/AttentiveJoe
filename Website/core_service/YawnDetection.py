import cv2
import dlib
import numpy as np
from datetime import datetime
import time

#net = cv2.dnn.readNetFromCaffe('./saved_model/deploy.prototxt.txt', './saved_model/res10_300x300_ssd_iter_140000.caffemodel')
from core_service.database import get_db_connection

PREDICTOR_PATH = "core_service/shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(PREDICTOR_PATH)
cascade_path='haarcascade_frontalface_default.xml'
cascade = cv2.CascadeClassifier(cascade_path)
detector = dlib.get_frontal_face_detector()

eye_cascPath = 'core_service/eye_tree.xml'  #eye detect model
face_cascPath = 'core_service/frontface_alt.xml'  #face detect model
faceCascade = cv2.CascadeClassifier(face_cascPath)
eyeCascade = cv2.CascadeClassifier(eye_cascPath)
connection = get_db_connection()
cursor = connection.cursor()

def get_landmarks(im):
    rects = detector(im, 1)

    #if len(rects) > 1:
    #    return "error"
    if len(rects) == 0:
        return "error"
    return np.matrix([[p.x, p.y] for p in predictor(im, rects[0]).parts()])


def annotate_landmarks(im, landmarks):
    im = im.copy()
    for idx, point in enumerate(landmarks):
        pos = (point[0, 0], point[0, 1])
        cv2.putText(im, str(idx), pos,
                    fontFace=cv2.FONT_HERSHEY_SCRIPT_SIMPLEX,
                    fontScale=0.4,
                    color=(0, 0, 255))
        cv2.circle(im, pos, 3, color=(0, 255, 255))
    return im

def top_lip(landmarks):
    top_lip_pts = []
    for i in range(50,53):
        top_lip_pts.append(landmarks[i])
    for i in range(61,64):
        top_lip_pts.append(landmarks[i])
    top_lip_all_pts = np.squeeze(np.asarray(top_lip_pts))
    top_lip_mean = np.mean(top_lip_pts, axis=0)
    return int(top_lip_mean[:,1])

def bottom_lip(landmarks):
    bottom_lip_pts = []
    for i in range(65,68):
        bottom_lip_pts.append(landmarks[i])
    for i in range(56,59):
        bottom_lip_pts.append(landmarks[i])
    bottom_lip_all_pts = np.squeeze(np.asarray(bottom_lip_pts))
    bottom_lip_mean = np.mean(bottom_lip_pts, axis=0)
    return int(bottom_lip_mean[:,1])

def mouth_open(image):
    landmarks = get_landmarks(image)

    if landmarks == "error":
        return image, 0

    image_with_landmarks = annotate_landmarks(image, landmarks)
    top_lip_center = top_lip(landmarks)
    bottom_lip_center = bottom_lip(landmarks)
    lip_distance = abs(top_lip_center - bottom_lip_center)
    # cv2.imshow('Result', image_with_landmarks)
    return image_with_landmarks, lip_distance

    #cv2.imshow('Result', image_with_landmarks)
    #cv2.imwrite('image_with_landmarks.jpg',image_with_landmarks)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
def yawn_detection_wrapper(frame):
    yawns = 0
    yawn_status = False
    print("Calling Yawn detection Core")
    img, yawn_status, yawns = yawn_detection_core(frame, yawns, yawn_status)
    return img

def yawn_detection_core(frame, yawns, yawn_status):
    image_landmarks, lip_distance = mouth_open(frame)
    #cv2.imshow('Live Landmarks', image_landmarks )

    prev_yawn_status = yawn_status

    if lip_distance > 25:
        yawn_status = True

        cv2.putText(frame, "Subject is Yawning", (50,450),
                    cv2.FONT_HERSHEY_COMPLEX, 1,(0,0,255),2)

        output_text = " Yawn Count: " + str(yawns + 1)

        query = ("INSERT INTO logs (activity, timestamp) VALUES (%s, %s)")
        data_log = (output_text, datetime.now())
        cursor.execute(query, data_log)
        connection.commit()

        cv2.putText(frame, output_text, (50,50),
                    cv2.FONT_HERSHEY_COMPLEX, 1,(0,255,127),2)

    else:
        yawn_status = False

    if prev_yawn_status == True and yawn_status == False:
        yawns += 1
        print("Yawn is detected !!!")

    return frame, yawn_status, yawns

def drowsiness_detection_wrapper(img, closed): 
    closed = drowsiness_detection_core(img, closed) 
    if closed == True:
        cv2.putText(img,'Eyes closed',(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
        # print('Eyes closed!!!')
        print('Eyes closed!!!')
        query = ("INSERT INTO logs (activity, timestamp) VALUES (%s, %s)")
        data_log = ('Eyes closed', datetime.now())
        cursor.execute(query, data_log)
        connection.commit()
    else:
        cv2.putText(img,'Eyes open',(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
        # print('Eyes open!!!')
    return img



def drowsiness_detection_core(img, closed):
    
    frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        frame,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        # flags = cv2.CV_HAAR_SCALE_IMAGE
    )
    # print("Found {0} faces!".format(len(faces)))
    if len(faces) > 0:
        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        frame_tmp = img[faces[0][1]:faces[0][1] + faces[0][3], faces[0][0]:faces[0][0] + faces[0][2]:1, :]
        frame = frame[faces[0][1]:faces[0][1] + faces[0][3], faces[0][0]:faces[0][0] + faces[0][2]:1]
        eyes = eyeCascade.detectMultiScale(
            frame,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            # flags = cv2.CV_HAAR_SCALE_IMAGE
        )
        if len(eyes) == 0:
            closed = True
        else:
            closed = False

    return closed
    

def test_pipeline():
    cap = cv2.VideoCapture(0)
    yawns = 0
    yawn_status = False
    closed = False


    while True:
        ret, frame = cap.read()
        img = yawn_detection_wrapper(frame)
        img = drowsiness_detection_wrapper(img, closed)
        cv2.imshow('Yawn Detection', img)

        if cv2.waitKey(1) == 13: #13 is the Enter Key
            break

    cap.release()
    cv2.destroyAllWindows()


