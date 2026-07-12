import json
from datetime import date
from database.models import AssetCategory, Asset, MaintenanceRequest, AuditCycle, AuditAsset

def setup_test_asset(client, admin_token, db):
    # Category
    client.post('/api/v1/organization/categories',
                headers={"Authorization": f"Bearer {admin_token}"},
                json={"category_name": "Test Category M"})
    cat = AssetCategory.query.filter_by(category_name="Test Category M").first()
    
    # Asset
    client.post('/api/v1/assets',
                headers={"Authorization": f"Bearer {admin_token}"},
                json={
                    "asset_name": "Maintenance Asset",
                    "serial_number": "SN-MAINT",
                    "category_id": cat.id
                })
    asset = Asset.query.filter_by(serial_number="SN-MAINT").first()
    return asset

def test_maintenance_lifecycle(client, admin_user, employee_user, app):
    """Test full maintenance lifecycle."""
    from extensions import db
    with app.app_context():
        asset = setup_test_asset(client, admin_user['token'], db)
        
        # 1. Raise request
        res = client.post('/api/v1/maintenance',
                          headers={"Authorization": f"Bearer {employee_user['token']}"},
                          json={
                              "asset_id": asset.id,
                              "issue_description": "Screen broken"
                          })
        assert res.status_code == 201
        req_id = json.loads(res.data)['data']['id']
        
        # 2. Approve request
        res = client.patch(f'/api/v1/maintenance/{req_id}/approve',
                           headers={"Authorization": f"Bearer {admin_user['token']}"})
        assert res.status_code == 200
        
        updated_asset = Asset.query.get(asset.id)
        assert updated_asset.lifecycle_status == "MAINTENANCE"
        
        # 3. Assign
        res = client.patch(f'/api/v1/maintenance/{req_id}/assign',
                           headers={"Authorization": f"Bearer {admin_user['token']}"},
                           json={"assigned_to": admin_user['user'].id})
        assert res.status_code == 200
        
        # 4. Start
        res = client.patch(f'/api/v1/maintenance/{req_id}/start',
                           headers={"Authorization": f"Bearer {admin_user['token']}"})
        assert res.status_code == 200
        
        # 5. Resolve
        res = client.patch(f'/api/v1/maintenance/{req_id}/resolve',
                           headers={"Authorization": f"Bearer {admin_user['token']}"})
        assert res.status_code == 200
        
        updated_asset = Asset.query.get(asset.id)
        assert updated_asset.lifecycle_status == "AVAILABLE"

def test_audit_cycle_creation(client, admin_user, app):
    """Test that audit cycle gets created and assets are attached."""
    from extensions import db
    with app.app_context():
        asset = setup_test_asset(client, admin_user['token'], db)
        
        res = client.post('/api/v1/audit/cycle',
                          headers={"Authorization": f"Bearer {admin_user['token']}"},
                          json={
                              "audit_name": "Q3 Audit",
                              "start_date": date.today().isoformat(),
                              "end_date": date.today().isoformat()
                          })
        assert res.status_code == 201
        cycle_id = json.loads(res.data)['data']['id']
        
        # Verify asset was added to audit
        audit_asset = AuditAsset.query.filter_by(audit_cycle_id=cycle_id, asset_id=asset.id).first()
        assert audit_asset is not None
        assert audit_asset.verification_status == "PENDING"
