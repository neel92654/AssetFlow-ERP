from datetime import datetime
from sqlalchemy import or_, and_
from extensions import db
from database.models import Resource, Booking
from activity_logs.service import ActivityLogService
from notifications.service import NotificationService

class BookingService:
    @staticmethod
    def get_all_bookings():
        return Booking.query.all()

    @staticmethod
    def create_booking(data, current_user_id):
        resource = Resource.query.get(data['resource_id'])
        if not resource or resource.availability_status != 'AVAILABLE':
            return None, "Resource not available"
            
        start_time = data['start_datetime']
        end_time = data['end_datetime']
        
        if start_time >= end_time:
            return None, "End time must be after start time"
            
        if start_time < datetime.utcnow():
            return None, "Cannot book in the past"

        # Conflict Detection:
        # Check if any existing upcoming or ongoing booking overlaps with the requested times
        conflict = Booking.query.filter(
            Booking.resource_id == resource.id,
            Booking.booking_status.in_(['UPCOMING', 'ONGOING']),
            or_(
                and_(Booking.start_datetime <= start_time, Booking.end_datetime > start_time),
                and_(Booking.start_datetime < end_time, Booking.end_datetime >= end_time),
                and_(Booking.start_datetime >= start_time, Booking.end_datetime <= end_time)
            )
        ).first()

        if conflict:
            return None, "Time slot is already booked"

        try:
            booking = Booking(
                resource_id=resource.id,
                booked_by=current_user_id,
                start_datetime=start_time,
                end_datetime=end_time,
                purpose=data.get('purpose')
            )
            db.session.add(booking)
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Booking", "Create Booking", "Booking", booking.id)
            NotificationService.send_notification(current_user_id, "Booking Confirmed", f"Your booking for {resource.resource_name} is confirmed.")
            
            return booking, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)

    @staticmethod
    def cancel_booking(booking_id, current_user_id):
        booking = Booking.query.get(booking_id)
        if not booking or booking.booking_status not in ['UPCOMING', 'ONGOING']:
            return False, "Invalid booking or already processed"
            
        try:
            booking.booking_status = 'CANCELLED'
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Booking", "Cancel Booking", "Booking", booking.id)
            NotificationService.send_notification(booking.booked_by, "Booking Cancelled", "Your booking has been cancelled.")
            
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    @staticmethod
    def reschedule_booking(booking_id, data, current_user_id):
        booking = Booking.query.get(booking_id)
        if not booking or booking.booking_status != 'UPCOMING':
            return None, "Can only reschedule upcoming bookings"
            
        start_time = data['start_datetime']
        end_time = data['end_datetime']
        
        if start_time >= end_time:
            return None, "End time must be after start time"
            
        # Conflict Detection excluding the current booking
        conflict = Booking.query.filter(
            Booking.id != booking.id,
            Booking.resource_id == booking.resource_id,
            Booking.booking_status.in_(['UPCOMING', 'ONGOING']),
            or_(
                and_(Booking.start_datetime <= start_time, Booking.end_datetime > start_time),
                and_(Booking.start_datetime < end_time, Booking.end_datetime >= end_time),
                and_(Booking.start_datetime >= start_time, Booking.end_datetime <= end_time)
            )
        ).first()

        if conflict:
            return None, "Time slot is already booked"
            
        try:
            booking.start_datetime = start_time
            booking.end_datetime = end_time
            db.session.commit()
            
            ActivityLogService.log_activity(current_user_id, "Booking", "Reschedule Booking", "Booking", booking.id)
            NotificationService.send_notification(booking.booked_by, "Booking Rescheduled", "Your booking has been rescheduled.")
            
            return booking, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
