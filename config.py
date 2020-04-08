import os

from dotenv import load_dotenv

module_path = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file
load_dotenv(os.path.join(module_path, '.env'))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_FLASK_KEY') or 'dev-secret-key'
    API_KEY = os.environ.get('API_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(module_path, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BETA_CODE = os.environ.get('BETA_CODE') or 'test'


class ProductionConfig(Config):
    DB_NAME = os.environ.get('RDS_DB_NAME')
    USER = os.environ.get('RDS_USERNAME')
    PASSWORD = os.environ.get('RDS_PASSWORD')
    HOST = os.environ.get('RDS_HOSTNAME')
    PORT = os.environ.get('RDS_PORT')

    SQLALCHEMY_DATABASE_URI = f'postgres://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB_NAME}'


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
