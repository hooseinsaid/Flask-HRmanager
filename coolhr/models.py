import jwt
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from coolhr import app, db

#use class for association so that an extra field of input can be accepted
employee_trainings = db.Table('employee_trainings',
                     db.Column('employee_id', db.Integer, db.ForeignKey('employees.employee_id')),
                     db.Column('training_id', db.Integer, db.ForeignKey('trainings.training_id'))
)

class Companies(db.Model):
    company_id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(64), index=True)
    company_username = db.Column(db.String(64), index=True, unique=True)
    company_email = db.Column(db.String(64), index=True, unique=True)
    company_password_hash = db.Column(db.String(128))
    employees = db.relationship('Employees', backref='employee', lazy='dynamic')
    trainings = db.relationship('Trainings', backref='training', lazy='dynamic')

    def __repr__(self):
        return '<Company {}>'.format(self.company_username)

    def set_password(self, password):
        self.company_password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.company_password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.company_username, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            company_username = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return Companies.query.filter_by(company_username=company_username).first()

class Employees(db.Model):
    employee_id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(64), index=True)
    employee_surname = db.Column(db.String(64), index=True)
    employee_username = db.Column(db.String(64), index=True, unique=True)
    employee_email = db.Column(db.String(64), index=True, unique=True)
    employee_password_hash = db.Column(db.String(128))
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'))
    training_subscriptions = db.relationship('Trainings', secondary=employee_trainings, backref=db.backref('subscribers', lazy='dynamic'))

    def __repr__(self):
        return '<Employee {}>'.format(self.employee_username)

    def set_password(self, password):
        self.employee_password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.employee_password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode({'reset_password': self.employee_username, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            employee_username = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return Employees.query.filter_by(employee_username=employee_username).first()
    
class Trainings(db.Model):
    training_id = db.Column(db.Integer, primary_key=True)
    training_name = db.Column(db.String(64), index=True)
    training_description = db.Column(db.String(1024))
    training_status = db.Column(db.Boolean, default=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.company_id'))
    date_created = db.Column(db.DateTime)
    date_completed = db.Column(db.DateTime)

    def __repr__(self):
        return '<Training {}>'.format(self.training_name)