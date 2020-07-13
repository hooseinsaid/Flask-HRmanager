import os
import secrets
from PIL import Image
from datetime import datetime
from flask import render_template, redirect, url_for, request, flash, session
from coolhr import app, db, mail
from coolhr.forms import *
from coolhr.email import send_password_reset_email, send_company_welcome_email
from coolhr.models import *
from functools import wraps


#add a functionality that takes them to the page they initially tried to visit if they are logged in correctly
def access_company(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not (session.get('company_email') or session.get('employee_email')):
            return redirect(url_for('company_username'))
        company = Companies.query.filter_by(company_email=session.get('company_email'),
                                            company_username=kwargs['company_username']).first()
        if company is None:
            return ('Access denied')
        return function(*args, **kwargs)
    return wrapper


def access_employee(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not (session.get('company_email') or session.get('employee_email')):
            return redirect(url_for('company_username'))
        employee = Employees.query.filter_by(employee_email=session.get('employee_email')).first()
        if employee is None:
            return ('Access denied')
        e_company = Companies.query.filter_by(company_id=employee.company_id).first()
        if e_company.company_username != kwargs['company_username']:
            return ('Access denied')
        return function(*args, **kwargs)
    return wrapper


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.route('/')
@app.route('/index')
def index():
    if session.get('company_email'):
        return "Your Company is signed in. redirect to company page"
    elif session.get('employee_email'):
        employee = Employees.query.filter_by(employee_email=session.get('employee_email')).first()
        company = Companies.query.filter_by(company_id=employee.company_id).first()
        return redirect(url_for('profile', company_username=company.company_username))
    return render_template('home.html')


@app.route('/register-company', methods=['GET', 'POST'])
def company_signup():
    if session.get('company_email'):
        return "Your Company is signed in. redirect to company page"
    elif session.get('employee_email'):
        return "Employee is already signed in. redirect to employee page"
    form = CompanyRegistrationForm()
    if form.validate_on_submit():
        company = Companies(company_name=form.company_username.data, company_username=form.company_username.data,
                            company_email=form.company_email.data)
        company.set_password(form.company_password.data)
        db.session.add(company)
        db.session.commit()
        flash('Your Company has been successfully registered.<br>Login here', 'dark')
        send_company_welcome_email(company)
        return redirect(url_for('login', company_username=form.company_username.data))
    return render_template('company_signup.html', form=form, alert_type='form-alert')


@app.route('/company-username', methods=['GET', 'POST'])
def company_username():
    if session.get('company_email'):
        return "Your Company is signed in. redirect to company page"
    elif session.get('employee_email'):
        return "Employee is already signed in. redirect to employee page"
    form = CompanyUsername()
    username = form.company_username.data
    if form.validate_on_submit():
        return redirect(url_for('login', company_username=username))
    return render_template('company_username.html', form=form, alert_type='form-alert')

@app.route('/<company_username>')
def redirectlogin(company_username):
    return redirect (url_for('login', company_username=company_username))

@app.route('/<company_username>/login', methods=['GET', 'POST'])
def login(company_username):
    if session.get('company_email'):
        return "Your Company is signed in. redirect to company page"
    elif session.get('employee_email'):
        return redirect(url_for('profile', company_username=company_username))
    form = LoginForm()
    #company2 is to check and make sure that the company found using email is same as the company found using username from the url
    pre_email = request.args.get('n_email')
    if pre_email:
        form.email.data = pre_email
    company2 = Companies.query.filter_by(company_username=company_username).first_or_404()
    company = Companies.query.filter_by(company_email=form.email.data, company_id=company2.company_id).first()
    employee = Employees.query.filter_by(employee_email=form.email.data, company_id=company2.company_id).first()
    if form.validate_on_submit():
        not_valid = 'None'
        if company is not None and company.check_password(form.password.data):
            session['company_email'] = company.company_email
            #check this code
            # next_page = request.args.get('next')
            # if next_page:
            #     return redirect(next_page)
            return "Here will be company's main page and it will be redirected to"
        elif employee is not None and employee.check_password(form.password.data):
            session['employee_email'] = employee.employee_email
            #check this code
            # next_page = request.args.get('next')
            # if next_page:
            #     return redirect(next_page)
            return redirect(url_for('profile', company_username=company_username))
        flash('Invalid username or password. Please try again', 'error')
    return render_template('general_login.html', form=form, company_username=company_username, alert_type='form-alert')


#Employees register here
@app.route('/<company_username>/register', methods=['GET', 'POST'])
def employeeregister(company_username):
    if session.get('company_email'):
        return "Your Company is signed in. redirect to company page"
    elif session.get('employee_email'):
        return "Employee is already signed in. redirect to employee page"
    company = Companies.query.filter_by(company_username=company_username).first_or_404()
    form = EmployeeRegistrationForm()
    if form.validate_on_submit():
        employee = Employees(employee_name=form.employee_name.data, employee_surname=form.employee_surname.data,
                             employee_username=form.employee_username.data, employee_email=form.employee_email.data,
                             employee=company)
        employee.set_password(form.employee_password.data)
        db.session.add(employee)
        db.session.commit()
        flash('Employee successfully registered', 'dark')
        return redirect(url_for('login', company_username=company_username))
    return render_template('employee_signup.html', form=form, company_username=company_username)


@app.route('/logout')
def logout():
   if session.get('company_email'):
       session.pop('company_email')
   elif session.get('employee_email'):
       session.pop('employee_email')
   return redirect(url_for('index'))


@app.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    if session.get('company_email'):
        return "Your Company is signed in. redirect to company page"
    elif session.get('employee_email'):
        return "Employee is already signed in. redirect to employee page"
    form = ResetPasswordnUsernameRequestForm()
    if form.validate_on_submit():
        company = Companies.query.filter_by(company_email=form.email.data).first()
        employee = Employees.query.filter_by(employee_email=form.email.data).first()
        if company:
            send_password_reset_email(company)
        elif employee:
            send_password_reset_email(employee)
        flash('Check your email for instructions on how to reset your password', 'dark')
    return render_template('reset_password_request.html', title='Reset Password', form=form, alert_type='form-alert')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if session.get('company_email'):
        return "Your Company is signed in. redirect to company page"
    elif session.get('employee_email'):
        return "Employee is already signed in. redirect to employee page"
    company = Companies.verify_reset_password_token(token)
    employee = Employees.verify_reset_password_token(token)
    if not (company or employee):
        # make a page to be returned
        return "link has expired or is invalid"
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if company:
            company.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been reset.', 'dark')
            return redirect(url_for('login', company_username=company.company_username, n_email=company.company_email))
        elif employee:
            e_company = Companies.query.get(employee.company_id)
            employee.set_password(form.password.data)
            db.session.commit()
            flash('Your password has been reset.', 'dark')
            return redirect(url_for('login', company_username=e_company.company_username, n_email=employee.employee_email))
    return render_template('reset_password.html', title='Reset Password', form=form, alert_type='form-alert')


@app.route('/recover-company-username', methods=['GET', 'POST'])
def recover_company_username():
    if session.get('company_email'):
        return "Your Company is signed in. redirect to company page"
    elif session.get('employee_email'):
        return "Employee is already signed in. redirect to employee page"
    form = ResetPasswordnUsernameRequestForm()
    if form.validate_on_submit():
        company = Companies.query.filter_by(company_email=form.email.data).first()
        employee = Employees.query.filter_by(employee_email=form.email.data).first()
        if company:
            company_username = company.company_username
            flash("Your Company's username is <strong><em>{}</em></strong>".format(company_username), "dark")
            return redirect(url_for('login', company_username=company_username, n_email=form.email.data))
        elif employee:
            company_username = Companies.query.filter_by(company_id=employee.company_id).first().company_username
            flash("Your Company's username is <strong><em>{}</em></strong>".format(company_username), "dark")
            return redirect(url_for('login', company_username=company_username, n_email=form.email.data))
        else:
            flash("User not Found. check your email for possible error", "warning")
    return render_template('recover_company_username.html', title='Recover Username', form=form, alert_type='form-alert')


#training creation
@app.route('/<company_username>/create-trainings', methods=['GET', 'POST'])
@access_company
def trainings(company_username):
    form = TrainingForm()
    company = Companies.query.filter_by(company_username=company_username).first_or_404()
    training = Trainings.query.filter_by(training_name=form.training_name.data, company_id=company.company_id).first()
    available_trainings = Trainings.query.filter_by(company_id=company.company_id).all()
    if form.training_submit.data:
        if form.validate_on_submit():
            if training is None:
                new_training = Trainings(training_name=form.training_name.data,
                                        training_description=form.training_description.data, 
                                        date_created=datetime.utcnow(), training=company)
                db.session.add(new_training)
                db.session.commit()
                flash('Training has been published. Employees can now view them and subscribe')
                return redirect(url_for('trainings', company_username=company_username))
            else:
                flash("There's a training with a similar name")
    return render_template('create_trainings.html', form=form, training=available_trainings, company_username=company_username)


@app.route('/<company_username>/manage-trainings', methods=['GET', 'POST'])
@access_company
def manage_trainings(company_username):
    if request.form.get("mark_complete"):
        training_id = request.form.get("mark_complete")
    elif request.form.get("delete"):
        training_id = request.form.get("delete")
    training = Trainings.query.filter_by(training_id=training_id).first()
    if request.form.get("mark_complete"):
        if training.training_status != False:
            training.training_status = False
            training.date_completed = datetime.utcnow()
            db.session.commit()
            flash("Training status changed")
        else:
            flash("Training status has since changed")
    if request.form.get("delete"):
        if training is not None:
            db.session.delete(training)
            db.session.commit()
            flash("Training deleted")
        else:
            flash("Training has since been deleted")
    return redirect(url_for('trainings', company_username=company_username))


@app.route('/<company_username>/training-deets', methods=['GET', 'POST'])
@access_company
def trainings_deets(company_username):
    form = TrainingForm()
    company = Companies.query.filter_by(company_username=company_username).first_or_404()
    training = Trainings.query.filter_by(training_name=request.args.get("v"), company_id=company.company_id).first_or_404()
    training2 = Trainings.query.filter_by(training_name=form.training_name.data, company_id=company.company_id).first()
    
    # update training
    if form.training_submit.data:
        if form.validate_on_submit():
            if training is not None and training.training_status != False:
                if training.training_name != form.training_name.data:
                    if training2 is None:
                        training.training_name = form.training_name.data
                        training.training_description = form.training_description.data
                        db.session.commit()
                        flash("Training updated")
                        return redirect(url_for('trainings', company_username=company_username))
                    else:
                        flash("There's a training with a similar name")
                elif training.training_description != form.training_description.data:
                    training.training_description = form.training_description.data
                    db.session.commit()
                    flash("Training description updated")
                    return redirect(url_for('trainings', company_username=company_username))
                else:
                    flash("Training details are same as old ones")
    elif request.method == 'GET':
        form.training_name.data = training.training_name
        form.training_description.data = training.training_description
    else:
        form.training_name.data = training.training_name
        form.training_description.data = training.training_description

    # add employee to training
    if request.form.get("add"):
        employee = Employees.query.filter_by(employee_id=request.form.get("add"), company_id=company.company_id).first()
        if employee is not None:
            if training is not None:
                if training.training_status != False:
                    if training not in employee.training_subscriptions:
                        training.subscribers.append(employee)
                        db.session.commit()
                        flash("You've successfully added {} to {}".format(employee.employee_name, training.training_name))
                    else:
                        flash("{} is already subscribed to {}".format(employee.employee_name, training.training_name))
                        return redirect(url_for('trainings_deets', company_username=company_username, v=training.training_name))
                else:
                    flash("This training has been marked as Completed")
            else:
                flash("This training has been deleted")

    # remove employee from training
    elif request.form.get("remove"):
        employee = Employees.query.filter_by(employee_id=request.form.get("remove"), company_id=company.company_id).first()
        if employee is not None:
            if training is not None:
                if training.training_status != False:
                    if training in employee.training_subscriptions:
                        training.subscribers.remove(employee)
                        db.session.commit()
                        flash("You've successfully removed {} from {}".format(employee.employee_name, training.training_name))
                    else:
                        flash("{} is already unsubscribed from {}".format(employee.employee_name, training.training_name))
                        return redirect(url_for('trainings_deets', company_username=company_username, v=training.training_name))
                else:
                    flash("This training has been marked as Completed")
            else:
                flash("This training has been deleted")
    return render_template('training_deets.html', form=form, training=training, company=company)


@app.route('/<company_username>/create-projects', methods=['GET', 'POST'])
@access_company
def create_projects(company_username):
    pass





@app.route('/<company_username>/subscribe-training', methods=['GET', 'POST'])
@access_employee
def training_subscription(company_username):
    employee = Employees.query.filter_by(employee_email=session.get('employee_email')).first()
    training_available = Trainings.query.filter_by(company_id=employee.company_id).all()
    if request.form.get("subscribe"):
        trainings = Trainings.query.filter_by(training_id=request.form.get("subscribe"), training_status=True).first()
        if trainings is not None:
            if trainings not in employee.training_subscriptions:
                trainings.subscribers.append(employee)
                db.session.commit()
                flash("You've been subscribed to {}".format(trainings.training_name))
                return redirect(url_for('training_subscription', company_username=company_username))
            else:
                flash("You're already subscribed to {}".format(trainings.training_name))
                return redirect(url_for('training_subscription', company_username=company_username))
        else:
            flash("This training is no longer available for subscription")
            return redirect(url_for('training_subscription', company_username=company_username))
    elif request.form.get("unsubscribe"):
        trainings = Trainings.query.filter_by(training_id=request.form.get("unsubscribe"), training_status=True).first()
        if trainings is not None:
            if trainings in employee.training_subscriptions:
                trainings.subscribers.remove(employee)
                db.session.commit()
                flash("You've been unsubscribed from {}".format(trainings.training_name))
                return redirect(url_for('training_subscription', company_username=company_username))
            else:
                flash("You're already unsubscribed from {}".format(trainings.training_name))
                return redirect(url_for('training_subscription', company_username=company_username))
        else:
            flash("This training has been completed or is no longer available")
            return redirect(url_for('training_subscription', company_username=company_username))
    return render_template('training_subscribe.html', employee=employee, title="Trainings", training_available=training_available, company_username=company_username)


@app.route('/<company_username>/profile', methods=['GET', 'POST'])
@access_employee
def profile(company_username):
    employee = Employees.query.filter_by(employee_email=session.get('employee_email')).first()
    form = EmployeeUpdateProfileForm()
    form2 = UploadImageForm()
    if form.employee_submit.data:
        if form.validate_on_submit():
            if (form.employee_name.data != employee.employee_name or form.employee_surname.data != employee.employee_surname or 
                form.employee_username.data != employee.employee_username or form.employee_email.data != employee.employee_email):
                if form.employee_name.data != employee.employee_name:
                    employee.employee_name = form.employee_name.data
                if form.employee_surname.data != employee.employee_surname:
                    employee.employee_surname = form.employee_surname.data
                if form.employee_username.data != employee.employee_username:
                    employee.employee_username = form.employee_username.data
                if form.employee_email.data != employee.employee_email:
                    employee.employee_email = form.employee_email.data
                    session['employee_email'] = employee.employee_email
                db.session.commit()
                flash("Your account information has been updated",'success')
                return redirect(url_for('profile', company_username=company_username))
            if (form.employee_name.data == employee.employee_name and form.employee_surname.data == employee.employee_surname and 
                form.employee_username.data == employee.employee_username and form.employee_email.data == employee.employee_email):
                flash('Account data has not been changed', 'warning')
                return redirect(url_for('profile', company_username=company_username))
    elif form2.upload.data:
        if form2.validate_on_submit():
            old_image = employee.employee_image
            image_file = save_images(form2.image.data, old_image)
            employee.employee_image = image_file
            db.session.commit()
            flash('Image has been uploaded', 'success')
        return redirect(url_for('profile', company_username=company_username))
    elif request.method == 'GET':
        form.employee_name.data = employee.employee_name
        form.employee_surname.data = employee.employee_surname
        form.employee_username.data = employee.employee_username
        form.employee_email.data = employee.employee_email
    return render_template('employee_profile.html', form=form, form2=form2, title="Profile", employee=employee, company_username=company_username)


def save_images(form_image, imageto_replace):

    #delete former image fn if it exists in the directory and filename is not None from db
    if imageto_replace is not None:
        if imageto_replace != '':
            imageto_replace_path = os.path.join(app.root_path, 'static', 'profile_images', 'avatars', imageto_replace)
            if os.path.exists(imageto_replace_path):
                os.remove(imageto_replace_path)

    #upload new image fn
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_image.filename)
    image_fn = random_hex + f_ext
    image_path = os.path.join(app.root_path, 'static', 'profile_images', 'avatars', image_fn)
    output_size = (600, 600)
    i = Image.open(form_image)
    i.thumbnail(output_size)
    i.save(image_path)

    return image_fn

