# S&OP Portal - Project Architecture

## Technology Stack Summary

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Authentication**: JWT (JSON Web Tokens)
- **Excel Processing**: pandas, openpyxl
- **API Documentation**: Swagger/OpenAPI (auto-generated)
- **Validation**: Pydantic V2
- **Task Queue**: Celery + Redis (for background tasks)
- **Email**: python-email-validator, email sending library

### Frontend
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **State Management**: TanStack Query (React Query) + Zustand
- **Routing**: React Router v6
- **UI Library**: Ant Design (antd) - excellent for enterprise apps
- **Data Grid**: AG-Grid Community (Excel-like features)
- **Charts**: Recharts
- **Forms**: React Hook Form + Zod validation
- **HTTP Client**: Axios with interceptors
- **Excel Export**: SheetJS (xlsx)

### DevOps
- **Containerization**: Docker + Docker Compose
- **Web Server**: Nginx (reverse proxy)
- **Process Manager**: Uvicorn (ASGI server)
- **Environment**: python-dotenv

---

## Project Directory Structure

```
sop-portal/
│
├── backend/                          # Python FastAPI backend
│   ├── alembic/                      # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application entry
│   │   ├── config.py                 # Configuration settings
│   │   ├── database.py               # Database connection
│   │   │
│   │   ├── models/                   # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── customer.py
│   │   │   ├── product.py
│   │   │   ├── sales_history.py
│   │   │   ├── sop_cycle.py
│   │   │   ├── sop_forecast.py
│   │   │   └── ...
│   │   │
│   │   ├── schemas/                  # Pydantic schemas (API contracts)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── customer.py
│   │   │   ├── product.py
│   │   │   ├── forecast.py
│   │   │   └── ...
│   │   │
│   │   ├── api/                      # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── deps.py               # Dependencies (auth, db)
│   │   │   │
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py           # Login, logout, token refresh
│   │   │       ├── users.py          # User management
│   │   │       ├── customers.py      # Customer CRUD
│   │   │       ├── products.py       # Product CRUD
│   │   │       ├── sales_history.py  # Sales data
│   │   │       ├── sop_cycles.py     # S&OP cycle management
│   │   │       ├── forecasts.py      # Forecast CRUD
│   │   │       ├── imports.py        # Excel import endpoints
│   │   │       ├── exports.py        # Report export endpoints
│   │   │       └── dashboard.py      # Dashboard data
│   │   │
│   │   ├── services/                 # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── customer_service.py
│   │   │   ├── product_service.py
│   │   │   ├── import_service.py     # Excel import logic
│   │   │   ├── export_service.py     # Report generation
│   │   │   ├── forecast_service.py
│   │   │   ├── calculation_service.py # Averages, trends
│   │   │   └── email_service.py
│   │   │
│   │   ├── utils/                    # Utilities
│   │   │   ├── __init__.py
│   │   │   ├── security.py           # Password hashing, JWT
│   │   │   ├── excel_helper.py       # Excel processing
│   │   │   ├── date_helper.py        # Date calculations
│   │   │   └── validators.py
│   │   │
│   │   ├── core/                     # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   └── config.py
│   │   │
│   │   └── tasks/                    # Celery tasks (background)
│   │       ├── __init__.py
│   │       ├── import_tasks.py
│   │       └── report_tasks.py
│   │
│   ├── tests/                        # Unit and integration tests
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_customers.py
│   │   └── ...
│   │
│   ├── requirements.txt              # Python dependencies
│   ├── requirements-dev.txt          # Dev dependencies
│   ├── .env.example                  # Environment variables template
│   ├── alembic.ini                   # Alembic configuration
│   └── Dockerfile
│
├── frontend/                         # React frontend
│   ├── public/
│   │   ├── favicon.ico
│   │   └── index.html
│   │
│   ├── src/
│   │   ├── main.tsx                  # Application entry
│   │   ├── App.tsx                   # Root component
│   │   ├── vite-env.d.ts
│   │   │
│   │   ├── api/                      # API client
│   │   │   ├── axios.ts              # Axios configuration
│   │   │   ├── auth.ts
│   │   │   ├── customers.ts
│   │   │   ├── products.ts
│   │   │   ├── forecasts.ts
│   │   │   └── ...
│   │   │
│   │   ├── components/               # Reusable components
│   │   │   ├── common/
│   │   │   │   ├── Layout.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── Table.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   └── ...
│   │   │   │
│   │   │   ├── forms/
│   │   │   │   ├── CustomerForm.tsx
│   │   │   │   ├── ProductForm.tsx
│   │   │   │   └── ...
│   │   │   │
│   │   │   └── charts/
│   │   │       ├── SalesChart.tsx
│   │   │       ├── TrendChart.tsx
│   │   │       └── ...
│   │   │
│   │   ├── pages/                    # Page components
│   │   │   ├── auth/
│   │   │   │   ├── Login.tsx
│   │   │   │   └── ForgotPassword.tsx
│   │   │   │
│   │   │   ├── dashboard/
│   │   │   │   └── Dashboard.tsx
│   │   │   │
│   │   │   ├── customers/
│   │   │   │   ├── CustomerList.tsx
│   │   │   │   ├── CustomerDetail.tsx
│   │   │   │   └── CustomerImport.tsx
│   │   │   │
│   │   │   ├── products/
│   │   │   │   ├── ProductList.tsx
│   │   │   │   ├── ProductDetail.tsx
│   │   │   │   └── ProductImport.tsx
│   │   │   │
│   │   │   ├── sales-history/
│   │   │   │   └── SalesHistory.tsx
│   │   │   │
│   │   │   ├── sop/
│   │   │   │   ├── SOPCycleList.tsx
│   │   │   │   ├── SOPCycleDetail.tsx
│   │   │   │   ├── ForecastEntry.tsx     # Data entry page
│   │   │   │   ├── ForecastImport.tsx
│   │   │   │   └── ForecastReview.tsx
│   │   │   │
│   │   │   ├── reports/
│   │   │   │   ├── ReportList.tsx
│   │   │   │   └── ReportViewer.tsx
│   │   │   │
│   │   │   └── admin/
│   │   │       ├── UserManagement.tsx
│   │   │       └── SystemSettings.tsx
│   │   │
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── useCustomers.ts
│   │   │   ├── useProducts.ts
│   │   │   ├── useForecasts.ts
│   │   │   └── ...
│   │   │
│   │   ├── store/                    # Zustand stores
│   │   │   ├── authStore.ts
│   │   │   ├── uiStore.ts
│   │   │   └── ...
│   │   │
│   │   ├── types/                    # TypeScript types
│   │   │   ├── user.ts
│   │   │   ├── customer.ts
│   │   │   ├── product.ts
│   │   │   ├── forecast.ts
│   │   │   └── ...
│   │   │
│   │   ├── utils/                    # Utility functions
│   │   │   ├── formatters.ts
│   │   │   ├── validators.ts
│   │   │   ├── dateHelpers.ts
│   │   │   └── excelHelpers.ts
│   │   │
│   │   ├── styles/                   # Global styles
│   │   │   ├── globals.css
│   │   │   └── variables.css
│   │   │
│   │   └── config/
│   │       └── constants.ts
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── .env.example
│   └── Dockerfile
│
├── docker-compose.yml                # Docker orchestration
├── .gitignore
├── README.md
└── docs/
    ├── API.md                        # API documentation
    ├── DEPLOYMENT.md                 # Deployment guide
    └── USER_GUIDE.md                 # User manual

```

