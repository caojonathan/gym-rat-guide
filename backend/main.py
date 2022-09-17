from flask import Flask,request,jsonify
from flask_restx import Api,Resource,fields
from config import DevConfig
from models import Exercise,User
from exts import db
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import JWTManager,create_access_token, create_refresh_token,jwt_required

app = Flask(__name__)
app.config.from_object(DevConfig)

db.init_app(app)

migrate=Migrate(app,db)
JWTManager(app)

api = Api(app,doc='/docs')

exercise_model=api.model( 
    "Exercise",
    {
        "id":fields.Integer(),
        "title":fields.String(),
        "description":fields.String()
    }
)

signup_model=api.model(
    "Signup",
    {
        "username":fields.String(),
        "email": fields.String(),
        "password":fields.String()
    }
)

login_model=api.model(
    "Login",
    {
        "username":fields.String(),
        "password":fields.String()
    }
)

@api.route('/hello')
class HelloResource(Resource):
    def get(self):
        return {"message":"Hello World"}


@api.route('/signup')
class SignUp(Resource):
    @api.expect(signup_model)
    def post(self):

        data=request.get_json()

        username = data.get('username')

        db_user=User.query.filter_by(username=username).first()

        if db_user is not None: 
            return jsonify({"message": f"user with username {username} already exists"})

        new_user = User(
            username =data.get('username'),
            email= data.get('email'),
            password= generate_password_hash(data.get('password'))
        )

        new_user.save()

        return jsonify({"message": f"User Successfully Created"})

        
        

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        data=request.get_json()

        username=data.get('username')
        password=data.get('password')
        
        db_user=User.query.filter_by(username=username).first()

        if db_user and check_password_hash(db_user.password, password):
            access_token= create_access_token(identity=db_user.username)
            refresh_token=create_refresh_token(identity=db_user.username)

            return jsonify({"access_token": access_token, "refresh_token": refresh_token})


@api.route('/exercises')
class ExercisesResource(Resource):
    @api.marshal_list_with(exercise_model)
    def get(self):
        """ get all exercises """
        exercises = Exercise.query.all()

        return exercises
        
    @api.marshal_with(exercise_model)
    @api.expect(exercise_model)
    @jwt_required()
    def post(self):
        """ create a new exercises """

        data = request.get_json()

        new_exercise = Exercise(
            title=data.get('title'),
            description=data.get('description')
        )

        new_exercise.save()

        return new_exercise,201

@api.route('/exercises/<int:id>')
class ExerciseResource(Resource):
    
    @api.marshal_with(exercise_model)
    def get(self,id):
        """" get exercise by id """
        exercise=Exercise.query.get_or_404(id)
        return exercise
    
    @api.marshal_with(exercise_model)
    @jwt_required()
    def put(self,id):
        """" update an exercise by id"""
        exercise_to_update = Exercise.query.get_or_404(id)

        data=request.get_json()
        exercise_to_update.update(data.get('title'),data.get('description'))

        return exercise_to_update
    
    @api.marshal_with(exercise_model)
    @jwt_required()
    def delete(self,id):
        """" delete an exercise by id"""
        exercise_to_delete=Exercise.query.get_or_404(id)
        exercise_to_delete.delete()
        return exercise_to_delete
        
    


@app.shell_context_processor
def make_shell_context():
    return{
        "db":db,
        "Exercise":Exercise
    }

if __name__ == '__main__':
    app.run()