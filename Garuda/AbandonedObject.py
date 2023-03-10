import cv2
import numpy as np
import tensorflow as tf
import math


class DetectorAPI:
    def __init__(self, path_to_ckpt):
        self.path_to_ckpt = path_to_ckpt

        self.detection_graph = tf.Graph()
        with self.detection_graph.as_default():   
            od_graph_def = tf.compat.v1.GraphDef()
            with tf.io.gfile.GFile(self.path_to_ckpt, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

        self.default_graph = self.detection_graph.as_default()
        self.sess = tf.compat.v1.Session(graph=self.detection_graph)

        # Definite input and output Tensors for detection_graph
        self.image_tensor = self.detection_graph.get_tensor_by_name('image_tensor:0')
        # Each box represents a part of the image where a particular object was detected.
        self.detection_boxes = self.detection_graph.get_tensor_by_name('detection_boxes:0')
        # Each score represent how level of confidence for each of the objects.
        # Score is shown on the result image, together with the class label.
        self.detection_scores = self.detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = self.detection_graph.get_tensor_by_name('detection_classes:0')
        self.num_detections = self.detection_graph.get_tensor_by_name('num_detections:0')
        
    def processFrame(self, image):
            # Expand dimensions since the trained_model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image, axis=0)
        # Actual detection.
#             start_time = time.time()
            (boxes, scores, classes, num) = self.sess.run(
                [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
                feed_dict={self.image_tensor: image_np_expanded})
#             end_time = time.time()

#             print("Elapsed Time:", end_time-start_time)

            im_height, im_width,_ = image.shape
            boxes_list = [None for i in range(boxes.shape[1])]
            for i in range(boxes.shape[1]):
                boxes_list[i] = (int(boxes[0,i,0] * im_height),
                            int(boxes[0,i,1]* im_width),
                            int(boxes[0,i,2] * im_height),
                            int(boxes[0,i,3]*im_width))

            return boxes_list, scores[0].tolist(), [int(x) for x in classes[0].tolist()], int(num[0])

    def close(self):
        self.sess.close()
        self.default_graph.close()




def abandoned_detection(camera):
    _, ref_img = camera.read()
    model_path = r'D:\Kushagramati\Garuda\Garuda_full_first\Pre-Trained Models\ssd_mobilenet_v1_coco_2017_11_17\frozen_inference_graph.pb'
    odapi = DetectorAPI(path_to_ckpt=model_path)
    threshold_person = 0.5
    person_center=(0,0)
    item_center=(0,0)
    lst = [0,0]
    cnt1 = 0

    while True:
        rval, frame = camera.read()
        boxes, scores, classes, num = odapi.processFrame(frame)
        for i in range(len(boxes)):
                # Class 1 represents human
            if (classes[i] == 1 and scores[i] > threshold_person):
                    box = boxes[i]
                    cv2.rectangle(frame,(box[1],box[0]),(box[3],box[2]),(255,0,0),2)
                    person_center = ((box[1]+box[3])/2,(box[2]+box[0])/2)
            else:
                person_center = (0,0)
        diff = cv2.absdiff(ref_img, frame)
        gray=cv2.cvtColor(diff,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)
        contours, hierarchy = cv2.findContours(thresh.copy(),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            x,y,w,h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)
            if area > 1000 and area < 20000:
                if w > 89 and h > 100:
                    lst.append((x,y,w,h))
                    for i in range(len(lst)):
                        if lst[i]==lst[i-1] and lst[i]==lst[i-2]:
                            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                            item_center = ((2*x+w)/2, (2*y+h)/2)
                            x_distance = abs(person_center[0]-item_center[0])
                            y_distance = abs(person_center[1]-item_center[1])
                            distance = math.sqrt((person_center[0]-item_center[0])**2 + (person_center[1]-item_center[1])**2)
                            if distance > 500 and x_distance>250 and y_distance>250:
                                if lst[i]==lst[i-20] and lst[i]==lst[i-40] and lst[i]==lst[i-60]:
                                    cnt1 = cnt1 + 1
                                    if cnt1 > 20:    
                                        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,0,255),2)
                                        print("abandoned object at :" + str(distance))
                        else:
                            item_center = (0,0)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

        # return frame