"""
Quick test script to verify the SAMARTH backend is working.
Run this after starting the server with: uvicorn app.main:app --reload
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    """Pretty print API response."""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    print()

def test_health_check():
    """Test 1: Health check endpoint."""
    print("🔍 Testing Health Check...")
    response = requests.get(f"{BASE_URL}/health")
    print_response("Health Check", response)
    return response.status_code == 200

def test_root():
    """Test 2: Root endpoint."""
    print("🔍 Testing Root Endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print_response("Root Endpoint", response)
    return response.status_code == 200

def test_student_registration():
    """Test 3: Student registration."""
    print("🔍 Testing Student Registration...")
    data = {
        "email": "teststudent@example.com",
        "password": "test123",
        "full_name": "Test Student",
        "skills": ["Python", "FastAPI", "REST API"],
        "interests": ["Web Development", "Backend"],
        "location": "Delhi"
    }
    response = requests.post(f"{BASE_URL}/student/register", json=data)
    print_response("Student Registration", response)
    
    if response.status_code == 201:
        token = response.json().get("token")
        return token
    return None

def test_student_login(email, password):
    """Test 4: Student login."""
    print("🔍 Testing Student Login...")
    data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/student/login", json=data)
    print_response("Student Login", response)
    
    if response.status_code == 200:
        return response.json().get("token")
    return None

def test_get_profile(token):
    """Test 5: Get student profile."""
    print("🔍 Testing Get Profile...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/student/profile", headers=headers)
    print_response("Get Profile", response)
    return response.status_code == 200

def test_get_recommendations(token):
    """Test 6: Get recommendations."""
    print("🔍 Testing Get Recommendations...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {"limit": 5}
    response = requests.post(f"{BASE_URL}/student/recommend", headers=headers, json=data)
    print_response("Get Recommendations", response)
    return response.status_code == 200

def test_search_internships():
    """Test 7: Search internships."""
    print("🔍 Testing Search Internships...")
    params = {"keyword": "Python", "location": "Delhi"}
    response = requests.get(f"{BASE_URL}/student/internships/search", params=params)
    print_response("Search Internships", response)
    return response.status_code == 200

def test_admin_login():
    """Test 8: Admin login."""
    print("🔍 Testing Admin Login...")
    data = {
        "email": "admin@samarth.gov",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/admin/login", json=data)
    print_response("Admin Login", response)
    
    if response.status_code == 200:
        return response.json().get("token")
    return None

def test_admin_summary(admin_token):
    """Test 9: Admin summary."""
    print("🔍 Testing Admin Summary...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/admin/summary", headers=headers)
    print_response("Admin Summary", response)
    return response.status_code == 200

def test_admin_view_internships(admin_token):
    """Test 10: Admin view all internships."""
    print("🔍 Testing Admin View Internships...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BASE_URL}/admin/internships", headers=headers)
    print_response("Admin View Internships", response)
    return response.status_code == 200

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 SAMARTH Backend API Test Suite")
    print("="*60)
    print("\n⚠️  Make sure the server is running: uvicorn app.main:app --reload")
    print("   Server should be at: http://localhost:8000\n")
    
    results = []
    
    # Basic tests
    results.append(("Health Check", test_health_check()))
    results.append(("Root Endpoint", test_root()))
    
    # Student tests
    token = test_student_registration()
    results.append(("Student Registration", token is not None))
    
    if token:
        results.append(("Get Profile", test_get_profile(token)))
        results.append(("Get Recommendations", test_get_recommendations(token)))
    
    # Test login with registered student
    login_token = test_student_login("teststudent@example.com", "test123")
    results.append(("Student Login", login_token is not None))
    
    # Search test (no auth required)
    results.append(("Search Internships", test_search_internships()))
    
    # Admin tests
    admin_token = test_admin_login()
    results.append(("Admin Login", admin_token is not None))
    
    if admin_token:
        results.append(("Admin Summary", test_admin_summary(admin_token)))
        results.append(("Admin View Internships", test_admin_view_internships(admin_token)))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Check the server logs and ensure it's running.")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server!")
        print("   Make sure the server is running:")
        print("   uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
