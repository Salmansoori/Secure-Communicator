from flask import Flask, render_template, redirect, request, url_for, Response, session
import pyrebase
from user_input_filter import *
import cv2
import firebase_admin
from firebase_admin import credentials, firestore, storage

# config = {
#   "apiKey": "secret key",
#   "authDomain": " ",
#   "databaseURL": " ",
#   "projectId": " ",
#   "storageBucket": " ",
#   "messagingSenderId": " ",
#   "appId": " ",
#   "measurementId": " "
# }

config = {
    "apiKey": "AIzaSyAC8zIhZqHSkWaMOBqOXNopxdS4cP9WXh0",
    "authDomain": "encryp-chat-8568c.firebaseapp.com",
    "databaseURL": "https://encryp-chat-8568c-default-rtdb.firebaseio.com/",
    "projectId": "encryp-chat-8568c",
    "storageBucket": "encryp-chat-8568c.appspot.com",
    "messagingSenderId": "957818347815",
    "appId": "1:957818347815:web:8c6e4bb000a52b78af4902"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()
auth = firebase.auth()

cred = credentials.Certificate(r'C:\Users\ASUS\Desktop\Secure-Communicator\Secure Communicator\secret_key.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'encryp-chat-8568c.appspot.com'
})

firestore_db = firestore.client()
bucket = storage.bucket()

app = Flask(__name__)


@app.route('/capture_image')
def capture_image():
    return render_template("capture.html")


def upload(file_name, json_data):
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    blob.make_public()
    # print(blob.public_url)
    json_data['ImageURL'] = blob.public_url

    return update_database(json_data)


def update_database(json_data):
    print(json_data)
    firestore_db.collection(u'UserData').document(json_data['email']).set(json_data)
    print("Registration Successful")
    return 0


# def get():
#     print("*" * 50)
#     data = firestore_db.collection('UserData').get()
#     for i in data:
#         print(i.to_dict())
#     print("*" * 50)
#     return app.add_url_rule('/login', redirect_to=url_for('static', filename='templates/login.html'))
#     # return redirect(url_for('.login'))
#
#     # @app.route('/add_data')
#     # def add(email, user, ImageURL):
#     #     firestore_db.collection(u'songs').add({'email': email, 'user': user, 'ImageURL': ImageURL})
#     #     return True


def gen(json_data):
    i = 0
    video = cv2.VideoCapture(0)
    file_name = str(json_data['email']) + '.jpg'
    while True:
        i += 1
        success, image = video.read()
        ret, jpeg = cv2.imencode('.jpg', image)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        if i >= 80:
            video.release()
            cv2.destroyAllWindows()
            cv2.imwrite(file_name, image)

            return upload(file_name, json_data)


@app.route('/video_feed')
def video_feed():
    name = request.args['username']
    # name = "test"
    token = session['user']
    data = auth.get_account_info(token)

    json_data = {
        'email': data['users'][0]['email'],
        'ImageURL': '',
        'user': name,
    }
    return Response(gen(json_data), mimetype='multipart/x-mixed-replace;boundary=frame')


@app.route('/user_info')
def user_info():
    token = session['user']
    user = auth.get_account_info(token)
    print(user)
    return render_template('home.html')


@app.route("/")
def ind():
    return render_template("home.html")


@app.route("/home")
def index():
    return render_template("home.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    # form=LoginForm(request.form)
    unsuccessful = "Please check your credentials"
    successful = "Login successful"
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        try:
            sign_user = auth.sign_in_with_email_and_password(email, password)
            sign_user = auth.refresh(sign_user['refreshToken'])
            session['user'] = sign_user['idToken']

            user_data = firestore_db.collection('UserData').document(email).get().to_dict()
            print(user_data)    # {email, user, ImageURL}

            # FACE VERIFICATION

            # if face_verify(user_data['ImageURL']):
            #     return render_template("login.html", s=successful)
            #     # return redirect(url_for('.video_feed', message=json_data))
            # else:
            #     return render_template('login.html', us=unsuccessful)
            return render_template('login.html', s=successful)

        except:
            return render_template("login.html", us=unsuccessful)
    return render_template('login.html')


# def logout():

@app.route("/register", methods=['POST', 'GET'])
def register():
    unsuccessful = "Your confirm_password does not match with password"
    successful = "SignUp successful"
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:  # or not check_email(email) or not check_pass(password):
            return render_template("register.html", us=unsuccessful)
        else:
            user = auth.create_user_with_email_and_password(email, password)
            session['user'] = user['idToken']
            # token = session['user']
            # data = auth.get_account_info(token)
            # json_data = {
            #     'email': data['users'][0]['email'],
            #     'ImageURL': '',
            #     'user': name
            # }
            return render_template("capture.html", s=successful, username=name)

    return render_template("register.html")


# def chat():


if __name__ == "__main__":
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug=True, port=5000)
