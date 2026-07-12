from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, Enum, String
from extensions import db

class Base(db.Model):
    __abstract__ = True
    
    id = db.Column(db.BigInteger, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, nullable=True)
    updated_by = db.Column(db.Integer, nullable=True)
    status = db.Column(db.Enum('ACTIVE', 'INACTIVE', name='status_enum'), default='ACTIVE')

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.BigInteger, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    users = db.relationship('User', backref='role', lazy=True)

class Department(Base):
    __tablename__ = 'departments'
    
    department_name = db.Column(db.String(100), nullable=False)
    parent_department_id = db.Column(db.BigInteger, db.ForeignKey('departments.id'), nullable=True)
    department_head_id = db.Column(db.BigInteger, db.ForeignKey('users.id', use_alter=True, name="fk_dept_head"), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Self-referential relationship
    sub_departments = db.relationship('Department', backref=db.backref('parent', remote_side='Department.id'))
    
    # Note: department_head relationship is defined below after User model.

class User(Base):
    __tablename__ = 'users'
    
    employee_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(15), nullable=True, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    role_id = db.Column(db.BigInteger, db.ForeignKey('roles.id'), nullable=False)
    department_id = db.Column(db.BigInteger, db.ForeignKey('departments.id'), nullable=True)
    
    profile_image = db.Column(db.String(255), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)
    account_status = db.Column(db.Enum('ACTIVE', 'INACTIVE', 'LOCKED', name='account_status_enum'), default='ACTIVE')
    
    department = db.relationship('Department', foreign_keys=[department_id], backref='employees', lazy=True)

# Add relation for department head to User
Department.department_head = db.relationship('User', foreign_keys=[Department.department_head_id], post_update=True)

class AssetCategory(Base):
    __tablename__ = 'asset_categories'
    category_name = db.Column(db.String(100), nullable=False, unique=True)
    warranty_period = db.Column(db.Integer, nullable=True) # in months
    description = db.Column(db.Text, nullable=True)

class Asset(Base):
    __tablename__ = 'assets'
    asset_tag = db.Column(db.String(50), nullable=False, unique=True, index=True)
    asset_name = db.Column(db.String(255), nullable=False)
    serial_number = db.Column(db.String(100), nullable=False, unique=True, index=True)
    category_id = db.Column(db.BigInteger, db.ForeignKey('asset_categories.id'), nullable=False, index=True)
    department_id = db.Column(db.BigInteger, db.ForeignKey('departments.id'), nullable=True, index=True)
    acquisition_date = db.Column(db.Date, nullable=True)
    acquisition_cost = db.Column(db.Numeric(10, 2), nullable=True)
    condition = db.Column(db.Enum('NEW', 'GOOD', 'FAIR', 'POOR', name='condition_enum'), default='NEW')
    lifecycle_status = db.Column(db.Enum('AVAILABLE', 'ALLOCATED', 'RESERVED', 'MAINTENANCE', 'LOST', 'RETIRED', 'DISPOSED', name='lifecycle_status_enum'), default='AVAILABLE')
    location = db.Column(db.String(255), nullable=True)
    qr_code = db.Column(db.String(255), nullable=True)
    image = db.Column(db.String(255), nullable=True)
    is_shared = db.Column(db.Boolean, default=False)
    remarks = db.Column(db.Text, nullable=True)
    
    category = db.relationship('AssetCategory', backref='assets', lazy=True)
    department = db.relationship('Department', backref='department_assets', lazy=True)

class AssetDocument(Base):
    __tablename__ = 'asset_documents'
    asset_id = db.Column(db.BigInteger, db.ForeignKey('assets.id'), nullable=False)
    document_name = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    document_path = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    
    asset = db.relationship('Asset', backref='documents', lazy=True)

class Allocation(Base):
    __tablename__ = 'allocations'
    asset_id = db.Column(db.BigInteger, db.ForeignKey('assets.id'), nullable=False)
    employee_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    department_id = db.Column(db.BigInteger, db.ForeignKey('departments.id'), nullable=False)
    allocation_date = db.Column(db.DateTime, default=datetime.utcnow)
    expected_return_date = db.Column(db.DateTime, nullable=True)
    return_date = db.Column(db.DateTime, nullable=True)
    allocation_status = db.Column(db.Enum('ALLOCATED', 'RETURNED', 'TRANSFERRED', 'OVERDUE', name='allocation_status_enum'), default='ALLOCATED')
    
    asset = db.relationship('Asset', backref='allocations', lazy=True)
    employee = db.relationship('User', foreign_keys=[employee_id], backref='allocations', lazy=True)

class TransferRequest(Base):
    __tablename__ = 'transfer_requests'
    allocation_id = db.Column(db.BigInteger, db.ForeignKey('allocations.id'), nullable=False)
    requested_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    approved_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    transfer_status = db.Column(db.Enum('REQUESTED', 'APPROVED', 'REJECTED', 'COMPLETED', name='transfer_status_enum'), default='REQUESTED')
    
    allocation = db.relationship('Allocation', backref='transfer_requests', lazy=True)

class Resource(Base):
    __tablename__ = 'resources'
    resource_name = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)
    availability_status = db.Column(db.Enum('AVAILABLE', 'UNAVAILABLE', name='resource_availability_enum'), default='AVAILABLE')

