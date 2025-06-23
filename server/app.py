from flask import Flask, request, session, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from models import db, User, Recipe
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'development-key')
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)

class Signup(Resource):
    def post(self):
        data = request.get_json()
        
        try:
            user = User(
                username=data['username'],
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            user.password_hash = data['password']
            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id
            
            return user.to_dict(), 201
        except Exception as e:
            return {'errors': [str(e)]}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return {'error': 'Unauthorized'}, 401
            
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Unauthorized'}, 401
            
        return user.to_dict(), 200

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data['username']).first()
        
        if user and user.authenticate(data['password']):
            session['user_id'] = user.id
            return user.to_dict(), 200
        else:
            return {'error': 'Invalid username or password'}, 401

class Logout(Resource):
    def delete(self):
        if 'user_id' in session:
            session.pop('user_id')
            return {}, 204
        return {'error': 'Unauthorized'}, 401

class RecipeIndex(Resource):
    def get(self):
        if 'user_id' not in session:
            return {'error': 'Unauthorized'}, 401
            
        recipes = [recipe.to_dict() for recipe in Recipe.query.all()]
        return recipes, 200

    def post(self):
        if 'user_id' not in session:
            return {'error': 'Unauthorized'}, 401
            
        data = request.get_json()
        try:
            recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data['minutes_to_complete'],
                user_id=session['user_id']
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except Exception as e:
            return {'errors': [str(e)]}, 422# In User model
def to_dict(self):
    return {
        'id': self.id,
        'username': self.username,
        'image_url': self.image_url,
        'bio': self.bio
    }

# In Recipe model
def to_dict(self):
    return {
        'id': self.id,
        'title': self.title,
        'instructions': self.instructions,
        'minutes_to_complete': self.minutes_to_complete,
        'user': self.user.to_dict()
    }
        

api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(RecipeIndex, '/recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)