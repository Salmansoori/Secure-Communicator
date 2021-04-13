import numpy as np
from flask import Flask, render_template, redirect, request, url_for, Response, session, jsonify, make_response
import pyrebase
from user_input_filter import *
from encryption import do_encrypt, do_decrypt
import requests
from datetime import datetime
import pytz
import json
import cv2
import face_recognition
import pickle
import firebase_admin
from firebase_admin import credentials, firestore, storage

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

cred = credentials.Certificate(r'secret_key.json')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'encryp-chat-8568c.appspot.com'
})

firestore_db = firestore.client()
bucket = storage.bucket()

video = cv2.VideoCapture(0)
app = Flask(__name__)

###############    API CALL SECTION FOR ANDROID #####################
#****************************************************************************

@app.route('/api/user/encrypt', methods=['POST'])
def enc():
    content = request.data.decode('utf-8')
    body = json.loads(content)
    msg = str(body['message'])

    enc = do_encrypt(msg)
    data = {
        "message":str(enc)
    }

    return make_response(jsonify(data), 200)


@app.route('/api/user/decrypt', methods=['POST'])
def dec():
    content = request.data.decode('utf-8')
    body = json.loads(content)

    try:
        msg = body['message'].split("'")[1]
        dec = do_decrypt(msg)
        data = {
            "message":str(dec)
        }
        return make_response(jsonify(data), 200)

    except:
        data = {
               "message":"could not decrypt"
            }
        return make_response(jsonify(data), 200)


@app.route('/api/user/register', methods = ['POST'])
def app_register():
    content =  request.data.decode('utf-8')
    body = json.loads(content)
    data = {
            "status": "unsuccessful"
        }

    try:
        email = body['email']
        user = body['user']
        ImageURL = body['Url']
        json_data = {
            "email": email,
            "user": user,
            "ImageURL": ImageURL
        }

        if update_db_app(json_data):
            data['status'] =  "successful"
            # res = make_response(jsonify(data), 200)
            # res.headers['Access-Control-Allow-Origin'] = '*'
            print(data)
            return make_response(jsonify(data), 200)
        else:
            return make_response(jsonify(data), 200)

    except KeyError:
        data ["status"] = "Improper details provided"
        return make_response(jsonify(data), 200)


def update_db_app(json_data):
    enc_data = face_encoding_update(json_data['ImageURL'])
    file_name = str(json_data['email']) + ".txt"
    f = open(file_name, "wb")
    f.write(pickle.dumps(enc_data))
    f.close()

    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    blob.make_public()

    json_data['enc_url'] = blob.public_url
    try:
        firestore_db.collection(u'UserData').document(json_data['email']).set(json_data)
        return True
    except:
        return False



@app.route('/api/user/login', methods = ['POST'])
def app_login():
    content =  request.data.decode('utf-8')
    body = json.loads(content)

    data = {
        "status": "unsuccessful",
    }

    try:
        email = body['email']
        temp_url = body['temp_url']
        json_data = firestore_db.collection('UserData').document(email).get().to_dict()
        try:
            verified = face_verification(json_data, temp_url)

            if not verified:
                return make_response(jsonify(data), 200)

            data["status"] = "successful"
            return make_response(jsonify(data), 200)

        except (KeyError, IndexError):
            data["status"] = "Improper details provided"
            return make_response(jsonify(data), 200)

    except KeyError:
        data["status"] = "Improper details provided"
        return make_response(jsonify(data), 200)


#****************************************************************************#


verified = False


def check_login():
    if "user_id" in session and "user" in session:
        return True
    else:
        return False


def face_verification(json_data, new_url):
    # Encoding loaded
    try:
        res = requests.get(json_data['enc_url'])
        data = pickle.loads(res.content)

        # Image Loaded
        resp = requests.get(new_url, stream=True).raw
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        encodings = face_recognition.face_encodings(rgb)[0]
        matches = face_recognition.compare_faces(data, encodings)
        return matches[0]
    except (KeyError, IndexError):
        return False


@app.route('/verification', methods=["POST","GET"])
def verification():
    token = session['user']
    data = auth.get_account_info(token)
    email = data['users'][0]['email']
    user_data = firestore_db.collection('UserData').document(email).get().to_dict()

    img = request.files['image'].read()
    # CHANGE TO TEMP.JPG
    file_name = str(user_data['email']) + '.jpg'
    f = open(file_name, 'wb')
    f.write(img)
    f.close()

    return upload_temp(file_name, user_data)

   # return Response(generate(user_data), mimetype='multipart/x-mixed-replace;boundary=frame')


def upload_temp(file_name, json_data):
    global verified
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    blob.make_public()

    new_url = blob.public_url
    try:
        verified = face_verification(json_data, new_url)
    except (KeyError, IndexError):
        return render_template("unauthorize.html")

    # print(verified)
    return redirect(url_for('profile'))


@app.route("/profile")
def profile():
    if not check_login():
        return render_template("unauthorize.html")
    session['is_login'] = str(verified)

    token = session['user']
    data = auth.get_account_info(token)
    email = data['users'][0]['email']
    json_data = firestore_db.collection('UserData').document(email).get().to_dict()

    username = json_data['user']
    return render_template("home.html", username=username)


