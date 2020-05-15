from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.fields.html5 import DateField, TimeField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from coolhr.models import *

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class CompanyUsername(FlaskForm):
    company_username = StringField('Company Username', validators=[DataRequired()])
    submit = SubmitField('Continue')

    def validate_company_username(self, username):
        company = Companies.query.filter_by(company_username=username.data).first()
        if company is None:
            raise ValidationError('Your Company has not been registered yet')

class CompanyRegistrationForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(min=4, max=64)])
    company_username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)], render_kw={"placeholder": "username"})
    company_email = StringField('Email', validators=[DataRequired(), Email(), Length(min=4, max=64)])
    company_password = PasswordField('Password', validators=[DataRequired()])
    company_password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('company_password', message='passwords must match')])
    company_submit = SubmitField('Register')

    def validate_company_username(self, username):
        company = Companies.query.filter_by(company_username=username.data).first()
        employee = Employees.query.filter_by(employee_username=username.data).first()
        if company or employee is not None:
            raise ValidationError('Username is already taken. Please choose a different one')

    def validate_company_email(self, email):
        company = Companies.query.filter_by(company_email=email.data).first()
        employee = Employees.query.filter_by(employee_email=email.data).first()
        if company or employee is not None:
            raise ValidationError('Email is already taken. Please choose a different one')

class EmployeeRegistrationForm(FlaskForm):
    employee_name = StringField('Name', validators=[DataRequired(), Length(min=4, max=64)])
    employee_surname = StringField('Surname', validators=[DataRequired(), Length(min=4, max=64)])
    employee_username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    employee_email = StringField('Email', validators=[DataRequired(), Email(), Length(min=4, max=64)])
    employee_password = PasswordField('Password', validators=[DataRequired()])
    employee_password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('employee_password', message='passwords must match')])
    employee_submit = SubmitField('Register')

    def validate_employee_username(self, username):
        company = Companies.query.filter_by(company_username=username.data).first()
        employee = Employees.query.filter_by(employee_username=username.data).first()
        if company or employee is not None:
            raise ValidationError('Username is already taken. Please choose a different one')

    def validate_employee_email(self, email):
        company = Companies.query.filter_by(company_email=email.data).first()
        employee = Employees.query.filter_by(employee_email=email.data).first()
        if company or employee is not None:
            raise ValidationError('Email is already taken. Please choose a different one')

class TrainingForm(FlaskForm):
    training_name = StringField('Traning Name', validators=[DataRequired(), Length(min=4, max=64)])
    training_description = TextAreaField('Training Description', validators=[Length(min=0, max=1024)])
    training_submit = SubmitField('Publish Training')

# class EditTrainingForm(FlaskForm):
#     training_name = StringField('Traning Name', validators=[DataRequired(), Length(min=4, max=64)])
#     training_description = TextAreaField('Training Description', validators=[Length(min=0, max=1024)])
#     training_submit = SubmitField('Save Changes')


class ResetPasswordnUsernameRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password', message='passwords must match')])
    submit = SubmitField('Confirm')

# class RecoverCompanyUsernameForm(FlaskForm):
#     email = StringField('Email', validators=[DataRequired(), Email()])
#     submit = SubmitField('Continue')


#deal with duplications like RecoverCompanyUsernameForm and ResetPasswordRequestForm and EditTrainingForm and TrainingForm



