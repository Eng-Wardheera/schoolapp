from datetime import datetime

import os
import textwrap
import traceback
from flask import Flask, flash, jsonify, redirect, render_template, url_for
from flask_cors import CORS
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from authlib.integrations.flask_client import OAuth
from flask_wtf import CSRFProtect
import pytz
from dotenv import load_dotenv





from app.utils import translate_to_somali

# Extensions - single instance only!
db = SQLAlchemy()
migrate = Migrate() # 2. Bilow

mail = Mail()  # Create Mail instance
login_manager = LoginManager()

 # Enable CSRF globally
csrf = CSRFProtect()

# Global Variables: 1
# Upload config & model
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Global Variables: 2
UPLOAD_FOLDER = "static/backend/uploads"


MAX_RETRIES = 5  # try 5 times to get a unique journey_code

 # ----- Timezone -----
  
# Google OAuth


oauth = OAuth()  # global instance
google = None    # placeholder
githup = None

EAT = pytz.timezone("Africa/Nairobi")

def now_eat():
    """Return current datetime in Nairobi timezone"""
    return datetime.now(EAT)

# Load environment variables from .env file
load_dotenv()


#-------------------------------------------------------------
# Function: 29 create_app()
# Ujeeddo: Diyaarinta Flask App iyadoo la isku xiro configs, extensions, 
# filters, blueprints, errors, iyo security
#-------------------------------------------------------------
def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    # Secure Secret Key
    app.secret_key = os.getenv('SECRET_KEY', 'XWt7819618552904Sm32Mxx2102dklF')
   
    csrf.init_app(app)  # ✅ INIT

    # Configuration
    # Ka soo akhri link-ga Neon ee aad Vercel gelisay
    database_url = os.getenv('DATABASE_URL')

    if database_url:
        # Tani waxay saxaysaa haddii link-gu ku bilaawdo postgres:// (oo Vercel badanaa keento)
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Haddii link-ga la waayo, wuxuu isticmaalayaa SQLite local ahaan
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fallback.db'

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

   
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    # create_app() dhexdiisa
    app.config['DEBUG'] = False
    app.config['PROPAGATE_EXCEPTIONS'] = False

     # Configure Flask to use Gmail's SMTP server
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587  # TLS port
    app.config['MAIL_USERNAME'] = 'liilove668@gmail.com'  # Your Gmail address
    app.config['MAIL_PASSWORD'] = 'dvml ylyo ivek xrab'  # Your Gmail password or App password
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
   

    # Mailtrap Emails per month: 500 emails.
    # Emails per month: Ranges from 5,000 to 50,000 or more emails per month (depending on the plan).
    # app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
    # app.config['MAIL_PORT'] = 2525
    # app.config['MAIL_USERNAME'] = '7b42cad38f6faa'
    # app.config['MAIL_PASSWORD'] = '822aaeb2f01426'
    # app.config['MAIL_USE_TLS'] = True
    # app.config['MAIL_USE_SSL'] = False
 
 

  
    # Enable CORS for your frontend origin
     # Ka akhri port environment
    port = int(os.getenv("PORT", 7000))
    frontend_origin = os.getenv("FRONTEND_ORIGIN", f"http://127.0.0.1:{port}")

    # Dynamic CORS origin
    CORS(app, resources={r"/*": {"origins": frontend_origin}})

    # OAuth init
    # OAuth init
    oauth.init_app(app)
    global google
    google = oauth.register(
        name='google',
         client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET"),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    # OAuth setup
    oauth.init_app(app)
    global github
    github = oauth.register(
        name='github',
        client_id=os.getenv("GITHUB_CLIENT_ID"),
        client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )

  

  
    @app.template_filter('getattr')
    def getattr_filter(obj, name):
        return getattr(obj, name, None)

    # Import and register your routes (assuming routes.py)
   
    @app.template_filter('translate')
    def translate_filter(text):
        return translate_to_somali(text)

    # Initialize extensions
    db.init_app(app)
    mail.init_app(app)  # Make sure you call init_app on the mail object
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    # Register blueprints
   

    # 27 Filter: Format datetime for input[type="datetime-local"]
    @app.template_filter('datetimeformat_input')
    def datetimeformat_input(value):
        if not value:
            return ''
        return value.strftime('%Y-%m-%dT%H:%M')
    
    # 28 Example: in filters.py (Jinja filter)
    @app.template_filter('datetimeformat_input_dateOnly')
    def datetimeformat_input_dateOnly(value):
        return value.strftime('%Y-%m-%d')  # only date


    # Import models and blueprints



    from app.modal import User
    from .routes import bp 
    from .sub_route import zp 
    
    app.register_blueprint(bp) # ,url_prefix='/main'
    app.register_blueprint(zp) # ,url_prefix='/sub'  flask db init, flask db migrate -m "added academic_year_id to exam_subjects", flask db upgrade
    migrate.init_app(app, db)

    # Oggolow dhammaan domains ama ku xadid domain gaar ah:
    

    @app.errorhandler(404)
    def not_found_error(error):
        from app.modal import SettingsData
        # Si toos ah u soo saar Settings-ka si bogga 404 uusan u dhiman
        site_settings = SettingsData.query.first() 
        return render_template("backend/errors/auth-404-creative.html", settings=site_settings), 404


    # ✅ Add template filter to app
    @app.template_filter('time_since')
    def time_since_filter(seconds):
        """Convert seconds to human-readable time like '5 minutes ago'."""
        seconds = int(seconds)
        intervals = (
            ('month', 2592000),  # 30*24*60*60
            ('week', 604800),    # 7*24*60*60
            ('day', 86400),
            ('hour', 3600),
            ('minute', 60),
            ('second', 1),
        )

        for name, count in intervals:
            value = seconds // count
            if value:
                return f"{value} {name}{'s' if value > 1 else ''} ago"
        return "just now"
    
    # 30 Custom 500 handler
    @app.errorhandler(500)
    def internal_error(error):
        from flask import request, render_template
        from app import db # Hubi in aad soo dhowaysato db
        
        # Haddii qalad database ku dhaco, dib u celi (rollback)
        db.session.rollback()

        current_time = datetime.now(EAT).strftime("%Y-%m-%d %H:%M:%S")
        request_url = request.url
        user_info = current_user.username if current_user.is_authenticated else "Guest"

        error_message = str(error)
        # Traceback waxaan u baahanahay oo kaliya haddii aan nahay Debug Mode
        error_trace = traceback.format_exc() if app.debug else None

        # Soo qaado settings-ka sidii 404-ta
        from app.modal import SettingsData
        site_settings = SettingsData.query.first()

        return render_template(
            "backend/errors/auth-500-creative.html", # Magaca template-kaaga
            settings=site_settings,
            time=current_time,
            user=user_info,
            url=request_url,
            message=error_message,
            trace=error_trace,
            debug=app.debug
        ), 500

 

    @login_manager.unauthorized_handler
    def unauthorized():
        flash("Fadlan marka hore soo gal nidaamka.")
        return redirect(url_for('main.login')) # 'login' waa magaca function-ka login-kaaga

    @app.context_processor
    def inject_settings():
        from app.modal import SettingsData   # ✔️ HALKAN GELI
        return dict(settings=SettingsData.query.first())
        
    # 31 Login user loader
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
