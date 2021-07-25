from .account import account_bp

def init_app(app):
    app.register_blueprint(account_bp)
