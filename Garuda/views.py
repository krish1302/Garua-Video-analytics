import cv2, time
from flask_cors import cross_origin
from flask import Response, redirect, render_template, url_for
from Garuda import app
from Garuda.model import mysql




def createCursor():
    cursor = mysql.connection.cursor()

    # conn = mysql.connector.connect(**config)
    # cursor = conn.cursor()
    return cursor

def commit():
    return  mysql.connection.commit()
    # conn = mysql.connector.connect(**config)
    # return conn.commit()

def createCamera():
    while True:
        camera = cv2.VideoCapture(0)  # use 0 for web camera
        # "rtsp://admin:12345@192.168.1.222:554/Streaming/Channels/401/"
        #  for cctv camera use rtsp://username:password@ip_address:554/user=username_password='password'_channel=channel_number_stream=0.sdp' instead of camera
        # for local webcam use cv2.VideoCapture(0)

        return camera

camera = createCamera()

def gen_frames():  # generate frame by frame from camera
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result


@app.route('/video_feed')
@cross_origin()
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/garuda')
def index():
    cursor = createCursor()
    cursor.execute('SELECT * FROM `ga_user`')
    data = cursor.fetchall()
    return render_template('garuda.html', name ='Balakrihnan',data = data)

@app.route('/')
def static_index():
    return redirect(url_for('index'))
