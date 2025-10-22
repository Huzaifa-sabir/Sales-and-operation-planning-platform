# S&OP Portal - Quick Start Guide

## For Developers Starting with This Project

This is a complete S&OP (Sales & Operations Planning) Portal with FastAPI backend and React frontend.

---

## Prerequisites

- **Python**: 3.11+
- **Node.js**: 18+
- **MongoDB**: 6.0+ (local or Atlas)
- **Git**: Latest version

---

## Backend Setup (5 minutes)

### 1. Navigate to Backend Directory
```bash
cd sop-portal-backend
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create `.env` file in `sop-portal-backend/`:
```env
# Database
MONGODB_URI=mongodb://localhost:27017/sop_portal

# JWT Secret (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Email (optional for notifications)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 5. Start Backend
```bash
python run.py
```

Expected output:
```
INFO - Starting S&OP Portal v1.0.0
INFO - Creating database indexes...
INFO - Initializing default settings...
INFO - Starting background scheduler...
INFO - Uvicorn running on http://0.0.0.0:8000
```

### 6. Verify Backend
Open browser: http://localhost:8000/api/docs

You should see the Swagger UI with all API endpoints.

---

## Frontend Setup (3 minutes)

### 1. Navigate to Frontend Directory
```bash
cd sop-portal-frontend
```

### 2. Install Dependencies
```bash
npm install
```

### 3. Configure Environment
Create `.env` file in `sop-portal-frontend/`:
```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=S&OP Portal
VITE_APP_VERSION=1.0.0
```

### 4. Start Frontend
```bash
npm run dev
```

Expected output:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 5. Verify Frontend
Open browser: http://localhost:5173

---

## Default Admin Account

After first backend startup, a default admin account is created:

```
Email: admin@sopportal.com
Password: admin123
```

**IMPORTANT**: Change this password immediately after first login!

---

## Project Structure

```
d:\Heavy\
├── sop-portal-backend/          # FastAPI Backend
│   ├── app/
│   │   ├── config/              # Configuration (database, settings, indexes)
│   │   ├── middleware/          # Middleware (rate limiting)
│   │   ├── models/              # Pydantic models (10 models)
│   │   ├── routers/             # API endpoints (12 routers, 60+ endpoints)
│   │   ├── services/            # Business logic (12 services)
│   │   ├── utils/               # Utilities (email, excel, scheduler, auth)
│   │   └── main.py              # Application entry point
│   ├── storage/
│   │   ├── uploads/             # Uploaded files
│   │   └── reports/             # Generated reports
│   ├── requirements.txt         # Python dependencies
│   ├── run.py                   # Start script
│   └── .env                     # Environment variables
│
├── sop-portal-frontend/         # React Frontend
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   ├── context/             # React context (state)
│   │   ├── hooks/               # Custom hooks
│   │   └── App.tsx              # Root component
│   ├── package.json             # Node dependencies
│   └── .env                     # Environment variables
│
└── FRONTEND_BACKEND_INTEGRATION_GUIDE.md  # Complete API documentation
```

---

## Key Features

### ✅ Authentication & Authorization
- JWT-based authentication
- Role-based access control (Admin, Sales Rep, Manager)
- Session management

### ✅ User Management
- User CRUD operations
- Role assignment
- Profile management

### ✅ Data Management
- **Customers**: Territory-based customer management
- **Products**: Item catalog with categories
- **Pricing Matrix**: Customer-product pricing
- **Sales History**: Historical sales data tracking

### ✅ S&OP Cycle Management
- Create and manage planning cycles
- Cycle status workflow (DRAFT → OPEN → CLOSED)
- Automatic cycle closure

### ✅ Forecasting
- Submit forecasts by customer-product-month
- Approval workflow (DRAFT → SUBMITTED → APPROVED/REJECTED)
- Historical forecast tracking

### ✅ Reporting
- Pre-built reports with caching
- Excel export
- Email delivery

### ✅ System Settings
- 16 configurable system settings
- Category-based organization
- Public/private settings

### ✅ Audit Logging
- 30+ tracked actions
- User activity history
- Entity change tracking
- Critical event monitoring

### ✅ Notifications
- Email notifications for:
  - New cycle opened
  - Deadline reminders
  - Submission confirmations

### ✅ Background Jobs
- Automated deadline reminders (daily 9 AM)
- Auto-close cycles (every hour)
- Cleanup old files (daily 2 AM)
- Archive audit logs (weekly)

### ✅ Security
- Rate limiting (60 req/min)
- Password hashing
- Input validation
- CORS protection

---

## Common Development Tasks

### Create New Admin User
```python
from app.services.user_service import UserService
from app.models.user import UserCreate

user_data = UserCreate(
    firstName="John",
    lastName="Doe",
    email="john@example.com",
    password="password123",
    employeeId="EMP001",
    role="admin"
)
await user_service.create_user(user_data)
```

### Test API Endpoint
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@sopportal.com&password=admin123"

# Use token
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Add New API Endpoint

1. Create model in `app/models/`
2. Create service in `app/services/`
3. Create router in `app/routers/`
4. Register router in `app/routers/__init__.py`

### Generate New Report

