from flask import Flask, render_template, request, redirect, url_for, flash, make_response, jsonify, send_from_directory
from flask_mail import Mail
from models import db, User, TempUser, Bus, BusStop, Driver, AcademicResource, Event, Alumni, Faculty, Club, ClubMembership, CommunityPost, Admin
from config import Config
from utils.auth import generate_token, generate_session_token, get_expiry_time, is_token_expired
from utils.email_utils import send_verification_email
from utils.decorators import login_required, admin_required, driver_required
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
mail = Mail(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    user_id = request.cookies.get('user_id')
    if user_id:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first() or TempUser.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('signup'))
        
        verification_token = generate_token()
        temp_user = TempUser(
            name=name,
            email=email,
            verification_token=verification_token,
            expires_at=get_expiry_time(15)
        )
        temp_user.set_password(password)
        
        db.session.add(temp_user)
        db.session.commit()
        
        send_verification_email(mail, email, verification_token, name)
        
        flash('Verification email sent! Please check your inbox.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')

@app.route('/verify/<token>')
def verify_email(token):
    temp_user = TempUser.query.filter_by(verification_token=token).first()
    
    if not temp_user:
        flash('Invalid verification link', 'error')
        return redirect(url_for('login'))
    
    if is_token_expired(temp_user.expires_at):
        db.session.delete(temp_user)
        db.session.commit()
        flash('Verification link expired. Please register again.', 'error')
        return redirect(url_for('signup'))
    
    user = User(
        name=temp_user.name,
        email=temp_user.email,
        password_hash=temp_user.password_hash
    )
    
    db.session.add(user)
    db.session.delete(temp_user)
    db.session.commit()
    
    flash('Email verified successfully! Please login.', 'success')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        force_logout = request.form.get('force_logout')
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password', 'error')
            return redirect(url_for('login'))
        
        if user.login_status and not force_logout:
            flash('Account is active on another device', 'warning')
            return render_template('login.html')
        
        session_token = generate_session_token()
        user.session_token = session_token
        user.login_status = True
        user.last_login_device = request.headers.get('User-Agent', 'Unknown')
        db.session.commit()
        
        response = make_response(redirect(url_for('dashboard')))
        response.set_cookie('user_id', str(user.id), max_age=30*24*60*60)
        response.set_cookie('session_token', session_token, max_age=30*24*60*60)
        
        flash('Login successful!', 'success')
        return response
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id)
    
    if user:
        user.login_status = False
        user.session_token = None
        db.session.commit()
    
    response = make_response(redirect(url_for('login')))
    response.delete_cookie('user_id')
    response.delete_cookie('session_token')
    
    flash('Logged out successfully', 'success')
    return response

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id)
    upcoming_events_count = Event.query.filter_by(is_upcoming=True).count()
    
    return render_template('dashboard.html', user=user, upcoming_events_count=upcoming_events_count)

@app.route('/profile')
@login_required
def profile():
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)

@app.route('/update-profile', methods=['POST'])
@login_required
def update_profile():
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id)
    
    user.course = request.form.get('course')
    user.branch = request.form.get('branch')
    user.batch = request.form.get('batch')
    user.year = request.form.get('year')
    
    db.session.commit()
    flash('Profile updated successfully', 'success')
    return redirect(url_for('profile'))

@app.route('/bus-tracking')
@login_required
def bus_tracking():
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id)
    buses = Bus.query.filter_by(is_active=True).all()
    return render_template('bus-tracking.html', user=user, buses=buses)

@app.route('/select-bus', methods=['POST'])
@login_required
def select_bus():
    user_id = request.cookies.get('user_id')
    user = User.query.get(user_id)
    data = request.get_json()
    
    user.selected_bus_id = data.get('bus_id')
    db.session.commit()
    
    return jsonify({'message': 'Bus selected successfully'})

@app.route('/bus/<int:bus_id>/data')
@login_required
def bus_data(bus_id):
    bus = Bus.query.get_or_404(bus_id)
    stops = BusStop.query.filter_by(bus_id=bus_id).order_by(BusStop.stop_order).all()
    
    return jsonify({
        'bus_number': bus.bus_number,
        'current_lat': bus.current_lat,
        'current_lng': bus.current_lng,
        'stops': [{
            'stop_name': stop.stop_name,
            'lat': stop.lat,
            'lng': stop.lng,
            'is_crossed': stop.is_crossed
        } for stop in stops]
    })

@app.route('/bus/<int:bus_id>/location')
@login_required
def bus_location(bus_id):
    bus = Bus.query.get_or_404(bus_id)
    return jsonify({
        'lat': bus.current_lat,
        'lng': bus.current_lng,
        'last_updated': bus.last_updated.isoformat() if bus.last_updated else None
    })

@app.route('/driver/login', methods=['GET', 'POST'])
def driver_login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        
        driver = Driver.query.filter_by(name=name).first()
        
        if not driver or not driver.check_password(password):
            flash('Invalid credentials', 'error')
            return redirect(url_for('driver_login'))
        
        response = make_response(redirect(url_for('driver_panel')))
        response.set_cookie('driver_id', str(driver.id), max_age=24*60*60)
        response.set_cookie('driver_token', generate_session_token(), max_age=24*60*60)
        
        return response
    
    return render_template('driver.html')

