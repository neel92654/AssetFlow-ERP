import logging
from extensions import db
from database.models import Notification

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def send_notification(user_id, title, message, priority="INFO", notification_type="System"):
        try:
            notif = Notification(
                user_id=user_id,
                title=title,
                message=message,
                priority=priority.upper(),
                notification_type=notification_type
            )
            db.session.add(notif)
            db.session.commit()
            logger.info(f"NOTIFICATION | User: {user_id} | Title: {title} | Message: {message}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to send notification: {e}")

    @staticmethod
    def mark_read(notification_id, user_id):
        notif = Notification.query.filter_by(id=notification_id, user_id=user_id).first()
        if notif:
            notif.read_status = True
            db.session.commit()
            return True
        return False
