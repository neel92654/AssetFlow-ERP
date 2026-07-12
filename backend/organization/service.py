from extensions import db
from database.models import Department, AssetCategory, User, Role
from activity_logs.service import ActivityLogService

class OrganizationService:
    # --- Departments ---
    @staticmethod
    def get_all_departments():
        return Department.query.all()

    @staticmethod
    def create_department(data, current_user_id):
        if Department.query.filter_by(department_name=data['department_name']).first():
            return None, "Department name must be unique"
        
        dept = Department(
            department_name=data['department_name'],
            parent_department_id=data.get('parent_department_id'),
            department_head_id=data.get('department_head_id'),
            description=data.get('description'),
            created_by=current_user_id
        )
        db.session.add(dept)
        db.session.commit()
        
        ActivityLogService.log_activity(current_user_id, "Organization", "Create Department", "Department", dept.id)
        return dept, None

    @staticmethod
    def update_department(dept_id, data, current_user_id):
        dept = Department.query.get(dept_id)
        if not dept:
            return None, "Department not found"
            
        if 'department_name' in data and data['department_name'] != dept.department_name:
            if Department.query.filter_by(department_name=data['department_name']).first():
                return None, "Department name must be unique"
            dept.department_name = data['department_name']
            
        if 'parent_department_id' in data:
            dept.parent_department_id = data['parent_department_id']
        if 'department_head_id' in data:
            dept.department_head_id = data['department_head_id']
        if 'description' in data:
            dept.description = data['description']
            
        dept.updated_by = current_user_id
        db.session.commit()
        
        ActivityLogService.log_activity(current_user_id, "Organization", "Update Department", "Department", dept.id)
        return dept, None

    @staticmethod
    def delete_department(dept_id, current_user_id):
        dept = Department.query.get(dept_id)
        if not dept:
            return False, "Department not found"
            
        # Check if department has employees or assets
        if dept.employees or dept.department_assets:
            return False, "Cannot delete department with active employees or assets"
            
        dept.status = 'INACTIVE'
        dept.updated_by = current_user_id
        db.session.commit()
        
        ActivityLogService.log_activity(current_user_id, "Organization", "Delete Department", "Department", dept.id)
        return True, None

    # --- Categories ---
    @staticmethod
    def get_all_categories():
        return AssetCategory.query.all()
        
    @staticmethod
    def create_category(data, current_user_id):
        if AssetCategory.query.filter_by(category_name=data['category_name']).first():
            return None, "Category name must be unique"
            
        category = AssetCategory(
            category_name=data['category_name'],
            warranty_period=data.get('warranty_period'),
            description=data.get('description'),
            created_by=current_user_id
        )
        db.session.add(category)
        db.session.commit()
        
        ActivityLogService.log_activity(current_user_id, "Organization", "Create Category", "AssetCategory", category.id)
        return category, None
        
    @staticmethod
    def update_category(cat_id, data, current_user_id):
        category = AssetCategory.query.get(cat_id)
        if not category:
            return None, "Category not found"
            
        if 'category_name' in data and data['category_name'] != category.category_name:
            if AssetCategory.query.filter_by(category_name=data['category_name']).first():
                return None, "Category name must be unique"
            category.category_name = data['category_name']
            
        if 'warranty_period' in data:
            category.warranty_period = data['warranty_period']
        if 'description' in data:
            category.description = data['description']
            
        category.updated_by = current_user_id
        db.session.commit()
        
        ActivityLogService.log_activity(current_user_id, "Organization", "Update Category", "AssetCategory", category.id)
        return category, None

    @staticmethod
    def delete_category(cat_id, current_user_id):
        category = AssetCategory.query.get(cat_id)
        if not category:
            return False, "Category not found"
            
        category.status = 'INACTIVE'
        category.updated_by = current_user_id
        db.session.commit()
        
        ActivityLogService.log_activity(current_user_id, "Organization", "Delete Category", "AssetCategory", category.id)
        return True, None
        
    # --- Employees ---
    @staticmethod
    def get_all_employees():
        return User.query.all()
        
    @staticmethod
    def update_employee(emp_id, data, current_user_id, current_user_role):
        emp = User.query.get(emp_id)
        if not emp:
            return None, "Employee not found"
            
        if 'role_id' in data:
            if current_user_role != 'Admin':
                return None, "Only Admin can change roles"
            emp.role_id = data['role_id']
            
        if 'account_status' in data:
            if current_user_role != 'Admin':
                return None, "Only Admin can change account status"
            emp.account_status = data['account_status']
            
        if 'department_id' in data:
            dept = Department.query.get(data['department_id'])
            if not dept or dept.status != 'ACTIVE':
                return None, "Invalid or inactive department"
            emp.department_id = data['department_id']
            
        emp.updated_by = current_user_id
        db.session.commit()
        
        ActivityLogService.log_activity(current_user_id, "Organization", "Update Employee", "User", emp.id)
        return emp, None
