from flask import Flask,render_template,redirect,request, url_for
import pyrebase

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


app=Flask(__name__)

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
            #auth.get_account_info(user['idToken'])
            return render_template("register.html",s=successful)    
    return render_template("register.html")

#def chat():
    

if __name__ == "__main__":
    app.run(debug=True)

