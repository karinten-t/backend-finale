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

# Configs (unchanged)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'
app.secret_key = 'shhh-very-secret'

# Init (unchanged)
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# ----------- AUTH ROUTES (Fixed) -----------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get('email')).first()  # Changed to email
    if user and user.authenticate(data.get('password')):
        token = create_access_token(identity=user.id)
        return jsonify({
            "user": user.to_dict(rules=('-_password_hash',)),
            "access_token": token  # Consistent key name
        }), 200
    return jsonify({"message": "Invalid credentials"}), 401  # Error key standardized

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
        return jsonify({
            "user": new_user.to_dict(rules=('-_password_hash',)),
            "message": "Registration successful"  # Added success message
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Username or email already exists"}), 409  # Standardized key

# ... [Keep all other routes unchanged] ...

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))