import json
from database.models import User

def test_login_success(client, admin_user):
    """Test successful login with valid credentials."""
    response = client.post('/api/v1/auth/login', 
                           data=json.dumps({
                               "email": "admin@test.com",
                               "password": "Password@123"
                           }),
                           content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] is True
    assert 'access_token' in data['data']
    assert 'refresh_token' in data['data']
    assert data['data']['role'] == 'Admin'

def test_login_invalid_password(client, admin_user):
    """Test login with wrong password."""
    response = client.post('/api/v1/auth/login', 
                           data=json.dumps({
                               "email": "admin@test.com",
                               "password": "WrongPassword!"
                           }),
                           content_type='application/json')
    
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data['success'] is False

def test_profile_protected(client, admin_user):
    """Test that profile endpoint requires auth and returns correct data."""
    # Without token
    res1 = client.get('/api/v1/auth/profile')
    assert res1.status_code == 401
    
    # With token
    res2 = client.get('/api/v1/auth/profile', 
                      headers={"Authorization": f"Bearer {admin_user['token']}"})
    assert res2.status_code == 200
    data = json.loads(res2.data)
    assert data['data']['email'] == "admin@test.com"
