from extensions import db
from database.models import Asset, Booking, Allocation, TransferRequest, MaintenanceRequest, AuditCycle, Notification, ActivityLog
from datetime import datetime, timedelta

class DashboardService:
    @staticmethod
    def get_kpis():
        now = datetime.utcnow()
        upcoming_returns_date = now + timedelta(days=7)
        
        return {
            "assets_available": Asset.query.filter_by(lifecycle_status='AVAILABLE').count(),
            "assets_allocated": Asset.query.filter_by(lifecycle_status='ALLOCATED').count(),
            "assets_under_maintenance": Asset.query.filter_by(lifecycle_status='MAINTENANCE').count(),
            "pending_transfers": TransferRequest.query.filter_by(transfer_status='REQUESTED').count(),
            "upcoming_returns": Allocation.query.filter(
                Allocation.allocation_status == 'ALLOCATED',
                Allocation.expected_return_date <= upcoming_returns_date,
                Allocation.expected_return_date >= now
            ).count(),
            "overdue_returns": Allocation.query.filter(
                Allocation.allocation_status == 'ALLOCATED',
                Allocation.expected_return_date < now
            ).count(),
            "active_bookings": Booking.query.filter(Booking.booking_status.in_(['UPCOMING', 'ONGOING'])).count(),
            "open_audits": AuditCycle.query.filter_by(audit_status='OPEN').count()
        }

    @staticmethod
    def get_recent_activity(limit=20):
        return ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(limit).all()
        
    @staticmethod
    def get_recent_notifications(user_id, limit=5):
        return Notification.query.filter_by(user_id=user_id, read_status=False).order_by(Notification.created_at.desc()).limit(limit).all()
