from marshmallow import Schema, fields, validate

class AssetSchema(Schema):
    id = fields.Int(dump_only=True)
    asset_tag = fields.Str(dump_only=True)
    asset_name = fields.Str(required=True, validate=validate.Length(min=1, max=255))
    serial_number = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category_id = fields.Int(required=True)
    department_id = fields.Int(allow_none=True)
    acquisition_date = fields.Date(allow_none=True)
    acquisition_cost = fields.Float(allow_none=True)
    condition = fields.Str(validate=validate.OneOf(['NEW', 'GOOD', 'FAIR', 'POOR']))
    lifecycle_status = fields.Str(dump_only=True)
    location = fields.Str(allow_none=True)
    qr_code = fields.Str(dump_only=True)
    image = fields.Str(dump_only=True)
    is_shared = fields.Bool()
    remarks = fields.Str(allow_none=True)

class AssetDocumentSchema(Schema):
    id = fields.Int(dump_only=True)
    document_name = fields.Str()
    document_type = fields.Str()
    document_path = fields.Str()
    uploaded_at = fields.DateTime()
