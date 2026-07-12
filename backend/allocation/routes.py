from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from allocation.schema import AllocationSchema, TransferRequestSchema
from allocation.service import AllocationService
from utils.common import success_response, error_response
from database.models import Allocation

allocation_bp = Blueprint('allocation', __name__)

@allocation_bp.route('', methods=['POST'])
@jwt_required()
def allocate_asset():
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Permission denied", status_code=403)
        
    schema = AllocationSchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    allocation, error_msg = AllocationService.allocate_asset(data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg, status_code=409 if "available" in error_msg else 400)
    return success_response("Asset allocated successfully", schema.dump(allocation), status_code=201)

@allocation_bp.route('/<int:id>/return', methods=['PATCH'])
@jwt_required()
def return_asset(id):
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Permission denied", status_code=403)
        
    success, error_msg = AllocationService.return_asset(id, get_jwt_identity())
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Asset returned successfully")

@allocation_bp.route('/transfer-request', methods=['POST'])
@jwt_required()
def request_transfer():
    schema = TransferRequestSchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    transfer, error_msg = AllocationService.request_transfer(data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Transfer requested successfully", schema.dump(transfer), status_code=201)

@allocation_bp.route('/<int:id>/approve', methods=['PATCH'])
@jwt_required()
def approve_transfer(id):
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager', 'Department Head']:
        return error_response("Permission denied", status_code=403)
        
    success, error_msg = AllocationService.approve_transfer(id, get_jwt_identity(), action="APPROVED")
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Transfer request approved")

@allocation_bp.route('/<int:id>/reject', methods=['PATCH'])
@jwt_required()
def reject_transfer(id):
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager', 'Department Head']:
        return error_response("Permission denied", status_code=403)
        
    success, error_msg = AllocationService.approve_transfer(id, get_jwt_identity(), action="REJECTED")
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Transfer request rejected")

@allocation_bp.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    allocations = Allocation.query.order_by(Allocation.allocation_date.desc()).all()
    schema = AllocationSchema(many=True)
    return success_response("History retrieved", schema.dump(allocations))
