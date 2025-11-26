# ✅ How to Check if SAMARTH Backend is Working

## 🎯 Quick Verification (3 Steps)

### Step 1: Install Dependencies
```bash
cd samarth
pip install -r requirements.txt
```

### Step 2: Start the Server
```bash
uvicorn app.main:app --reload
```

**Look for this output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 3: Test It

**Option A: Open in Browser (Easiest)**
- Go to: **http://localhost:8000/docs**
- You should see the Swagger UI with all API endpoints
- Click "Try it out" on any endpoint to test

**Option B: Health Check**
- Open: **http://localhost:8000/health**
- Should show: `{"status":"healthy"}`

**Option C: Run Test Script**
```bash
# In a new terminal (keep server running)
cd samarth
python test_api.py
```

---

## 🔍 Detailed Verification

### 1. Check Server is Running
Open browser: http://localhost:8000

Should see:
```json
{
  "message": "Welcome to SAMARTH Backend API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### 2. Check Interactive Docs
Open: http://localhost:8000/docs

You should see:
- ✅ All student routes listed
- ✅ All admin routes listed
- ✅ "Try it out" buttons on each endpoint

### 3. Test Student Registration
In Swagger UI:
1. Find `/student/register`
2. Click "Try it out"
3. Fill in:
   ```json
   {
     "email": "test@example.com",
     "password": "test123",
     "full_name": "Test User",
     "skills": ["Python"],
     "location": "Delhi"
   }
   ```
4. Click "Execute"
5. Should get response with `student_id` and `token`

### 4. Test Admin Login
In Swagger UI:
1. Find `/admin/login`
2. Click "Try it out"
3. Fill in:
   ```json
   {
     "email": "admin@samarth.gov",
     "password": "admin123"
   }
   ```
4. Click "Execute"
5. Should get response with `admin_id` and `token`

### 5. Test Recommendations
1. First register/login as student (get token)
2. Find `/student/recommend`
3. Click "Try it out"
4. Click "Authorize" button (top right)
5. Enter: `Bearer YOUR_TOKEN_HERE`
6. Fill in request body:
   ```json
   {
     "limit": 5
   }
   ```
7. Click "Execute"
8. Should get list of internships with scores

---

## ✅ Success Checklist

- [ ] Server starts without errors
- [ ] Can access http://localhost:8000
- [ ] Can access http://localhost:8000/docs
- [ ] Health check returns `{"status":"healthy"}`
- [ ] Can register a student
- [ ] Can login as admin
- [ ] Can get student profile (with token)
- [ ] Can get recommendations
- [ ] Can search internships
- [ ] Can view admin summary

---

## 🐛 Common Issues & Fixes

### Issue: "ModuleNotFoundError: email-validator"
**Fix:**
```bash
pip install email-validator
```

### Issue: "Port already in use"
**Fix:**
```bash
uvicorn app.main:app --reload --port 8001
```

### Issue: "Cannot import app"
**Fix:**
Make sure you're in the `samarth` directory:
```bash
cd samarth
uvicorn app.main:app --reload
```

### Issue: "Connection refused"
**Fix:**
- Make sure server is running
- Check the port (default: 8000)
- Try: http://127.0.0.1:8000 instead of localhost

---

## 📊 Expected Test Results

When you run `python test_api.py`, you should see:

```
🧪 SAMARTH Backend API Test Suite
============================================================

✅ PASS - Health Check
✅ PASS - Root Endpoint
✅ PASS - Student Registration
✅ PASS - Get Profile
✅ PASS - Get Recommendations
✅ PASS - Student Login
✅ PASS - Search Internships
✅ PASS - Admin Login
✅ PASS - Admin Summary
✅ PASS - Admin View Internships

✅ Passed: 10/10
🎉 All tests passed! Backend is working correctly!
```

---

## 🎉 You're All Set!

If all checks pass, your backend is working correctly! 🚀

For more detailed testing, see `TESTING_GUIDE.md`
