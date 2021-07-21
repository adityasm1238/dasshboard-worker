from dotenv import load_dotenv
import os
load_dotenv()

# Statement for enabling the development environment
ENV = os.environ['FLASK_ENV']
DEBUG = False
if os.environ['FLASK_ENV'] == 'development':
    DEBUG = True

# Define the application directory

BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

MONGODB_SETTINGS = {
    'host': os.environ['MONGO_URI'],
    'connect':False
}

JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']

THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = os.environ['CSRF_SESSION_KEY']

# Secret key for signing cookies
SECRET_KEY = os.environ['SECRET']

CELERY_BROKER_URL=os.environ['REDIS_URL']
CELERY_RESULT_BACKEND=os.environ['REDIS_URL']

FERNET_DASHBOARD_KEY = os.environ['FERNET_KEY']