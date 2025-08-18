from flask import Blueprint

# Main routes
main_bp = Blueprint('main', __name__)

# API routes  
api_bp = Blueprint('api', __name__)

# Favicon and static routes
favicon_bp = Blueprint('favicon', __name__)

# Import route handlers
from app.routes import main, api, favicon