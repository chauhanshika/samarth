# Testing Guide - SAMARTH Backend

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd samarth
pip install -r requirements.txt
```

### 2. Start the Server
```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. Verify Server is Running

Open your browser and go to:
- **API Root**: http://localhost:8000
- **Interactive Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 🧪 Testing Methods

### Method 1: Using Swagger UI (Easiest)

1. Go to http://localhost:8000/docs
2. You'll see all available endpoints
3. Click "Try it out" on any endpoint
4. Fill in the required fields
5. Click "Execute"
6. See the response

### Method 2: Using cURL (Command Line)

#### Test Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy"}
```

#### Test Student Registration
```bash
curl -X POST "http://localhost:8000/student/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123",
    "full_name": "John Doe",
    "skills": ["Python", "FastAPI"],
    "interests": ["Web Development"],
    "location": "Delhi"
  }'
```

#### Test Student Login
```bash
curl -X POST "http://localhost:8000/student/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "password123"
  }'
```

Save the `token` from the response!

#### Test Get Profile (Use token from login)
```bash
curl -X GET "http://localhost:8000/student/profile" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

#### Test Admin Login
```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@samarth.gov",
    "password": "admin123"
  }'
```

#### Test Get Recommendations
```bash
curl -X POST "http://localhost:8000/student/recommend" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "limit": 5
  }'
```

### Method 3: Using Python Requests

Create a test file `test_api.py`:

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Test Health Check
response = requests.get(f"{BASE_URL}/health")
print("Health Check:", response.json())

# 2. Register a student
register_data = {
    "email": "test@example.com",
    "password": "test123",
    "full_name": "Test User",
    "skills": ["Python", "FastAPI"],
    "interests": ["Web Development"],
    "location": "Delhi"
}
response = requests.post(f"{BASE_URL}/student/register", json=register_data)
print("Registration:", response.json())
token = response.json()["token"]

# 3. Get Profile
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/student/profile", headers=headers)
print("Profile:", response.json())

# 4. Get Recommendations
response = requests.post(
    f"{BASE_URL}/student/recommend",
    headers=headers,
    json={"limit": 5}
)
print("Recommendations:", response.json())

# 5. Admin Login
admin_data = {
    "email": "admin@samarth.gov",
    "password": "admin123"
}
response = requests.post(f"{BASE_URL}/admin/login", json=admin_data)
print("Admin Login:", response.json())
admin_token = response.json()["token"]

# 6. Get Admin Summary
admin_headers = {"Authorization": f"Bearer {admin_token}"}
response = requests.get(f"{BASE_URL}/admin/summary", headers=admin_headers)
print("Admin Summary:", response.json())
```

Run it:
```bash
python test_api.py
```

---

## ✅ Expected Results

### Health Check
```json
{"status": "healthy"}
```

### Student Registration
```json
{
  "student_id": 1,
  "email": "student@example.com",
  "full_name": "John Doe",
  "token": "long_random_token_string"
}
```

### Recommendations
```json
[
  {
    "internship": {
      "id": 4,
      "title": "Government Digital Services Intern",
      "description": "...",
      "skills_required": ["Python", "Database", "API Development"],
      "location": "Delhi",
      "source": "admin",
      "admin_can_apply": true,
      "apply_url": null,
      "created_at": "2024-01-01T12:00:00"
    },
    "score": 75.5,
    "can_apply": true
  },
  ...
]
```

### Admin Summary
```json
{
  "total_submissions": 0,
  "total_allocations": 0,
  "total_interns": 0,
  "pending_applications": 0
}
```

---

## 🔍 Common Issues

### Port Already in Use
If port 8000 is busy:
```bash
uvicorn app.main:app --reload --port 8001
```

### Module Not Found
Make sure you're in the `samarth` directory or install as package:
```bash
pip install -e .
```

### Import Errors
Check that all files are in the correct structure and `__init__.py` files exist.

---

## 📝 Quick Test Checklist

- [ ] Server starts without errors
- [ ] Health check returns `{"status": "healthy"}`
- [ ] Swagger UI loads at `/docs`
- [ ] Can register a new student
- [ ] Can login with registered student
- [ ] Can get student profile with token
- [ ] Can get recommendations
- [ ] Can login as admin
- [ ] Can view admin summary
- [ ] Can search internships
- [ ] Can apply to admin-added internship (not scraper ones)

---

## 🎯 Test Scenarios

### Scenario 1: Complete Student Flow
1. Register → Get token
2. Login → Verify token works
3. Update profile → Add more skills
4. Get recommendations → Should see scored internships
5. Search internships → Filter by location/skills
6. Apply to admin internship → Should succeed
7. Try to apply to scraper internship → Should fail with error

### Scenario 2: Complete Admin Flow
1. Login as admin → Get token
2. View summary → See dashboard stats
3. Add new internship → Create admin-added internship
4. View all internships → See both scraper and admin internships
5. View applications → See student applications
6. Allocate internship → Approve an application

---

Happy Testing! 🚀
