from threading import Thread
from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, send_from_directory, jsonify
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

        rows = db.execute("SELECT * FROM post ORDER BY created_at DESC")
        posts = []

        for post in rows:

            post_id = post['id']
            post_content = post['description']
            picturepath = post['picturePath'] if not None else None
            liked_rows = db.execute("SELECT * FROM liked WHERE postId = ?", post_id)
            likes = len(liked_rows)
            comment_rows = db.execute("SELECT * FROM comment WHERE POSTID = ?", post_id)
            comments = len(comment_rows)
            created_at = post['created_at']
            created_at = time_format(created_at)
            userId = post['userId']
            userPicturePath = db.execute("SELECT pictureId FROM user WHERE id = ?", userId)[0]['pictureId']
            userPicturePath = id_path(userPicturePath)
            post_username = db.execute("SELECT username FROM user WHERE id = ?", userId)[0]['username']
            yeargroup = db.execute("SELECT yearorposition FROM user WHERE id = ?", userId)[0]['yearorposition']
            yeargroup = yeargroup_format(yeargroup)
            major = db.execute("SELECT major FROM user WHERE id = ?", userId)[0]['major']
            major = major_format(major)

            post_details = {'class': yeargroup, 'postContent': post_content, 'username': post_username, 'profilePicturePath': userPicturePath, 'picturePath': picturepath, 'time': created_at, 'likes':likes, 'class': yeargroup, 'post_id': post_id, 'major': major, 'comments': comments}
            posts.append(post_details)
        
        return render_template("index.html", username = username, image = picture_path, posts = posts)


@app.route("/login_username", methods=["POST"])
def login_username():
    username = request.get_json()['username']
    rows = db.execute("SELECT * FROM user WHERE username = ?", username)
    if len(rows) == 0:
        return jsonify({"success": False, "message": "Username not found"})
    else:
        return jsonify({"success": True})

@app.route("/login", methods=["GET", "POST"])
def login():

    session.clear()

    if request.method == "POST":
        
        username = request.get_json()['username']
        password = request.get_json()['password']

        rows = db.execute("SELECT * FROM user WHERE username = ?", username)

        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return jsonify({"success": False, "message": "Username and Password do not match"})

        session["user_id"] = rows[0]["id"]

        return jsonify({"success": True})
    
    else:

        return render_template("login.html")

@app.route("/register", methods=["GET"])
def register():

    if request.method == "GET":
        statuses = ["Student", "Alumni", "Staff"]
        return render_template("register.html", statuses = statuses)
    

@app.route('/registerj', methods = ['POST'])
def registerj():

    username = request.get_json()['username']
    email = request.get_json()['email']
    status = request.get_json()['status']
    
    statuses_lower = ["student", "alumni", "staff"]

    if exists_user(username):
        return jsonify({'success': False, 'message': 'Username already in use'}), 409
    if exists_email(email):
        return jsonify({'success': False, 'message': 'Email already in use'}), 409
    if status.lower() not in statuses_lower:
        return jsonify({'success': False, 'message': 'Invalid status'}), 409
    
    return jsonify({'success': True}), 200

@app.route("/upload", methods=["POST"])
def upload():

    picture = request.files.get("profile_picture")
    location = "profile_pic"
    response = picture_handler(picture, location)

    if response != False:
    
        return jsonify({'success': True, 'image_id': response}), 200
    
    else:

        return jsonify({'success': False, 'message': 'Image file is not uploaded or is not supported'}), 409
    
@app.route("/record", methods=["POST"]) 
def record():

    name = request.get_json()['name']
    username = request.get_json()['username']
    username = username.lower()
    email = request.get_json()['email']
    status = request.get_json()['status']
    profile_picture = request.get_json()['profile_picture']
    code = generate_code()
    db.execute("INSERT INTO user (name, username, email, status, pictureId, yearorposition, hash, regnumber) VALUES (?, ?, ?, ?, ?,'','',?)", name, username, email, status, profile_picture, code)
    user_id = db.execute("SELECT id FROM user WHERE username = ?", username)[0]['id']
    session["registration_id"] = user_id
    return jsonify({'success': True, 'email': email, 'code': code}), 200

@app.route("/send_email", methods = ["POST"])
def send_email():

    email = request.get_json()['email']
    code = request.get_json()['code']
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

    return jsonify({"success": True, "message": "Check the code sent to your mail."}), 200

@app.route("/year", methods = ["GET", "POST"])
@registration_required
def year():

    years = list(range(2002,2028))
    years.reverse()
    majors = ['Computer Science','Computer Engineering','Mechanical Engineering','Electrical and E. Engineering', 'Business Admin', 'Management Infomation Systems', 'Mechatronics']
    return render_template("year.html", id = session["registration_id"], years = years, majors = majors)

