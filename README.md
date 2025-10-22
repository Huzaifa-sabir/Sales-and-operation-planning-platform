# S&OP Portal - Sales & Operations Planning System

A comprehensive web-based Sales & Operations Planning (S&OP) portal built with FastAPI and React, designed to streamline forecast management, reporting, and collaborative planning processes.

[![Status](https://img.shields.io/badge/status-production--ready-green)]()
[![Backend](https://img.shields.io/badge/backend-FastAPI-009688)]()
[![Frontend](https://img.shields.io/badge/frontend-React-61DAFB)]()
[![Database](https://img.shields.io/badge/database-MongoDB-47A248)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

---

## Overview

The S&OP Portal is an enterprise-grade solution for managing sales forecasting cycles, customer-product relationships, pricing matrices, and generating comprehensive reports. It features role-based access control, automated notifications, background job scheduling, and comprehensive audit logging.

### Key Capabilities

- **User Management**: Role-based access control (Admin, Manager, Sales Rep)
- **Data Management**: Customers, products, pricing matrix, sales history
- **S&OP Cycles**: Create and manage planning cycles with automated workflows
- **Forecasting**: Submit and approve forecasts with multi-level review process
- **Reporting**: Generate Excel reports with caching and email delivery
- **System Settings**: Configurable system parameters without code changes
- **Audit Logging**: Comprehensive tracking of all critical actions
- **Notifications**: Automated email notifications for key events
- **Background Jobs**: Scheduled tasks for reminders, cleanup, and automation

---

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- MongoDB 6.0+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Heavy
   ```

2. **Setup Backend** (2 minutes)
   ```bash
   cd sop-portal-backend
   python -m venv venv
   source venv/Scripts/activate  # Windows
   pip install -r requirements.txt

   # Create .env file with MongoDB and SMTP credentials
   python run.py
   ```

3. **Setup Frontend** (2 minutes)
   ```bash
   cd sop-portal-frontend
   npm install

   # Create .env file with API URL
   npm run dev
   ```

4. **Access the Application**
   - Backend API: http://localhost:8000/api/docs
   - Frontend UI: http://localhost:5173
   - Default login: `admin@sopportal.com` / `admin123`

**Detailed setup instructions**: See [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              React Frontend (TypeScript)            │
│  Authentication, Data Management, Reporting UI      │
└───────────────────┬─────────────────────────────────┘
                    │ REST API (JWT Auth)
┌───────────────────▼─────────────────────────────────┐
│         Rate Limiter (60 req/min)                   │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│              FastAPI Backend (Python)                │
│  ┌──────────────────────────────────────────────┐   │
│  │ 12 Routers | 60+ Endpoints | 12 Services    │   │
│  └──────────────────────────────────────────────┘   │
└───────────────────┬─────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────┐
│              MongoDB (10 Collections)                │
│  Users, Customers, Products, Cycles, Forecasts,     │
│  Reports, Settings, Audit Logs, etc.                │
└──────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────┐
│         Background Scheduler (APScheduler)           │
│  • Deadline Reminders (Daily 9 AM)                  │
│  • Auto-close Cycles (Hourly)                       │
│  • Cleanup Tasks (Daily/Weekly)                     │
└──────────────────────────────────────────────────────┘
```

---

## Features

### 🔐 Authentication & Authorization
- JWT-based authentication
- Role-based access control (RBAC)
- Session management with configurable timeout
- Password hashing with bcrypt

### 👥 User Management
- User CRUD operations
- Role assignment (Admin, Manager, Sales Rep)
- Profile management
- Activity tracking

### 📊 Data Management
- **Customers**: Territory-based customer organization
- **Products**: Item catalog with categories and descriptions
- **Pricing Matrix**: Customer-product-specific pricing
- **Sales History**: Historical sales data with monthly aggregation

### 🔄 S&OP Cycle Management
- Create planning cycles with start/end dates
- Cycle status workflow (DRAFT → OPEN → CLOSED)
- Automatic cycle closure after deadline
- Cycle performance analytics

### 📈 Forecasting
- Submit forecasts by customer-product-month
- Multi-level approval workflow (DRAFT → SUBMITTED → APPROVED/REJECTED)
- Comments and revision tracking
- Historical forecast comparison

### 📑 Reporting
- Pre-built report templates:
  - Forecast Summary by Cycle
  - Sales vs Forecast Comparison
  - Customer Performance Analysis
  - Product Performance Analysis
  - Territory Performance Analysis
- Excel export with formatting
- Report caching for performance
- Email delivery with attachments

### ⚙️ System Settings
- 16 configurable settings across 7 categories
- Public/private setting flags
- Category-based organization (General, Notifications, Email, Security, etc.)
- No code changes required for configuration updates

### 📝 Audit Logging
- 30+ tracked action types
- 4 severity levels (INFO, WARNING, ERROR, CRITICAL)
- User activity history
- Entity change tracking with before/after values
- Critical event monitoring
- Configurable retention (default: 90 days)

### 📧 Email Notifications
- Professional HTML email templates
- Automated notifications for:
  - New cycle opened (to all sales reps)
  - Deadline reminders (X days before close)
  - Submission confirmations (to submitter + admins)
- SMTP configuration via settings
- Enable/disable per event type

### ⏰ Background Jobs
- **Deadline Reminders**: Daily at 9 AM
- **Auto-close Cycles**: Every hour
- **Cleanup Temp Files**: Daily at 2 AM
- **Archive Audit Logs**: Weekly on Sunday at 3 AM
- Configurable schedules and thresholds

### 🛡️ Security Features
- Rate limiting (60 requests/minute)
- Input validation (Pydantic models)
- CORS protection
- Password complexity requirements
- IP address tracking
- Audit trail for compliance

---

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - User logout

### Users
- `GET /api/v1/users` - List users (admin)
- `POST /api/v1/users` - Create user (admin)
- `PUT /api/v1/users/{id}` - Update user (admin)
- `DELETE /api/v1/users/{id}` - Delete user (admin)

### S&OP Cycles
- `GET /api/v1/sop-cycles` - List cycles
- `POST /api/v1/sop-cycles` - Create cycle (admin)
- `PUT /api/v1/sop-cycles/{id}` - Update cycle (admin)
- `PUT /api/v1/sop-cycles/{id}/status` - Change status (admin)

### Forecasts
- `GET /api/v1/forecasts` - List forecasts
- `POST /api/v1/forecasts` - Submit forecast
- `PUT /api/v1/forecasts/{id}` - Update forecast
- `PUT /api/v1/forecasts/{id}/approve` - Approve forecast (manager)
- `PUT /api/v1/forecasts/{id}/reject` - Reject forecast (manager)

### Reports
- `GET /api/v1/reports/forecast-summary/{cycleId}` - Generate forecast summary
- `GET /api/v1/reports/sales-vs-forecast/{cycleId}` - Sales vs forecast comparison
- `GET /api/v1/reports/download/{reportId}` - Download report
- `POST /api/v1/reports/email` - Email report

### Settings
- `GET /api/v1/settings/public` - Get public settings (no auth)
- `GET /api/v1/settings` - List all settings (admin)
- `PUT /api/v1/settings/{key}` - Update setting (admin)

### Audit Logs
- `GET /api/v1/audit-logs` - List logs with filters (admin)
- `GET /api/v1/audit-logs/my-activity` - User's activity
- `GET /api/v1/audit-logs/entity/{type}/{id}` - Entity history
- `GET /api/v1/audit-logs/critical-events` - Critical events (admin)

**Complete API documentation**: http://localhost:8000/api/docs (when running)

**Integration guide**: See [FRONTEND_BACKEND_INTEGRATION_GUIDE.md](FRONTEND_BACKEND_INTEGRATION_GUIDE.md)

---

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Language**: Python 3.11+
- **Database**: MongoDB 6.0+ with Motor (async)
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Validation**: Pydantic 2.0+
- **Email**: aiosmtplib
- **Scheduler**: APScheduler
- **Excel**: openpyxl, pandas
- **Server**: Uvicorn (ASGI)

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **HTTP Client**: Axios
- **Routing**: React Router
- **UI**: Material-UI / Tailwind CSS

### Infrastructure
- **Database**: MongoDB (standalone or Atlas)
- **Reverse Proxy**: Nginx (recommended)
- **Deployment**: Docker / Kubernetes (optional)
- **File Storage**: Local / S3 (configurable)

---

## Project Structure

```
Heavy/
├── sop-portal-backend/              # FastAPI Backend
│   ├── app/
│   │   ├── config/                  # Configuration
│   │   │   ├── database.py          # MongoDB connection
│   │   │   ├── settings.py          # App settings
│   │   │   └── indexes.py           # Database indexes
│   │   ├── middleware/              # Middleware
│   │   │   └── rate_limiter.py      # Rate limiting
│   │   ├── models/                  # Pydantic models (10 files)
│   │   ├── routers/                 # API endpoints (12 routers)
│   │   ├── services/                # Business logic (12 services)
│   │   ├── utils/                   # Utilities
│   │   │   ├── auth_dependencies.py # Auth helpers
│   │   │   ├── email_service.py     # Email sending
│   │   │   ├── excel_processor.py   # Excel processing
│   │   │   ├── scheduler.py         # Background jobs
│   │   │   └── notification_templates.py  # Email templates
│   │   └── main.py                  # Application entry
│   ├── storage/
│   │   ├── uploads/                 # Uploaded files
│   │   └── reports/                 # Generated reports
│   ├── requirements.txt             # Python dependencies
│   └── run.py                       # Start script
│
├── sop-portal-frontend/             # React Frontend
│   ├── src/
│   │   ├── components/              # React components
│   │   ├── pages/                   # Page components
│   │   ├── services/                # API services
│   │   ├── context/                 # State management
│   │   ├── hooks/                   # Custom hooks
│   │   └── App.tsx                  # Root component
│   └── package.json                 # Node dependencies
│
├── QUICK_START_GUIDE.md             # Quick setup guide
├── FRONTEND_BACKEND_INTEGRATION_GUIDE.md  # API integration
├── STEP_10_IMPLEMENTATION_SUMMARY.md      # Detailed docs
└── README.md                        # This file
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md) | Quick setup and development guide |
| [FRONTEND_BACKEND_INTEGRATION_GUIDE.md](FRONTEND_BACKEND_INTEGRATION_GUIDE.md) | Complete API integration guide |
| [STEP_10_IMPLEMENTATION_SUMMARY.md](STEP_10_IMPLEMENTATION_SUMMARY.md) | Detailed implementation documentation |
| [/api/docs](http://localhost:8000/api/docs) | Interactive API documentation (Swagger UI) |

---

## Development

### Running Tests

**Backend**:
```bash
cd sop-portal-backend
pytest
```

**Frontend**:
```bash
cd sop-portal-frontend
npm test
```

### Adding New Features

1. **Backend**:
   - Create model in `app/models/`
   - Create service in `app/services/`
   - Create router in `app/routers/`
   - Register router in `app/routers/__init__.py`

2. **Frontend**:
   - Create API service in `src/services/`
   - Create components in `src/components/`
   - Add routes in `src/App.tsx`

3. **Test & Document**:
   - Write tests
   - Update API documentation
   - Update integration guide

### Code Quality

- **Type hints**: All Python code uses type hints
- **Validation**: Pydantic models for all data
- **Error handling**: Comprehensive exception handling
- **Logging**: Structured logging throughout
- **Documentation**: Docstrings on all functions
- **Security**: OWASP best practices

---

## Deployment

### Development
```bash
# Backend
cd sop-portal-backend
python run.py

# Frontend
cd sop-portal-frontend
npm run dev
```

### Production

**Backend**:
```bash
cd sop-portal-backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend**:
```bash
cd sop-portal-frontend
npm run build
# Serve dist/ folder with Nginx or static hosting
```

**Docker** (optional):
```bash
# Build images
docker build -t sop-portal-backend ./sop-portal-backend
docker build -t sop-portal-frontend ./sop-portal-frontend

# Run with docker-compose
docker-compose up -d
```

**Production checklist**: See [STEP_10_IMPLEMENTATION_SUMMARY.md](STEP_10_IMPLEMENTATION_SUMMARY.md#production-deployment-checklist)

---

## Configuration

### Backend Environment Variables

```env
# Database
MONGODB_URI=mongodb://localhost:27017/sop_portal

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# Email
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### Frontend Environment Variables

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=S&OP Portal
VITE_APP_VERSION=1.0.0
```

### System Settings (Configurable via UI/API)

All settings can be modified through the admin panel or API without code changes:

- Reminder days before cycle close (default: 3)
- Auto-close cycles (default: enabled)
- Email notifications (default: enabled)
- Rate limit threshold (default: 60 req/min)
- Session timeout (default: 8 hours)
- Report expiry (default: 30 days)
- Audit log retention (default: 90 days)
- File upload limits (default: 10 MB)

---

## Performance

### Optimizations Implemented

- ✅ **Database Indexes**: 30+ indexes for query optimization
- ✅ **Report Caching**: Generated reports cached for reuse
- ✅ **Async Operations**: All I/O operations are asynchronous
- ✅ **Connection Pooling**: MongoDB connection pooling
- ✅ **Pagination**: All list endpoints support pagination
- ✅ **Rate Limiting**: Prevents API abuse
- ✅ **Background Jobs**: Heavy operations in background

### Scalability

- **Horizontal scaling**: Stateless backend design
- **Database**: MongoDB supports sharding
- **File storage**: Can use S3 for distributed storage
- **Load balancing**: Multiple backend instances supported
- **Caching**: Ready for Redis integration

---

## Security

### Implemented Security Measures

- ✅ JWT authentication with expiration
- ✅ Password hashing with bcrypt
- ✅ Role-based access control (RBAC)
- ✅ Rate limiting (60 requests/minute)
- ✅ Input validation (Pydantic)
- ✅ CORS protection
- ✅ Audit logging for compliance
- ✅ IP address tracking
- ✅ File upload validation
- ✅ SQL injection prevention (NoSQL)
- ✅ XSS prevention (React escaping)
- ✅ Session timeout

### Security Best Practices

- Change default admin password immediately
- Use strong SECRET_KEY in production
- Enable HTTPS in production
- Regularly update dependencies
- Review audit logs periodically
- Implement backup strategy
- Use environment variables for secrets
- Enable monitoring and alerts

---

## Monitoring & Maintenance

### Application Health

- **Health Check**: `GET /health` endpoint
- **API Documentation**: `GET /api/docs`
- **Logs**: Check `logs/` directory or stdout
- **Audit Logs**: Review via admin panel or API

### Regular Maintenance

- **Daily**: Review critical audit events
- **Weekly**: Check background job execution
- **Monthly**: Update dependencies, review performance
- **Quarterly**: Full backup test, security audit

### Troubleshooting

Common issues and solutions documented in [QUICK_START_GUIDE.md](QUICK_START_GUIDE.md#troubleshooting)

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines

- Follow existing code style
- Add type hints to all functions
- Write tests for new features
- Update documentation
- Add audit logging for critical actions
- Follow security best practices

---

## License

This project is licensed under the MIT License.

---

## Support

### Documentation
- [Quick Start Guide](QUICK_START_GUIDE.md)
- [Integration Guide](FRONTEND_BACKEND_INTEGRATION_GUIDE.md)
- [Implementation Details](STEP_10_IMPLEMENTATION_SUMMARY.md)
- [API Docs](http://localhost:8000/api/docs) (when running)

### Troubleshooting
- Check application logs
- Verify environment configuration
- Review audit logs for errors
- Check MongoDB connection
- Verify SMTP credentials (for emails)

### Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [MongoDB Documentation](https://www.mongodb.com/docs/)
- [APScheduler Documentation](https://apscheduler.readthedocs.io/)

---

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - JavaScript library for user interfaces
- [MongoDB](https://www.mongodb.com/) - Document database
- [Motor](https://motor.readthedocs.io/) - Async MongoDB driver
- [APScheduler](https://apscheduler.readthedocs.io/) - Job scheduling
- [Pydantic](https://docs.pydantic.dev/) - Data validation

---

## Status

**Current Version**: 1.0.0
**Status**: ✅ Production Ready
**Last Updated**: October 18, 2025

### Completed Features

- ✅ Authentication & Authorization
- ✅ User Management
- ✅ Customer Management
- ✅ Product Management
- ✅ Pricing Matrix
- ✅ Sales History
- ✅ Excel Import/Export
- ✅ S&OP Cycle Management
- ✅ Forecasting & Approval Workflow
- ✅ Report Generation
- ✅ System Settings
- ✅ Audit Logging
- ✅ Email Notifications
- ✅ Background Job Scheduler
- ✅ Rate Limiting
- ✅ Performance Optimization
- ✅ Complete API Documentation

### Next Steps

- [ ] Frontend UI implementation
- [ ] Advanced analytics dashboard
- [ ] Real-time notifications (WebSocket)
- [ ] Mobile app support
- [ ] Advanced reporting templates
- [ ] Data export/import utilities
- [ ] Multi-language support
- [ ] Docker compose setup

---

**Made with ❤️ for efficient S&OP planning**
