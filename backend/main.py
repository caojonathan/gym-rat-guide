from flask import Flask,request,jsonify
from flask_restx import Api
from config import DevConfig
from models import Exercise,User
from exts import db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from exercises import exercise_ns
from auth import auth_ns


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)

    migrate=Migrate(app,db)
    JWTManager(app)

    api = Api(app,doc='/docs')

    api.add_namespace(exercise_ns)
    api.add_namespace(auth_ns)


    @app.shell_context_processor
    def make_shell_context():
        return{
            "db":db,
            "Exercise":Exercise,
            "user":User
        }

    if __name__ == '__main__':
        app.run()

    return app

