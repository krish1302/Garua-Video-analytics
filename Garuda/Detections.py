import cv2
from flask import Response
from Garuda.model import mysql
from flask_cors import cross_origin
from Garuda import app
from Garuda.views import createCursor, commit
from Garuda.LineCrossing import line_detection
from Garuda.Loitering import loitering_detection
from Garuda.carTracking import car_detection
from Garuda.AbandonedObject import abandoned_detection

# camera = cv2.VideoCapture(r'D:\Kushagramati\New folder\Garuda_vivek_final\Garuda_vivek_final\DYN_Line.mp4')
# camera = cv2.VideoCapture("rtsp://admin:12345@192.168.1.222:554/Streaming/Channels/401/")


# def gen_frames():  # generate frame by frame from camera
#     while True:
#         # Capture frame-by-frame
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             frame1 = loitering_detection(frame)
#             frame2 = line_detection(frame1)

#             ret, buffer = cv2.imencode('.jpg', frame2)
#             frame2 = buffer.tobytes()
#             yield (b'--frame\r\n'
#                     b'Content-Type: image/jpeg\r\n\r\n' + frame2 + b'\r\n')  # concat frame one by one and show result


# @app.route('/final')
# @cross_origin()
# def all_detection():
#     #Video streaming route. Put this in the src attribute of an img tag
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/car_detection/<id>')
@cross_origin()
def car_detect(id):
    cursor = createCursor()
    cursor.execute('SELECT * FROM `ga_camera` WHERE `CAM_ID` = %s;',(id))
    data = cursor.fetchone()
    # "rtsp://admin:12345@192.168.1.222:554/Streaming/Channels/401/"
    url = "rtsp://"+data[2]+":"+str(data[3])+"@"+data[5]+":"+str(data[4])+"/Streaming/Channels/"+str(data[6])+"/"
    commit()
    cam = cv2.VideoCapture(url)
    # cam = cv2.VideoCapture(0)
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(car_detection(cam), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/object_detection/<id>')
@cross_origin()
def object_detect(id):
    cursor = createCursor()
    cursor.execute('SELECT * FROM `ga_camera` WHERE `CAM_ID` = %s;',(id))
    data = cursor.fetchone()
    # "rtsp://admin:12345@192.168.1.222:554/Streaming/Channels/401/"
    url = "rtsp://"+data[2]+":"+str(data[3])+"@"+data[5]+":"+str(data[4])+"/Streaming/Channels/"+str(data[6])+"/"
    commit()
    cam = cv2.VideoCapture(url)
    # cam = cv2.VideoCapture(0)
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(abandoned_detection(cam), mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/loitering/<id>')
@cross_origin()
def loitering(id):
    cursor = createCursor()
    cursor.execute('SELECT * FROM `ga_camera` WHERE `CAM_ID` = %s;',(id))
    data = cursor.fetchone()
    # "rtsp://admin:12345@192.168.1.222:554/Streaming/Channels/401/"
    url = "rtsp://"+data[2]+":"+str(data[3])+"@"+data[5]+":"+str(data[4])+"/Streaming/Channels/"+str(data[6])+"/"
    commit()
    cam = cv2.VideoCapture(url)
    # cam = cv2.VideoCapture(0)
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(loitering_detection(cam), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/line_detection/<id>')
@cross_origin()
def line(id):
    cursor = createCursor()
    cursor.execute('SELECT * FROM `ga_camera` WHERE `CAM_ID` = %s;',(id))
    data = cursor.fetchone()
    # "rtsp://admin:12345@192.168.1.222:554/Streaming/Channels/401/"
    url = "rtsp://"+data[2]+":"+str(data[3])+"@"+data[5]+":"+str(data[4])+"/Streaming/Channels/"+str(data[6])+"/"
    commit()
    cam = cv2.VideoCapture(url)
    # cam = cv2.VideoCapture(0)
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(line_detection(cam), mimetype='multipart/x-mixed-replace; boundary=frame')
