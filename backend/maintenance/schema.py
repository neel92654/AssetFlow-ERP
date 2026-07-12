from marshmallow import Schema, fields, validate

class MaintenanceRequestSchema(Schema):
    id = fields.Int(dump_only=True)
    asset_id = fields.Int(required=True)
    raised_by = fields.Int(dump_only=True)
    assigned_to = fields.Int(allow_none=True)
    priority = fields.Str(validate=validate.OneOf(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']))
    issue_description = fields.Str(required=True)
    attachment = fields.Str(allow_none=True)
    maintenance_status = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
