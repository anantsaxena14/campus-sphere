from flask_mail import Message
from flask import url_for

def send_verification_email(mail, user_email, verification_token, user_name):
    verification_url = url_for('verify_email', token=verification_token, _external=True)
    
    msg = Message(
        subject='Campus Sphere - Verify Your Email',
        recipients=[user_email]
    )
    
    msg.html = f'''
    <html>
        <body style="font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px;">
                <h2 style="color: #667eea;">Welcome to Campus Sphere!</h2>
                <p>Hi {user_name},</p>
                <p>Thank you for registering. Please verify your email address by clicking the button below:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Verify Email
                    </a>
                </div>
                <p>This link will expire in 15 minutes.</p>
                <p>If you didn't create an account, please ignore this email.</p>
                <p>Best regards,<br>Campus Sphere Team</p>
            </div>
        </body>
    </html>
    '''
    
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
