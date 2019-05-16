from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from flaskext.markdown import Markdown

UPLOAD_FOLDER = os.path.abspath(os.path.dirname(__file__)) + '/static/images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
Markdown(app)
from blog import models, auth, display


app.register_blueprint(auth.bp, url_prefix='/')
app.register_blueprint(display.main, url_prefix='/')
app.register_blueprint(display.categories, url_prefix='/<category>')
