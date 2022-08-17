from env import app
from flask import render_template, request, flash, redirect, url_for, session
from env.models import User, Room, Reserva
from env import db
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from markupsafe import escape
import sqlite3
import uuid

'''
Login - Sebastian
'''
@app.route('/')
@app.route('/LoginForm', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = escape(request.form["Correo"])
        password = escape(request.form["Contrasena"])
        
        print(f'Usuario: {username}')
        print(f'Contraseña:{password}')

        with sqlite3.connect("./env/db/hoteldb.db") as con: 
            cur= con.cursor()
            sql = cur.execute("SELECT password_hash FROM user where email_address = ?",[username]).fetchone()
            rol = cur.execute("SELECT rol FROM user where email_address = ?",[username]).fetchone() 
            sql2 = cur.execute("SELECT * FROM user where email_address = ?", [username]).fetchall()
           
            print(sql[0])
            print(rol)
            print(sql2)

            if sql!=None:
                clavehash = sql[0]
                session.clear()
                if check_password_hash(clavehash,password):
                    session["loginsuccess"] = True
                    session['Correo'] = username
                   
                    if rol[0]=="Usuario":
                        return redirect(url_for('Reservar'))
                        #return render_template("shop.html", datosuser = sql2[0], session = session)
                    if rol[0]=="Administrador":
                        return redirect(url_for("adminPage"))
                    if rol[0]=="Super Administrador":
                        return redirect(url_for("home_page")) 
                       
                else:
                    return redirect(url_for('login')) 

    return render_template("LoginForm.html")

#---Cerrar sesion---#
@app.route('/logout')
def logout():
    session.pop('loginsuccess', None)   #--Destruir despues de cerrar--
    return redirect(url_for('login'))

@app.route('/RegisterForm', methods=['GET', 'POST'])
def newUser():
    if request.method == "POST":
        nombre = escape(request.form["nombre"])
        birth = datetime.strptime(request.form["edad"],'%Y-%m-%d')
        rol = "Usuario"
        telefono = request.form["telefono"]
        cedula = request.form["cedula"]
        correo = request.form["correo"]
        password = escape(request.form["contrasena"])
        hash_pass = generate_password_hash(password)
        

        with sqlite3.connect("./env/db/hoteldb.db") as con: 
            sql = con.cursor() 
            sql.execute("INSERT INTO user(name, birth_date, rol, phone, document, email_address, password_hash) values (?, ?, ?, ?, ?, ?, ?)",(nombre, birth, rol,telefono, cedula, correo, hash_pass))
            con.commit() 
            session['name'] = nombre
            
            return redirect(url_for("login"))
    return redirect(url_for("newUser"))

'''
Reservar Habitaciones - Jorge
'''

@app.route('/habitaciones')
def Reservar():    
    return render_template("shop.html")

@app.route('/asignarHabitacion/<int:nHab>',methods=['GET','POST'])
def AsignarHabitacion(nHab):
    
    conn = sqlite3.connect('./env/db/hoteldb.db')
    cursor = conn.cursor()
    instruction = f"SELECT check_out_date FROM reserva WHERE room_booking = '{nHab}'ORDER BY id DESC;"
    cursor.execute(instruction)
    fmin = cursor.fetchone()
    conn.commit()
    conn.close()
    
    if fmin ==None:
        fmin = datetime.now()
        fmin = fmin.strftime("%Y-%m-%d")
    else:
        fmin = fmin[0]
        fmin = fmin[:10]
    print(fmin)
    usuario = session['Correo']
    return render_template("shop-single.html",nHab=nHab,usuario=usuario,fmin=fmin)

@app.route('/VerReserva')
def ver_reserva():
    usuario = session['Correo']
    conn = sqlite3.connect("./env/db/hoteldb.db")
    cursor = conn.cursor()
    instruction = f"SELECT id FROM user WHERE email_address = '{usuario}'"
    cursor.execute(instruction)
    id = cursor.fetchone()
    conn.commit()
    conn.close()
    id=int(id[0])
    print(id)

    conn = sqlite3.connect("./env/db/hoteldb.db")
    cursor = conn.cursor()
    instruction2 = f"SELECT room_booking,check_in_date,check_out_date,costo_reserva FROM reserva WHERE user_booking = {id} ORDER BY id DESC;"
    cursor.execute(instruction2)
    reserva = cursor.fetchone()
    conn.commit()
    conn.close()
    hab=reserva[0]
    fecha_ingreso=reserva[1]
    fecha_salida=reserva[2]
    costo = reserva[3]
    
    return render_template("Avisoreserva.html",hab=hab,fecha_ingreso=fecha_ingreso,fecha_salida=fecha_salida,costo=costo,usuario=usuario)

@app.route('/rHab/<int:nHab>',methods=['GET','POST'])
def reservaHabitacion(nHab):
    usuario = session['Correo']
    conn = sqlite3.connect("./env/db/hoteldb.db")
    cursor = conn.cursor()
    instruction = f"SELECT id FROM user WHERE email_address = '{usuario}'"
    cursor.execute(instruction)
    Ide = cursor.fetchone()
    conn.commit()
    conn.close()
    Ide=int(Ide[0])

    if request.method == 'POST':
        NumeroHab = nHab
        fecha_ingreso = request.form['fecha_ingreso']
        fecha_salida = request.form['fecha_egreso']
        #num_reserva = str(uuid.uuid4().int)
        date1=datetime.strptime(fecha_ingreso, '%Y-%m-%d')
        date2=datetime.strptime(fecha_salida, '%Y-%m-%d')
        #dif= (date2-date1).days
        #dif=dif.days
        #precio = (dif*100000)
        
        if (date2-date1).days > 0:
            Reserva.create_reserva(date1, date2,NumeroHab,Ide)
            return redirect(url_for("ver_reserva"))
            
        else:
            
            return redirect(url_for("Reserva"))

'''
Panel SuperUsuario - Vicente
'''

@app.route('/controlpanel')
def home_page():
    user_rol = User.query.filter_by(email_address = session['Correo']).first().rol
    
    if user_rol == "Super Administrador":
        return render_template('panelSuper.html')
    else:
        return redirect(url_for('Reservar'))
    
@app.route('/control_user', methods=['GET','POST'])
def crud_usuario_page():
    
    user_rol = User.query.filter_by(email_address = session['Correo']).first().rol
    
    if user_rol == "Super Administrador":
        
        if request.method == 'POST':        
            updated_user = User.query.filter_by(id=request.form.get('id')).first()        
            if request.form.get('action') == 'editar':            
                updated_user.name = request.form.get('name')
                updated_user.birth_date = datetime.strptime(str(request.form.get('nacimiento')),'%Y-%m-%d')
                updated_user.rol = request.form.get('rol')
                updated_user.phone = request.form.get('phone')
                updated_user.document = request.form.get('documento')
                updated_user.email = request.form.get('email')
                db.session.add(updated_user)
                db.session.commit()            
                flash('Usuario actualizado',category='success')        
            if request.form.get('action') == 'agregar':            
                User.create_user(request.form.get('name'),datetime.strptime(str(request.form.get('nacimiento')),'%Y-%m-%d'),request.form.get('rol'),request.form.get('phone'),
                                 request.form.get('documento'),request.form.get('email'),'password_temp')            
                flash('Usuario Creado',category='success')             
            if request.form.get('action') == 'eliminar':            
                User.delete_user(updated_user.id)
                flash('Usuario eliminado',category='success')          
            return redirect(url_for('crud_usuario_page'))
        if request.method == 'GET':        
            users = User.query.all()
            return render_template('userCrud.html',users = users)
    
    else: 
        #flash('Usuario invalido', category = 'error')
        return redirect(url_for('Reservar'))
    

@app.route('/control_rooms', methods=['GET','POST'])
def crud_room_page():
    
    if request.method == 'POST':
        
        updated_room = Room.query.filter_by(id=request.form.get('id')).first()
        
        if request.form.get('action') == 'editar':
            
            try:
                
                updated_room.roomNumber = request.form.get('name')
                updated_room.disponibilidad = request.form.get('disponibilidad')
                     
                db.session.add(updated_room)
                db.session.commit()
            
                flash('Habitacion actualizada con exito',category='success')
                
            except:
                
                flash('Revise informacion suministrada',category='danger')
        
        if request.form.get('action') == 'agregar':
            
            try:  
                Room.create_room(request.form.get('room_number'), int(request.form.get('disponibilidad')))
                flash('Habitacion creada con exito',category='success') 
            except:
                flash('Revise informacion suministrada',category='danger')
        
        if request.form.get('action') == 'eliminar':
            
            Room.delete_room(id=updated_room.id)
            flash('Habitacion eliminada', category='success') 
            
        return redirect(url_for('crud_room_page'))
        
    if request.method == 'GET':
        
        rooms = Room.query.all()
        return render_template('roomCrud.html',rooms = rooms)

@app.route('/control_reservation', methods=['GET','POST'])
def crud_reservation_page():
    
    if request.method == 'POST':
        
        updated_reserva = Reserva.query.filter_by(id=request.form.get('id')).first()
               
        if request.form.get('action') == 'eliminar':
            
            try:
                
                Reserva.delete_reserva(id=updated_reserva.id)
                flash('Habitacion eliminada', category='success')
            
            except:
                              
                flash('Revise informacion suministrada', category='danger')
                
        return redirect(url_for('crud_reservation_page'))
                          
    if request.method == 'GET':
    
        reservations = Reserva.query.all()
        return render_template('reservationCrud.html', reservations=reservations)

'''
Panel Administrador - Erlin
'''

@app.route('/Administrador')
def adminPage():
    return render_template('Administrador.html')

@app.route('/control_user_admin', methods=['GET','POST'])
def crud_usuario_admin():
    
    if request.method == 'POST':        
        updated_user = User.query.filter_by(id=request.form.get('id')).first()        
        if request.form.get('action') == 'editar':            
            updated_user.name = request.form.get('name')
            updated_user.birth_date = datetime.strptime(str(request.form.get('nacimiento')),'%Y-%m-%d')
            updated_user.rol = request.form.get('rol')
            updated_user.phone = request.form.get('phone')
            updated_user.document = request.form.get('documento')
            updated_user.email = request.form.get('email')
            db.session.add(updated_user)
            db.session.commit()            
            flash('Usuario actualizado',category='success')        
        if request.form.get('action') == 'agregar':            
            User.create_user(request.form.get('name'),datetime.strptime(str(request.form.get('nacimiento')),'%Y-%m-%d'),request.form.get('rol'),request.form.get('phone'),
                             request.form.get('documento'),request.form.get('email'),'password_temp')            
            flash('Usuario Creado',category='success')             
        if request.form.get('action') == 'eliminar':            
            User.delete_user(updated_user.id)
            flash('Usuario eliminado',category='success')          
        return redirect(url_for('crud_usuario_admin'))    
    if request.method == 'GET':        
        users = User.query.all()
        return render_template('userCrudAdmin.html',users = users)

@app.route('/control_rooms_admin', methods=['GET','POST'])
def crud_room_admin():
    
    if request.method == 'POST':        
        updated_room = Room.query.filter_by(id=request.form.get('id')).first()        
        if request.form.get('action') == 'editar':            
            try:                
                updated_room.roomNumber = request.form.get('name')
                updated_room.disponibilidad = request.form.get('disponibilidad')                     
                db.session.add(updated_room)
                db.session.commit()            
                flash('Habitacion actualizada con exito',category='success')                
            except:                
                flash('Revise informacion suministrada',category='danger')        
        if request.form.get('action') == 'agregar':            
            try:  
                Room.create_room(request.form.get('room_number'), int(request.form.get('disponibilidad')))
                flash('Habitacion creada con exito',category='success') 
            except:
                flash('Revise informacion suministrada',category='danger')        
        if request.form.get('action') == 'eliminar':            
            Room.delete_room(id=updated_room.id)
            flash('Habitacion eliminada', category='success')             
        return redirect(url_for('crud_room_admin'))        
    if request.method == 'GET':        
        rooms = Room.query.all()
        return render_template('roomCrudAdmin.html',rooms = rooms)
