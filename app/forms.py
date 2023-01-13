from flask_wtf import FlaskForm
from flask import request
from wtforms import StringField, DateTimeField, PasswordField, BooleanField, SubmitField, TextAreaField, DateField, SelectField, SelectMultipleField, widgets, BooleanField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, InputRequired
from app.models import User, Room, Meeting,  Servicio, UserInRole
from datetime import datetime, date
from flask_login import current_user
from flask_babel import _, lazy_gettext as _l



class LoginForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesion')

class RegistrationForm(FlaskForm):
    username = StringField('Nombre de usuario', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField(
        'Repite la contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarme')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Por favor utiliza un nombre de usuario distinto.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Por favor utiliza una direccion de e-mail distinta.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('Acerca de mi',
                             validators=[Length(min=0, max=140)])
    first_name = TextAreaField('Nombre(s)',
                             validators=[Length(min=0, max=30)])
    first_last_name = TextAreaField('Primer apellido',
                             validators=[Length(min=0, max=30)])
    second_last_name = TextAreaField('Segundo apellido',
                             validators=[Length(min=0, max=30)])
    date_of_birth = DateField('Fecha de nacimiento', validators=[DataRequired()],format="%Y-%m-%d")
    submit = SubmitField('Actualizar')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Por favor utiliza un nombre de usuario distinto.')


class EmptyForm(FlaskForm):
    submit = SubmitField('Enviar')


class PostForm(FlaskForm):
    post = TextAreaField('Escribe algo', validators=[DataRequired()])
    submit = SubmitField('Enviar')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField(
        'Repite la contaseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Solicitar contraseña nueva')

class ResetPasswordRequestForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    submit = SubmitField('Solicitar contraseña nueva')

class UserChoiceIterable(object):
    def __iter__(self):
        users=User.query.all()
        choices=[(user.id,'{user.username}') for user in users]
        choices=[choice for choice in choices if 'admin' not in choice[1]] # do not delete admin
        for choice in choices:
            yield choice

class RoomChoiceIterable(object):
    def __iter__(self):
        rooms=Room.query.all()
        choices=[(room.id,room.roomName) for room in rooms]
        for choice in choices:
            yield choice


class DoctorChoiceIterable(object):
    def __iter__(self):
        doctores=UserInRole.query.filter_by(role_id=1).all()
        choices=[(doctor.user_id,User.query.filter_by(id=doctor.user_id).all()) for doctor in doctores]

        for choice in choices:
            yield choice

class PacienteChoiceIterable(object):
    def __iter__(self):
        pacientes=UserInRole.query.filter_by(role_id=2).all()
        choices=[(paciente.user_id, User.query.filter_by(id=paciente.user_id).all()) for paciente in pacientes]

        for choice in choices:
            yield choice

class ServicioChoiceIterable(object):
    def __iter__(self):
        servicios=Servicio.query.all()
        choices=[(servicio.id,servicio.servicioName) for servicio in servicios]
        for choice in choices:
            yield choice



class BookmeetingForm(FlaskForm):
    title=StringField('Asunto de la consulta',validators=[DataRequired()])
    servicios=SelectField('Seleccione servicio',coerce=int,choices=ServicioChoiceIterable())
    rooms=SelectField('Seleccione',coerce=int,choices=RoomChoiceIterable())
    doctores=SelectField('Seleccione dentista',coerce=int,choices=DoctorChoiceIterable())

    date=DateField("Fecha", validators=([InputRequired(), DataRequired()]),format="%Y-%m-%d")
    startTime=SelectField('Elige la hora de inicio (en formato de 24 hrs)',coerce=int,choices=[(i,i) for i in range(9,19)])
    #duration=SelectField('Choose duration of the meeting(in hours)',coerce=int,choices=[(i,i) for i in range(1,6)])
    participants_user=current_user
    submit=SubmitField('Agendar')


    def validate_title(self,title):
        meeting=Meeting.query.filter_by(title=self.title.data).first()
        if meeting is not None: # username exist
            raise ValidationError('Por favor utiliza un titulo de cita distinto.')

    #def validate_date(self,date):
        #if self.date.data<datetime.datetime.now().date():
        #    raise ValidationError('Solo puede agendar a partir del dia de mañana.')


class BookmeetingFormDr(FlaskForm):
    title=StringField('Asunto de la consulta',validators=[DataRequired()])
    servicios=SelectField('Seleccione servicio',coerce=int,choices=ServicioChoiceIterable())
    rooms=SelectField('Seleccione consultorio',coerce=int,choices=RoomChoiceIterable())
    doctores=SelectField('Seleccione dentista',coerce=int,choices=DoctorChoiceIterable())
    pacientes=SelectField('Seleccione paciente',coerce=int,choices=PacienteChoiceIterable())
    date=DateField("Fecha", validators=([InputRequired(), DataRequired()]))
    startTime=SelectField('Elige la hora de inicio (en formato de 24 hrs)',coerce=int,choices=[(i,i) for i in range(9,19)])
    duration=SelectField('Elige la duracion de la consulta (en horas)',coerce=int,choices=[(i,i) for i in range(1,6)])
    participants_user=current_user
    edit_precio=BooleanField('Ajustar precio')
    precio_nuevo=StringField('Ingrese precio')
    submit=SubmitField('Agendar')

    def validate_title(self,title):
        meeting=Meeting.query.filter_by(title=self.title.data).first()
        if meeting is not None: # username exist
            raise ValidationError('Por favor utiliza un titulo de cita distinto.')

    def validate_date(self,date):
        if self.date.data<datetime.datetime.now().date():
            raise ValidationError('Solo puede agendar a partir del día de mañana.')


class MeetingChoiceIterable(object):
    def __iter__(self):
        meetings=Meeting.query.filter_by(estado='Activa').order_by(Meeting.date).all()
        #meetings=Meeting.query.filter_by(doctorId=current_user.id).order_by(Meeting.date).all()
        choices=[(meeting.id,f'{meeting.servicio} con {User.query.filter_by(id=meeting.pacienteId).first().username} en {Room.query.filter_by(id=meeting.roomId).first().roomName} el dia {meeting.date.date()} a las {meeting.startTime}') for meeting in meetings]
        for choice in choices:
            yield choice

class CancelacionForm(FlaskForm):
    ids=SelectField('Elige la cita que deseas cancelar',coerce=int,choices=MeetingChoiceIterable())
    submit=SubmitField('Cancelar')

class EditarForm(FlaskForm):
    ids=SelectField('Elige la cita que deseas modificar',coerce=int,choices=MeetingChoiceIterable())
    title=StringField('Asunto de la consulta',validators=[DataRequired()])
    servicios=SelectField('Seleccione servicio',coerce=int,choices=ServicioChoiceIterable())
    rooms=SelectField('Seleccione',coerce=int,choices=RoomChoiceIterable())
    doctores=SelectField('Seleccione dentista',coerce=int,choices=DoctorChoiceIterable())
    date=DateField("Fecha", validators=([InputRequired(), DataRequired()]))
    startTime=SelectField('Seleccione hora',coerce=int,choices=[(i,i) for i in range(9,19)])
    submit=SubmitField('Editar Cita')

class PagosForm(FlaskForm):
    ids=SelectField('Elige la cita cuyo pago deseas registrar',coerce=int,choices=MeetingChoiceIterable())
    submit=SubmitField('Enviar')
