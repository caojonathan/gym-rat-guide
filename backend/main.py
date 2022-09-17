from flask import Flask,request
from flask_restx import Api,Resource,fields
from config import DevConfig
from models import Exercise
from exts import db
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(DevConfig)

db.init_app(app)

migrate=Migrate(app,db)

api = Api(app,doc='/docs')

exercise_model=api.model( 
    "Exercise",
    {
        "id":fields.Integer(),
        "title":fields.String(),
        "description":fields.String()
    }
)


@api.route('/hello')
class HelloResource(Resource):
    def get(self):
        return {"message":"Hello World"}

@api.route('/exercises')
class ExercisesResource(Resource):
    @api.marshal_list_with(exercise_model)
    def get(self):
        """ get all exercises """
        exercises = Exercise.query.all()

        return exercises
        
    @api.marshal_with(exercise_model)
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
    def put(self,id):
        """" update an exercise by id"""
        exercise_to_update = Exercise.query.get_or_404(id)

        data=request.get_json()
        exercise_to_update.update(data.get('title'),data.get('description'))

        return exercise_to_update
    
    @api.marshal_with(exercise_model)
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