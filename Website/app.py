import os
import cv2
from flask import Flask, render_template, Response, request, flash
from core_service.backend_utils import Recognizer
from core_service.database import get_db_connection

#connection = get_db_connection()
#cursor = connection.cursor()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'qwerty123'

PATH = '\\'.join(os.path.abspath(__file__).split('\\')[0:-1])
recognizer = Recognizer(
    camera_src=0
)

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['user_name']
    print(text)
    return render_template("face_registration.html", username = text)

@app.route("/adminlogin")
def admin():
    return render_template("adminlogin.html")

@app.route("/logtable")
def logtable():
    data = ""
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM logs GROUP BY user_name, activity")
    data = cursor.fetchall()
    connection.commit()
    print(data)
    return render_template("logtable.html", data=data)


@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/face_registration")
def face_registration():
    camera = request.args.get("camera")
    username = request.args.get("username");
    print("Check",username)
    if camera is not None and camera == 'off':
        recognizer.close()
        recognizer.setUsername(username)
        flash("Camera turn off!", "info")
    elif camera is not None and camera == 'on':
        recognizer.open()
        recognizer.setUsername(username)
        flash("Camera turn on!", "success")
    print("camera status", recognizer.status())
    return render_template("face_registration.html", is_camera=recognizer.status())
    
@app.route('/video_feed')
def video_feed():
    return Response(recognizer.gen_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)