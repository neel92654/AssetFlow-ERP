from create_app import create_app
from extensions import db
from database.models import AssetCategory, Department

app = create_app()

with app.app_context():
    # Departments
    departments_data = [
        {"name": "Engineering", "desc": "Software and Hardware Engineering"},
        {"name": "Human Resources", "desc": "HR and Talent Acquisition"},
        {"name": "Finance", "desc": "Accounting and Finance"},
        {"name": "Operations", "desc": "Daily Operations and Logistics"},
        {"name": "Sales & Marketing", "desc": "Sales, Marketing, and PR"}
    ]
    
    for dept in departments_data:
        existing = Department.query.filter_by(department_name=dept["name"]).first()
        if not existing:
            new_dept = Department(department_name=dept["name"], description=dept["desc"])
            db.session.add(new_dept)
            print(f"Added department: {dept['name']}")
    
    # Categories
    categories_data = [
        {"name": "Laptops & Computers", "warranty": 36, "desc": "Standard issue computing devices"},
        {"name": "Mobile Devices", "warranty": 12, "desc": "Smartphones and tablets"},
        {"name": "Office Furniture", "warranty": 120, "desc": "Desks, chairs, and cabinets"},
        {"name": "Networking Equipment", "warranty": 24, "desc": "Routers, switches, and APs"},
        {"name": "Vehicles", "warranty": 60, "desc": "Company cars and delivery vans"},
        {"name": "Software Licenses", "warranty": 12, "desc": "Annual or perpetual software licenses"}
    ]
    
    for cat in categories_data:
        existing = AssetCategory.query.filter_by(category_name=cat["name"]).first()
        if not existing:
            new_cat = AssetCategory(category_name=cat["name"], warranty_period=cat["warranty"], description=cat["desc"])
            db.session.add(new_cat)
            print(f"Added category: {cat['name']}")
            
    db.session.commit()
    print("Database seeded successfully with initial Departments and Categories!")
