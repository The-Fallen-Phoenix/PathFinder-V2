from flask import Flask, render_template
from flask_jwt_extended import JWTManager
from flask_caching import Cache
from config import Config
from models import db, User
from routes import api_bp

cache = Cache()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    
    app.register_blueprint(api_bp, url_prefix='/api')

    # Initialize the database and create admin
    with app.app_context():
        db.create_all()
        create_default_admin()

    # Serve the VueJS single page application
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_vue_app(path):
        return render_template('index.html')

    return app

def create_default_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        new_admin = User(username='admin', role='admin', status='approved')
        new_admin.set_password('admin123') # Default password
        db.session.add(new_admin)
        db.session.commit()
        print("Default admin created (username: admin, password: admin123)")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
