from flask import redirect, session, flash
from functools import wraps
from cs50 import SQL
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename

import random
import uuid
import os
import string

db = SQL("sqlite:///community.db")

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def registration_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("registration_id") is None:
            return redirect("/register")
        return f(*args, **kwargs)
    return decorated_function

def time_format(created_at):

    months = ["Jan", "Feb", "Mar", "Apr", "May", "June", "July", "Aug", "Sep", "Oct", "Nov", "Dec"]
    day, time = created_at.split()
    hours, minutes, _ = time.split(':')
    time = f"{hours}:{minutes}"
    year, month, day = day.split('-')
    month = months[int(month)-1]
    day = int(day)
    date_format = f"{time} {day} {month}"
    return date_format

def exists_user(username):

    rows = db.execute("SELECT * FROM user WHERE username = ?", username)
    
    return len(rows) != 0

def exists_email(email):

    rows = db.execute("SELECT * FROM user WHERE email = ?", email)

    return len(rows) != 0

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

def liked_already(userId,postId):
    rows = db.execute("SELECT * FROM liked WHERE postId = ? and userId = ?", postId, userId)
    return len(rows) != 0