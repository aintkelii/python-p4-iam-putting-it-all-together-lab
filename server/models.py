from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from config import db
# db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    _password_hash = db.Column(db.String)
    image_url=db.Column(db.String)
    bio=db.Column(db.String)
    # Add other required columns
    
    recipes = db.relationship('Recipe', backref='user')
    
    @property
    def password(self):
        raise AttributeError('Password is not readable')
    
    @password.setter
    def password(self, password):
        self._password_hash = generate_password_hash(password)
    
    def authenticate(self, password):
        return check_password_hash(self._password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            # Include other fields
        }

class Recipe(db.Model):
    __tablename__ = 'recipes'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Add validations as needed