from threading import Thread
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, send_from_directory
from flask_session import Session
from flask_mail import Mail, Message
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helper import *
from dotenv import load_dotenv


import random
import string
import os
import uuid

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

            fullname = post['fullname']
            post_username = post['username']
            post_content = post['description']
            userPicturePath = post['userPicturePath']
            picturepath = post['picturePath'] if not None else None
            likes = post['likes']
            created_at = post['created_at']
            created_at = time_format(created_at)
            userId = post['userId']
            yeargroup = db.execute("SELECT yearorposition FROM user WHERE id = ? ", userId)[0]['yearorposition']
            yeargroup = str(yeargroup)[2:]
            yeargroup = f"C'{yeargroup}"

            post_details = {'class': yeargroup, 'fullname' : fullname, 'postContent': post_content, 'username': post_username, 'profilePicturePath': userPicturePath, 'picturePath': picturepath, 'time': created_at, 'likes':likes, 'class': yeargroup}
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
        years = list(range(2002,2028))
        majors = ['Computer Science','Computer Engineering','Mechanical Engineering','Electrical and E. Engineering', 'Business Admin', 'Management Infomation Systems', 'Mechatronics']
        return render_template("year.html", years=years, majors=majors)

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

        

def exists_user(username):

    rows = db.execute("SELECT * FROM user WHERE username = ?", username)
    
    return len(rows) != 0

def exists_email(email):

    rows = db.execute("SELECT * FROM user WHERE email = ?", email)

    return len(rows) != 0


@app.route("/year", methods = ["GET", "POST"])
@registration_required
def year():

    if request.method == "GET":

        years = list(range(2002,2028))
        majors = ['Computer Science','Computer Engineering','Mechanical Engineering','Electrical and E. Engineering', 'Business Admin', 'Management Infomation Systems', 'Mechatronics']
        return render_template("year.html", id = session["registration_id"], years = years, majors = majors)
    
    if request.method == "POST":

        year = request.form.get("class")
        password = request.form.get("password")
        confirmation = request.form.get("confirm")
        code = request.form.get("code")
        id = request.form.get("id")
        
        
        if not year or int(year) < 2002 or int(year) > 2027:
            flash("Select your graduation year")
            return redirect("/year")
        
        userCode = db.execute("SELECT regnumber FROM user WHERE id = ?", id)
        userCode = userCode[0]["regnumber"]

        print(f"Code: {code}, User Code: {userCode}")
        if not code or code != userCode:
            flash("Invalid code")
            return redirect("/year")
        
        message = validate_password(password, confirmation)
        

        if message == True:
            session["user_id"] = id
            db.execute("UPDATE user SET yearorposition = ?, hash = ? WHERE id = ?", year, generate_password_hash(password), id)
            return redirect("/")


def validate_password(password, confirmation):

    if not password:
        flash("Provide a password")
        return redirect("/year")
    
    if not confirmation:
        flash("Confirm your password")
        return redirect("/year")
    
    if password != confirmation:
        flash("Passwords do not match")
        return redirect("/year")
    
    if len(password) < 8:
        flash("Password must be at least 8 characters")
        return redirect("/year")
    
    if not any(char.isdigit() for char in password):
        flash("Password must contain at least one number")
        return redirect("/year")
    
    if not any(char.isupper() for char in password):
        flash("Password must contain at least one uppercase letter")
        return redirect("/year")
    
    if not any(char.islower() for char in password):
        flash("Password must contain at least one lowercase letter")
        return redirect("/year")
    
    return True

def generate_code():
    characters = string.ascii_letters + string.digits + string.punctuation
    code = ''.join(random.choice(characters) for _ in range(6))
    return code

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

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

def picture_handler(image_file, location): 

    filename = image_file.filename
    if image_file and allowed_file(filename):
        savedir = f"assets/{location}/" 
        os.makedirs(savedir, exist_ok=True)
        unique_filename = generate_unique_filename(filename)
        image_path = os.path.join(savedir, unique_filename)
        image_file.save(image_path) 
        db.execute("INSERT INTO image (imagePath) VALUES(?)", image_path)
        
        image_id = db.execute("SELECT id FROM image where imagePath = ?", image_path)[0]['id']
        return image_id

    else:

        return False

def deletePicture(id):

    imagePath = db.execute("SELECT imagePath FROM image where id = ?", id)[0]['imagePath']
    db.execute("DELETE FROM image WHERE id = ?", id)
    
    try:
        os.remove(imagePath)
        return True
    except FileNotFoundError:
        return False
    except OSError as e:
        return e

def cleanfile(id):
    response = deletePicture(id)
    if response != True:
        print(response)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}  # Add any other allowed extensions
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    unique_filename = str(uuid.uuid4()) + '_' + secure_filename(filename)
    return unique_filename

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
            db.execute("INSERT INTO post(userId, username, fullname, description, userPicturePath, picturePath, likes) values(?,?,?,?,?,?,?)", userId, username, fullname, postContent, userPicturePath, picture_path, 0)
            return redirect("/")

        db.execute("INSERT INTO post(userId, username, fullname, description, userPicturePath, likes) values(?,?,?,?,?,?)", userId, username, fullname, postContent, userPicturePath, 0)
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