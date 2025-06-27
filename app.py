from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token, get_jwt_identity
)
from sqlalchemy.exc import IntegrityError
from config import db
from models import User, Recipe
from flask_cors import CORS
from datetime import timedelta
import os

app = Flask(__name__)

# ✅ Proper global CORS configuration
CORS(app,
     origins=["https://frontend-testfinal.onrender.com"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# ================== CONFIG ==================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_COOKIE_CSRF_PROTECT'] = False
app.secret_key = 'shhh-very-secret'

# ================== INIT ==================
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# ================= AUTH ROUTES =================
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"message": "Email and password required"}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and user.authenticate(data['password']):
        token = create_access_token(identity=user.id)
        return jsonify({
            "user": user.to_dict(rules=('-_password_hash',)),
            "access_token": token
        }), 200
    return jsonify({"message": "Invalid credentials"}), 401

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({"message": "Missing required fields"}), 400

    try:
        new_user = User(
            username=data['username'],
            email=data['email']
        )
        new_user.password_hash = data['password']
        db.session.add(new_user)
        db.session.commit()
        return jsonify({
            "user": new_user.to_dict(rules=('-_password_hash',)),
            "message": "Registration successful"
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Username or email already exists"}), 409

# ================= PROFILE ROUTES =================
@app.route('/me', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify(user.to_dict(rules=('-_password_hash',))), 200

@app.route('/me', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404

    data = request.get_json()
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']

    try:
        db.session.commit()
        return jsonify({
            "user": user.to_dict(rules=('-_password_hash',)),
            "message": "Profile updated"
        }), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Username or email already exists"}), 409

# ================= RECIPE ROUTES =================
@app.route('/recipes', methods=['GET'])
@jwt_required()
def get_all_recipes():
    user_id = get_jwt_identity()
    recipes = Recipe.query.filter_by(user_id=user_id).all()
    return jsonify([recipe.to_dict() for recipe in recipes]), 200

@app.route('/recipes', methods=['POST'])
@jwt_required()
def create_recipe():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'title' not in data or 'ingredients' not in data or 'instructions' not in data:
        return jsonify({"message": "Missing required fields"}), 400

    recipe = Recipe(
        title=data['title'],
        description=data.get('description', ''),
        ingredients=data['ingredients'],
        instructions=data['instructions'],
        category=data.get('category', ''),
        user_id=user_id
    )

    db.session.add(recipe)
    db.session.commit()
    return jsonify(recipe.to_dict()), 201

@app.route('/recipes/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_recipe(id):
    user_id = get_jwt_identity()
    recipe = Recipe.query.filter_by(id=id, user_id=user_id).first()

    if not recipe:
        return jsonify({"message": "Recipe not found"}), 404

    db.session.delete(recipe)
    db.session.commit()
    return jsonify({"message": "Recipe deleted"}), 200

# ================= ERROR HANDLERS =================
@app.errorhandler(404)
def not_found(e):
    return jsonify({"message": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"message": "Internal server error"}), 500

# ================= RUN =================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
