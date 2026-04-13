from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from authlib.integrations.flask_client import OAuth

# ----------------------
# Flask Extensions
# ----------------------
db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
csrf = CSRFProtect()
oauth = OAuth()
