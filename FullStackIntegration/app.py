import os
import cv2
from flask import Flask, render_template, Response, request, flash
from core_service.backend_utils import Recognizer


app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty123'

PATH = '\\'.join(os.path.abspath(__file__).split('\\')[0:-1])
recognizer = Recognizer(
    camera_src=0
)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/face_registration")
def face_registration():
    camera = request.args.get("camera")

    if camera is not None and camera == 'off':
        recognizer.close()
        flash("Camera turn off!", "info")
    elif camera is not None and camera == 'on':
        recognizer.open()
        flash("Camera turn on!", "success")
    print("camera status", recognizer.status())
    return render_template("face_registration.html", is_camera=recognizer.status())
    
@app.route('/video_feed')
def video_feed():
    return Response(recognizer.gen_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)