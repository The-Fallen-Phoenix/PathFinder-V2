from flask import Flask, render_template
from config import Config
from models.schema import db, User
from extensions import cache, jwt

def create_app():
    app = Flask(
        __name__, 
        template_folder='../frontend/templates',
        static_folder='../frontend/static'
    )
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    
    from routes.api_routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()
        create_default_admin()

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_vue_app(path):
        return render_template('index.html')

    return app

def create_default_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        new_admin = User(
            username='admin',
            email='24f3001829@ds.study.iitm.ac.in',
            role='admin',
            status='approved'
        )
        new_admin.set_password('admin123')
        db.session.add(new_admin)
        db.session.commit()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
