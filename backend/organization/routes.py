from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from organization.schema import DepartmentSchema, CategorySchema, EmployeeUpdateSchema
from organization.service import OrganizationService
from utils.common import success_response, error_response
from auth.schema import UserProfileSchema

org_bp = Blueprint('organization', __name__)

# --- Departments ---
@org_bp.route('/departments', methods=['GET'])
def get_departments():
    depts = OrganizationService.get_all_departments()
    schema = DepartmentSchema(many=True)
    return success_response("Departments retrieved successfully", schema.dump(depts))

@org_bp.route('/departments', methods=['POST'])
@jwt_required()
def create_department():
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return error_response("Only Admin can create departments", status_code=403)
        
    schema = DepartmentSchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    dept, error_msg = OrganizationService.create_department(data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg)
    return success_response("Department created successfully", schema.dump(dept), status_code=201)

@org_bp.route('/departments/<int:id>', methods=['PUT'])
@jwt_required()
def update_department(id):
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return error_response("Only Admin can update departments", status_code=403)
        
    schema = DepartmentSchema(partial=True)
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    dept, error_msg = OrganizationService.update_department(id, data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg, status_code=400 if "unique" in error_msg else 404)
    return success_response("Department updated successfully", schema.dump(dept))

@org_bp.route('/departments/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_department(id):
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return error_response("Only Admin can delete departments", status_code=403)
        
    success, error_msg = OrganizationService.delete_department(id, get_jwt_identity())
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Department deactivated successfully")

# --- Categories ---
@org_bp.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    categories = OrganizationService.get_all_categories()
    schema = CategorySchema(many=True)
    return success_response("Categories retrieved successfully", schema.dump(categories))

@org_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Permission denied", status_code=403)
        
    schema = CategorySchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    category, error_msg = OrganizationService.create_category(data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg)
    return success_response("Category created successfully", schema.dump(category), status_code=201)

@org_bp.route('/categories/<int:id>', methods=['PUT'])
@jwt_required()
def update_category(id):
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Permission denied", status_code=403)
        
    schema = CategorySchema(partial=True)
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    category, error_msg = OrganizationService.update_category(id, data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Category updated successfully", schema.dump(category))

@org_bp.route('/categories/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_category(id):
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Permission denied", status_code=403)
        
    success, error_msg = OrganizationService.delete_category(id, get_jwt_identity())
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Category deactivated successfully")

# --- Employees ---
@org_bp.route('/employees', methods=['GET'])
@jwt_required()
def get_employees():
    employees = OrganizationService.get_all_employees()
    schema = UserProfileSchema(many=True)
    return success_response("Employees retrieved successfully", schema.dump(employees))

@org_bp.route('/employees/<int:id>', methods=['PUT'])
@jwt_required()
def update_employee(id):
    claims = get_jwt()
    role = claims.get('role')
    
    schema = EmployeeUpdateSchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    emp, error_msg = OrganizationService.update_employee(id, data, get_jwt_identity(), role)
    
    if error_msg:
        return error_response(error_msg, status_code=403 if "Only Admin" in error_msg else 400)
        
    user_schema = UserProfileSchema()
    return success_response("Employee updated successfully", user_schema.dump(emp))
