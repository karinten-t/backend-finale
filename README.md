### Features
1. User Registration & Login with JWT Authentication

2. View & Update Logged-in User Profile

3. Create, Read, and Delete Recipes (User-specific)

4. Secure Password Hashing (Flask-Bcrypt)

5. CORS Configuration for external frontend access

6. SQLite database (can easily switch to PostgreSQL or MySQL)

7. Error handling for 404 and 500

8. Clean MVC project structure

### Technologies Used
1. Python 3.8+

2. Flask

3. Flask SQLAlchemy

4. Flask JWT Extended

5. Flask CORS

6. Flask Migrate

7. Flask Bcrypt

8. SQLAlchemy Serializer

9. SQLite (default database)

### backendproject structure
│
├── app.py                 # Main application file
├── models.py              # SQLAlchemy models (User, Recipe)
├── config.py              # DB + Bcrypt initialization
├── migrations/            # Flask-Migrate auto-generated files
├── .venv/                 # Virtual environment (not pushed to Git)
├── requirements.txt       # Python dependencies
└── README.md              # This file

### GETTING STARTED
1. ## clone the project
git clone: https://github.com/your-username/recipes-api.git
cd backendproject

2. ## create and activate the virtual environment

python3 -m venv .venv
source .venv/bin/activate  # Mac/Linux
# OR
.venv\Scripts\activate     # Windows

3. ## install dependancies
pipenv install  -r requirements.txt

4. ## run migrations and create a db
flask db init
flask db migrate -m "Initial"
flask db upgrade

5. ## start server
flask run --host=0.0.0.0 --port=10000

### API ENDPOINTS
## Auth
1. POST /register – Register new user

2. POST /login – Authenticate and get JWT token
 Profile

3. GET /me – Get current user's profile (JWT required)

4. PUT /me – Update current user's username or email (JWT required)
Recipes

5. GET /recipes – Get all recipes for current user (JWT required)

6. POST /recipes – Create a new recipe (JWT required)

7. DELETE /recipes/<id> – Delete a recipe by ID (JWT required)

## example of use
# step 1: register
{
  "username": "travinne",
  "email": "trav@example.com",
  "password": "strongpassword123"
}

# step 2: login
{
  "email": "trav@example.com",
  "password": "strongpassword123"
}

# step 3: recipe
{
  "title": "chai",
  "ingredients": "water, tea leaves, sugar, milk",
  "instructions": "Boil the water add milk add tea leaves add sugar .",
  "category": "kenyan"
}

###  CORS CONFIGURATION
. The app is CORS-enabled to allow requests from your frontend (e.g., React on Render):
CORS(app,
     origins=["https://frontend-testfinal.onrender.com"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

### ERROR HANDLING
1. 404 Not Found – Returned when resource does not exist

2. 409 Conflict – Duplicate email or username

3. 401 Unauthorized – Invalid login credentials

4. 500 Internal Server Error – Unexpected server issue

