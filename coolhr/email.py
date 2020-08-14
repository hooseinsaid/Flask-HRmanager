<<<<<<< HEAD
from flask import render_template
from flask_mail import Message
from coolhr import app, mail


def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    if hasattr(user, 'company_name'):
        email = user.company_email
    elif hasattr(user, 'employee_name'):
        email = user.employee_email
    send_email('Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def send_company_welcome_email(user):
    email = user.company_email
    send_email('Welcome to CoolHR', sender=app.config['ADMINS'][0], recipients=[email],
                text_body=render_template('email/welcome.txt', user=user),
                html_body=render_template('email/welcome.html', user=user))
=======
from flask import render_template
from flask_mail import Message
from coolhr import app, mail

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token()
    if hasattr(user, 'company_name'):
        email = user.company_email
    elif hasattr(user, 'employee_name'):
        email = user.employee_email
    send_email('Reset Your Password',
               sender=app.config['ADMINS'][0], recipients=[email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))


def send_welcome_email(user, username):
    if hasattr(user, 'company_name'):
        email = user.company_email
    elif hasattr(user, 'employee_name'):
        email = user.employee_email
    send_email('Welcome to CoolHR', sender=app.config['ADMINS'][0], recipients=[email],
                text_body=render_template('email/welcome.txt', user=user, username=username),
                html_body=render_template('email/welcome.html', user=user, username=username))

def send_company_username_email(user, username):
    if hasattr(user, 'company_name'):
        email = user.company_email
    elif hasattr(user, 'employee_name'):
        email = user.employee_email
    send_email("Your Company's username", sender=app.config['ADMINS'][0], recipients=[email],
               text_body=render_template('email/send_company_username.txt', user=user, username=username),
               html_body=render_template('email/send_company_username.html', user=user, username=username))
>>>>>>> 0bbe1e5d49a9ce97c9b9f0bf747ea067addf507b
