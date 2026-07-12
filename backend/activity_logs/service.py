import logging
from extensions import db
from database.models import ActivityLog

logger = logging.getLogger(__name__)

class ActivityLogService:
    @staticmethod
    def log_activity(user_id, module, action, entity=None, entity_id=None, description=None, ip_address=None, device=None):
        try:
            log = ActivityLog(
                user_id=user_id,
                module=module,
                action=action,
                entity=entity,
                entity_id=entity_id,
                description=description,
                ip_address=ip_address,
                device=device
            )
            db.session.add(log)
            db.session.commit()
            logger.info(f"ACTIVITY LOG | User: {user_id} | Module: {module} | Action: {action}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to log activity: {e}")