@app.route("/yearpost", methods = ["POST"])
def yearpost():
    
    year = request.get_json()['year']
    major = request.get_json()['major']
    id = request.get_json()['id']
    password = request.get_json()['password']
    confirm = request.get_json()['confirm']
    code = request.get_json()['code']
    majors = ['Computer Science','Computer Engineering','Mechanical Engineering','Electrical and E. Engineering', 'Business Admin', 'Management Infomation Systems', 'Mechatronics']
    
    if int(year) < 2002 or int(year) > 2027:
        return jsonify({"success": False, "message": "Invalid Graduation Year"})
    
    if major not in majors:
        return jsonify({"success": False, "message": "Invalid Major"})
    
    userCode = db.execute("SELECT regnumber FROM user WHERE id = ?", id)[0]["regnumber"]

    if code != userCode:
        return jsonify({"success": False, "message": "Invalid code"})
    
    message = validate_password(password, confirm)
    if message == True:

        session["user_id"] = id
        db.execute("UPDATE user SET yearorposition = ?, major = ?, hash = ? WHERE id = ?", year, major, generate_password_hash(password), id)
        return jsonify({"success": True})
    
    else:
        return jsonify({"success": False, "message": message})


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
        username, _ , _ = user_details()

        if image_id:
            picture_path = db.execute("SELECT imagePath from image where id = ?", image_id)[0]['imagePath']
            db.execute("INSERT INTO post(userId, description, picturePath) values(?,?,?)", userId, postContent, picture_path)
            return redirect("/")

        db.execute("INSERT INTO post(userId, description) values(?,?)", userId, postContent)
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

def user_profile(username):

    fullname = db.execute("SELECT name FROM user WHERE username = ?", username)[0]['name']
    userId = db.execute("SELECT id FROM user WHERE username = ?", username)[0]['id']
    image_id = db.execute("SELECT pictureId FROM user WHERE username = ?", username)[0]['pictureId']
    path = id_path(image_id)
    classgroup = db.execute("SELECT yearorposition FROM user WHERE username = ?", username)[0]['yearorposition']
    classgroup = f"C'{classgroup[2:]}"
    major = db.execute("SELECT major FROM user WHERE username = ?", username)[0]['major']
    date = db.execute("SELECT created_at FROM user WHERE username = ?", username)[0]['created_at']
    date = time_format(date)
    date = date.split()
    date = f"{date[1]} {date[2]}"
    perimeter = db.execute("SELECT * FROM circle WHERE user_id = ? or friend_id = ? and status = 'APPROVE'", userId, userId)
    perimeter = len(perimeter)

    return fullname, path, classgroup, major, date, perimeter


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)



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
        userPicture = f"/{userPicture}"
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
@login_required
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
    
    user_list = []

    for user in username_list:
        fullname = db.execute("SELECT name FROM user WHERE username = ?", user)[0]['name']
        user_dict = {"fullname": fullname, "username":user}
        user_list.append(user_dict)

    if len(username_list) > 0:
        return jsonify({"success": True, "results":user_list})
    else:
        return jsonify({"success": False, "message":"User not found"})

@app.route("/users/<username>")
@login_required
def user(username):
    
    userId = db.execute("SELECT id FROM user WHERE username = ?", username)[0]['id']

    bio = db.execute("SELECT bio FROM user WHERE id = ?", userId)[0]['bio'] if not None else ''
    rows = db.execute("SELECT * FROM post WHERE userId = ?", userId)
    length = len(rows)
    print(f"Length is {length}")
    if length > 0:
        divexist = True
    else:
        divexist = False
    
    posts = []
    fullname, path, classgroup, major, date, perimeter = user_profile(username)

    for post in rows:

        post_id = post['id']
        post_content = post['description']
        picturepath = post['picturePath'] if not None else None
        liked_rows = db.execute("SELECT * FROM liked WHERE postId = ?", post_id)
        likes = len(liked_rows)
        comment_rows = db.execute("SELECT * FROM comment WHERE POSTID = ?", post_id)
        comments = len(comment_rows)
        created_at = post['created_at']
        created_at = time_format(created_at)
        p_major = major_format(major)
        post_details = {'postContent': post_content, 'picturePath': picturepath, 'time': created_at, 'likes':likes, 'post_id': post_id, 'comments': comments, 'major':p_major, 'divexist': divexist}
        posts.append(post_details)
        
    posts.reverse()

    if userId == session['user_id']:
        return render_template("profile.html", image = path, username = username, fullname = fullname, classgroup = classgroup, major = major, date = date, perimeter = perimeter, posts = posts, bio = bio)
    else:
        return render_template("otherprofile.html", image = path, username = username, fullname = fullname, classgroup = classgroup, major = major, date = date, perimeter = perimeter, posts = posts, bio = bio)


