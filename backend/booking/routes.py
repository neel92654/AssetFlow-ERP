from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from booking.schema import BookingSchema, ResourceSchema
from booking.service import BookingService
from utils.common import success_response, error_response
from database.models import Resource

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/resources', methods=['GET'])
@jwt_required()
def get_resources():
    resources = Resource.query.all()
    schema = ResourceSchema(many=True)
    return success_response("Resources retrieved", schema.dump(resources))

@bookings_bp.route('', methods=['GET'])
@jwt_required()
def get_bookings():
    bookings = BookingService.get_all_bookings()
    schema = BookingSchema(many=True)
    return success_response("Bookings retrieved", schema.dump(bookings))

@bookings_bp.route('', methods=['POST'])
@jwt_required()
def create_booking():
    schema = BookingSchema()
    errors = schema.validate(request.json)
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    booking, error_msg = BookingService.create_booking(data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg, status_code=409 if "booked" in error_msg else 400)
    return success_response("Booking created successfully", schema.dump(booking), status_code=201)

@bookings_bp.route('/<int:id>/cancel', methods=['PATCH'])
@jwt_required()
def cancel_booking(id):
    success, error_msg = BookingService.cancel_booking(id, get_jwt_identity())
    if error_msg:
        return error_response(error_msg, status_code=400)
    return success_response("Booking cancelled successfully")

@bookings_bp.route('/<int:id>/reschedule', methods=['PATCH'])
@jwt_required()
def reschedule_booking(id):
    schema = BookingSchema(partial=True)
    errors = schema.validate(request.json)
    if 'start_datetime' not in request.json or 'end_datetime' not in request.json:
        return error_response("start_datetime and end_datetime are required")
        
    if errors:
        return error_response("Validation failed", errors)
        
    data = schema.load(request.json)
    booking, error_msg = BookingService.reschedule_booking(id, data, get_jwt_identity())
    
    if error_msg:
        return error_response(error_msg, status_code=409 if "booked" in error_msg else 400)
    return success_response("Booking rescheduled successfully", schema.dump(booking))