---

## Key Features Implementation

### 1. Authentication & Authorization

**Backend (FastAPI):**
```python
# JWT-based authentication
# Role-based access control (RBAC)
# Middleware for route protection

@router.post("/login")
async def login(credentials: LoginSchema):
    # Validate credentials
    # Generate JWT token
    # Return user + token

@router.get("/me", dependencies=[Depends(get_current_user)])
async def get_current_user():
    # Return current user info
```

**Frontend (React):**
```typescript
// Auth context/store
// Protected routes
// Token refresh logic
// Automatic logout on token expiry

const ProtectedRoute = ({ children, roles }) => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) return <Navigate to="/login" />;
  if (roles && !roles.includes(user.role)) return <Forbidden />;

  return children;
};
```

---

### 2. Customer Management

**Features:**
- List all customers (with filters, search, pagination)
- Add/Edit/Delete customers
- Import from Excel
- View customer sales history
- Assign to sales rep

**API Endpoints:**
```
GET    /api/v1/customers              # List customers
GET    /api/v1/customers/{id}         # Get customer detail
POST   /api/v1/customers              # Create customer
PUT    /api/v1/customers/{id}         # Update customer
DELETE /api/v1/customers/{id}         # Delete customer
POST   /api/v1/customers/import       # Import from Excel
GET    /api/v1/customers/{id}/sales   # Customer sales history
```

---

### 3. Product Management

**Features:**
- List all products (with filters by group, location)
- Add/Edit/Delete products
- Import from Excel
- Product activation matrix management

