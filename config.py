import os


class Config:
    SECRET_KEY = os.environ.get(
        'SESSION_SECRET') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'srms.inventory@gmail.com'
    MAIL_PASSWORD = 'ilslkasxuyqcqnke'  # ⚠ App Password only, never real Gmail password
    MAIL_DEFAULT_SENDER = 'srms.inventory@gmail.com'

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'ppt', 'pptx', 'jpg', 'jpeg', 'png'
    }