@app.route('/driver/panel')
@driver_required
def driver_panel():
    driver_id = request.cookies.get('driver_id')
    driver = Driver.query.get(driver_id)
    return render_template('driver.html', driver=driver)

@app.route('/driver/toggle-location', methods=['POST'])
@driver_required
def toggle_location():
    driver_id = request.cookies.get('driver_id')
    driver = Driver.query.get(driver_id)
    driver.is_sharing_location = not driver.is_sharing_location
    db.session.commit()
    return jsonify({'status': driver.is_sharing_location})

@app.route('/driver/update-location', methods=['POST'])
@driver_required
def update_location():
    driver_id = request.cookies.get('driver_id')
    driver = Driver.query.get(driver_id)
    data = request.get_json()
    
    if driver.bus:
        driver.bus.current_lat = data.get('lat')
        driver.bus.current_lng = data.get('lng')
        driver.bus.last_updated = datetime.utcnow()
        db.session.commit()
    
    return jsonify({'success': True})

@app.route('/driver/logout')
def driver_logout():
    response = make_response(redirect(url_for('driver_login')))
    response.delete_cookie('driver_id')
    response.delete_cookie('driver_token')
    return response

@app.route('/academic-resources')
@login_required
def academic_resources():
    resources = AcademicResource.query.all()
    return render_template('academic-resources.html', resources=resources)

@app.route('/download-resource/<int:resource_id>')
@login_required
def download_resource(resource_id):
    resource = AcademicResource.query.get_or_404(resource_id)
    resource.views += 1
    db.session.commit()
    
    try:
        directory = os.path.dirname(resource.file_path)
        filename = os.path.basename(resource.file_path)
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        flash(f'Error downloading resource: {str(e)}', 'error')
        return redirect(url_for('academic_resources'))

@app.route('/events')
@login_required
def events():
    now = datetime.utcnow()
    upcoming_events = Event.query.filter(Event.event_date >= now).order_by(Event.event_date).all()
    past_events = Event.query.filter(Event.event_date < now).order_by(Event.event_date.desc()).all()
    return render_template('events.html', upcoming_events=upcoming_events, past_events=past_events)

@app.route('/alumni')
@login_required
def alumni():
    alumni_list = Alumni.query.all()
    return render_template('alumni.html', alumni=alumni_list)

@app.route('/faculty')
@login_required
def faculty():
    faculty_list = Faculty.query.all()
    return render_template('faculty.html', faculty=faculty_list)

@app.route('/community')
@login_required
def community():
    posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).all()
    return render_template('community.html', posts=posts)

@app.route('/create-post', methods=['POST'])
@login_required
def create_post():
    user_id = request.cookies.get('user_id')
    content = request.form.get('content')
    post_type = request.form.get('post_type')
    
    banned_words = ['spam', 'abuse', 'offensive']
    for word in banned_words:
        if word.lower() in content.lower():
            flash('Your post contains inappropriate content', 'error')
            return redirect(url_for('community'))
    
    post = CommunityPost(
        user_id=user_id,
        content=content,
        post_type=post_type
    )
    
    db.session.add(post)
    db.session.commit()
    
    flash('Post created successfully', 'success')
    return redirect(url_for('community'))

@app.route('/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = CommunityPost.query.get_or_404(post_id)
    post.likes += 1
    db.session.commit()
    return jsonify({'likes': post.likes})

@app.route('/clubs')
@login_required
def clubs():
    clubs_list = Club.query.all()
    return render_template('clubs.html', clubs=clubs_list)

@app.route('/club/<int:club_id>/join', methods=['POST'])
@login_required
def join_club(club_id):
    user_id = request.cookies.get('user_id')
    
    existing = ClubMembership.query.filter_by(user_id=user_id, club_id=club_id).first()
    if existing:
        return jsonify({'message': 'Already a member'})
    
    membership = ClubMembership(user_id=user_id, club_id=club_id)
    db.session.add(membership)
    db.session.commit()
    
    return jsonify({'message': 'Membership request sent'})

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        admin = Admin.query.filter_by(username=username).first()
        
        if not admin or not admin.check_password(password):
            flash('Invalid credentials', 'error')
            return redirect(url_for('admin_login'))
        
        response = make_response(redirect(url_for('admin_dashboard')))
        response.set_cookie('admin_id', str(admin.id), max_age=24*60*60)
        response.set_cookie('admin_token', generate_session_token(), max_age=24*60*60)
        
        return response
    
    return render_template('admin/admin-login.html')

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_buses': Bus.query.count(),
        'total_events': Event.query.count(),
        'total_clubs': Club.query.count()
    }
    return render_template('admin/admin-dashboard.html', stats=stats)

@app.route('/admin/logout')
def admin_logout():
    response = make_response(redirect(url_for('admin_login')))
    response.delete_cookie('admin_id')
    response.delete_cookie('admin_token')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
