from marshmallow import Schema, fields

class NotificationSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    title = fields.Str()
    message = fields.Str()
    priority = fields.Str()
    notification_type = fields.Str()
    read_status = fields.Bool()
    created_at = fields.DateTime()
