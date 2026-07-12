from marshmallow import Schema, fields, validate

class AllocationSchema(Schema):
    id = fields.Int(dump_only=True)
    asset_id = fields.Int(required=True)
    employee_id = fields.Int(required=True)
    department_id = fields.Int(required=True)
    allocation_date = fields.DateTime(dump_only=True)
    expected_return_date = fields.DateTime(allow_none=True)
    return_date = fields.DateTime(dump_only=True)
    allocation_status = fields.Str(dump_only=True)

class TransferRequestSchema(Schema):
    id = fields.Int(dump_only=True)
    allocation_id = fields.Int(required=True)
    reason = fields.Str(required=True)
    transfer_status = fields.Str(dump_only=True)