@app.route("/deletepost/<post_id>", methods=["POST"])
@login_required
def deletepost(post_id):

    try:
        db.execute("DELETE FROM COMMENT WHERE POSTID = ?", post_id)
        db.execute("DELETE FROM LIKED WHERE postId = ?", post_id)
        db.execute("DELETE FROM POST WHERE id = ?", post_id)
        length = len(db.execute("SELECT * FROM POST WHERE userId = ?", session['user_id']))
        return jsonify({"success":True, "length":length})
    except Exception as e:
        return jsonify({"error":str(e)})

@app.route('/explore')
@login_required
def explore():

    circle_requests = get_circle_requests()
    suggestions = get_suggestions()
    username = db.execute("SELECT username FROM user WHERE id = ?", session['user_id'])[0]['username']
    return render_template('explore.html', circle_requests = circle_requests, username = username, suggestions = suggestions)

def get_circle_requests():

    userId = session['user_id']
    user_list = circle_requests(userId)

    if len(user_list) > 0:

        users = []

        for row in user_list:

            userId = row['id']
            fullname = row['name']
            username = row['username']
            picId = row['pictureId']
            path = id_path(picId)
            major = row['major']
            major = major_format(major)
            clas =  row['yearorposition']
            clas = f"C'{clas[2:]}"
            user_dict = {"name": fullname, "path":path, "major":major, "class": clas, "username":username, "id":userId}
            users.append(user_dict)
        
        return users
    
    else:

        return []

def get_suggestions():

    userId = session['user_id']
    rows = db.execute("SELECT id FROM user")
    valid_ids = [str(x['id']) for x in rows if not circle_exists(userId, x['id']) if x['id'] != userId]
    
    if valid_ids:
        string = ",".join(valid_ids)
        query = f"SELECT * FROM user WHERE id IN ({string})"
        user_rows = db.execute(query)
        users = []

        for row in user_rows:

            userId = row['id']
            fullname = row['name']
            username = row['username']
            picId = row['pictureId']
            path = id_path(picId)
            major = row['major']
            major = major_format(major)
            clas =  row['yearorposition']
            clas = f"C'{clas[2:]}"
            user_dict = {"name": fullname, "path":path, "major":major, "class": clas, "username":username, "id":userId}
            users.append(user_dict)
        
        return users
    
    else:
        return []

@app.route('/circle', methods =["POST"])
@login_required
def circle():

    friend_id = request.get_json()['id']
    user_id = session['user_id']

    if not circle_exists(user_id, friend_id):
        db.execute("INSERT INTO circle(user_id, friend_id, status) VALUES(?,?,'PENDING')", user_id, friend_id)
        return jsonify({"success": True})
    else:
        return jsonify({"success": False})

@app.route('/approve', methods =["POST"])
@login_required
def approve():

    friend_id = request.get_json()['id']
    user_id = session['user_id']

    if circle_exists(user_id, friend_id):
        db.execute("UPDATE circle SET status = 'APPROVE' WHERE user_id = ? and friend_id = ?", friend_id, user_id)
        return jsonify({"success": True})
    
    else:

        return jsonify({"success": False})
    
def circle_exists(user_id, friend_id):

    request = db.execute("SELECT * FROM circle WHERE user_id = ? and friend_id = ?", user_id, friend_id)
    receive = db.execute("SELECT * FROM circle WHERE user_id = ? and friend_id = ?", friend_id, user_id)

    return len(request) > 0 or len(receive) > 0

def circle_requests(user_id):

    receive = db.execute("SELECT user_id FROM circle WHERE friend_id = ? and status = 'PENDING'",  user_id)
    id = [str(x['user_id']) for x in receive]
    query_string = ','.join(id)
    query = f"SELECT * FROM user WHERE id in ({query_string})"
    rows = db.execute(query)
    return rows

@app.route('/checkuser', methods = ["POST"])
def checkUsername():

    username = request.get_json()['username']
    username = username.lower()

    if exists_user(username):
        return jsonify({"success": False, "message": f"Username '{username}' already in use"})
    
    else:

        return jsonify({"success": True})

@app.route('/checkemail', methods = ["POST"])
def checkEmail():
    
    email = request.get_json()['email']
    if exists_email(email):

        return jsonify({"success": False, "message": f"Email '{email}' already in use"})
    
    else:

        return jsonify({"success": True})

@app.route('/code_compare', methods = ["POST"])
def code_compare():

    code = request.get_json()['code']
    regId = request.get_json()['regId']

    codeDB = db.execute("SELECT regnumber FROM user WHERE id = ?", regId)[0]['regnumber']
    if code == codeDB:

        return jsonify({"success": True})
    
    else:

        return jsonify({"success": False, "message": "Code does not match with code sent to your email"})
    
