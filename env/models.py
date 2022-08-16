from datetime import date
from env import db
from env import func
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import uuid


class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(length=45), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    rol = db.Column(db.String(length=20), nullable=False)
    phone = db.Column(db.Integer, nullable=False, unique=True)
    document = db.Column(db.Integer, nullable=False, unique=True)
    email_address = db.Column(db.String(length=50),
                              nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    comments = db.relationship(
        'Calificacion', backref='comment_by', lazy=True)

    booked = db.relationship(
        'Reserva', backref='booked_by', lazy=True)
    
    #@property
    #def password(self):
    #    return self.password
    #
    #@password.setter
    #def password(self, plain_text_password):
    #    self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')
#
    #def check_password_correction(self, attempted_password):
    #    return bcrypt.check_password_hash(self.password_hash, attempted_password)
        

    def __init__(self, name: str, birth_date: date, rol: str, phone: int, document: int, email_address: str,
                 password_hash: str):
        self.name = name
        self.birth_date = birth_date
        self.rol = rol
        self.phone = phone
        self.document = document
        self.email_address = email_address
        self.password_hash = password_hash

    def __repr__(self):
        return f'User: {self.name} \n'

    def create_user(name: str, birth_date: str, rol: str, phone: int, document: int, email_address: str,
                    password: str):
        
        password_hash = generate_password_hash("password")
        
        user = User(name, birth_date, rol, phone,
                    document, email_address, password_hash)

        db.session.add(user)
        db.session.commit()
        db.session.close()

    def delete_user(id:int):
        User.query.filter_by(id=id).delete()
        db.session.commit()
        db.session.close()


class Reserva(db.Model):

    __tablename__ = 'reserva'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    num_reserva = db.Column(db.String, unique=True, nullable=False)
    check_in_date = db.Column(db.DateTime, nullable=False)
    check_out_date = db.Column(db.DateTime, nullable=False)
    dias_reserva = db.Column(db.Integer, nullable=False)
    costo_reserva = db.Column(db.String, nullable=False)

    room_booking = db.Column(db.Integer, db.ForeignKey('room.id'))
    user_booking = db.Column(db.Integer, db.ForeignKey('user.id'))

    '''
    Por favor revisar - ajustar la forma de instanciar al flujo de trabajo, creo 
    que en este caso se puede generar la reserva completa referenciando tanto la habitacion 
    como el usuario a partir del logueo.
    '''
    def __init__(self, check_in_date: date, check_out_date: date, dias_reserva:int,costo_reserva:str,room_booking:int,user_booking:int):
        self.num_reserva = str(uuid.uuid4().int) #se crea un codigo de reserva con baja probabilidad de repeticion
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.dias_reserva = dias_reserva
        self.costo_reserva = costo_reserva
        self.room_booking = room_booking
        self.user_booking = user_booking

    def create_reserva(check_in_date:date, check_out_date:date, room_booking:int,user_booking:int):
    
        '''
        Esta funcion para calcular el numero de dias de la reserva y guardar en db
        Solo recibe valores en formato date asi que se debe ajustar el tipo antes de entrar aca
        '''
        PRECIO_HABITACION = 100000
        
        dias_reserva = (check_out_date - check_in_date).days 
        
        costo_reserva = dias_reserva * PRECIO_HABITACION
        reserva = Reserva(check_in_date, check_out_date, dias_reserva, costo_reserva, room_booking,user_booking)
        db.session.add(reserva)
        db.session.commit()

    def delete_reserva(id:int):
        Reserva.query.filter_by(id=id).delete()
        db.session.commit()
        db.session.close()

    def __repr__(self):
        return f'Reserva No.: {self.num_reserva} - Estado: {self.disponibilidad} \n'



class Room(db.Model):
    __tablename__ = 'room'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roomNumber = db.Column(db.String(length=3), nullable=False, unique=True)
    disponibilidad = db.Column(db.Integer, nullable=False)
    costo = db.Column(db.Integer, nullable=False)

    calificacion = db.relationship(
        'Calificacion', backref='room_score', lazy=True)

    reserva = db.relationship(
        'Reserva', backref='room_booked', lazy=True)

    def __init__(self, roomNumber: str, disponibilidad: int):
        self.roomNumber = roomNumber
        self.disponibilidad = disponibilidad
        self.costo = 100000

    def create_room(roomNumber: str, disponibilidad: int):
        room = Room(roomNumber, disponibilidad)
        db.session.add(room)
        db.session.commit()

    def delete_room(id:int):
        Room.query.filter_by(id=id).delete()
        db.session.commit()
        db.session.close()

    def __repr__(self):
        return f'Habitacion No.: {self.roomNumber} - Estado: {self.disponibilidad} \n'


class Calificacion(db.Model):

    __tablename__ = 'score'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    num_score = db.Column(db.Integer, nullable=False)
    comentario = db.Column(db.String(length=150), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())

    room_commented = db.Column(db.Integer, db.ForeignKey('room.id'))
    commented_by = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, num_score: int, comentario: str):
        self.num_score = num_score
        self.comentario = comentario

    def create_score(num_score: int, comentario: str):
        score = Calificacion(num_score, comentario)
        db.session.add(score)
        db.session.commit()
        db.session.close()

    def delete_score(id:int):
        Calificacion.query.filter_by(id=id).delete()
        db.session.commit()
        db.session.close()

    def __repr__(self):
        return f'Calificacion: {self.num_score} - Comentario: {self.comentario} \n'

def delete_record(id:int):
    User.delete_user(id)
    Reserva.delete_reserva(id)
    Calificacion.delete_score(id)
    Room.delete_room(id)