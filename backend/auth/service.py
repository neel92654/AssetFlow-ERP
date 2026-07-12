from datetime import datetime
from flask_jwt_extended import create_access_token, create_refresh_token
from extensions import db, bcrypt
from database.models import User, Role
from activity_logs.service import ActivityLogService
from notifications.service import NotificationService

class AuthService:
    @staticmethod
    def login(email, password):
        user = User.query.filter_by(email=email).first()
        
        if not user or not bcrypt.check_password_hash(user.password_hash, password):
            ActivityLogService.log_activity(
                user_id=user.id if user else None,
                module="Authentication",
                action="Failed Login",
                description=f"Failed login attempt for {email}"
            )
            return None, "Invalid email or password"
            
        if user.account_status != 'ACTIVE':
            return None, f"Account is {user.account_status.lower()}"
            
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate tokens
        additional_claims = {"role": user.role.role_name}
        access_token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=str(user.id))
        
        ActivityLogService.log_activity(
            user_id=user.id,
            module="Authentication",
            action="Login",
            description="User logged in successfully"
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user.id,
            "role": user.role.role_name
        }, None

    @staticmethod
    def signup(data):
        if data['password'] != data['confirm_password']:
            return None, "Passwords do not match"
            
        if User.query.filter_by(email=data['email']).first():
            return None, "Email is already registered"
            
        if User.query.filter_by(phone=data['phone']).first():
            return None, "Phone number is already registered"
            
        # Assign 'Employee' role by default
        employee_role = Role.query.filter_by(role_name='Employee').first()
        if not employee_role:
            return None, "Default role 'Employee' not found in system"
            
        # Auto-generate employee code (e.g., EMP000001)
        last_user = User.query.order_by(User.id.desc()).first()
        new_id = (last_user.id + 1) if last_user else 1
        employee_code = f"EMP{new_id:06d}"
        
        hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        
        new_user = User(
            employee_code=employee_code,
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            password_hash=hashed_pw,
            department_id=data['department_id'],
            role_id=employee_role.id,
            is_verified=True, # Auto-verify for now
            account_status='ACTIVE'
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            ActivityLogService.log_activity(
                user_id=new_user.id,
                module="Authentication",
                action="Signup",
                description="New employee account created"
            )
            
            NotificationService.send_notification(
                user_id=new_user.id,
                title="Welcome to AssetFlow ERP",
                message="Your account has been created successfully."
            )
            
            return new_user, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
