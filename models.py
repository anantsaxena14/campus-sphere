from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class TempUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    verification_token = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255))
    course = db.Column(db.String(50))
    branch = db.Column(db.String(50))
    batch = db.Column(db.String(20))
    year = db.Column(db.Integer)
    selected_bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'))
    selected_stop = db.Column(db.String(100))
    login_status = db.Column(db.Boolean, default=False)
    session_token = db.Column(db.String(100))
    last_login_device = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Bus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bus_number = db.Column(db.String(20), unique=True, nullable=False)
    route_description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    current_lat = db.Column(db.Float)
    current_lng = db.Column(db.Float)
    last_updated = db.Column(db.DateTime)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    
    stops = db.relationship('BusStop', backref='bus', lazy=True, cascade='all, delete-orphan')
    users = db.relationship('User', backref='selected_bus', lazy=True, foreign_keys=[User.selected_bus_id])

class BusStop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('bus.id'), nullable=False)
    stop_name = db.Column(db.String(100), nullable=False)
    stop_order = db.Column(db.Integer, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    is_crossed = db.Column(db.Boolean, default=False)

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    assigned_bus = db.Column(db.Integer, db.ForeignKey('bus.id'))
    is_sharing_location = db.Column(db.Boolean, default=False)
    
    bus = db.relationship('Bus', backref='driver', foreign_keys=[Bus.driver_id], uselist=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class AcademicResource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(50), nullable=False)
    branch = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    views = db.Column(db.Integer, default=0)
    
    uploader = db.relationship('User', backref='resources', foreign_keys=[uploaded_by])

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(100))
    registration_link = db.Column(db.String(255))
    is_upcoming = db.Column(db.Boolean, default=True)
    highlight_images = db.Column(db.Text)

class Alumni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    batch = db.Column(db.String(20))
    current_designation = db.Column(db.String(100))
    company = db.Column(db.String(100))
    linkedin_profile = db.Column(db.String(255))
    email = db.Column(db.String(100))

class Faculty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    subjects = db.Column(db.Text)
    mobile = db.Column(db.String(15))
    email = db.Column(db.String(100))
    linkedin = db.Column(db.String(255))

class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    club_type = db.Column(db.String(50))
    secretary_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    secretary = db.relationship('User', backref='led_clubs', foreign_keys=[secretary_id])
    memberships = db.relationship('ClubMembership', backref='club', lazy=True, cascade='all, delete-orphan')

class ClubMembership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    verified_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    user = db.relationship('User', backref='club_memberships', foreign_keys=[user_id])
    verifier = db.relationship('User', foreign_keys=[verified_by])

class CommunityPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)
    
    author = db.relationship('User', backref='posts', foreign_keys=[user_id])

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    permissions = db.Column(db.Text)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
