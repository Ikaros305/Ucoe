# Importimg the Libraries
from functools import wraps
import sys
import os
import pyrebase
import json
from flask import *
from flask_mail import Mail, Message


#############   TEST EMAIL ID   ###############
config = {
    "apiKey": "AIzaSyDKM5jToFhKzJOiEyI13T-7uTZhut-fzVk",
    "authDomain": "test-db319.firebaseapp.com",
    "databaseURL": "https://test-db319.firebaseio.com",
    "projectId": "test-db319",
    "storageBucket": "test-db319.appspot.com",
    "messagingSenderId": "878248691705",
    "appId": "1:878248691705:web:feb670fc0bc47710421f28",
    "measurementId": "G-F07GBFWC5S",
}

# init firebase
firebase = pyrebase.initialize_app(config)
# real time database instance
db = firebase.database()
# auth instance
auth = firebase.auth()
# admin Credentials
admin_email = {"admin1@gmail.com": "password", "admin2@gmail.com": "password"}


# db.child("Names").push({"Name": "Utsav", "Email" : "utsav@gmail.com"})
# db.child("Names/Student Names/-M4w_T2u6lIePYjnq1Ht").update({"Name": "Utsav", "Email" : "maan@gmail.com"})
# users = db.child("Names/Student Names/-M4w_T2u6lIePYjnq1Ht").get()
# print(users.val())
# db.child("Names/Student Names/-M4w_T2u6lIePYjnq1Ht").remove()

# new instance of Flask
app = Flask(__name__)

#####FOR MAIL#####
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USERNAME"] = "sample1test.it2@gmail.com"
app.config["MAIL_PASSWORD"] = "youknowhowto"
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = True
mail = Mail(app)
#####FOR MAIL#####

###############dedsec's TEST#################
# post = {
#     "title": "Amadeus",
#     "content": "I am the Greatest Luhar who ever lived",
#     "author": "dedsec995"
# }
# db.child("Posts").push(post)
###############dedsec's TEST#################


# index route
@app.route("/", methods=["GET", "POST"])
def index():
    allposts = db.child("Posts").get()
    if request.method == "POST":
        if request.form["submit"] == "Send Message":
            try:
                name = request.form["name"]
                email = request.form["email"]
                message = request.form["message"]
                msg = Message(
                    "Hello {}".format(name.capitalize()),
                    sender="sample1test.it2@gmail.com",
                    recipients=[email],
                )
                msg.body = "Hello {}, \n We received your mail regarding a query \n This is your Query :- {} \n \n We hope to resolve your Query as soon as possible".format(
                    name.capitalize(), message
                )
                mail.send(msg)
                query = {
                    "email": email,
                    "message": message,
                    "name": name
                }
                db.child("Queries").push(query)
                return render_template("thankyou.htm")
            except:
                return render_template("failed.htm")
        elif request.form["submit"] == "logout":
            auth.current_user = None
    if allposts.val() == None:
        return render_template("index.html", auth=auth)
    else:
        # return render_template("index.html", posts=allposts)
        return render_template("index.html", auth=auth)

# Webinar


@app.route("/webinar", methods=["GET", "POST"])
def webinar():
    if request.method == "POST":
        if request.form["submit"] == "logout":
            auth.current_user = None
    return render_template("webinar.html", auth=auth)


# signup route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if auth.current_user != None:
        return redirect(url_for("index"))
    if request.method == "POST":
        if request.form["submit"] == "signup":
            # get the request form data
            email = request.form["email"]
            password = request.form["password"]
            try:
                name = request.form["name"]
                lastname = request.form["lastname"]
                db.child("Student Name").push(
                    {
                        "Name": name,
                        "Lastname": lastname,
                        "Email ID": email,
                        "Password": password,
                    }
                )
                # create the user
                auth.create_user_with_email_and_password(email, password)
                return redirect('/login')
            except:
                return render_template("login.html", message="The email is already taken, try another one, please")
            # sname = db.child("Student Name").get()
            # to = sname.val()
            # return render_template("login.html", t=to.values())
    return render_template("signup.html", auth=auth)


