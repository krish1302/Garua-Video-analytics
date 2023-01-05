import cv2
import datetime
from flask import Response
from flask_cors import cross_origin
import imutils
import numpy as np
from Garuda.centroidtracker import CentroidTracker
from Garuda import app
from Garuda.views import createCamera

protopath = "D:/Kushagramati/Garuda-Angular-NodeJS-MySQL/usecase/MobileNetSSD_deploy.prototxt"
modelpath = "D:/Kushagramati/Garuda-Angular-NodeJS-MySQL/usecase/MobileNetSSD_deploy.caffemodel"
detector = cv2.dnn.readNetFromCaffe(prototxt=protopath, caffeModel=modelpath)


CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

tracker = CentroidTracker(maxDisappeared=5, maxDistance=70)


def non_max_suppression_fast(boxes, overlapThresh):
    try:
        if len(boxes) == 0:
            return []

        if boxes.dtype.kind == "i":
            boxes = boxes.astype("float")

        pick = []

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(y2)

        while len(idxs) > 0:
            last = len(idxs) - 1
            i = idxs[last]
            pick.append(i)

            xx1 = np.maximum(x1[i], x1[idxs[:last]])
            yy1 = np.maximum(y1[i], y1[idxs[:last]])
            xx2 = np.minimum(x2[i], x2[idxs[:last]])
            yy2 = np.minimum(y2[i], y2[idxs[:last]])

            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)

            overlap = (w * h) / area[idxs[:last]]

            idxs = np.delete(idxs, np.concatenate(([last],
                                                   np.where(overlap > overlapThresh)[0])))

        return boxes[pick].astype("int")
    except Exception as e:
        print("Exception occurred in non_max_suppression : {}".format(e))



def car_detection(camera):
    fps_start_time = datetime.datetime.now()
    fps = 0
    total_frames = 0
    object_id_list=[]
    dtime=dict()
    dwell_time=dict()


    while True:
        ret, frame = camera.read()
        # cv2.line(img=frame, pt1=(80, 600), pt2=(1000, 550), color=(0, 0, 255), thickness=3, lineType=8, shift=0)

        frame = imutils.resize(frame, width=450)

        # cv2.resize(frame, (700, 700))
        total_frames = total_frames + 1

        (H, W) = frame.shape[:2]

        blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)

        detector.setInput(blob)
        car_detections = detector.forward()
        rects = []
        for i in np.arange(0, car_detections.shape[2]):
            confidence = car_detections[0, 0, i, 2]
            if confidence > 0.8:
                idx = int(car_detections[0, 0, i, 1])

                if CLASSES[idx] != "car":
                    continue

                car_box = car_detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                (startX, startY, endX, endY) = car_box.astype("int")
                rects.append(car_box)

        boundingboxes = np.array(rects)
        boundingboxes = boundingboxes.astype(int)
        rects = non_max_suppression_fast(boundingboxes, 0.3)

        objects = tracker.update(rects)
        for (objectId, bbox) in objects.items():
            x1, y1, x2, y2 = bbox
            x1 = int(x1)
            y1 = int(y1)
            x2 = int(x2)
            y2 = int(y2)
            if objectId not in object_id_list:
                object_id_list.append(objectId)
                dtime[objectId]=datetime.datetime.now()
                dwell_time[objectId]=0
            else:
                curr_time = datetime.datetime.now()
                old_time = dtime[objectId]
                time_diff = curr_time - old_time
                dtime[objectId] = datetime.datetime.now()
                sec = time_diff.total_seconds()
                dwell_time[objectId] += sec

            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
            text = "{}|{:.2f}".format(objectId, float(dwell_time[objectId]))
            time = round(float(dwell_time[objectId]),2)
            text1="Alert"
            # text = "ID: {}".format(objectId)
            cv2.putText(frame, text, (x1, y1-5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 0), 1)
            print(time)

            if(time>30) :
                cv2.putText(frame, text1, (180, 15), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(frame, text, (x1, y1 - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)

        fps_end_time = datetime.datetime.now()
        time_diff = fps_end_time - fps_start_time
        if time_diff.seconds == 0:
            fps = 0.0
        else:
            fps = (total_frames / time_diff.seconds)

        fps_text = "FPS: {:.2f}".format(fps)

        # Displaying FPS
        cv2.putText(frame, fps_text, (10, 240), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (128, 0, 128), 1)

        print(fps_text)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

        # return frame