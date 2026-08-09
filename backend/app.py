from flask import Flask, render_template
from config import Config
from models.schema import db, User
from extensions import cache, jwt

def create_app():
    # 1. Initialize the Flask application
    # We tell Flask where to find our HTML and CSS files using relative paths
    app = Flask(__name__, 
                template_folder='../frontend/templates',
                static_folder='../frontend/static')
                
    # 2. Load configurations from config.py (like Database URI and Secret Keys)
    app.config.from_object(Config)

    # 3. Bind the extensions to our Flask app
    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    
    # 4. Register our API routes from api_routes.py
    # By using url_prefix='/api', all routes in that file will automatically start with /api
    from routes.api_routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    # 5. Database Setup (Runs every time the server starts)
    with app.app_context():
        # Create all database tables if they don't exist yet
        db.create_all()
        # Ensure there is always a default admin account
        create_default_admin()

    # 6. Serve the VueJS Frontend
    # This is a "catch-all" route. Any URL typed in the browser that isn't an API will serve our index.html.
    # Vue Router then takes over on the frontend to show the correct page.
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_vue_app(path):
        return render_template('index.html')

    return app

def create_default_admin():
    """Creates a default admin user if one doesn't exist."""
    admin = User.query.filter_by(role='admin').first()
    
    if not admin:
        # Create the admin profile
        new_admin = User(username='admin', role='admin', status='approved')
        new_admin.set_password('admin123') # Default password for the admin
        
        # Save to the database
        db.session.add(new_admin)
        db.session.commit()
        
        print("Default admin created (username: admin, password: admin123)")

# This block runs when you execute `python app.py`
if __name__ == '__main__':
    app = create_app()
    # debug=True automatically restarts the server when you make code changes
    app.run(debug=True)
