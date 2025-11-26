# SAMARTH Backend API

A complete FastAPI backend for the SAMARTH internship platform, supporting both Students (Appliers) and Government Admins.

## 🚀 Features

### Student Features
- ✅ Student registration and login
- ✅ Profile view and update
- ✅ Internship search (by keyword, location, skills)
- ✅ Personalized internship recommendations
- ✅ Apply for internships (only admin-added internships)

### Admin Features
- ✅ Admin login
- ✅ Dashboard with summary statistics
- ✅ Manually add internships
- ✅ View all internships (scraper + admin-added)
- ✅ View all applications
- ✅ Allocate internships to students

### Matching Engine
- ✅ Rule-based scoring model
- ✅ Score calculation based on:
  - Skill match (0-50 points)
  - Location match (0-30 points)
  - Interest match (0-20 points)
- ✅ Sorted recommendations (highest score first)
- ✅ Apply button logic: Only admin-added internships can be applied to

## 📁 Project Structure

```
samarth/
│ app/
│   main.py                 # FastAPI app entry point
│   routes/
│     student_routes.py     # Student endpoints
│     admin_routes.py       # Admin endpoints
│     internship_routes.py  # General internship routes
│   schemas/
│     student_schema.py     # Student Pydantic schemas
│     admin_schema.py       # Admin Pydantic schemas
│     internship_schema.py  # Internship Pydantic schemas
│     application_schema.py # Application/Allocation schemas
│   services/
│     matching_engine.py    # Recommendation scoring logic
│   utils/
│     helpers.py            # Dummy data storage & utilities
│   __init__.py
requirements.txt
README.md
```

## 🛠️ Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

   Or:
   ```bash
   python -m uvicorn app.main:app --reload
   ```

3. **Access the API:**
   - API: http://localhost:8000
   - Interactive Docs: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## 📡 API Endpoints

### Student Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/student/register` | Register a new student |
| POST | `/student/login` | Student login |
| GET | `/student/profile` | Get student profile |
| PUT | `/student/profile/update` | Update student profile |
| GET | `/student/internships/search` | Search internships |
| POST | `/student/recommend` | Get personalized recommendations |
| POST | `/student/apply/{internship_id}` | Apply for an internship |

### Admin Routes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/admin/login` | Admin login |
| GET | `/admin/summary` | Get dashboard summary |
| POST | `/admin/internships/add` | Add a new internship |
| GET | `/admin/internships` | View all internships |
| GET | `/admin/applications` | View all applications |
| POST | `/admin/allocate/{application_id}` | Allocate internship to student |

## 🔐 Authentication

Currently using simple token-based authentication (stored in memory).

**Default Admin Credentials:**
- Email: `admin@samarth.gov`
- Password: `admin123`

**Note:** In production, implement:
- JWT tokens
- Password hashing (bcrypt)
- Token expiration
- Refresh tokens

## 📊 Data Models

### Internships
- Two types: `scraper` and `admin`
- Scraper internships: Only for recommendations (no apply button)
- Admin internships: Can be recommended AND applied to

### Applications
- Students can only apply to admin-added internships
- Status: `pending`, `approved`, `rejected`, `allocated`

### Allocations
- Created when admin allocates an internship to a student
- Status: `allocated`, `completed`, `cancelled`

## 🧪 Testing

The backend includes dummy data for testing:
- 3 scraper-added internships
- 2 admin-added internships
- 1 default admin account

You can test the API using:
- Interactive Swagger UI at `/docs`
- Postman or any HTTP client
- cURL commands

## 🔄 Next Steps (TODO)

1. **Database Integration:**
   - Replace dummy data with SQLAlchemy + PostgreSQL
   - Add proper migrations

2. **Security:**
   - Implement password hashing
   - Add JWT authentication
   - Add rate limiting

3. **Scraper Integration:**
   - Connect scraper service to add internships
   - Set `source="scraper"` for scraper-added internships

4. **ML Integration:**
   - Replace rule-based matching with ML model
   - Add feature engineering pipeline

5. **Additional Features:**
   - Email notifications
   - File uploads (resumes, documents)
   - Application status tracking
   - Student dashboard

## 📝 Notes

- All data is currently stored in-memory (dummy data)
- Data will be lost on server restart
- Designed to be easily migrated to a real database
- All models and schemas are production-ready

## 🤝 Contributing

This is a SIH-level project. For production use, implement:
- Database persistence
- Proper authentication
- Error handling
- Logging
- Testing suite
- CI/CD pipeline

## 📄 License

This project is part of the SAMARTH platform.
