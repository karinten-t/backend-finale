from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from sqlalchemy.exc import IntegrityError
from config import db
from models import User, Recipe
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app,
     origins=[
         "http://localhost:3000",
         "https://frontend-testfinal.onrender.com"
     ],
     supports_credentials=True)

# Configs
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.secret_key = 'shhh-very-secret'

# Init
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# ----------- AUTH ROUTES -----------

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    try:
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        new_user.password_hash = data['password']
        db.session.add(new_user)
        db.session.commit()
        return jsonify(user=new_user.to_dict(rules=('-_password_hash',))), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Username or email already exists."), 409

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user and user.authenticate(data.get('password')):
        token = create_access_token(identity=user.id)
        return jsonify(user=user.to_dict(rules=('-_password_hash',)), access_token=token), 200
    return jsonify(error="Invalid credentials."), 401

# ----------- USER PROFILE -----------

@app.route('/me', methods=['GET'])
@jwt_required()
def me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(user.to_dict(rules=('-_password_hash',))), 200

@app.route('/me', methods=['PUT'])
@jwt_required()
def update_me():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify(error="User not found"), 404

    data = request.get_json()
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']

    try:
        db.session.commit()
        return jsonify(user=user.to_dict(rules=('-_password_hash',))), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Username or email already exists."), 409

# ----------- RECIPE ROUTES -----------

@app.route('/recipes', methods=['GET'])
@jwt_required()
def get_all_recipes():
    recipes = Recipe.query.all()
    return jsonify([r.to_dict() for r in recipes]), 200

@app.route('/recipes/<int:id>', methods=['GET'])
@jwt_required()
def get_recipe(id):
    recipe = Recipe.query.get(id)
    if recipe:
        return jsonify(recipe.to_dict()), 200
    return jsonify(error="Recipe not found"), 404

@app.route('/recipes', methods=['POST'])
@jwt_required()
def create_recipe():
    data = request.get_json()
    current_user_id = get_jwt_identity()
    recipe = Recipe(
        title=data['title'],
        description=data.get('description', ''),
        ingredients=data['ingredients'],
        instructions=data['instructions'],
        category=data.get('category', ''),
        user_id=current_user_id
    )
    db.session.add(recipe)
    db.session.commit()
    return jsonify(recipe.to_dict()), 201

@app.route('/recipes/<int:id>', methods=['PATCH'])
@jwt_required()
def update_recipe(id):
    data = request.get_json()
    recipe = Recipe.query.get(id)
    current_user_id = get_jwt_identity()

    if not recipe:
        return jsonify(error="Recipe not found"), 404
    if recipe.user_id != current_user_id:
        return jsonify(error="Not authorized to update this recipe"), 403

    for key in ['title', 'description', 'ingredients', 'instructions', 'category']:
        if key in data:
            setattr(recipe, key, data[key])

    db.session.commit()
    return jsonify(recipe.to_dict()), 200

@app.route('/recipes/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(id):
    recipe = Recipe.query.get(id)
    current_user_id = get_jwt_identity()

    if not recipe:
        return jsonify(error="Recipe not found"), 404
    if recipe.user_id != current_user_id:
        return jsonify(error="Not authorized to delete this recipe"), 403

    db.session.delete(recipe)
    db.session.commit()
    return jsonify(message="Recipe deleted"), 200

# ----------- ENTRY POINT -----------

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
