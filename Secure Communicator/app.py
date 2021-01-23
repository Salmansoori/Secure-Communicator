from flask import Flask, render_template, redirect, request, url_for, Response, session
import pyrebase
from user_input_filter import *
import cv2
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



# def update_database():

    # run encoding function

    # @app.route('/read_data')
    # def get():
    #     data = firestore_db.collection('UserData').get()
    #     for i in data:
    #         print(i.to_dict())
    #         # Dict output
    #         #     {'email': email, 'user': user, 'ImageURL': ImageURL}
    #     return render_template('home.html')
    #
    #
    # @app.route('/add_data')
    # def add(email, user, ImageURL):
    #     firestore_db.collection(u'songs').add({'email': email, 'user': user, 'ImageURL': ImageURL})
    #     return True

@app.route('/capture_image')
def capture_image():
    return render_template("capture.html")    

def gen(h):
    i = 0
    video = cv2.VideoCapture(0)
    while True:  
        i += 1
        success, image = video.read()
        ret, jpeg = cv2.imencode('.jpeg', image)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        # print(i)
        if i >= 100:
            # del video
            video.release()
            cv2.destroyAllWindows()
            # email should the name of image
            cv2.imwrite(r'image1.jpeg', image)
           
            return upload('image1.jpeg')

@app.route('/videocamera')
def video_feed():
    global video
    return Response(gen(video), mimetype='multipart/x-mixed-replace;boundary=frame')


  
# ************************************  
  
@app.route('/user_info')
def user_info():
    token = session['user']
    user = auth.get_account_info(token)
    print(user)
    return render_template('home.html')

  
@app.route("/home")
def index():
    return render_template("home.html")

@app.route("/login", methods=["POST","GET"])
def login():
    #form=LoginForm(request.form)
    unsuccessful="Please check your credentials"
    successful="Login successful"
    if request.method=="POST":
        email=request.form['email']
        password=request.form['password']
        try:
            auth.sign_in_with_email_and_password(email,password)
            return render_template("login.html",s=successful)
        except:
            return render_template("login.html",us=unsuccessful)   
    return render_template('login.html')


#def logout():

@app.route("/register", methods=['POST','GET'])
def register():
    unsuccessful="Your confirm_password does not match with password"
    successful="SignUp successful"
    if request.method=="POST":
        name=request.form['name']
        email=request.form['email']
        password=request.form['password']
        confirm_password=request.form['confirm_password']
        if password!=confirm_password:
            return render_template("register.html",us=unsuccessful)
        else:
            user=auth.create_user_with_email_and_password(email,password)
            auth.get_account_info(user['idToken'])
            return render_template("capture.html",s=successful)    
    return render_template("register.html")






#def chatrooms():




#def chat():
    

if __name__ == "__main__":
    app.run(debug=True)



