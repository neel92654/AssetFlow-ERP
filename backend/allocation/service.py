from datetime import datetime
from extensions import db
from database.models import Asset, User, Department, Allocation, TransferRequest
from activity_logs.service import ActivityLogService
from notifications.service import NotificationService

class AllocationService:
    @staticmethod
    def allocate_asset(data, current_user_id):
        asset = Asset.query.get(data['asset_id'])
        if not asset or asset.lifecycle_status != 'AVAILABLE':
            return None, "Asset is not available for allocation"
            
        employee = User.query.get(data['employee_id'])
        if not employee or employee.account_status != 'ACTIVE':
            return None, "Invalid or inactive employee"
            
        dept = Department.query.get(data['department_id'])
        if not dept or dept.status != 'ACTIVE':
            return None, "Invalid or inactive department"

        try:
            allocation = Allocation(
                asset_id=asset.id,
                employee_id=employee.id,
                department_id=dept.id,
                expected_return_date=data.get('expected_return_date')
            )
            
            asset.lifecycle_status = 'ALLOCATED'
            
            db.session.add(allocation)
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Allocation", "Allocate Asset", "Allocation", allocation.id)
            NotificationService.send_notification(employee.id, "Asset Allocated", f"Asset {asset.asset_name} has been allocated to you.")
            
            return allocation, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def return_asset(allocation_id, current_user_id):
        allocation = Allocation.query.get(allocation_id)
        if not allocation or allocation.allocation_status != 'ALLOCATED':
            return False, "Invalid allocation record or already returned"
            
        try:
            allocation.allocation_status = 'RETURNED'
            allocation.return_date = datetime.utcnow()
            
            asset = Asset.query.get(allocation.asset_id)
            asset.lifecycle_status = 'AVAILABLE'
            
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Allocation", "Return Asset", "Allocation", allocation.id)
            NotificationService.send_notification(allocation.employee_id, "Asset Returned", f"Asset {asset.asset_name} return confirmed.")
            
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def request_transfer(data, current_user_id):
        allocation = Allocation.query.get(data['allocation_id'])
        if not allocation or allocation.allocation_status != 'ALLOCATED':
            return None, "Invalid allocation record"
            
        # Optional: verify if requester is the current owner
        if allocation.employee_id != current_user_id:
            # Check if admin/asset manager (handled in routes)
            pass
            
        transfer = TransferRequest(
            allocation_id=allocation.id,
            requested_by=current_user_id,
            reason=data.get('reason')
        )
        
        db.session.add(transfer)
        db.session.commit()
        
        ActivityLogService.log_activity(current_user_id, "Allocation", "Transfer Requested", "TransferRequest", transfer.id)
        return transfer, None

    @staticmethod
    def approve_transfer(transfer_id, current_user_id, action="APPROVED"):
        transfer = TransferRequest.query.get(transfer_id)
        if not transfer or transfer.transfer_status != 'REQUESTED':
            return False, "Invalid transfer request or already processed"
            
        if action == "REJECTED":
            transfer.transfer_status = 'REJECTED'
            transfer.approved_by = current_user_id
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Allocation", "Transfer Rejected", "TransferRequest", transfer.id)
            NotificationService.send_notification(transfer.requested_by, "Transfer Rejected", "Your transfer request was rejected.")
            return True, None
            
        elif action == "APPROVED":
            transfer.transfer_status = 'APPROVED'
            transfer.approved_by = current_user_id
            
            # The actual transfer logic depends on specific rules (e.g. freeing up the asset or reallocating it).
            # We'll just mark it as approved, freeing the asset for the next allocation.
            allocation = transfer.allocation
            allocation.allocation_status = 'TRANSFERRED'
            allocation.return_date = datetime.utcnow()
            
            asset = Asset.query.get(allocation.asset_id)
            asset.lifecycle_status = 'AVAILABLE'
            
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Allocation", "Transfer Approved", "TransferRequest", transfer.id)
            NotificationService.send_notification(transfer.requested_by, "Transfer Approved", "Your transfer request was approved.")
            
            return True, None
        return False, "Invalid action"
