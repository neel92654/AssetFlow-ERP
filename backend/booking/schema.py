from marshmallow import Schema, fields, validate

class ResourceSchema(Schema):
    id = fields.Int(dump_only=True)
    resource_name = fields.Str(required=True)
    resource_type = fields.Str(required=True)
    location = fields.Str(allow_none=True)
    capacity = fields.Int(allow_none=True)
    availability_status = fields.Str(dump_only=True)

class BookingSchema(Schema):
    id = fields.Int(dump_only=True)
    resource_id = fields.Int(required=True)
    booked_by = fields.Int(dump_only=True)
    start_datetime = fields.DateTime(required=True)
    end_datetime = fields.DateTime(required=True)
    purpose = fields.Str(allow_none=True)
    booking_status = fields.Str(dump_only=True)
