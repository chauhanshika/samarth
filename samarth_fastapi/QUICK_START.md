# 🚀 Quick Start - Testing SAMARTH Backend

## Step 1: Install Dependencies

```bash
cd samarth
pip install -r requirements.txt
```

## Step 2: Start the Server

```bash
uvicorn app.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

## Step 3: Verify It's Working

### Option A: Browser (Easiest)
1. Open browser and go to: **http://localhost:8000/docs**
2. You'll see the interactive API documentation
3. Click "Try it out" on any endpoint to test it

### Option B: Health Check
Open in browser: **http://localhost:8000/health**

Should show: `{"status":"healthy"}`

### Option C: Run Test Script
In a **new terminal** (keep server running):
```bash
cd samarth
python test_api.py
```

This will run all tests automatically!

## Step 4: Quick Manual Tests

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

### Test 2: Register a Student
Go to http://localhost:8000/docs → `/student/register` → Try it out

Or use curl:
```bash
curl -X POST "http://localhost:8000/student/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"test123\",\"full_name\":\"Test User\",\"skills\":[\"Python\"],\"location\":\"Delhi\"}"
```

### Test 3: Admin Login
Go to http://localhost:8000/docs → `/admin/login` → Try it out

Use credentials:
- Email: `admin@samarth.gov`
- Password: `admin123`

## ✅ Success Indicators

- ✅ Server starts without errors
- ✅ Can access http://localhost:8000/docs
- ✅ Health check returns `{"status":"healthy"}`
- ✅ Can register a student
- ✅ Can login as admin
- ✅ Can get recommendations

## 🐛 Troubleshooting

**Port already in use?**
```bash
uvicorn app.main:app --reload --port 8001
```

**Module not found?**
Make sure you're in the `samarth` directory:
```bash
cd samarth
uvicorn app.main:app --reload
```

**Import errors?**
Check that all files exist in the correct structure.

## 📚 More Details

See `TESTING_GUIDE.md` for comprehensive testing instructions.
