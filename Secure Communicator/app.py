from flask import Flask, render_template, redirect, request, url_for
import pyrebase
from user_input_filter import *

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

app = Flask(__name__)


@app.route("/")
def index():
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
        # if not check_email(email):
        #     # do not proceed to login
        password = request.form['password']
        # if not check_pass(password):
        #     # do not proceed to login
        try:
            auth.sign_in_with_email_and_password(email, password)
            return render_template("login.html", s=successful)
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
        if password != confirm_password:
            return render_template("register.html", us=unsuccessful)
        else:
            user = auth.create_user_with_email_and_password(email, password)
            # auth.get_account_info(user['idToken'])
            return render_template("register.html", s=successful)
    return render_template("register.html")


# def chat():


if __name__ == "__main__":
    app.run(debug=True)
