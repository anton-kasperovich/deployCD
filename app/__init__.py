from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_oauthlib.client import OAuth
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.debug = True
app.config.from_object('config')
db = SQLAlchemy(app)
login_manager = LoginManager(app)
bootstrap = Bootstrap(app)
toolbar = DebugToolbarExtension(app)

oauth = OAuth(app)
gitlab = oauth.remote_app('gitlab', app_key='GITLAB')
oauth.init_app(app)

from app import views, models