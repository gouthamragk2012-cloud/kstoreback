from flask_mail import Mail, Message
from flask import current_app
import random
import string

mail = Mail()

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, first_name, verification_code):
    """Send verification code email to user"""
    try:
        msg = Message(
            subject='Verify Your KStore Account',
            recipients=[email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # HTML email body
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
                .code-box {{
                    background: white;
                    border: 2px dashed #667eea;
                    padding: 20px;
                    text-align: center;
                    margin: 20px 0;
                    border-radius: 8px;
                }}
                .code {{
                    font-size: 32px;
                    font-weight: bold;
                    color: #667eea;
                    letter-spacing: 8px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 20px;
                    color: #666;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to KStore!</h1>
                </div>
                <div class="content">
                    <h2>Hi {first_name},</h2>
                    <p>Thank you for registering with KStore. To complete your registration, please verify your email address using the code below:</p>
                    
                    <div class="code-box">
                        <p style="margin: 0; color: #666;">Your Verification Code</p>
                        <div class="code">{verification_code}</div>
                    </div>
                    
                    <p>This code will expire in <strong>15 minutes</strong>.</p>
                    <p>If you didn't create an account with KStore, please ignore this email.</p>
                    
                    <div class="footer">
                        <p>© 2025 KStore. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text fallback
        msg.body = f"""
        Hi {first_name},
        
        Thank you for registering with KStore!
        
        Your verification code is: {verification_code}
        
        This code will expire in 15 minutes.
        
        If you didn't create an account with KStore, please ignore this email.
        
        © 2025 KStore. All rights reserved.
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_welcome_email(email, first_name):
    """Send welcome email after successful verification"""
    try:
        msg = Message(
            subject='Welcome to KStore!',
            recipients=[email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 10px 10px 0 0;
                }}
                .content {{
                    background: #f9f9f9;
                    padding: 30px;
                    border-radius: 0 0 10px 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Account Verified!</h1>
                </div>
                <div class="content">
                    <h2>Hi {first_name},</h2>
                    <p>Your email has been successfully verified! You can now enjoy all the features of KStore.</p>
                    <p>Start shopping and discover amazing products!</p>
                    <p>Happy Shopping! 🛍️</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.body = f"""
        Hi {first_name},
        
        Your email has been successfully verified!
        
        You can now enjoy all the features of KStore.
        
        Happy Shopping!
        """
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False
