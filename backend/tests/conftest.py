import pytest
import os
from create_app import create_app
from extensions import db
from database.models import Role, User, Department, AssetCategory, Resource
from flask_jwt_extended import create_access_token

import pymysql
import urllib.parse
from config import Config

def create_test_db():
    db_username = Config.DB_USERNAME
    db_password = Config.DB_PASSWORD
    db_host = Config.DB_HOST
    db_port = int(Config.DB_PORT)
    
    conn = pymysql.connect(host=db_host, user=db_username, password=db_password, port=db_port)
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS assetflow_test")
    conn.commit()
    cursor.close()
    conn.close()

def drop_test_db():
    db_username = Config.DB_USERNAME
    db_password = Config.DB_PASSWORD
    db_host = Config.DB_HOST
    db_port = int(Config.DB_PORT)
    
    conn = pymysql.connect(host=db_host, user=db_username, password=db_password, port=db_port)
    cursor = conn.cursor()
    cursor.execute("DROP DATABASE IF EXISTS assetflow_test")
    conn.commit()
    cursor.close()
    conn.close()

@pytest.fixture(scope='session')
def app():
    """Create and configure a new app instance for each test session."""
    os.environ['FLASK_ENV'] = 'testing'
    
    create_test_db()
    
    app = create_app('testing')
    
    db_pwd_enc = urllib.parse.quote_plus(Config.DB_PASSWORD)
    test_db_uri = f"mysql+pymysql://{Config.DB_USERNAME}:{db_pwd_enc}@{Config.DB_HOST}:{Config.DB_PORT}/assetflow_test"
    
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": test_db_uri,
        "JWT_SECRET_KEY": "test_jwt_secret",
        "BCRYPT_LOG_ROUNDS": 4 # Make tests fast
    })

    with app.app_context():
        db.create_all()
        # Seed basic roles
        roles = ['Admin', 'Asset Manager', 'Department Head', 'Employee']
        for r in roles:
            db.session.add(Role(role_name=r))
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test cli runner for the app."""
    return app.test_cli_runner()

@pytest.fixture(scope='session')
def admin_user(app):
    """Creates an admin user and returns the user object and a valid JWT."""
    from database.models import Role, User
    from extensions import db, bcrypt
    
    with app.app_context():
        admin_role = Role.query.filter_by(role_name='Admin').first()
        user = User(
            employee_code='A001',
            first_name='Admin',
            last_name='User',
            email='admin@test.com',
            phone='1234567890',
            password_hash=bcrypt.generate_password_hash('Password@123').decode('utf-8'),
            role_id=admin_role.id,
            account_status='ACTIVE'
        )
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = create_access_token(identity=str(user.id), additional_claims={'role': 'Admin'})
        return {'user': user, 'token': token}

@pytest.fixture(scope='session')
def employee_user(app):
    """Creates a regular employee user."""
    from database.models import Role, User
    from extensions import db, bcrypt
    
    with app.app_context():
        emp_role = Role.query.filter_by(role_name='Employee').first()
        user = User(
            employee_code='E001',
            first_name='Emp',
            last_name='Loyee',
            email='emp@test.com',
            phone='0987654321',
            password_hash=bcrypt.generate_password_hash('Password@123').decode('utf-8'),
            role_id=emp_role.id,
            account_status='ACTIVE'
        )
        db.session.add(user)
        db.session.commit()
        
        token = create_access_token(identity=str(user.id), additional_claims={'role': 'Employee'})
        return {'user': user, 'token': token}