@app.route("/login", methods=["GET", "POST"])
def login():
    if auth.current_user != None:
        return redirect(url_for("index"))
    if request.method == "POST":
        if request.form["submit"] == "login":
            email = request.form["email"]
            password = request.form["password"]
            try:
                # login in the user
                user = auth.sign_in_with_email_and_password(email, password)
                users = db.child("Student Name").get()
                user = users.val()
                for key, values in user.items():
                    # return values
                    for inkey, invalues in values.items():
                        # return inkey
                        if email in invalues:
                            user_name = values["Name"].upper()
                            try:
                                news_get = db.child("News Updates").get()
                                return render_template(
                                    "student.html",
                                    news=news_get.val(),
                                    user_detail=user_name,
                                    auth=auth
                                )
                            except:
                                return "No NEWS FOUND."
                                # return "NO NEWS FOUND"
                            return render_template("index.html", user_detail=user_name, auth=auth)
                return render_template("index.html", t=user, auth=auth)
            except:
                # print("Wrong Pass")
                return render_template("login.html", message="Wrong Credentials")
            # print(login)

        elif request.form["submit"] == "pass":
            return redirect(url_for("forgotpass"))
            # return render_template("forgotpass.html")
    return render_template("login.html", auth=auth)


@app.route("/news", methods=["GET", "POST"])
def news():

    if request.method == "POST":
        if request.form["submit"] == "logout":
            auth.current_user = None
    users = db.child("Student Name").get()
    user = users.val()
    if auth.current_user != None:
        for key, values in user.items():
            # return values
            for inkey, invalues in values.items():
                # return inkey
                if auth.current_user["email"] in invalues:
                    user_name = values["Name"].upper()
                    try:
                        news_get = db.child("News Updates").get()

                        return render_template("student.html", news=news_get.val(), user_detail=user_name, auth=auth)

                    except:
                        return "No NEWS FOUND."
    else:
        try:
            news_get = db.child("News Updates").get()

            return render_template("student.html", news=news_get.val(), auth=auth)

        except:
            return "No NEWS FOUND."


@app.route("/forgotpass", methods=["GET", "POST"])
def forgotpass():
    if request.method == "POST":
        if request.form["submit"] == "pass":
            email = request.form["email"]
            auth.send_password_reset_email(email)

            # elif request.form["submit"] == "get":
            #     users = db.child("Student Name").get()
            #     a = users.val()
            #     # sub = json.loads(users.val())
            #     print(type(users.val()))
            #     return a
    return render_template("forgotpass.html")


@app.route("/admin.html", methods=["GET", "POST"])
def admin():
    allquery = db.child("Queries").get()
    if request.method == "POST":
        if request.form["submit"] == "add":
            headline = request.form["headline"]
            story = request.form["story"]
            db.child("News Updates").push(
                # {"Headline": headline, "Story": story,}
                {headline: story}
            )
            query_get = db.child("Queries").get()
            return render_template("admin.html",
                                   query=query_get.val(),
                                   user_detail=user_name)

        # elif request.form["submit"] == "news":
        #     try:
        #         news_get = db.child("News Updates").get()
        #         return render_template("news.html", news=news_get.val())
        #     except:
        #         return "NO NEWS FOUND"
        # news = news_get.val()
    if allquery.val() == None:
        return render_template("admin.html")
    else:
        return render_template("admin.html", querys=allquery)


@app.route("/adminlogin.html", methods=["GET", "POST"])
def adminlogin():
    if request.method == "POST":
        if request.form["submit"] == "adminlogin":
            email = request.form["email"]
            password = request.form["password"]
            try:
                admin_email[email] == password
                try:
                    login = auth.sign_in_with_email_and_password(
                        email, password)
                    return render_template("admin.html")
                except:
                    return "Errorrrr Loading page please try again Later......"
            except:
                return "Wrong Email or Password"

            # print(login)

        elif request.form["submit"] == "home":
            return render_template("index.html")
    return render_template("adminlogin.html")


if __name__ == "__main__":
    app.run(debug=True)