class Booking(Base):
    __tablename__ = 'bookings'
    resource_id = db.Column(db.BigInteger, db.ForeignKey('resources.id'), nullable=False, index=True)
    booked_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False, index=True)
    end_datetime = db.Column(db.DateTime, nullable=False, index=True)
    purpose = db.Column(db.String(255), nullable=True)
    booking_status = db.Column(db.Enum('UPCOMING', 'ONGOING', 'COMPLETED', 'CANCELLED', name='booking_status_enum'), default='UPCOMING')
    
    resource = db.relationship('Resource', backref='bookings', lazy=True)
    user = db.relationship('User', backref='bookings', lazy=True)

class MaintenanceRequest(Base):
    __tablename__ = 'maintenance_requests'
    asset_id = db.Column(db.BigInteger, db.ForeignKey('assets.id'), nullable=False)
    raised_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    priority = db.Column(db.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='priority_enum'), default='MEDIUM')
    issue_description = db.Column(db.Text, nullable=False)
    attachment = db.Column(db.String(255), nullable=True)
    maintenance_status = db.Column(db.Enum('PENDING', 'APPROVED', 'REJECTED', 'TECHNICIAN_ASSIGNED', 'IN_PROGRESS', 'RESOLVED', name='maintenance_status_enum'), default='PENDING')
    
    asset = db.relationship('Asset', backref='maintenance_requests', lazy=True)
    raiser = db.relationship('User', foreign_keys=[raised_by], backref='raised_maintenance', lazy=True)
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_maintenance', lazy=True)

class AuditCycle(Base):
    __tablename__ = 'audit_cycles'
    audit_name = db.Column(db.String(255), nullable=False)
    department_id = db.Column(db.BigInteger, db.ForeignKey('departments.id'), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    audit_status = db.Column(db.Enum('OPEN', 'IN_PROGRESS', 'CLOSED', name='audit_status_enum'), default='OPEN')

class AuditAsset(db.Model):
    __tablename__ = 'audit_assets'
    id = db.Column(db.BigInteger, primary_key=True)
    audit_cycle_id = db.Column(db.BigInteger, db.ForeignKey('audit_cycles.id'), nullable=False)
    asset_id = db.Column(db.BigInteger, db.ForeignKey('assets.id'), nullable=False)
    verification_status = db.Column(db.Enum('VERIFIED', 'MISSING', 'DAMAGED', 'PENDING', name='verification_status_enum'), default='PENDING')
    remarks = db.Column(db.Text, nullable=True)
    verified_by = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    verified_at = db.Column(db.DateTime, nullable=True)
    
    audit_cycle = db.relationship('AuditCycle', backref='audit_assets', lazy=True)
    asset = db.relationship('Asset', backref='audit_records', lazy=True)

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    priority = db.Column(db.Enum('INFO', 'WARNING', 'SUCCESS', 'CRITICAL', name='notification_priority_enum'), default='INFO')
    notification_type = db.Column(db.String(50), nullable=True)
    read_status = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='notifications', lazy=True)

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id'), nullable=True)
    module = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    entity = db.Column(db.String(50), nullable=True)
    entity_id = db.Column(db.BigInteger, nullable=True)
    description = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    device = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', backref='activity_logs', lazy=True)