@app.route('/users/changebio', methods = ["GET","POST"])
@login_required
def changebio():
    
    if request.method == "POST":

        bio = request.get_json()['bio']
        userId = session['user_id']
        username = db.execute("SELECT username FROM user WHERE id = ?", userId)[0]['username']
        db.execute('UPDATE user SET bio = ? WHERE id = ?', bio, userId)
        return jsonify({"success": True, "username" : username})
    
    else:

        username = db.execute("SELECT username FROM user WHERE id = ?", session['user_id'])[0]['username']
        return render_template("bio.html", username = username)

@app.route('/users/changeusername', methods = ["GET","POST"])
@login_required
def changeusername():
    
    if request.method == "POST":

        username = request.get_json()['username']
        username = username.lower()
        userId = session['user_id']
        db.execute('UPDATE user SET username = ? WHERE id = ?', username, userId)
        return jsonify({"success": True, "username" : username})
    
    else:

        username = db.execute("SELECT username FROM user WHERE id = ?", session['user_id'])[0]['username']
        return render_template("username.html", username = username)

@app.route('/users/changepassword', methods = ["GET","POST"])
@login_required
def changepassword():
    
    if request.method == "POST":

        newpassword = request.get_json()['newpassword']
        userId = session['user_id']
        username = db.execute("SELECT username FROM user WHERE id = ?", userId)[0]['username']
        hash = generate_password_hash(newpassword)
        db.execute('UPDATE user SET hash = ? WHERE id = ?', hash, userId)
        return jsonify({"success": True, "username" : username})
    
    else:

        username = db.execute("SELECT username FROM user WHERE id = ?", session['user_id'])[0]['username']
        return render_template("password.html", username = username)

@app.route('/checkoldpassword', methods = ["POST"])
@login_required
def checkoldpassword():
    
    oldpassword = request.get_json()['oldPassword']
    if existsOldPassword(oldpassword):
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Old password is incorrect"})


def existsOldPassword(password):

    hash = db.execute("SELECT hash FROM user WHERE id = ?", session['user_id'])[0]['hash']
    return check_password_hash(hash, password)

@app.route('/users/changegroup', methods = ["GET","POST"])
@login_required
def changegroup():
    
    if request.method == "POST":

        classg = request.get_json()['classg']
        classg = int(classg)
        years = list(range(2002,2028))
        userId = session['user_id']
        username = db.execute("SELECT username FROM user WHERE id = ?", userId)[0]['username']
        
        if classg in years:
            db.execute('UPDATE user SET yearorposition = ? WHERE id = ?', classg, userId)
            return jsonify({"success": True, "username" : username})
        else:
            return jsonify({"success": False, "message": "Invalid Year Group"})
    
    else:

        years = list(range(2002,2028))
        years.reverse()
        username = db.execute("SELECT username FROM user WHERE id = ?", session['user_id'])[0]['username']
        return render_template("group.html", username = username, years=years)

@app.route('/users/changemajor', methods = ["GET","POST"])
@login_required
def changemajor():
    
    if request.method == "POST":

        major = request.get_json()['major']
        majors = ['Computer Science','Computer Engineering','Mechanical Engineering','Electrical and E. Engineering', 'Business Admin', 'Management Infomation Systems', 'Mechatronics']
        userId = session['user_id']
        username = db.execute("SELECT username FROM user WHERE id = ?", userId)[0]['username']
        
        if major in majors:
            db.execute('UPDATE user SET major = ? WHERE id = ?', major, userId)
            return jsonify({"success": True, "username" : username})
        else:
            return jsonify({"success": False, "message": "Invalid Major"})
    
    else:

        majors = ['Computer Science','Computer Engineering','Mechanical Engineering','Electrical and E. Engineering', 'Business Admin', 'Management Infomation Systems', 'Mechatronics']
        username = db.execute("SELECT username FROM user WHERE id = ?", session['user_id'])[0]['username']
        return render_template("majors.html", username = username, majors = majors)

@app.route('/users/changeprofile', methods = ["GET","POST"])
@login_required
def changeprofile():
    
    if request.method == "POST":

        picture = request.files.get("profile_picture")
        location = "profile_pic"
        response = picture_handler(picture, location)
        username = db.execute("SELECT username FROM user WHERE id = ?", session['user_id'])[0]['username']

        if response != False:
            image_id = response
            db.execute("UPDATE user SET pictureId = ? WHERE id = ?", image_id, session['user_id'])
            return jsonify({'success': True, 'message': "Profile picture changed successfully", "username" : username})
        
        else:

            return jsonify({'success': False, 'message': 'Image file is not uploaded or is not supported'})
    
    else:

        username = db.execute("SELECT username FROM user WHERE id = ?", session['user_id'])[0]['username']
        return render_template("changeprofile.html", username = username)

    
    


