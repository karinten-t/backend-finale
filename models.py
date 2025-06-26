from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates, relationship
from sqlalchemy.ext.hybrid import hybrid_property
from config import db, bcrypt  

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    serialize_rules = ('-recipes.user', '-_password_hash',)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)

    recipes = relationship('Recipe', backref='user', cascade='all, delete')

    @validates('email')
    def validate_email(self, key, email):
        if '@' not in email or '.' not in email:
            raise ValueError("Please provide a valid email address.")
        return email

    @hybrid_property
    def password_hash(self):
        raise AttributeError("Password hash is write-only.")

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password.encode()).decode()

    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode())


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'

    serialize_rules = ('-user.recipes',)

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    ingredients = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    category = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
