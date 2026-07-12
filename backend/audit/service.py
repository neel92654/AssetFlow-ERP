from datetime import datetime
from extensions import db
from database.models import AuditCycle, AuditAsset, Asset
from activity_logs.service import ActivityLogService
from notifications.service import NotificationService

class AuditService:
    @staticmethod
    def get_audit_cycles():
        return AuditCycle.query.order_by(AuditCycle.start_date.desc()).all()

    @staticmethod
    def create_audit_cycle(data, current_user_id):
        cycle = AuditCycle(
            audit_name=data['audit_name'],
            department_id=data.get('department_id'),
            location=data.get('location'),
            start_date=data['start_date'],
            end_date=data['end_date']
        )
        try:
            db.session.add(cycle)
            db.session.commit()
            
            # Fetch all matching assets to add to audit_assets table
            query = Asset.query.filter_by(lifecycle_status='AVAILABLE') # Or other rules based on business logic
            if data.get('department_id'):
                query = query.filter_by(department_id=data['department_id'])
            if data.get('location'):
                query = query.filter_by(location=data['location'])
                
            assets_to_audit = query.all()
            for asset in assets_to_audit:
                audit_asset = AuditAsset(
                    audit_cycle_id=cycle.id,
                    asset_id=asset.id
                )
                db.session.add(audit_asset)
                
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Audit", "Create Audit", "AuditCycle", cycle.id)
            return cycle, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def verify_asset(data, current_user_id):
        audit_asset = AuditAsset.query.filter_by(audit_cycle_id=data['audit_cycle_id'], asset_id=data['asset_id']).first()
        if not audit_asset:
            return None, "Asset not found in this audit cycle"
            
        try:
            audit_asset.verification_status = data['verification_status']
            audit_asset.remarks = data.get('remarks')
            audit_asset.verified_by = current_user_id
            audit_asset.verified_at = datetime.utcnow()
            
            # If audit cycle is OPEN, mark it IN_PROGRESS
            cycle = AuditCycle.query.get(data['audit_cycle_id'])
            if cycle.audit_status == 'OPEN':
                cycle.audit_status = 'IN_PROGRESS'
                
            db.session.commit()
            ActivityLogService.log_activity(current_user_id, "Audit", "Verify Asset", "AuditAsset", audit_asset.id)
            return audit_asset, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def close_audit(cycle_id, current_user_id):
        cycle = AuditCycle.query.get(cycle_id)
        if not cycle or cycle.audit_status == 'CLOSED':
            return False, "Invalid audit cycle or already closed"
            
        try:
            cycle.audit_status = 'CLOSED'
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Audit", "Close Audit", "AuditCycle", cycle.id)
            # Notify Admin
            NotificationService.send_notification(current_user_id, "Audit Closed", f"Audit {cycle.audit_name} has been closed.")
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)
