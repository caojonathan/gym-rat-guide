from flask import Flask,request,jsonify
from flask_restx import Namespace, Resource, fields
from models import Exercise
from werkzeug.security import generate_password_hash,check_password_hash
from flask_jwt_extended import JWTManager,create_access_token, create_refresh_token,jwt_required



exercise_ns= Namespace('exercise', description = "A namespace for exercises")

@exercise_ns.route('/hello')
class HelloResource(Resource):
    def get(self):
        return {"message":"Hello World"}




exercise_model=exercise_ns.model( 
    "Exercise",
    {
        "id":fields.Integer(),
        "title":fields.String(),
        "description":fields.String()
    }
)


@exercise_ns.route('/exercises')
class ExercisesResource(Resource):
    @exercise_ns.marshal_list_with(exercise_model)
    def get(self):
        """ get all exercises """
        exercises = Exercise.query.all()

        return exercises
        
    @exercise_ns.marshal_with(exercise_model)
    @exercise_ns.expect(exercise_model)
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

@exercise_ns.route('/exercises/<int:id>')
class ExerciseResource(Resource):
    
    @exercise_ns.marshal_with(exercise_model)
    def get(self,id):
        """" get exercise by id """
        exercise=Exercise.query.get_or_404(id)
        return exercise
    
    @exercise_ns.marshal_with(exercise_model)
    @jwt_required()
    def put(self,id):
        """" update an exercise by id"""
        exercise_to_update = Exercise.query.get_or_404(id)

        data=request.get_json()
        exercise_to_update.update(data.get('title'),data.get('description'))

        return exercise_to_update
    
    @exercise_ns.marshal_with(exercise_model)
    @jwt_required()
    def delete(self,id):
        """" delete an exercise by id"""
        exercise_to_delete=Exercise.query.get_or_404(id)
        exercise_to_delete.delete()
        return exercise_to_delete