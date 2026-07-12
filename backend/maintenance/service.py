from extensions import db
from database.models import Asset, MaintenanceRequest, User
from activity_logs.service import ActivityLogService
from notifications.service import NotificationService

class MaintenanceService:
    @staticmethod
    def get_all_requests():
        return MaintenanceRequest.query.order_by(MaintenanceRequest.created_at.desc()).all()

    @staticmethod
    def raise_request(data, current_user_id):
        asset = Asset.query.get(data['asset_id'])
        if not asset:
            return None, "Asset not found"
            
        req = MaintenanceRequest(
            asset_id=asset.id,
            raised_by=current_user_id,
            priority=data.get('priority', 'MEDIUM'),
            issue_description=data['issue_description'],
            attachment=data.get('attachment')
        )
        
        try:
            db.session.add(req)
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Maintenance", "Raise Request", "MaintenanceRequest", req.id)
            # Notify Asset Manager
            NotificationService.send_notification(current_user_id, "Maintenance Raised", f"Request for {asset.asset_name} submitted successfully.")
            return req, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def approve_request(req_id, current_user_id):
        req = MaintenanceRequest.query.get(req_id)
        if not req or req.maintenance_status != 'PENDING':
            return False, "Invalid request or not pending"
            
        try:
            req.maintenance_status = 'APPROVED'
            
            # Update Asset Status to Under Maintenance
            asset = Asset.query.get(req.asset_id)
            asset.lifecycle_status = 'MAINTENANCE'
            
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Maintenance", "Approve Request", "MaintenanceRequest", req.id)
            NotificationService.send_notification(req.raised_by, "Maintenance Approved", "Your maintenance request has been approved.")
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def reject_request(req_id, current_user_id):
        req = MaintenanceRequest.query.get(req_id)
        if not req or req.maintenance_status != 'PENDING':
            return False, "Invalid request or not pending"
            
        try:
            req.maintenance_status = 'REJECTED'
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Maintenance", "Reject Request", "MaintenanceRequest", req.id)
            NotificationService.send_notification(req.raised_by, "Maintenance Rejected", "Your maintenance request has been rejected.")
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def assign_technician(req_id, data, current_user_id):
        req = MaintenanceRequest.query.get(req_id)
        if not req or req.maintenance_status != 'APPROVED':
            return False, "Request must be approved before assigning technician"
            
        technician = User.query.get(data['assigned_to'])
        if not technician:
            return False, "Invalid technician"
            
        try:
            req.assigned_to = technician.id
            req.maintenance_status = 'TECHNICIAN_ASSIGNED'
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Maintenance", "Assign Technician", "MaintenanceRequest", req.id)
            NotificationService.send_notification(technician.id, "Maintenance Assigned", "You have been assigned a new maintenance task.")
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def start_maintenance(req_id, current_user_id):
        req = MaintenanceRequest.query.get(req_id)
        if not req or req.maintenance_status != 'TECHNICIAN_ASSIGNED':
            return False, "Request must be assigned first"
            
        try:
            req.maintenance_status = 'IN_PROGRESS'
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Maintenance", "Start Maintenance", "MaintenanceRequest", req.id)
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def resolve_maintenance(req_id, current_user_id):
        req = MaintenanceRequest.query.get(req_id)
        if not req or req.maintenance_status != 'IN_PROGRESS':
            return False, "Request must be in progress"
            
        try:
            req.maintenance_status = 'RESOLVED'
            
            # Asset is available again
            asset = Asset.query.get(req.asset_id)
            asset.lifecycle_status = 'AVAILABLE'
            
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Maintenance", "Resolve Maintenance", "MaintenanceRequest", req.id)
            NotificationService.send_notification(req.raised_by, "Maintenance Resolved", f"Maintenance for {asset.asset_name} has been resolved.")
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
