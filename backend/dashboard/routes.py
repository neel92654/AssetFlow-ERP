from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from dashboard.service import DashboardService
from utils.common import success_response
from activity_logs.schema import ActivityLogSchema
from notifications.schema import NotificationSchema

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/kpis', methods=['GET'])
@jwt_required()
def get_kpis():
    kpis = DashboardService.get_kpis()
    return success_response("KPIs retrieved", kpis)

@dashboard_bp.route('/recent-activity', methods=['GET'])
@jwt_required()
def get_recent_activity():
    activity = DashboardService.get_recent_activity()
    schema = ActivityLogSchema(many=True)
    return success_response("Recent activity retrieved", schema.dump(activity))

@dashboard_bp.route('/notifications', methods=['GET'])
@jwt_required()
def get_recent_notifications():
    notifications = DashboardService.get_recent_notifications(get_jwt_identity())
    schema = NotificationSchema(many=True)
    return success_response("Recent notifications retrieved", schema.dump(notifications))
