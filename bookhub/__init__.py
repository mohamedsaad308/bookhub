import os
from flask import Flask, session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = '0745aa4aef12dcf75449bfabe77da9aa'
app.config["JSON_SORT_KEYS"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://ikpgjnrchcdhau:5d7d9d70298a6c5a5abfc86cb165a6f81368d73e31ee97aa53a60c8eaa868f88@ec2-52-87-58-157.compute-1.amazonaws.com:5432/d8a0ob5ogiao3q'
db = SQLAlchemy(app)
# To connect to database with only sql commands
os.environ["DATABASE_URL"] = "postgres://ikpgjnrchcdhau:5d7d9d70298a6c5a5abfc86cb165a6f81368d73e31ee97aa53a60c8eaa868f88@ec2-52-87-58-157.compute-1.amazonaws.com:5432/d8a0ob5ogiao3q"
engine = create_engine(os.getenv("DATABASE_URL"))
sql = scoped_session(sessionmaker(bind=engine))

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from bookhub import routes