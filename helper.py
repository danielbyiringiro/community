from flask import redirect, session
from functools import wraps

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