**API Endpoints:**
```
GET    /api/v1/products               # List products
GET    /api/v1/products/{id}          # Get product detail
POST   /api/v1/products               # Create product
PUT    /api/v1/products/{id}          # Update product
DELETE /api/v1/products/{id}          # Delete product
POST   /api/v1/products/import        # Import from Excel
GET    /api/v1/products/matrix        # Get activation matrix
POST   /api/v1/products/matrix        # Update matrix
```

---

### 4. Sales History (24 Months)

**Features:**
- View historical sales data
- Filter by date range, customer, product, sales rep
- Display averages and trends
- Export to Excel

**API Endpoints:**
```
GET    /api/v1/sales-history          # List sales (with filters)
POST   /api/v1/sales-history/import   # Import from Excel
GET    /api/v1/sales-history/summary  # Get aggregated data
GET    /api/v1/sales-history/trends   # Get trend analysis
```

**UI Components:**
- Data table with sorting/filtering
- Charts showing trends
- Average calculations (6-month, 12-month, 24-month)

---

### 5. S&OP Cycle Management (Admin Only)

**Features:**
- Create new S&OP cycle
- Set start/close dates
- Define planning period (16 months)
- Open/Close cycles
- Send email notifications to sales reps

**API Endpoints:**
```
GET    /api/v1/sop-cycles             # List cycles
GET    /api/v1/sop-cycles/{id}        # Get cycle detail
POST   /api/v1/sop-cycles             # Create cycle
PUT    /api/v1/sop-cycles/{id}        # Update cycle
DELETE /api/v1/sop-cycles/{id}        # Delete cycle
POST   /api/v1/sop-cycles/{id}/open   # Open cycle
POST   /api/v1/sop-cycles/{id}/close  # Close cycle
POST   /api/v1/sop-cycles/{id}/notify # Send notifications
```

---

### 6. Forecast Data Entry (Sales Reps)

**Features:**
- Excel-like grid interface for data entry
- Import from Excel (pre-filled template)
- Manual entry directly in portal
- 16 months of planning (first 12 mandatory)
- Save drafts
- Submit for review

**Two Input Methods:**

**A) Portal Entry:**
- AG-Grid with inline editing
- Auto-calculate total amount (quantity × price)
- Validation (mandatory fields)
- Real-time save

**B) Excel Upload:**
- Download template (pre-filled with customer/product data)
- Upload filled template
- Validate and import
- Show errors if any

**API Endpoints:**
```
GET    /api/v1/forecasts                        # Get forecasts for cycle
GET    /api/v1/forecasts/template               # Download Excel template
POST   /api/v1/forecasts                        # Create/update forecasts
POST   /api/v1/forecasts/import                 # Import from Excel
POST   /api/v1/forecasts/submit                 # Submit forecasts
GET    /api/v1/forecasts/{cycle_id}/status      # Submission status
```

---

### 7. Reporting & Export

