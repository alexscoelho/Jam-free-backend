from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), unique=False, nullable=False)
    last_name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    account_type = db.Column(db.String(80), unique=False, nullable=False)
    language = db.Column(db.String(80), unique=False, nullable=False)
    teacher = db.relationship('Teacher', backref='user', uselist=False, lazy=True)
    student = db.relationship('Student', backref='user', uselist=False, lazy=True)

    def __repr__(self):
        return '<User %r>' % self.account_type

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instrument= db.Column(db.String(120), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<Teacher %r>' % self.user_id

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instrument = db.Column(db.String(120), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return '<User %r>' % self.user_id

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }