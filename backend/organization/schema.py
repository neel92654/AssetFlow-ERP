from marshmallow import Schema, fields, validate

class DepartmentSchema(Schema):
    id = fields.Int(dump_only=True)
    department_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    parent_department_id = fields.Int(allow_none=True)
    department_head_id = fields.Int(allow_none=True)
    description = fields.Str(allow_none=True)
    status = fields.Str(dump_only=True)
    
class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    category_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    warranty_period = fields.Int(allow_none=True) # in months
    description = fields.Str(allow_none=True)
    status = fields.Str(dump_only=True)

class EmployeeUpdateSchema(Schema):
    role_id = fields.Int()
    account_status = fields.Str(validate=validate.OneOf(['ACTIVE', 'INACTIVE', 'LOCKED']))
    department_id = fields.Int()
