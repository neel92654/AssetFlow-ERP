from marshmallow import Schema, fields, validate, validates, ValidationError
from database.models import User, Department
import re

class SignupSchema(Schema):
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone = fields.Str(required=True, validate=validate.Length(min=10, max=15))
    password = fields.Str(required=True, validate=validate.Length(min=8))
    confirm_password = fields.Str(required=True)
    department_id = fields.Int(required=True)
    
    @validates('password')
    def validate_password(self, value):
        # Must contain uppercase, lowercase, number, special character
        if not re.search(r'[A-Z]', value):
            raise ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[a-z]', value):
            raise ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r'\d', value):
            raise ValidationError("Password must contain at least one number.")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("Password must contain at least one special character.")

    @validates('department_id')
    def validate_department(self, value):
        dept = Department.query.get(value)
        if not dept:
            raise ValidationError("Department does not exist.")
        if dept.status != 'ACTIVE':
            raise ValidationError("Department is inactive.")

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class UserProfileSchema(Schema):
    id = fields.Int()
    employee_code = fields.Str()
    first_name = fields.Str()
    last_name = fields.Str()
    email = fields.Email()
    phone = fields.Str()
    role = fields.Method("get_role_name")
    department = fields.Method("get_department_name")
    is_verified = fields.Bool()
    last_login = fields.DateTime()
    
    def get_role_name(self, obj):
        return obj.role.role_name if obj.role else None

    def get_department_name(self, obj):
        return obj.department.department_name if obj.department else None
