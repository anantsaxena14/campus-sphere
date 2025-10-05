from functools import wraps
from flask import request, redirect, url_for, flash
from models import User, Admin

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.cookies.get('user_id')
        session_token = request.cookies.get('session_token')
        
        if not user_id or not session_token:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('login'))
        
        user = User.query.get(user_id)
        if not user or user.session_token != session_token:
            flash('Invalid session. Please login again', 'warning')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_id = request.cookies.get('admin_id')
        admin_token = request.cookies.get('admin_token')
        
        if not admin_id or not admin_token:
            flash('Please login as admin', 'warning')
            return redirect(url_for('admin_login'))
        
        admin = Admin.query.get(admin_id)
        if not admin:
            flash('Invalid admin session', 'warning')
            return redirect(url_for('admin_login'))
        
        return f(*args, **kwargs)
    return decorated_function

def driver_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        driver_id = request.cookies.get('driver_id')
        driver_token = request.cookies.get('driver_token')
        
        if not driver_id or not driver_token:
            flash('Please login as driver', 'warning')
            return redirect(url_for('driver_login'))
        
        return f(*args, **kwargs)
    return decorated_function
