import json
from database.models import Department, AssetCategory, Asset

def test_create_department_admin(client, admin_user):
    """Admin should be able to create a department."""
    res = client.post('/api/v1/organization/departments',
                      headers={"Authorization": f"Bearer {admin_user['token']}"},
                      json={"department_name": "IT Dept"})
    
    assert res.status_code == 201
    data = json.loads(res.data)
    assert data['data']['department_name'] == "IT Dept"

def test_create_department_employee(client, employee_user):
    """Employee should NOT be able to create a department."""
    res = client.post('/api/v1/organization/departments',
                      headers={"Authorization": f"Bearer {employee_user['token']}"},
                      json={"department_name": "HR Dept"})
    
    assert res.status_code == 403

def test_create_category(client, admin_user):
    """Admin should be able to create a category."""
    res = client.post('/api/v1/organization/categories',
                      headers={"Authorization": f"Bearer {admin_user['token']}"},
                      json={"category_name": "Laptops", "warranty_period": 36})
    
    assert res.status_code == 201

def test_register_asset(client, admin_user):
    """Test asset registration flow."""
    # 1. Create a category
    client.post('/api/v1/organization/categories',
                headers={"Authorization": f"Bearer {admin_user['token']}"},
                json={"category_name": "Desktops"})
    
    category = AssetCategory.query.filter_by(category_name="Desktops").first()
    
    # 2. Register asset
    res = client.post('/api/v1/assets',
                      headers={"Authorization": f"Bearer {admin_user['token']}"},
                      json={
                          "asset_name": "Dell Optiplex",
                          "serial_number": "SN-DELL-001",
                          "category_id": category.id
                      })
    
    assert res.status_code == 201
    data = json.loads(res.data)
    assert data['data']['asset_name'] == "Dell Optiplex"
    assert data['data']['lifecycle_status'] == "AVAILABLE"
    assert data['data']['asset_tag'].startswith("AF")
