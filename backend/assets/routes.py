from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from assets.schema import AssetSchema, AssetDocumentSchema
from assets.service import AssetService
from utils.common import success_response, error_response

assets_bp = Blueprint('assets', __name__)

@assets_bp.route('', methods=['GET'])
@jwt_required()
def get_assets():
    filters = request.args.to_dict()
    assets = AssetService.get_all_assets(filters)
    schema = AssetSchema(many=True)
    return success_response("Assets retrieved successfully", schema.dump(assets))

@assets_bp.route('', methods=['POST'])
@jwt_required()
def register_asset():
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Only Admin or Asset Manager can register assets", status_code=403)
        
    schema = AssetSchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    asset, error_msg = AssetService.create_asset(data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Asset registered successfully", schema.dump(asset), status_code=201)

@assets_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_asset(id):
    asset = AssetService.get_asset_by_id(id)
    if not asset:
        return error_response("Asset not found", status_code=404)
        
    schema = AssetSchema()
    return success_response("Asset details retrieved successfully", schema.dump(asset))

@assets_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_asset(id):
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Permission denied", status_code=403)
        
    schema = AssetSchema(partial=True)
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    asset, error_msg = AssetService.update_asset(id, data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Asset updated successfully", schema.dump(asset))

@assets_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_asset(id):
    claims = get_jwt()
    if claims.get('role') not in ['Admin', 'Asset Manager']:
        return error_response("Permission denied", status_code=403)
        
    success, error_msg = AssetService.delete_asset(id, get_jwt_identity())
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Asset deactivated successfully")

@assets_bp.route('/<int:id>/documents', methods=['POST'])
@jwt_required()
def upload_document(id):
    if 'file' not in request.files:
        return error_response("No file provided")
        
    file = request.files['file']
    if file.filename == '':
        return error_response("No selected file")
        
    doc_type = request.form.get('document_type', 'Other')
    
    doc, error_msg = AssetService.upload_document(
        asset_id=id, 
        file=file, 
        document_type=doc_type, 
        current_user_id=get_jwt_identity(),
        upload_folder=current_app.config['UPLOAD_FOLDER']
    )
    
    if error_msg:
        return error_response(error_msg, status_code=400)
        
    schema = AssetDocumentSchema()
    return success_response("Document uploaded successfully", schema.dump(doc), status_code=201)
