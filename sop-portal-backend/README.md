# S&OP Portal Backend API

Backend API for the Sales & Operations Planning Portal built with FastAPI and MongoDB.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- MongoDB 4.4+ (local or MongoDB Atlas)

### Installation

1. **Create and activate virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
# Copy .env.example to .env
cp .env.example .env

# Edit .env file with your configuration
```

4. **Install and start MongoDB:**

**Option 1: MongoDB Atlas (Cloud)**
- Create free account at https://www.mongodb.com/cloud/atlas
- Create cluster and get connection string
- Update `MONGODB_URL` in .env file

**Option 2: Local MongoDB**
```bash
# Windows - Download from https://www.mongodb.com/try/download/community
# After installation, MongoDB runs as a service

# Linux
sudo apt-get install -y mongodb
sudo systemctl start mongodb

# Mac
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

5. **Run the application:**
```bash
# Using run.py
python run.py

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the API:**
- API: http://localhost:8000
- Interactive API docs: http://localhost:8000/api/docs
- Alternative docs: http://localhost:8000/api/redoc

## 📁 Project Structure

```
sop-portal-backend/
├── app/
│   ├── config/           # Configuration files
│   │   ├── settings.py   # Environment settings
│   │   └── database.py   # Database connection
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas (request/response)
│   ├── routers/          # API route handlers
│   ├── services/         # Business logic
│   ├── utils/            # Utility functions
│   └── main.py           # FastAPI application
├── uploads/              # Temporary file uploads
├── .env                  # Environment variables
├── .env.example          # Environment template
├── requirements.txt      # Python dependencies
├── run.py                # Run script
└── README.md             # This file
```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```env
# Database
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=sop_portal

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=480

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Email (optional)
EMAIL_ENABLED=False
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 📋 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - User logout

### Users (Admin only)
- `GET /api/v1/users` - List users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

### Customers
- `GET /api/v1/customers` - List customers
- `POST /api/v1/customers` - Create customer
- `GET /api/v1/customers/{id}` - Get customer
- `PUT /api/v1/customers/{id}` - Update customer
- `DELETE /api/v1/customers/{id}` - Delete customer
- `POST /api/v1/customers/import` - Import from Excel
- `GET /api/v1/customers/export` - Export to Excel

### Products
- `GET /api/v1/products` - List products
- `POST /api/v1/products` - Create product
- `GET /api/v1/products/{id}` - Get product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `POST /api/v1/products/import` - Import from Excel
- `GET /api/v1/products/export` - Export to Excel

### Sales History
- `GET /api/v1/sales-history` - Get sales history with filters

### S&OP Cycles (Admin only)
- `GET /api/v1/sop/cycles` - List cycles
- `POST /api/v1/sop/cycles` - Create cycle
- `GET /api/v1/sop/cycles/{id}` - Get cycle
- `PUT /api/v1/sop/cycles/{id}` - Update cycle
- `DELETE /api/v1/sop/cycles/{id}` - Delete cycle
- `POST /api/v1/sop/cycles/{id}/open` - Open cycle
- `POST /api/v1/sop/cycles/{id}/close` - Close cycle
- `POST /api/v1/sop/cycles/{id}/notify` - Send notifications

### Forecasts
- `GET /api/v1/forecasts` - Get forecasts
- `POST /api/v1/forecasts` - Save forecast draft
- `PUT /api/v1/forecasts/{id}` - Update forecast
- `POST /api/v1/forecasts/{id}/submit` - Submit forecast

### Reports
- `POST /api/v1/reports/generate` - Generate report
- `GET /api/v1/reports/{id}/download` - Download report

### Settings (Admin only)
- `GET /api/v1/settings` - Get settings
- `PUT /api/v1/settings` - Update settings

## 🗄️ Database Schema

### Collections:
- **users** - System users (admin, sales_rep)
- **customers** - Customer master data
- **products** - Product master data
- **productCustomerMatrix** - Customer-product relationships
- **salesHistory** - Historical sales data
- **sopCycles** - S&OP planning cycles
- **sopForecasts** - Forecast data
- **sopSubmissions** - Forecast submission tracking

See `MONGODB_SCHEMA.md` for detailed schema documentation.

## 🔐 Authentication

- JWT-based authentication
- Access tokens expire after 8 hours (configurable)
- Role-based access control (Admin, Sales Rep)
- Password hashing with bcrypt

### Default Users

**Admin:**
- Username: `admin`
- Password: `admin123`
- Email: admin@heavygarlic.com

**Sales Rep:**
- Username: `sales`
- Password: `sales123`
- Email: sales@heavygarlic.com

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## 📦 Dependencies

### Core
- **FastAPI** - Modern web framework
- **Uvicorn** - ASGI server
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation

### Authentication
- **python-jose** - JWT tokens
- **passlib** - Password hashing
- **bcrypt** - Secure hashing algorithm

### Utilities
- **openpyxl** - Excel file handling
- **pandas** - Data manipulation
- **aiosmtplib** - Async email sending
- **jinja2** - Email templates

## 🚀 Deployment

### Using Docker (Coming soon)
```bash
docker build -t sop-portal-api .
docker run -p 8000:8000 sop-portal-api
```

### Manual Deployment
1. Set up Python environment on server
2. Install dependencies
3. Configure production .env file
4. Set up MongoDB (Atlas recommended for production)
5. Run with production ASGI server (Gunicorn + Uvicorn)

## 📝 Development Status

### ✅ Completed
- [x] Project structure
- [x] Environment configuration
- [x] Database connection setup
- [x] CORS middleware
- [x] Basic application setup

### 🚧 In Progress
- [ ] Authentication endpoints
- [ ] User management
- [ ] Customer & Product APIs
- [ ] Sales History API
- [ ] S&OP Cycle management
- [ ] Forecast entry system
- [ ] Reports generation
- [ ] Excel import/export
- [ ] Email notifications

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit pull request

## 📄 License

Proprietary - Heavy Garlic

## 📧 Support

For support, email support@heavygarlic.com

---

**Version:** 1.0.0
**Last Updated:** October 17, 2025
