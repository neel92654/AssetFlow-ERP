from marshmallow import Schema, fields

class ActivityLogSchema(Schema):
    id = fields.Int()
    user_id = fields.Int()
    module = fields.Str()
    action = fields.Str()
    entity = fields.Str()
    entity_id = fields.Int()
    description = fields.Str()
    ip_address = fields.Str()
    device = fields.Str()
    timestamp = fields.DateTime()
