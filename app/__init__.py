from flask import Flask, Blueprint, request, jsonify,render_template
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
from cryptography.fernet import Fernet

app = Flask(__name__)
CORS(app)

app.config.from_object('config')

#Initializing celery - Used to run long background tasks
from app.celery_creater import make_celery
celery = make_celery(app)

fernet = Fernet(str(app.config['FERNET_DASHBOARD_KEY']).encode())

jwt = JWTManager(app=app)

db = MongoEngine(app)

api = Blueprint('api',__name__,url_prefix='/api')

from app.user.controllers import user
api.register_blueprint(user)

app.register_blueprint(api)


@app.errorhandler(404)
@app.errorhandler(405)
def _handle_error(ex):
    if request.path.startswith('/api/'):
        return jsonify(error=str(ex)), ex.code
    else:
        return ex