import random
from django.core.mail import send_mail

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_via_email(email, otp):
    subject = "Your OTP Verification Code"
    message = f"Your One Time Password is {otp}. It will expire in 5 minutes."
    send_mail(subject, message, "dezacodex@gmail.com", [email])
