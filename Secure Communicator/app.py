import numpy as np
from flask import Flask, flash, render_template, redirect, request, url_for, Response, session
import pyrebase
from user_input_filter import *
import cv2
import requests
from datetime import datetime 
import pytz
from backend import *
import firebase_admin
from firebase_admin import credentials, firestore, storage

config = {
  "apiKey": "secret key",
  "authDomain": " ",
  "databaseURL": " ",
  "projectId": " ",
  "storageBucket": " ",
  "messagingSenderId": " ",
  "appId": " ",
  "measurementId": " "
}
firebase = pyrebase.initialize_app(config)  
db=firebase.database()
auth = firebase.auth()


cred = credentials.Certificate(r'json file path')
firebase_admin.initialize_app(cred, {
    'storageBucket': 'your storageBucket url'
})

firestore_db = firestore.client()
bucket = storage.bucket()


video = cv2.VideoCapture(0)
app=Flask(__name__)

verified=False

def face_verification(json_data, new_url):
    # Encoding loaded
    res = requests.get(json_data['enc_url'])
    data = pickle.loads(res.content)

    # Image Loaded
    resp = requests.get(new_url, stream=True).raw
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    try:
        encodings = face_recognition.face_encodings(rgb)[0]
        matches = face_recognition.compare_faces(data, encodings)
        return matches[0]
    except:
        return False


@app.route('/verification')
def verification():
    token = session['user']
    data = auth.get_account_info(token)
    email = data['users'][0]['email']

    user_data = firestore_db.collection('UserData').document(email).get().to_dict()
    # enc_url = user_data['enc_url']
    return Response(generate(user_data), mimetype='multipart/x-mixed-replace;boundary=frame')



def generate(json_data):
    i = 0
    video = cv2.VideoCapture(0)
    file_name = str(json_data['email']) + 'temp.jpg'
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
            # face_encoding_update(image)
            # return 0
            return upload_temp(file_name, json_data)   



def upload_temp(file_name, json_data):
    global verified
    blob = bucket.blob(file_name)
    blob.upload_from_filename(file_name)
    blob.make_public()
    new_url = blob.public_url
    print(new_url, "new_url")
    verified = face_verification(json_data, new_url)
    print(verified)
    return verified
#    if not verified:
        #value=False
        #return redirect(url_for("error",verify=verify))
#        print("NO access")
#        return False

        
#    else:
        #value=True
#       return redirect(url_for("error",verify=verify))
#        print("face verified")
#        return True


@app.route("/after_login")
def after_login():
    temp=True
    token = session['user']
    data = auth.get_account_info(token)
    email = data['users'][0]['email']
    json_data = firestore_db.collection('UserData').document(email).get().to_dict()

    username = json_data['user']
    return render_template("home.html", v=temp, username=username)



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


@app.route('/capture_image')
def capture_image():
    return render_template("capture.html", username=name)


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
            # face_encoding_update(image)
            # return 0
            return upload(file_name, json_data)


@app.route('/videocamera')
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
            session['user_id']=user_data['email']
           # all_user=firestore_db.collection('UserData').get().to_dict()
           # print(all_user)
            print(user_data)    # {email, user, ImageURL, enc_url}

            return render_template('verify.html' )

            # new_url = ""
            #
            # # FACE VERIFICATION
            #
            # if face_verification(json_data=user_data, new_url=new_url):
            #     return render_template("login.html", s=successful)
            #     # return redirect(url_for('.video_feed', message=json_data))
            # else:
            #     return render_template('login.html', us=unsuccessful)
            # # return render_template('login.html', s=successful)

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
    successful = "SignUp successful"
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:  # or not check_email(email) or not check_pass(password):
            return render_template("register.html", us=unsuccessful)
        else:
            try:
                user = auth.create_user_with_email_and_password(email, password)
                session['user'] = user['idToken']
                #token = session['user']
                #data = auth.get_account_info(token)
                # json_data = {
                #     'email': data['users'][0]['email'],
                #     'ImageURL': '',
                #     'user': name
                # }
                return render_template("capture.html", s=successful, username=name)
            except:
                return render_template('register.html', un=unsuccessful)

    return render_template("register.html")

@app.route("/chatroom/<string:email>", methods=['POST','GET'])
def chatroom(email):
   # if user_id in session:
            token = session['user']
            data = auth.get_account_info(token)
            my_email = data['users'][0]['email']

            session['to']=email
#            print(my_email)
#            to = email
#            print(to)
            if request.method=="POST":
                txt_body=request.form['text_body']
                tz_India = pytz.timezone('Asia/Kolkata') 
                datetime_India = datetime.now(tz_India)
#                print("India time:", datetime_India.strftime("%Y-%m-%d %H:%M:%S"))
                timestamp=datetime_India.strftime("%Y-%m-%d %H:%M:%S")
                # send the messages 
                msg ={ 'from' : my_email ,
                    'Time':timestamp,
                    'message': txt_body,
                    'to': email
                }
                firestore_db.collection('messages').add(msg)


            all_user=firestore_db.collection('UserData').get()
            users=[]
            for i in all_user:
                users.append( {'user': i.to_dict()['user'] , 'email': i.to_dict()['email'] })
#            print(users)    
            return render_template("chats_room.html",users=users)
#    else:
#        return render_template("login.html")    



@app.route('/chats', methods=['GET', 'POST'])
def chats():
    if 'user_id' in session:
        to = session['to']
#        print(to)
        token = session['user']
        data = auth.get_account_info(token)
        my_email = data['users'][0]['email']
#        uid = session['uid']
        # Get message
        #email="sangam@gmail.com"
#        print(session)
#        print(session['user_id'])
        all_chats=firestore_db.collection('messages').get()
        chats=[]
        for i in all_chats:
            if (i.to_dict()['to'] == to  and i.to_dict()['from']==my_email) or (i.to_dict()['from'] == to  and i.to_dict()['to']==my_email) :
                chats.append(i.to_dict())

        chats=sorted(chats, key = lambda x: datetime.strptime(x['Time'], "%Y-%m-%d %H:%M:%S"))
#       print(chats)

#       for i in chats:
#            print(i.to_dict())
        return render_template('chats.html', chats=chats, my_email=my_email )
    return redirect(url_for('login'))    


if __name__ == "__main__":
    app.run(debug=True)



