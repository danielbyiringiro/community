from threading import Thread
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory, jsonify
from flask_session import Session
from flask_mail import Mail
from werkzeug.security import check_password_hash, generate_password_hash
from helper import *
from dotenv import load_dotenv

import os


load_dotenv()

app = Flask(__name__)

# Custom filter

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
mail = Mail(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///community.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/assets/<path:folder>/<path:filename>')
def assets(folder, filename):
    return send_from_directory(f'assets/{folder}', filename)

@app.route("/", methods=["GET", "POST"])
@login_required
def index():

    if request.method == "GET":

        username, picture_path, _= user_details()

        rows = db.execute("SELECT * FROM post")
        posts = []

        for post in rows:

            post_id = post['id']
            post_username = post['username']
            post_content = post['description']
            userPicturePath = post['userPicturePath']
            picturepath = post['picturePath'] if not None else None
            liked_rows = db.execute("SELECT * FROM liked WHERE postId = ?", post_id)
            likes = len(liked_rows)
            comment_rows = db.execute("SELECT * FROM comment WHERE POSTID = ?", post_id)
            comments = len(comment_rows)
            created_at = post['created_at']
            created_at = time_format(created_at)
            userId = post['userId']
            yeargroup = db.execute("SELECT yearorposition FROM user WHERE id = ?", userId)[0]['yearorposition']
            yeargroup = yeargroup_format(yeargroup)
            major = db.execute("SELECT major FROM user WHERE id = ?", userId)[0]['major']
            major = major_format(major)

            post_details = {'class': yeargroup, 'postContent': post_content, 'username': post_username, 'profilePicturePath': userPicturePath, 'picturePath': picturepath, 'time': created_at, 'likes':likes, 'class': yeargroup, 'post_id': post_id, 'major': major, 'comments': comments}
            posts.append(post_details)
        
        posts.reverse()

        return render_template("index.html", username = username, image = picture_path, posts = posts)
    
@app.route("/login", methods=["GET", "POST"])
def login():

    
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            flash("Empty email")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Empty password")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM user WHERE email = ?", request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Email or password is wrong")
            return redirect("/login")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
    
    else:

        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":
        statuses = ["Student", "Alumni", "Staff"]
        return render_template("register.html", statuses = statuses)
    
    if request.method == "POST":

        name = request.form.get("name")
        username = request.form.get("username")
        email = request.form.get("email")
        status = request.form.get("status")
        
        image_file = request.files.get("image")
        
        location = "profile_pic"
        response = picture_handler(image_file, location)

        if response != False:
            image_id = response
        
        else:
            flash("Image file is not uploaded or is not supported")
            return redirect("/register")


        if not name:
            flash("Provide your name")
            cleanfile(image_id)

            return redirect("/register")
        
        if not username:
            flash("Provide your username")
            cleanfile(image_id)

            return redirect("/register")
        
        if not email:
            flash("Provide your email")
            cleanfile(image_id)

            return redirect("/register")
        
        if not status:
            flash("Select your status")
            cleanfile(image_id)

            return redirect("/register")
        
        if exists_user(username):
            flash("Username already in use")
            cleanfile(image_id)

            return redirect("/register")
        """
        domain = email.split("@")[1]

        if domain != "ashesi.edu.gh":
            flash("Use your Ashesi email")
            cleanfile(image_id)

            return redirect("/register")
        """

        if exists_email(email):
            flash("Email already in use")
            cleanfile(image_id)

            return redirect("/register")

        code = generate_code()

        db.execute("INSERT INTO user (name, username, email, status, regnumber, pictureId, yearorposition, hash) VALUES (?, ?, ?, ?, ?, ?, '','')", name, username, email, status, code, image_id)
        student_id = db.execute("SELECT id FROM user WHERE username = ?", username)[0]["id"]
        session["registration_id"] = student_id
        
        if send_email(email, code) == True:
            flash("Check registration code from your email ----- [Password must at leat have 8 characters, including a digit, lowercase and uppercase letter]")
            if status.lower() == "student" or status.lower() == "alumni":
                return redirect("/year")
            
            elif status.lower() == "staff":
                return redirect("/staff")

@app.route("/year", methods = ["GET", "POST"])
@registration_required
def year():

    if request.method == "GET":

        years = list(range(2002,2028))
        years.reverse()
        majors = ['Computer Science','Computer Engineering','Mechanical Engineering','Electrical and E. Engineering', 'Business Admin', 'Management Infomation Systems', 'Mechatronics']
        return render_template("year.html", id = session["registration_id"], years = years, majors = majors)
    
    if request.method == "POST":

        year = request.form.get("class")
        major = request.form.get("major")
        password = request.form.get("password")
        confirmation = request.form.get("confirm")
        code = request.form.get("code")
        id = request.form.get("id")
        
        
        if not year or int(year) < 2002 or int(year) > 2027:
            flash("Select your graduation year")
            return redirect("/year")
        
        userCode = db.execute("SELECT regnumber FROM user WHERE id = ?", id)
        userCode = userCode[0]["regnumber"]

        #print(f"Code: {code}, User Code: {userCode}")
        if not code or code != userCode:
            flash("Invalid code")
            return redirect("/year")
        
        message = validate_password(password, confirmation)
        

        if message == True:
            session["user_id"] = id
            db.execute("UPDATE user SET yearorposition = ?, major = ?, hash = ? WHERE id = ?", year, major, generate_password_hash(password), id)
            return redirect("/")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/newpost", methods = ["GET", "POST"])
@login_required
def newpost():

    if request.method =="POST":

        postContent = request.form.get("postContent")
        image_file = request.files.get("image")
        location = "post"
        response = picture_handler(image_file, location)

        if response != False:
            image_id = response
        else:
            image_id = None
        
        userId = session["user_id"]
        username, userPicturePath, fullname = user_details()

        if image_id:
            picture_path = db.execute("SELECT imagePath from image where id = ?", image_id)[0]['imagePath']
            db.execute("INSERT INTO post(userId, username, fullname, description, userPicturePath, picturePath) values(?,?,?,?,?,?)", userId, username, fullname, postContent, userPicturePath, picture_path)
            return redirect("/")

        db.execute("INSERT INTO post(userId, username, fullname, description, userPicturePath) values(?,?,?,?,?)", userId, username, fullname, postContent, userPicturePath)
        return redirect("/")


    else:
        username, picture_path, fullname = user_details()
        return render_template("post.html", username = username, image = picture_path, fullname = fullname)

def user_details():

    username = db.execute("SELECT username FROM user WHERE id = ?", session["user_id"])[0]['username']
    fullname = db.execute("SELECT name FROM user WHERE id = ?", session["user_id"])[0]['name']
    image_id = db.execute("SELECT pictureId FROM user WHERE id = ?", session["user_id"])[0]['pictureId']
    picture_path = db.execute("SELECT imagePath FROM image where id = ?", image_id)[0]['imagePath']

    return username, picture_path, fullname

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(email, code):
    sending_email = os.getenv("MAIL_USERNAME")
    msg = Message('Authentication Code', sender = sending_email, recipients=[email])
    msg.body = f"""
    Hi,
    
    Someone tried to sign up for a Community account
    with {email} as their email 
    address. If this was you, enter this confirmation code 
    in the app to complete the process: 
    
    Code: {code}

    From,
    Community
    """

    thread = Thread(target=send_async_email, args=(app, msg))
    thread.start()

    return True

@app.route("/liked/<post_id>", methods=["POST"])
@login_required
def liked(post_id):

    liked = liked_already(session['user_id'], post_id)
    if liked:
        db.execute("DELETE FROM liked WHERE postId = ? and userId = ?", post_id, session['user_id'])
    else:
        db.execute("INSERT INTO liked(postId, userId) values(?,?)", post_id, session["user_id"])
    
    rows = db.execute("SELECT * FROM liked WHERE postId = ?", post_id)
    return jsonify({"likes":len(rows), "liked":liked})

@app.route("/addcomment/", methods = ["POST"])
@login_required
def comment():

    try:
        comment_data = request.get_json()
        post_id = comment_data['post_id']
        user_id = comment_data['user_id']
        text = comment_data['text']
        db.execute("INSERT INTO COMMENT(COMMENT_TEXT, POSTID, userId) VALUES(?,?,?)", text, post_id, user_id)
        comments_count = db.execute("SELECT * FROM COMMENT WHERE POSTID = ?", post_id)
        comments_count = len(comments_count)
        username , _ , _ = user_details()

        return jsonify({"success":True, "count": comments_count, "text" : text, "username" : username})
    
    except Exception as e:

        return jsonify({"success":False, "error" : e})

@app.route('/comments', methods=['POST'])
@login_required
def comments():

    data = request.get_json()
    post_id = data['post_id']
    most_recent = db.execute("SELECT userId, comment_text FROM COMMENT WHERE POSTID = ? ORDER BY id DESC LIMIT 1", post_id)
        
    try:
        most_recent = most_recent[0]
        userId = most_recent['userId']
        username = db.execute("SELECT username FROM user WHERE id = ?", userId)[0]['username']
        text = most_recent['COMMENT_TEXT']

        return jsonify({"success": True, "text":text, "username":username})
    
    except IndexError as e:

        return jsonify({"success": False, "text": str(e)})
    
@app.route("/loadcomments", methods=["POST"])
def loadcomments():

    post_id = request.get_json()['post_id']
    comments = getallcomments(post_id)
    if len(comments) > 0:
        return jsonify({"success": True, "comments": comments})
    else:
        return jsonify({"success":False})

def getallcomments(post_id):

    comments = db.execute("SELECT comment_text, created_at, userId FROM comment WHERE postid = ? order by created_at desc", post_id)
    comments_list = []
    for comment in comments:
        text = comment['COMMENT_TEXT']
        time = comment['CREATED_AT']
        time = time_format(time)
        userId = comment['userId']
        pic_id = db.execute("SELECT pictureId FROM user WHERE id = ?", userId)
        pic_id = pic_id[0]['pictureId']
        userPicture = id_path(pic_id)
        userName = db.execute("SELECT username FROM user WHERE id = ?", userId)[0]['username']
        classgroup = db.execute("SELECT yearorposition FROM user WHERE id = ?", userId)[0]['yearorposition']
        classgroup = f"C'{classgroup[2:]}"
        major = db.execute("SELECT major FROM user WHERE id = ?", userId)[0]['major']
        major = major_format(major)
        major = f"{major} |"
        comment_dic = {"text":text, "time":time, "picture":userPicture, "username": userName, "class": classgroup, "major":major}
        comments_list.append(comment_dic)
    
    return comments_list

def id_path(picId):

    path = db.execute("SELECT imagePath from image where id = ?", picId)[0]['imagePath']
    
    return path

@app.route("/search", methods=["POST"])
def search():

    query = request.get_json()['query']
    query = query.lower()
    username_list = []

    search_username_first = db.execute("SELECT username FROM user WHERE LOWER(username) LIKE ? || '%' LIMIT 5", ('%' + query.lower(),))

    search_username_middle = db.execute("SELECT username FROM user WHERE LOWER(username) LIKE '%' || ? || '%' LIMIT 5", (query.lower(),))

    search_fullname_first = db.execute("SELECT username FROM user WHERE LOWER(name) LIKE ? || '%' LIMIT 5", ('%' + query.lower(),))

    search_fullname_middle = db.execute("SELECT username FROM user WHERE LOWER(name) LIKE '%' || ? || '%' LIMIT 5", (query.lower(),))

    for user in search_username_first:
        username_list.append(user['username'])

    for user in search_username_middle:
        username_list.append(user['username'])
    
    for user in search_fullname_first:
        username_list.append(user['username'])

    for user in search_fullname_middle:
        username_list.append(user['username'])

    username_set = set(username_list)
    username_list = list(username_set)
    print(username_list)
    if len(username_list) > 0:
        return jsonify({"success": True, "results":username_list})
    else:
        return jsonify({"success": False, "message":"User not found"})



