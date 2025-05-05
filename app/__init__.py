from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from config import Config
from .models.base import db, init_db
#from .routes import init_routes
from .api import api_bp

migrate = Migrate()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    init_db(app)
    migrate.init_app(app, db)
    CORS(app)
    limiter.init_app(app)
    jwt.init_app(app)

    # Exempt OPTIONS requests from rate limiting
    @app.before_request
    def skip_options_requests():
        from flask import request
        if request.method == 'OPTIONS':
            # Disable rate limiting for OPTIONS requests
            setattr(request, 'limiter_exempt', True)

    # Register API blueprint only
    app.register_blueprint(api_bp, url_prefix='/api')
    # init_routes(app)  # Removed to avoid redundant blueprint registrations

    return app
