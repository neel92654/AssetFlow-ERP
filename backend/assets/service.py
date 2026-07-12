import os
import uuid
from werkzeug.utils import secure_filename
from extensions import db
from database.models import Asset, AssetCategory, Department, AssetDocument
from activity_logs.service import ActivityLogService
from notifications.service import NotificationService

class AssetService:
    @staticmethod
    def get_all_assets(filters=None):
        query = Asset.query
        if filters:
            if 'category_id' in filters:
                query = query.filter_by(category_id=filters['category_id'])
            if 'department_id' in filters:
                query = query.filter_by(department_id=filters['department_id'])
            if 'status' in filters:
                query = query.filter_by(lifecycle_status=filters['status'])
        return query.all()

    @staticmethod
    def create_asset(data, current_user_id):
        # Validate unique serial number
        if Asset.query.filter_by(serial_number=data['serial_number']).first():
            return None, "Serial number already exists"
            
        category = AssetCategory.query.get(data['category_id'])
        if not category or category.status != 'ACTIVE':
            return None, "Invalid or inactive category"
            
        if data.get('department_id'):
            dept = Department.query.get(data['department_id'])
            if not dept or dept.status != 'ACTIVE':
                return None, "Invalid or inactive department"

        # Generate Asset Tag (e.g. AF000001)
        last_asset = Asset.query.order_by(Asset.id.desc()).first()
        new_id = (last_asset.id + 1) if last_asset else 1
        asset_tag = f"AF{new_id:06d}"
        
        # QR code generation placeholder
        qr_code = f"qr_{asset_tag}.png"

        asset = Asset(
            asset_tag=asset_tag,
            asset_name=data['asset_name'],
            serial_number=data['serial_number'],
            category_id=data['category_id'],
            department_id=data.get('department_id'),
            acquisition_date=data.get('acquisition_date'),
            acquisition_cost=data.get('acquisition_cost'),
            condition=data.get('condition', 'NEW'),
            lifecycle_status='AVAILABLE',
            location=data.get('location'),
            qr_code=qr_code,
            is_shared=data.get('is_shared', False),
            remarks=data.get('remarks'),
            created_by=current_user_id
        )
        
        db.session.add(asset)
        db.session.commit()
        
        ActivityLogService.log_activity(current_user_id, "Assets", "Register Asset", "Asset", asset.id)
        # Assuming we might want to notify asset managers in a real system
        
        return asset, None

    @staticmethod
    def get_asset_by_id(asset_id):
        return Asset.query.get(asset_id)

    @staticmethod
    def update_asset(asset_id, data, current_user_id):
        asset = Asset.query.get(asset_id)
        if not asset:
            return None, "Asset not found"
            
        if 'serial_number' in data and data['serial_number'] != asset.serial_number:
            if Asset.query.filter_by(serial_number=data['serial_number']).first():
                return None, "Serial number already exists"
            asset.serial_number = data['serial_number']
            
        if 'asset_name' in data:
            asset.asset_name = data['asset_name']
        if 'category_id' in data:
            asset.category_id = data['category_id']
        if 'department_id' in data:
            asset.department_id = data['department_id']
        if 'condition' in data:
            asset.condition = data['condition']
        if 'location' in data:
            asset.location = data['location']
        if 'is_shared' in data:
            asset.is_shared = data['is_shared']
        if 'remarks' in data:
            asset.remarks = data['remarks']
            
        asset.updated_by = current_user_id
        db.session.commit()
        
        ActivityLogService.log_activity(current_user_id, "Assets", "Update Asset", "Asset", asset.id)
        return asset, None

    @staticmethod
    def delete_asset(asset_id, current_user_id):
        asset = Asset.query.get(asset_id)
        if not asset:
            return False, "Asset not found"
            
        # Soft delete
        asset.status = 'INACTIVE'
        asset.updated_by = current_user_id
        db.session.commit()
        
        ActivityLogService.log_activity(current_user_id, "Assets", "Delete Asset", "Asset", asset.id)
        return True, None

    @staticmethod
    def upload_document(asset_id, file, document_type, current_user_id, upload_folder):
        asset = Asset.query.get(asset_id)
        if not asset:
            return None, "Asset not found"
            
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        if ext not in ['png', 'jpg', 'jpeg', 'pdf']:
            return None, "Invalid file format"
            
        unique_filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(upload_folder, 'assets', unique_filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file.save(filepath)
        
        doc = AssetDocument(
            asset_id=asset.id,
            document_name=filename,
            document_type=document_type,
            document_path=filepath,
            uploaded_by=current_user_id
        )
        db.session.add(doc)
        db.session.commit()
        
        ActivityLogService.log_activity(current_user_id, "Assets", "Upload Document", "AssetDocument", doc.id)
        return doc, None
