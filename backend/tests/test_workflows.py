import json
from datetime import datetime, timedelta
from database.models import AssetCategory, Asset, Department, Resource, Booking, Allocation

def setup_test_data(client, admin_token, db):
    # Category
    client.post('/api/v1/organization/categories',
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"category_name": "Test Category"})
    cat = AssetCategory.query.filter_by(category_name="Test Category").first()
    
    # Department
    client.post('/api/v1/organization/departments',
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"department_name": "Test Dept"})
    dept = Department.query.filter_by(department_name="Test Dept").first()
    
    # Asset
    client.post('/api/v1/assets',
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "asset_name": "Test Asset",
                    "serial_number": "SN-TEST",
                    "category_id": cat.id
                })
    asset = Asset.query.filter_by(serial_number="SN-TEST").first()
    
    # Resource
    res = Resource(resource_name="Conf Room A", resource_type="Room")
    db.session.add(res)
    db.session.commit()
    
    return asset, dept, res

def test_allocation_flow(client, admin_user, employee_user, app):
    """Test full allocation cycle: Allocate -> Return"""
    from extensions import db
    with app.app_context():
        asset, dept, _ = setup_test_data(client, admin_user['token'], db)
        
        # 1. Allocate asset to employee
        res1 = client.post('/api/v1/allocation',
                           headers={"Authorization": f"Bearer {admin_user['token']}"},
                           json={
                               "asset_id": asset.id,
                               "employee_id": employee_user['user'].id,
                               "department_id": dept.id
                           })
        assert res1.status_code == 201
        
        # Verify asset status is ALLOCATED
        updated_asset = Asset.query.get(asset.id)
        assert updated_asset.lifecycle_status == "ALLOCATED"
        
        allocation_id = json.loads(res1.data)['data']['id']
        
        # 2. Return asset
        res2 = client.patch(f'/api/v1/allocation/{allocation_id}/return',
                            headers={"Authorization": f"Bearer {admin_user['token']}"})
        assert res2.status_code == 200
        
        updated_asset = Asset.query.get(asset.id)
        assert updated_asset.lifecycle_status == "AVAILABLE"
        
        alloc = Allocation.query.get(allocation_id)
        assert alloc.allocation_status == "RETURNED"

def test_booking_conflict(client, employee_user, app):
    """Test resource booking conflict detection."""
    from extensions import db
    
    # Setup resource directly
    with app.app_context():
        resource = Resource(resource_name="Projector", resource_type="Device")
        db.session.add(resource)
        db.session.commit()
        res_id = resource.id
        
        now = datetime.utcnow()
        start_time1 = (now + timedelta(hours=1)).isoformat()
        end_time1 = (now + timedelta(hours=2)).isoformat()
        
        # 1. Successful booking
        res1 = client.post('/api/v1/bookings',
                           headers={"Authorization": f"Bearer {employee_user['token']}"},
                           json={
                               "resource_id": res_id,
                               "start_datetime": start_time1,
                               "end_datetime": end_time1
                           })
        assert res1.status_code == 201
        
        # 2. Conflicting booking (Overlaps exactly)
        res2 = client.post('/api/v1/bookings',
                           headers={"Authorization": f"Bearer {employee_user['token']}"},
                           json={
                               "resource_id": res_id,
                               "start_datetime": start_time1,
                               "end_datetime": end_time1
                           })
        assert res2.status_code == 409
        data = json.loads(res2.data)
        assert "already booked" in data['message']
