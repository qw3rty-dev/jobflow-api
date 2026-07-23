import os
from dotenv import load_dotenv

import resend

load_dotenv()
FROM_EMAIL = os.getenv("FROM_EMAIL")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend.api_key = RESEND_API_KEY


def send_email(to,subject,html):
    email = resend.Emails.send({
    "from": FROM_EMAIL,
    "to": to,
    "subject": subject,
    "html": html
    })


def send_verification_mail(user):
    
    to = user.email
    subject = "Verify your Jobflow account"
    
    html = f"""
    <h2>Verify your JobFlow Account</h2>
    <p>Hello {user.username},</p>
    <p>Your verification code is :</p>
    <h1>{user.verification_code}</h1>
    <p>This code expires in 10 minutes.</p>
    <p>If you didn't request this,ignore this email</p>

    """
    send_email(to,subject,html)


def send_welcome_mail(user):
    
    to = user.email
    subject = "Welcome to JobFlow."
    
    html = f"""
    <h2>Welcome to <strong>JobFlow</strong>!</h2>
    <p>Hello {user.username},</p>
    <p>Your JobFlow account is now verified and ready to use.</p>
    <p>Here's what you can do next:</p>
    <ul>
        <li> Save jobs </li>
        <li> Track your application status </li>
        <li> Add keywords and receive job notifications </li>
        <li> Organise your job search in one place </li>
    </ul>

    <p>We built JobFlow to help you stay organised throughout your job search.We hope JobFlow helps you discover your next opportunity.</p>
    
    <p>Happy job hunting!</p>
    
    <p><b>- qw3rty-dev </b><br>
    Creator of JobFlow</p>
    """
    send_email(to,subject,html)


def send_password_reset_otp(user):
    
    to = user.email
    subject = "Password reset OTP"
    
    html = f"""
    <h2>Password reset OTP</h2>
    <p>Hello {user.username},</p>
    <p>Use this OTP to reset your password :</p>
    <h1>{user.verification_code}</h1>
    <p>This code expires in 10 minutes.</p>
    <p>If you didn't request this,ignore this email</p>

    """
    send_email(to,subject,html)


def send_notification_email(user,jobs):

    job_cards = ""

    for job in jobs:
        job_cards += f"""
        <h3>{job.title}</h3>

        <p>
            <b>Company:</b> {job.company}<br>
            <b>Location:</b> {job.location}<br>
            <b>Source:</b> {job.source}<br>
        </p>

        <p>
            <a href="{job.link}">
                View Job
            </a>
        </p>

        <hr>
        """

    to = user.email
    subject = f"{len(jobs)} New {'Jobs' if len(jobs) > 1 else 'Job'} Matching Your Keywords"
    
    html = f"""
<!DOCTYPE html>
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">

    <h2>🎯 New Jobs Matching Your Keywords</h2>

    <p>Hi {user.username},</p>

    <p>
        We found <strong>{len(jobs)}</strong> new {'jobs' if len(jobs) > 1 else 'job'}
        matching your keywords on JobFlow.
    </p>

    {job_cards}

    <p>
        You're receiving this email because job notifications are enabled
        in your JobFlow account.
    </p>

    <p>
        Happy job hunting! 🚀
    </p>

    <p>
        <strong>— qw3rty-dev</strong><br>
        Creator of JobFlow
    </p>

</body>
</html>"""
    
    send_email(to,subject,html)
    print("email_sent")