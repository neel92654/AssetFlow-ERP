from create_app import create_app
from extensions import db
from database.models import User, Role

app = create_app()

with app.app_context():
    admin_role = Role.query.filter_by(role_name='Admin').first()
    if not admin_role:
        print("Admin role not found. Creating it...")
        admin_role = Role(role_name='Admin', description='System Administrator')
        db.session.add(admin_role)
        db.session.commit()
    
    # Get the latest registered user or user ID 2
    users = User.query.all()
    for user in users:
        print(f"Elevating user {user.email} (ID: {user.id}) to Admin...")
        user.role_id = admin_role.id
    
    db.session.commit()
    print("All existing users have been elevated to Admin successfully!")