**Features:**
- Consolidated S&OP report (all sales reps)
- Individual sales rep reports
- Sales comparison reports
- Group-wise summaries
- Export to Excel (matching customer's template format)
- Power BI integration (export data in compatible format)

**API Endpoints:**
```
GET    /api/v1/reports/consolidated    # Full S&OP report
GET    /api/v1/reports/sales-rep/{id}  # Sales rep report
GET    /api/v1/reports/comparison      # Sales comparison
GET    /api/v1/reports/powerbi-export  # Data for Power BI
POST   /api/v1/reports/generate        # Generate custom report
```

**Report Types:**
1. **Main Report**: Consolidated forecast by all reps
2. **Sales Rep Report**: Individual rep's data
3. **Group Summary**: By product group
4. **Customer Summary**: By customer
5. **Variance Report**: Actual vs Forecast

---

### 8. Dashboard

**Admin Dashboard:**
- Total customers, products, users
- S&OP cycle status
- Submission status by sales rep
- Sales trends
- Top customers/products

**Sales Rep Dashboard:**
- My customers
- My submission status
- Pending forecasts
- Recent sales performance
- Quick links to data entry

---

## Data Flow

### S&OP Monthly Process Flow

```
1. Admin creates new S&OP cycle
   └─> Defines start date, close date, planning period

2. System generates forecast records
   └─> For each active customer-product-sales rep combination
   └─> Creates 16 months of forecast placeholders

3. Admin opens cycle and sends notifications
   └─> Email with upload link sent to all sales reps

4. Sales reps receive notification
   └─> Option A: Download Excel template
       ├─> Template pre-filled with their customers/products
       ├─> Fill quantities and prices
       └─> Upload completed file
   └─> Option B: Enter data directly in portal
       ├─> Excel-like grid interface
       └─> Save as draft or submit

5. System validates and saves data
   └─> Checks mandatory fields (first 12 months)
   └─> Calculates totals
   └─> Marks submission status

6. Admin reviews submissions
   └─> Dashboard shows who has submitted
   └─> Can view/export individual rep data

7. Admin closes cycle
   └─> Generates final consolidated report
   └─> Exports to Excel for review meeting
   └─> Data available for Power BI

8. Next cycle begins
```

---

## Security Considerations

1. **Authentication**: JWT tokens with expiry
2. **Authorization**: Role-based access control
3. **Data Isolation**: Sales reps see only their customers
4. **Audit Trail**: All changes logged
5. **File Upload**: Validate file types, size limits, virus scanning
6. **SQL Injection**: Using ORM (SQLAlchemy) prevents this
7. **XSS Protection**: React escapes by default
8. **CSRF Protection**: Token-based API (no cookies for auth)
9. **HTTPS**: SSL/TLS in production
10. **Environment Variables**: Secrets in .env files

---

## Performance Optimization

1. **Database Indexing**: On frequently queried columns
2. **Pagination**: Limit records per page
3. **Caching**: Redis for frequently accessed data
4. **Lazy Loading**: Load data on demand
5. **Background Tasks**: Excel processing in Celery
6. **Database Connection Pooling**: SQLAlchemy pool
7. **Frontend Code Splitting**: Vite lazy loading
8. **CDN**: Static assets served from CDN

---

## Deployment Architecture

```
                                    ┌─────────────┐
                                    │   Browser   │
                                    └──────┬──────┘
                                           │
                                           │ HTTPS
                                           │
                              ┌────────────▼────────────┐
                              │     Nginx (Reverse      │
                              │     Proxy + SSL)        │
                              └─────────┬───────────────┘
                                        │
                        ┌───────────────┼───────────────┐
                        │               │               │
                        │               │               │
          ┌─────────────▼──┐   ┌───────▼──────┐  ┌────▼─────┐
          │  React Frontend │   │   FastAPI    │  │  Static  │
          │  (Static Files) │   │   Backend    │  │  Files   │
          └─────────────────┘   └───────┬──────┘  └──────────┘
                                        │
                        ┌───────────────┼───────────────┐
                        │               │               │
               ┌────────▼────────┐ ┌───▼────┐   ┌─────▼──────┐
               │   PostgreSQL    │ │ Redis  │   │   Celery   │
               │    Database     │ │ Cache  │   │   Worker   │
               └─────────────────┘ └────────┘   └────────────┘
```

**Production Deployment Options:**

1. **Docker + VPS** (DigitalOcean, Linode, AWS EC2)
2. **Managed Services** (AWS ECS, Google Cloud Run)
3. **Platform as a Service** (Heroku, Railway, Render)

---

## Development Workflow

### Initial Setup
```bash
# Clone repository
git clone <repo-url>

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with database credentials

# Run migrations
alembic upgrade head

# Start backend
uvicorn app.main:app --reload

# Frontend setup (new terminal)
cd frontend
npm install
cp .env.example .env
# Edit .env with API URL

# Start frontend
npm run dev
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

---

## Testing Strategy

### Backend Tests
- Unit tests for services
- Integration tests for APIs
- Test database with fixtures
- Coverage target: 80%+

### Frontend Tests
- Component tests (React Testing Library)
- Integration tests (Cypress/Playwright)
- E2E tests for critical flows

---

## Next Steps

1. ✅ **Requirements Analysis** - DONE
2. ✅ **Database Schema Design** - DONE
3. ✅ **Architecture Design** - DONE
4. ⏭️ **Project Setup** - Create folder structure
5. ⏭️ **Backend Development** - API implementation
6. ⏭️ **Frontend Development** - UI implementation
7. ⏭️ **Integration** - Connect frontend to backend
8. ⏭️ **Testing** - QA and bug fixes
9. ⏭️ **Deployment** - Production setup
10. ⏭️ **Training & Handover** - User training

---

## Estimated Timeline

**Phase 1: Setup & Core (4-5 weeks)**
- Week 1: Project setup, database, authentication
- Week 2: Customer & Product management
- Week 3: Sales history import and display
- Week 4: S&OP cycle management
- Week 5: Testing and refinement

**Phase 2: S&OP Process (3-4 weeks)**
- Week 6: Forecast data entry (portal)
- Week 7: Excel import/export
- Week 8: Reporting features
- Week 9: Testing and refinement

**Phase 3: Deployment (1-2 weeks)**
- Week 10-11: Production setup, training, launch

**Total: 10-12 weeks** (2.5-3 months)

This can be accelerated with more developers or by prioritizing features.
