from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app
from app.forms import LoginForm, EditProfileForm
from flask_login import current_user, login_user, login_required
from app.models import User, Meeting, Room
from flask_login import logout_user
from flask import request
from werkzeug.urls import url_parse
from app import db
from app.forms import RegistrationForm
from datetime import datetime, date
from app.forms import EmptyForm
from app.forms import BookmeetingForm, BookmeetingFormDr, CancelacionForm, EditarForm
from app.models import *

def check_role(roles):    # Declaración del decorador
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for r in roles:
                is_role=Role.query.filter_by(code=r).one_or_none()
                #is_role = Role.query.get(Role.code == r)
            #if is_role != None:
                is_user=UserInRole.query.filter_by(user_id=current_user.id)
                    #is_user = UserInRole.get_or_none(UserInRole.role_id == is_role.id,
                    #UserInRole.user_id == current_user.id)

                if is_user != None:
                    pass
            return func(*args, **kwargs)
            abort(403)
        return wrapper
    return decorator



@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    rol=UserInRole.query.filter_by(user_id=current_user.id).first().role_id
    return render_template('index.html', title='Inicio', rol=rol)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Iniciar Sesion', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        rol=UserInRole(user_id=user.id, role_id=2)
        db.session.add(rol)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    rol=UserInRole.query.filter_by(user_id=current_user.id).first().role_id
    return render_template('user.html', user=user, rol=rol)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)

@app.route('/book',methods=['GET','POST'])
@login_required
def book():
    form=BookmeetingForm()
    rol=UserInRole.query.filter_by(user_id=current_user.id).first().role_id
    if form.validate_on_submit():

        # check time collision
        meetingcollisions=Meeting.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).filter_by(roomId=form.rooms.data).all()
        print(len(meetingcollisions))
        for meetingcollision in meetingcollisions:
            # [a, b] overlaps with [x, y] iff b > x and a < y
            if (form.startTime.data<meetingcollision.endTime and (form.startTime.data+form.duration.data)>meetingcollision.startTime):
                flash(f'The time from {meetingcollision.startTime} to {meetingcollision.endTime} is already booked by {User.query.filter_by(id=meetingcollision.bookerId).first().username}.')
                return redirect(url_for('book'))

        # make booking
        booker=current_user
        #paciente=current_user
        #paciente=User.query.filter_by(id=form.paciente.data).first()
        room=Room.query.filter_by(id=form.rooms.data).first()
        doctor=User.query.filter_by(id=form.doctores.data).first()
        servicio=Servicio.query.filter_by(id=form.servicios.data).first()
        costo=servicio.servicioCosto
        endTime=form.startTime.data+1
        paciente=current_user
        participants_user=current_user

        meeting=Meeting(title=form.title.data,roomId=room.id,doctorId=doctor.id,pacienteId=paciente.id,servicioId=servicio.id,bookerId=booker.id,date=form.date.data,startTime=form.startTime.data,endTime=endTime, costo=costo)
        db.session.add(meeting)
        #print('dr'+ str(form.doctores.data), 'pte' + str(form.pacientes.data), 'bkr'+ str(booker))
        # Add booking log
        #log=CostLog(title=form.title.data,date=form.date.data,cost=cost*form.duration.data)
        #db.session.add(log)

        # Add participants records


        db.session.commit()
        flash('Booking success!')
        return redirect(url_for('index'))
    return render_template('book.html',title='Book Meeting',form=form, rol=rol)


@app.route('/agenda',methods=['GET','POST'])
@login_required
#@check_role(['dr'])
def agenda():
    form=BookmeetingFormDr()
    rol=UserInRole.query.filter_by(user_id=current_user.id).first().role_id
    print('estoyaqui')
    if  request.method=='POST' and form.validate_on_submit():

        # check time collision
        meetingcollisions=Meeting.query.filter_by(date=datetime.combine(form.date.data,datetime.min.time())).filter_by(roomId=form.rooms.data).all()
        print(len(meetingcollisions))
        for meetingcollision in meetingcollisions:
            # [a, b] overlaps with [x, y] iff b > x and a < y
            if (form.startTime.data<meetingcollision.endTime and (form.startTime.data+form.duration.data)>meetingcollision.startTime):
                flash(f'The time from {meetingcollision.startTime} to {meetingcollision.endTime} is already booked by {User.query.filter_by(id=meetingcollision.bookerId).first().username}.')
                return redirect(url_for('agenda'))
        booleano=form.edit_precio.data
        room=Room.query.filter_by(id=form.rooms.data).first()
        doctor=User.query.filter_by(id=form.doctores.data).first()
        paciente=User.query.filter_by(id=form.pacientes.data).first()
        servicio=Servicio.query.filter_by(id=form.servicios.data).first()
        costo=servicio.servicioCosto
        booker=current_user
        endTime=form.startTime.data+1
        participants_user=current_user
        if booleano==True:
            costo=form.precio_nuevo.data
            return costo
        # make booking

        meeting=Meeting(title=form.title.data,roomId=room.id,doctorId=doctor.id,servicioId=servicio.id,pacienteId=paciente.id,bookerId=booker.id,date=form.date.data,startTime=form.startTime.data,endTime=endTime, costo=costo)
        db.session.add(meeting)

            # Add booking log
            #log=CostLog(title=form.title.data,date=form.date.data,cost=cost*form.duration.data)
            #db.session.add(log)

            # Add participants records


        db.session.commit()

        flash('Cita agendada correctamente')
        return redirect(url_for('index'))
    return render_template('agenda.html',title='Agendar Cita',form=form,rol=rol)