def face_encoding_update(url):
    resp = requests.get(url, stream=True).raw
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    known_encodings = []
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # Use face_recognition to locate faces
    boxes = face_recognition.face_locations(rgb, model='hog')

    # Computing facial encoding
    encodings = face_recognition.face_encodings(rgb, boxes)
    for encoding in encodings:
        known_encodings.append(encoding)
    return known_encodings


def upload(file_name, json_data):
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    blob.make_public()
    json_data['ImageURL'] = blob.public_url
    return update_database(json_data)


def update_database(json_data):
    enc_data = face_encoding_update(json_data['ImageURL'])
    file_name = str(json_data['email']) + ".txt"
    f = open(file_name, "wb")
    f.write(pickle.dumps(enc_data))
    f.close()

    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    blob.make_public()

    json_data['enc_url'] = blob.public_url
    firestore_db.collection(u'UserData').document(json_data['email']).set(json_data)

    # print("Registration Successful")

    return redirect(url_for('index'))



@app.route("/get_image", methods=['POST','GET'])
def get_image():
    token = session['user']
    data = auth.get_account_info(token)
    name = session['user_name']

    json_data = {
        'email': data['users'][0]['email'],
        'ImageURL': '',
        'user': name ,
    }


    img = request.files['image'].read()
    file_name = str(json_data['email']) + '.jpg'
    f = open(file_name, 'wb')
    f.write(img)
    f.close()

    return upload(file_name,json_data)




@app.route("/")
def ind():
    return render_template("home.html")


@app.route("/home")
def index():
    return render_template("home.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    unsuccessful = "Please check your credentials"
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        try:
            sign_user = auth.sign_in_with_email_and_password(email, password)
            sign_user = auth.refresh(sign_user['refreshToken'])
            session['user'] = sign_user['idToken']
            user_data = firestore_db.collection('UserData').document(email).get().to_dict()
            session['user_id'] = user_data['email']

            return render_template('verify.html')

        except:
            return render_template("login.html", us=unsuccessful)

    return render_template('login.html')


@app.route("/logout")
def logout():
    if 'user_id' in session:
        session.clear()
        return redirect(url_for('index'))
    return redirect(url_for('login'))


@app.route("/register", methods=['POST', 'GET'])
def register():
    unsuccessful = "Your confirm_password does not match with password"
    wrong_email = "Email format is not satisfied "
    weak_pass = "Password is too weak"
    successful = "SignUp successful"
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            return render_template("register.html", us=unsuccessful)
        elif not check_email(email):
            return render_template("register.html", us=wrong_email)
        elif not check_pass(password):
            return render_template("register.html", us=weak_pass)
        else:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                session['user'] = user['idToken']
                session['user_name'] = name

                return render_template("camera.html", s=successful, username=name)
            except:
                return render_template('register.html', un=unsuccessful)

    return render_template("register.html")


@app.route("/chatroom/<string:email>", methods=['POST', 'GET'])
def chatroom(email):
    if not check_login():
        return render_template("unauthorize.html")

    if 'user_id' in session:
        token = session['user']
        data = auth.get_account_info(token)
        my_email = data['users'][0]['email']

        session['receiver_id'] = email
        to = email
        receiver_data = firestore_db.collection('UserData').document(to).get()
        session['receiver_name'] = receiver_data.to_dict()['user']

        if request.method == "POST":
            txt_body = request.form['text_body']

            tz_India = pytz.timezone('Asia/Kolkata')
            datetime_India = datetime.now(tz_India)
            timestamp = datetime_India.strftime("%Y-%m-%d %H:%M:%S")

            message = do_encrypt(message=txt_body)

            msg = {'from': my_email,
                   'Time': timestamp,
                   'message': message,
                   'to': email
                   }
            firestore_db.collection('messages').add(msg)

        all_user = firestore_db.collection('UserData').get()
        users = []
        for i in all_user:
            users.append({'user': i.to_dict()['user'], 'email': i.to_dict()['email']})

        return render_template("chats_room.html", users=users)

    return render_template("login.html")


@app.route('/chats', methods=['GET', 'POST'])
def chats():
    if not check_login():
        return render_template("unauthorize.html")

    if 'user_id' in session:
        to = session['receiver_id']

        token = session['user']
        data = auth.get_account_info(token)
        my_email = data['users'][0]['email']

        all_chats = firestore_db.collection('messages').get()

        chat_list = []
        for i in all_chats:
            if (i.to_dict()['to'] == to and i.to_dict()['from'] == my_email) or (
                    i.to_dict()['from'] == to and i.to_dict()['to'] == my_email):
                try:
                    decrypt_dict = i.to_dict()
                    msg = do_decrypt(decrypt_dict['message'])
                    decrypt_dict['message'] = msg
                    chat_list.append(decrypt_dict)
                except:
                    chat_list.append(i.to_dict())

        chat_list = sorted(chat_list, key=lambda x: datetime.strptime(x['Time'], "%Y-%m-%d %H:%M:%S"))

        return render_template('chats.html', chats=chat_list, my_email=my_email)
    return redirect(url_for('login'))



if __name__ == "__main__":
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(host='ec2-3-15-34-218.us-east-2.compute.amazonaws.com', port='8080',debug=True)
