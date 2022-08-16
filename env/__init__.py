from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

import os

db_path =os.path.abspath(os.getcwd())+'/env/db/hoteldb.db'
#print(db_path)

app = Flask(__name__,static_url_path="/static")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '0365968fd2da00888b679041'
db = SQLAlchemy(app)

from env import routes