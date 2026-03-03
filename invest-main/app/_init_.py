from flask import Flask
from .config import Config
from .extensions import csrf

def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config.from_object(Config)

    csrf.init_app(app)

    from .main.routes import bp as main_bp
    from .auth.routes import bp as auth_bp
    from .events.routes import bp as events_bp
    from .admin.routes import bp as admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(admin_bp)

    return app