1. Add report type to `app/models/report.py`
2. Implement generation logic in `app/services/report_service.py`
3. Add endpoint in `app/routers/reports.py`

---

## API Endpoints Overview

| Endpoint | Description | Auth Required |
|----------|-------------|---------------|
| `POST /auth/login` | Login | No |
| `GET /auth/me` | Current user | Yes |
| `GET /users` | List users | Admin |
| `GET /customers` | List customers | Yes |
| `GET /products` | List products | Yes |
| `GET /sop-cycles` | List cycles | Yes |
| `POST /forecasts` | Submit forecast | Yes |
| `GET /reports/forecast-summary/{cycleId}` | Generate report | Yes |
| `GET /settings/public` | Public settings | No |
| `GET /audit-logs` | Audit logs | Admin |

**Full API documentation**: See [FRONTEND_BACKEND_INTEGRATION_GUIDE.md](FRONTEND_BACKEND_INTEGRATION_GUIDE.md)

---

## Testing

### Backend Tests
```bash
cd sop-portal-backend
pytest
```

### Frontend Tests
```bash
cd sop-portal-frontend
npm test
```

### Manual Testing
1. Start both backend and frontend
2. Open http://localhost:5173
3. Login with admin credentials
4. Test core workflows:
   - Create customer/product
   - Create S&OP cycle
   - Submit forecast
   - Generate report
   - View audit logs

---

## Troubleshooting

### Backend won't start
- **Check MongoDB**: Ensure MongoDB is running
  ```bash
  # Check if MongoDB is running
  mongosh --eval "db.version()"
  ```
- **Check port**: Port 8000 might be in use
  ```bash
  # Change PORT in .env
  PORT=8001
  ```

### Frontend API calls fail
- **Check CORS**: Ensure frontend URL is in `CORS_ORIGINS`
- **Check backend**: Ensure backend is running on correct port
- **Check .env**: Verify `VITE_API_URL` is correct

### Rate limit errors
- **Adjust limit**: Change `requests_per_minute` in settings
- **Wait**: Wait 60 seconds for rate limit to reset

### Email notifications not working
- **SMTP credentials**: Verify `SMTP_USER` and `SMTP_PASSWORD`
- **Enable notifications**: Check `notification_email_enabled` setting
- **Gmail users**: Use App Password, not regular password

### Background jobs not running
- **Check logs**: Look for scheduler startup in logs
- **Check settings**: Verify `auto_close_cycles` is enabled
- **Restart**: Restart backend to reinitialize scheduler

---

## Development Workflow

### Adding New Feature

1. **Plan the feature**
   - Define data model
   - Plan API endpoints
   - Design UI components

2. **Backend implementation**
   ```bash
   # Create model
   app/models/my_feature.py

   # Create service
   app/services/my_feature_service.py

   # Create router
   app/routers/my_feature.py

   # Register router
   # Edit app/routers/__init__.py
   ```

3. **Frontend implementation**
   ```bash
   # Create API service
   src/services/myFeatureService.ts

   # Create components
   src/components/MyFeature/

   # Add routes
   # Edit src/App.tsx
   ```

4. **Test the feature**
   - Manual testing
   - Unit tests
   - Integration tests

5. **Document the feature**
   - Update API docs
   - Add to integration guide
   - Update README

---

## Production Deployment

### Quick Checklist
- [ ] Set `DEBUG=False`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure production MongoDB
- [ ] Set production SMTP credentials
- [ ] Update `CORS_ORIGINS`
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure backups

**Full deployment guide**: See [STEP_10_IMPLEMENTATION_SUMMARY.md](STEP_10_IMPLEMENTATION_SUMMARY.md#production-deployment-checklist)

---

## Useful Commands

### Backend
```bash
# Start backend
python run.py

# Run with auto-reload
uvicorn app.main:app --reload

# Check Python version
python --version

# Install new package
pip install package-name
pip freeze > requirements.txt
```

### Frontend
```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Install new package
npm install package-name
```

### Database
```bash
# Connect to MongoDB
mongosh

# List databases
show dbs

# Use database
use sop_portal

# List collections
show collections

# Query collection
db.users.find()

# Create backup
mongodump --db sop_portal --out backup/

# Restore backup
mongorestore --db sop_portal backup/sop_portal/
```

---

## Resources

- **API Documentation**: http://localhost:8000/api/docs
- **Integration Guide**: [FRONTEND_BACKEND_INTEGRATION_GUIDE.md](FRONTEND_BACKEND_INTEGRATION_GUIDE.md)
- **Implementation Details**: [STEP_10_IMPLEMENTATION_SUMMARY.md](STEP_10_IMPLEMENTATION_SUMMARY.md)
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **MongoDB Docs**: https://www.mongodb.com/docs/

---

## Support

For issues or questions:
1. Check the documentation files
2. Review API docs at `/api/docs`
3. Check application logs
4. Verify environment configuration

---

## Next Steps

1. ✅ **Setup complete** - Backend and frontend running
2. **Explore the application** - Login and test features
3. **Read integration guide** - Understand API structure
4. **Review codebase** - Familiarize with patterns
5. **Start development** - Add new features or customize

---

**Last Updated**: October 18, 2025
**Version**: 1.0.0
**Status**: Production Ready
