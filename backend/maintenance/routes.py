from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from maintenance.schema import MaintenanceRequestSchema
from maintenance.service import MaintenanceService
from utils.common import success_response, error_response

maintenance_bp = Blueprint('maintenance', __name__)

@maintenance_bp.route('', methods=['GET'])
@jwt_required()
def get_requests():
    reqs = MaintenanceService.get_all_requests()
    schema = MaintenanceRequestSchema(many=True)
    return success_response("Maintenance requests retrieved", schema.dump(reqs))

@maintenance_bp.route('', methods=['POST'])
@jwt_required()
def raise_request():
    schema = MaintenanceRequestSchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    req, error_msg = MaintenanceService.raise_request(data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Maintenance request raised", schema.dump(req), status_code=201)

@maintenance_bp.route('/<int:id>/approve', methods=['PATCH'])
@jwt_required()
def approve_request(id):
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Permission denied", status_code=403)
        
    success, error_msg = MaintenanceService.approve_request(id, get_jwt_identity())
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Maintenance request approved")

@maintenance_bp.route('/<int:id>/reject', methods=['PATCH'])
@jwt_required()
def reject_request(id):
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Permission denied", status_code=403)
        
    success, error_msg = MaintenanceService.reject_request(id, get_jwt_identity())
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Maintenance request rejected")

@maintenance_bp.route('/<int:id>/assign', methods=['PATCH'])
@jwt_required()
def assign_technician(id):
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Permission denied", status_code=403)
        
    if 'assigned_to' not in request.json:
        return error_response("assigned_to is required")
        
    success, error_msg = MaintenanceService.assign_technician(id, request.json, get_jwt_identity())
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Technician assigned successfully")

@maintenance_bp.route('/<int:id>/start', methods=['PATCH'])
@jwt_required()
def start_maintenance(id):
    success, error_msg = MaintenanceService.start_maintenance(id, get_jwt_identity())
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Maintenance started")

@maintenance_bp.route('/<int:id>/resolve', methods=['PATCH'])
@jwt_required()
def resolve_maintenance(id):
    success, error_msg = MaintenanceService.resolve_maintenance(id, get_jwt_identity())
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Maintenance resolved successfully")
