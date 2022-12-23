from datetime import datetime, date
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from app import login
from hashlib import md5
from time import time
import jwt
from app import app
from functools import wraps
from sqlalchemy import Column, ForeignKey, Integer, Table, create_engine, String
from sqlalchemy.orm import declarative_base, relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
#  tablaauxiliar=Table(
#       "tablaauxiliar",
#       Base.metadata,
#       Column("doctorId", ForeignKey("user.User.id")),
#       Column("pacienteId", ForeignKey("user.User.id")),
#       Column("bookerId", ForeignKey("user.User.id"))
#   )

engine=create_engine(u'sqlite:///:memory:', echo=True)
session=scoped_session(sessionmaker(bind=engine))


class User(UserMixin, db.Model):
    __tablename__="user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me= db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    #bookers=db.relationship('Meeting', backref='booker',lazy='dynamic')
    #doctors=db.relationship('Meeting', backref='doctor',lazy='dynamic')
    #pacientes=db.relationship('Meeting', backref='paciente',lazy='dynamic')
    #bookers=relationship('Meeting', back_populates='citabooker')
    #doctors=relationship('Meeting', back_populates='citadoctor')
    #pacientes=relationship('Meeting', back_populates='citapaciente')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self,password):
        self.password_hash=generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True, unique=True)
    code = db.Column(db.String(64), index=True, unique=True)





class UserInRole(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)




class Room(db.Model):
    id=db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    roomName=db.Column(db.String(64), nullable=False)
    meetings=db.relationship('Meeting',backref='room',lazy='dynamic')

    def __repr__(self):
        return f'Room {self.roomName}'

#class Doctor(db.Model):
#    id=db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
#    doctorName=db.Column(db.String(64), nullable=False)
#    meetings=db.relationship('Meeting',backref='doctor',lazy='dynamic')

#    def __repr__(self):
#        return f'Doctor {self.doctorName}'

class Servicio(db.Model):
    id=db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    servicioName=db.Column(db.String(64), nullable=False)
    servicioCosto=db.Column(db.Integer, nullable=False)
    meetings=db.relationship('Meeting',backref='servicio',lazy='dynamic')

    def __repr__(self):
        return f'Servicio {self.servicioName}'

class Meeting(db.Model):
    __tablename__="meeting"
    id=db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    title=db.Column(db.String(64),nullable=False,unique=True)
    roomId=db.Column(db.Integer, db.ForeignKey('room.id'), nullable=False)
    doctorId=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    servicioId=db.Column(db.Integer, db.ForeignKey('servicio.id'), nullable=False)
    bookerId=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pacienteId=db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date=db.Column(db.DateTime,nullable=False)
    startTime=db.Column(db.Integer,nullable=False)
    endTime=db.Column(db.Integer,nullable=False) # should be calculated with startTime and duration
    estatuspago=db.Column(db.String,default='No pagado', nullable=False)
    #duration=db.Column(db.Integer,nullable=False)
    costo=db.Column(db.Integer,nullable=False)
    doctor_Id=relationship("User", foreign_keys=[doctorId])
    booker_Id=relationship("User", foreign_keys=[bookerId])

    paciente_Id=relationship("User", foreign_keys=[pacienteId])

    # citabooker=db.relationship('User', back_populates='bookers')
    # citadoctor=db.relationship('User', back_populates='doctors')
    # citapaciente=db.relationship('User', back_populates='pacientes')




    def __repr__(self):
        return f'Meeting {self.id} for {self.id}'


Base.metadata.create_all(engine)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
