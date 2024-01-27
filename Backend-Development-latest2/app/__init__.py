from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate



db = SQLAlchemy()


def create_app(config_name='default'):
    app = Flask(__name__)

    if config_name == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        jwt = JWTManager(app)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['UPLOAD_FOLDER'] = '/Users/Peace Moongen/Desktop/profilepictures'
        app.config['JWT_SECRET_KEY'] = 'Akdsr45vfdfgddf3467'
        jwt = JWTManager(app)
        migrate = Migrate(app, db) 


    
    


    db.init_app(app)

    with app.app_context():
        from . import models 
        db.create_all()

    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app