#ajustar tabla uwu
@app.route('/miscitas')
def miscitas():

    meetings=Meeting.query.filter_by(doctorId=current_user.id).order_by(Meeting.date).all()
    meetingreturns=[]
    for meeting in meetings:

        meetingreturn=dict()
        meetingreturn['Servicio']=meeting.servicio
        #meetingreturn['Paciente']=User.query.filter_by(id=meeting.pacienteId).first().username
        meetingreturn['Paciente']=User.query.filter_by(id=meeting.pacienteId).first().username
        meetingreturn['Doctor']=User.query.filter_by(id=meeting.doctorId).first()
        meetingreturn['Agendadapor']=User.query.filter_by(id=meeting.bookerId).first()
        meetingreturn['Consultorio']=Room.query.filter_by(id=meeting.roomId).first()
        meetingreturn['Fecha']=meeting.date.date()
        meetingreturn['Hora']=f'A las {meeting.startTime} horas'
        meetingreturn['Observaciones']=meeting.title
        meetingreturn['Costo']=f'$ {meeting.costo} '
        meetingreturn['Estatuspago']=meeting.estatuspago
        meetingreturns.append(meetingreturn)


    return render_template('miscitas.html',meetings=meetingreturns)


@app.route('/cancelaciones',methods=['GET','POST'])
@login_required
#@check_role('[dr]')
def cancelaciones():
    if not current_user.is_authenticated:
        flash('Es necesario iniciar sesion para cancelar citas')
        return redirect(url_for('login'))

    form=CancelacionForm()
    if form.validate_on_submit():
        meeting=Meeting.query.filter_by(id=form.ids.data).first()

        if meeting.date<=datetime.now():
            flash(f'No es posible cancelar citas pasadas')
            return redirect(url_for('cancelaciones'))


            cancelacion=Meeting.query.filter_by(id=form.ids.data).update(estado='Cancelada')
            db.session.commit()

        flash(f'Cita {meeting.servicio} cancelada correctamente! ')
        return redirect(url_for('index'))
    return render_template('cancelaciones.html',title='Cancelar cita',form=form)


@app.route('/editar',methods=['GET','POST'])
@login_required
#@check_role('[dr]')
def editar():
    if not current_user.is_authenticated:
        flash('Es necesario iniciar sesion para editar citas')
        return redirect(url_for('login'))

    form=EditarForm()
    if form.validate_on_submit():
        servicio=Servicio.query.filter_by(id=form.servicios.data).first()
        meeting=Meeting.query.filter_by(id=form.ids.data).first()
        meeting.title=form.title.data
        meeting.room=Room.query.filter_by(id=form.rooms.data).first()
        endTime=form.startTime.data+1
        meeting.costo=servicio.servicioCosto
        meeting.doctor=User.query.filter_by(id=form.doctores.data).first()
        meeting.servicio=Servicio.query.filter_by(id=form.servicios.data).first()
        idpaciente=meeting.pacienteId
        if meeting.date<=datetime.now():
            flash(f'No es posible modificar citas pasadas')
            return redirect(url_for('editar'))

        #modificacion=Meeting.query.update(title=form.title.data, roomId=form.rooms.data, doctorId=form.doctores.data, servicioId=form.servicios.data, date=form.date.data, startTime=form.startTime.data, endTime=endTime )
        db.session.commit()
        flash(f'Cita {meeting.servicio} con {User.query.filter_by(id=idpaciente).first()} Modificada correctamente! ')
        return redirect(url_for('index'))
    return render_template('editar.html',title='Modificar cita',form=form)



@app.route('/_add_numbers')
def add_numbers():

    a = request.args.get('a', 0, type=str)
    servicio=Servicio.query.filter_by(id=a).first()
    costo=servicio.servicioCosto

    return jsonify(result=costo )

@app.route('/probardoctores',methods=['GET','POST'])
@login_required
def probdoctores():

    doctores=Doctor.query.filter_by(id=form.doctores.data).first()
    print(doctores)
