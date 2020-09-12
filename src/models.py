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
    files = db.relationship('Files', backref='user', uselist=False, lazy=True)

    def __repr__(self):
        return '<User %r>' % self.account_type

    def serialize(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "account_type": self.account_type,
            "language": self.language
        }

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instrument= db.Column(db.String(120), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return '<Teacher %r>' % self.id

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instrument = db.Column(db.String(120), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return '<User %r>' % self.id

class Files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    instrument = db.Column(db.String(120), unique=False, nullable=False)
    type_file = db.Column(db.String(120), unique=False, nullable=False)
    level = db.Column(db.String(120), unique=False, nullable=False)
    language = db.Column(db.String(120), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # agregarlo a los usuario

    def __repr__(self):
            return '<Files %r>' % self.id

    def serialize(self):
        return {
             "id": self.id,
             "instrument": self.instrument,
             "type_file": self.type_file,
             "level": self.level,
             "language": self.language,
        }

    




    

        

