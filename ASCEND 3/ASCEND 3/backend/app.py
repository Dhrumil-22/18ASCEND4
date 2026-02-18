from flask import Flask
from config import Config
from models import db, User
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'auth.login' 
login.login_view = 'auth.login' 
# CORS configuration - Allow all origins for development
CORS(app)

@login.request_loader
def load_user_from_request(request):
    # Check for Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            auth_token = auth_header.replace("Bearer ", "")
            user = User.verify_auth_token(auth_token)
            if user:
                return user
        except Exception as e:
            print(f"Token verification failed: {e}")
            return None
    return None

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
def index():
    return "ASCEND Backend is running!"

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

# Register Blueprints
# Import here to avoid circular dependencies if routes import app
from routes.auth import auth as auth_bp
from routes.api import api as api_bp

app.register_blueprint(auth_bp)
app.register_blueprint(api_bp)

if __name__ == '__main__':
    app.run(debug=True)
