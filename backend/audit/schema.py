from marshmallow import Schema, fields, validate

class AuditCycleSchema(Schema):
    id = fields.Int(dump_only=True)
    audit_name = fields.Str(required=True)
    department_id = fields.Int(allow_none=True)
    location = fields.Str(allow_none=True)
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    audit_status = fields.Str(dump_only=True)

class AuditAssetSchema(Schema):
    id = fields.Int(dump_only=True)
    audit_cycle_id = fields.Int(required=True)
    asset_id = fields.Int(required=True)
    verification_status = fields.Str(validate=validate.OneOf(['VERIFIED', 'MISSING', 'DAMAGED', 'PENDING']))
    remarks = fields.Str(allow_none=True)
    verified_by = fields.Int(dump_only=True)
    verified_at = fields.DateTime(dump_only=True)
