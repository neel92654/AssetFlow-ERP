from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from auth.schema import LoginSchema, SignupSchema, UserProfileSchema
from auth.service import AuthService
from database.models import User
from utils.common import success_response, error_response
from activity_logs.service import ActivityLogService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    schema = LoginSchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    
    result, error_msg = AuthService.login(data['email'], data['password'])
    if error_msg:
        return error_response(error_msg, status_code=401)
        
    return success_response("Login successful", result)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    schema = SignupSchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    user, error_msg = AuthService.signup(data)
    
    if error_msg:
        return error_response(error_msg)
        
    return success_response("User registered successfully", data={"user_id": user.id}, status_code=201)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    current_user_id = get_jwt_identity()
    ActivityLogService.log_activity(
        user_id=current_user_id,
        module="Authentication",
        action="Logout",
        description="User logged out successfully"
    )
    # To fully implement logout, we'd add the token to a blocklist
    return success_response("Logged out successfully")

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return error_response("User not found", status_code=404)
        
    schema = UserProfileSchema()
    return success_response("Profile retrieved successfully", schema.dump(user))

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user_id = get_jwt_identity()
    from flask_jwt_extended import create_access_token
    user = User.query.get(current_user_id)
    if not user or user.account_status != 'ACTIVE':
        return error_response("User inactive or not found", status_code=401)
        
    new_access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role.role_name})
    return success_response("Token refreshed successfully", {"access_token": new_access_token})
