from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from audit.schema import AuditCycleSchema, AuditAssetSchema
from audit.service import AuditService
from utils.common import success_response, error_response

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/cycle', methods=['GET'])
@jwt_required()
def get_cycles():
    cycles = AuditService.get_audit_cycles()
    schema = AuditCycleSchema(many=True)
    return success_response("Audit cycles retrieved", schema.dump(cycles))

@audit_bp.route('/cycle', methods=['POST'])
@jwt_required()
def create_cycle():
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return error_response("Only Admin can create audit cycles", status_code=403)
        
    schema = AuditCycleSchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    cycle, error_msg = AuditService.create_audit_cycle(data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Audit cycle created", schema.dump(cycle), status_code=201)

@audit_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_asset():
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Permission denied", status_code=403)
        
    schema = AuditAssetSchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    audit_asset, error_msg = AuditService.verify_asset(data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Asset verified", schema.dump(audit_asset))

@audit_bp.route('/cycle/<int:id>/close', methods=['PATCH'])
@jwt_required()
def close_cycle(id):
    claims = get_jwt()
    if claims.get('role') != 'Admin':
        return error_response("Only Admin can close audit cycles", status_code=403)
        
    success, error_msg = AuditService.close_audit(id, get_jwt_identity())
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Audit cycle closed successfully")
