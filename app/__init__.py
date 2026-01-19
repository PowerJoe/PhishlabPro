from flask import Flask, render_template, redirect, url_for
from flask_login import LoginManager, current_user
from flask_socketio import SocketIO
from config import config
from app.models import db, User
import os

login_manager = LoginManager()
socketio = SocketIO()

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    from dotenv import load_dotenv
    load_dotenv()
    
    app.config['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', app.config['SECRET_KEY'])
    
    db.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)
    
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from app.auth.routes import auth_bp
    from app.admin import admin_bp
    from app.campaigns import campaigns_bp
    from app.evilginx import evilginx_bp
    from app.email_gen import email_gen_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(campaigns_bp, url_prefix='/campaigns')
    app.register_blueprint(evilginx_bp, url_prefix='/evilginx')
    app.register_blueprint(email_gen_bp, url_prefix='/email-gen')
    
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return render_template('dashboard.html')
        return render_template('landing.html')
    
    with app.app_context():
        db.create_all()
    
    return app
