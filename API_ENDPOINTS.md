# S&OP Portal - API Endpoints Reference

Complete API endpoints documentation for the S&OP Portal backend.

**Base URL**: `http://localhost:8000/api/v1` (development)

---

## Authentication

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "full_name": "John Doe",
    "role": "admin",
    "email": "user@example.com"
  }
}
```

### Get Current User
```http
GET /auth/me
Authorization: Bearer {token}

Response 200:
{
  "id": 1,
  "username": "user@example.com",
  "full_name": "John Doe",
  "role": "admin",
  "email": "user@example.com",
  "is_active": true,
  "last_login": "2025-10-15T10:30:00Z"
}
```

### Logout
```http
POST /auth/logout
Authorization: Bearer {token}

Response 200:
{
  "message": "Successfully logged out"
}
```

---

## Users (Admin Only)

### List Users
```http
GET /users?page=1&limit=50&role=sales_rep&search=john
Authorization: Bearer {token}

Response 200:
{
  "total": 12,
  "page": 1,
  "limit": 50,
  "data": [
    {
      "id": 1,
      "username": "john.doe",
      "full_name": "John Doe",
      "email": "john@example.com",
      "role": "sales_rep",
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Get User
```http
GET /users/{id}
Authorization: Bearer {token}

Response 200:
{
  "id": 1,
  "username": "john.doe",
  "full_name": "John Doe",
  "email": "john@example.com",
  "role": "sales_rep",
  "is_active": true,
  "customer_count": 25,
  "created_at": "2025-01-01T00:00:00Z"
}
```

### Create User
```http
POST /users
Authorization: Bearer {token}
Content-Type: application/json

{
  "username": "john.doe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "role": "sales_rep"
}

Response 201:
{
  "id": 1,
  "username": "john.doe",
  "full_name": "John Doe",
  "email": "john@example.com",
  "role": "sales_rep",
  "is_active": true
}
```

### Update User
```http
PUT /users/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "John Smith",
  "is_active": false
}

Response 200:
{
  "id": 1,
  "username": "john.doe",
  "full_name": "John Smith",
  "email": "john@example.com",
  "role": "sales_rep",
  "is_active": false
}
```

### Delete User
```http
DELETE /users/{id}
Authorization: Bearer {token}

Response 204: No Content
```

---

## Customers

### List Customers
```http
GET /customers?page=1&limit=50&sales_rep_id=1&search=food&is_active=true
Authorization: Bearer {token}

Response 200:
{
  "total": 150,
  "page": 1,
  "limit": 50,
  "data": [
    {
      "id": 1,
      "customer_id": "PATITO-000001",
      "customer_name": "Industria Los Patitos",
      "sop_customer_name": "Los Patitos",
      "sales_rep_id": 1,
      "sales_rep_name": "John Doe",
      "city": "Miami",
      "state": "FL",
      "corporate_group": "Food Services",
      "is_active": true
    }
  ]
}
```

### Get Customer
```http
GET /customers/{id}
Authorization: Bearer {token}

Response 200:
{
  "id": 1,
  "customer_id": "PATITO-000001",
  "customer_name": "Industria Los Patitos",
  "sop_customer_name": "Los Patitos",
  "trim_customer_id": "PATITO-000001",
  "sales_rep_id": 1,
  "sales_rep": {
    "id": 1,
    "full_name": "John Doe"
  },
  "city": "Miami",
  "state": "FL",
  "address_1": "123 Main St",
  "address_2": "Suite 100",
  "zip": "33101",
  "corporate_group": "Food Services",
  "is_active": true,
  "total_sales_ytd": 125000.50,
  "product_count": 15,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-10-15T10:00:00Z"
}
```

### Create Customer
```http
POST /customers
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_id": "ABC-000001",
  "customer_name": "ABC Company",
  "sop_customer_name": "ABC",
  "sales_rep_id": 1,
  "city": "Miami",
  "state": "FL",
  "address_1": "123 Main St",
  "zip": "33101",
  "corporate_group": "Retail"
}

Response 201:
{
  "id": 151,
  "customer_id": "ABC-000001",
  "customer_name": "ABC Company",
  ...
}
```

### Update Customer
```http
PUT /customers/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "customer_name": "ABC Corporation",
  "sales_rep_id": 2
}

Response 200: Updated customer object
```

### Delete Customer
```http
DELETE /customers/{id}
Authorization: Bearer {token}

Response 204: No Content
```

### Import Customers from Excel
```http
POST /customers/import
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: customers.xlsx

Response 200:
{
  "total_rows": 100,
  "successful": 95,
  "failed": 5,
  "errors": [
    {
      "row": 15,
      "error": "Customer ID already exists"
    }
  ],
  "import_log_id": 123
}
```

### Get Customer Sales History
```http
GET /customers/{id}/sales?start_date=2024-01-01&end_date=2025-10-15
Authorization: Bearer {token}

Response 200:
{
  "customer_id": 1,
  "customer_name": "ABC Company",
  "sales_data": [
    {
      "year_month": "2025-10-01",
      "total_quantity": 1500,
      "total_sales": 45000.00,
      "product_count": 12
    }
  ],
  "summary": {
    "total_sales": 540000.00,
    "avg_monthly_sales": 45000.00,
    "trend": "increasing"
  }
}
```

---

## Products

### List Products
```http
GET /products?page=1&limit=50&group_code=G1&location=Miami&search=garlic
Authorization: Bearer {token}

Response 200:
{
  "total": 500,
  "page": 1,
  "limit": 50,
  "data": [
    {
      "id": 1,
      "item_code": "110001",
      "description": "Peeled Garlic 12x1 LB Garland",
      "group_code": "G1",
      "group_desc": "Group 1-2",
      "manufacturing_location": "Miami",
      "production_line": "Peeled Garlic Repack",
      "weight": 12,
      "uom": "CS",
      "is_active": true
    }
  ]
}
```

### Get Product
```http
GET /products/{id}
Authorization: Bearer {token}

Response 200:
{
  "id": 1,
  "item_code": "110001",
  "description": "Peeled Garlic 12x1 LB Garland",
  "group_code": "G1",
  "group_subgroup": "G1S7",
  "group_desc": "Group 1-2",
  "group_name": "12x1 lb P/G Domestic",
  "group_name2": "Peeled Garlic Repack",
  "manufacturing_location": "Miami",
  "production_line": "Peeled Garlic Repack",
  "pack_size": 12,
  "weight": 12,
  "uom": "CS",
  "is_active": true,
  "customer_count": 45,
  "avg_price": 52.00,
  "created_at": "2025-01-01T00:00:00Z"
}
```

### Create Product
```http
POST /products
Authorization: Bearer {token}
Content-Type: application/json

{
  "item_code": "999999",
  "description": "New Product",
  "group_code": "G1",
  "manufacturing_location": "Miami",
  "weight": 10,
  "uom": "CS"
}

Response 201: Created product object
```

### Update Product
```http
PUT /products/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "description": "Updated Product Description",
  "is_active": false
}

Response 200: Updated product object
```

### Delete Product
```http
DELETE /products/{id}
Authorization: Bearer {token}

Response 204: No Content
```

### Import Products from Excel
```http
POST /products/import
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: products.xlsx

Response 200:
{
  "total_rows": 500,
  "successful": 495,
  "failed": 5,
  "errors": [...],
  "import_log_id": 124
}
```

### Get/Update Product-Customer Matrix
```http
GET /products/matrix?product_id=1&customer_id=5
Authorization: Bearer {token}

Response 200:
{
  "data": [
    {
      "id": 1,
      "product_id": 1,
      "product_code": "110001",
      "customer_id": 5,
      "customer_name": "ABC Company",
      "is_active": true,
      "effective_date": "2025-01-01"
    }
  ]
}

POST /products/matrix
Authorization: Bearer {token}
Content-Type: application/json

{
  "activations": [
    {
      "product_id": 1,
      "customer_id": 5,
      "is_active": true
    }
  ]
}

Response 200:
{
  "updated": 1,
  "message": "Matrix updated successfully"
}
```

---

## Sales History

### Get Sales History
```http
GET /sales-history?customer_id=1&product_id=5&start_date=2024-01-01&end_date=2025-10-15
Authorization: Bearer {token}

Response 200:
{
  "total": 24,
  "data": [
    {
      "id": 1,
      "customer_id": 1,
      "customer_name": "ABC Company",
      "product_id": 5,
      "item_code": "110001",
      "description": "Peeled Garlic...",
      "year_month": "2025-10-01",
      "quantity": 500,
      "unit_price": 52.00,
      "total_sales": 26000.00,
      "gross_profit": 7800.00,
      "gross_profit_percent": 30.00
    }
  ]
}
```

### Import Sales History
```http
POST /sales-history/import
Authorization: Bearer {token}
Content-Type: multipart/form-data

file: sales_data.xlsx

Response 200:
{
  "total_rows": 5000,
  "successful": 4998,
  "failed": 2,
  "errors": [...],
  "import_log_id": 125
}
```

### Get Sales Summary
```http
GET /sales-history/summary?group_by=customer&start_date=2024-01-01
Authorization: Bearer {token}

Response 200:
{
  "summary": [
    {
      "customer_id": 1,
      "customer_name": "ABC Company",
      "total_quantity": 12000,
      "total_sales": 624000.00,
      "avg_monthly_sales": 52000.00,
      "month_count": 12
    }
  ]
}
```

### Get Sales Trends
```http
GET /sales-history/trends?entity_type=customer&entity_id=1&months=24
Authorization: Bearer {token}

Response 200:
{
  "entity": {
    "type": "customer",
    "id": 1,
    "name": "ABC Company"
  },
  "trends": [
    {
      "year_month": "2025-10-01",
      "total_sales": 52000.00,
      "vs_last_month_percent": 5.2,
      "vs_last_year_percent": 12.5
    }
  ],
  "averages": {
    "avg_6_months": 50000.00,
    "avg_12_months": 48000.00,
    "avg_24_months": 45000.00
  }
}
```

---

## S&OP Cycles

### List S&OP Cycles
```http
GET /sop-cycles?status=open&year=2025
Authorization: Bearer {token}

Response 200:
{
  "total": 12,
  "data": [
    {
      "id": 1,
      "cycle_name": "Nov 2025",
      "year": 2025,
      "month": 11,
      "start_date": "2025-10-15",
      "close_date": "2025-10-30",
      "planning_start_month": "2025-11-01",
      "status": "open",
      "submission_count": 8,
      "total_reps": 10,
      "completion_percent": 80.0
    }
  ]
}
```

### Get S&OP Cycle
```http
GET /sop-cycles/{id}
Authorization: Bearer {token}

Response 200:
{
  "id": 1,
  "cycle_name": "Nov 2025",
  "year": 2025,
  "month": 11,
  "start_date": "2025-10-15",
  "close_date": "2025-10-30",
  "planning_start_month": "2025-11-01",
  "planning_end_month": "2027-02-28",
  "status": "open",
  "created_by": {
    "id": 1,
    "full_name": "Admin User"
  },
  "submissions": [
    {
      "sales_rep_id": 1,
      "sales_rep_name": "John Doe",
      "status": "submitted",
      "submitted_at": "2025-10-20T15:30:00Z",
      "total_records": 250
    }
  ],
  "created_at": "2025-10-01T00:00:00Z"
}
```

### Create S&OP Cycle
```http
POST /sop-cycles
Authorization: Bearer {token}
Content-Type: application/json

{
  "cycle_name": "Dec 2025",
  "year": 2025,
  "month": 12,
  "start_date": "2025-11-15",
  "close_date": "2025-11-30",
  "planning_start_month": "2025-12-01"
}

Response 201:
{
  "id": 2,
  "cycle_name": "Dec 2025",
  "status": "draft",
  ...
}
```

### Update S&OP Cycle
```http
PUT /sop-cycles/{id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "close_date": "2025-11-25"
}

Response 200: Updated cycle object
```

### Open S&OP Cycle
```http
POST /sop-cycles/{id}/open
Authorization: Bearer {token}

Response 200:
{
  "id": 1,
  "status": "open",
  "message": "Cycle opened successfully"
}
```

### Close S&OP Cycle
```http
POST /sop-cycles/{id}/close
Authorization: Bearer {token}

Response 200:
{
  "id": 1,
  "status": "closed",
  "message": "Cycle closed successfully"
}
```

### Send Notifications
```http
POST /sop-cycles/{id}/notify
Authorization: Bearer {token}
Content-Type: application/json

{
  "sales_rep_ids": [1, 2, 3]  // Optional, omit to send to all
}

Response 200:
{
  "sent": 10,
  "failed": 0,
  "message": "Notifications sent successfully"
}
```

---

## Forecasts

### Get Forecasts
```http
GET /forecasts?cycle_id=1&sales_rep_id=1&customer_id=5
Authorization: Bearer {token}

Response 200:
{
  "cycle": {
    "id": 1,
    "cycle_name": "Nov 2025"
  },
  "data": [
    {
      "id": 1,
      "customer_id": 5,
      "customer_name": "ABC Company",
      "product_id": 10,
      "item_code": "110001",
      "description": "Peeled Garlic...",
      "forecasts": [
        {
          "forecast_month": "2025-11-01",
          "forecast_month_number": 1,
          "quantity": 500,
          "unit_price": 52.00,
          "total_amount": 26000.00,
          "is_mandatory": true
        },
        // ... 15 more months
      ]
    }
  ]
}
```

### Download Forecast Template
```http
GET /forecasts/template?cycle_id=1&sales_rep_id=1
Authorization: Bearer {token}

Response 200: Excel file download
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="forecast_template_john_doe_nov2025.xlsx"
```

### Create/Update Forecasts
```http
POST /forecasts
Authorization: Bearer {token}
Content-Type: application/json

{
  "cycle_id": 1,
  "forecasts": [
    {
      "customer_id": 5,
      "product_id": 10,
      "forecast_month": "2025-11-01",
      "forecast_month_number": 1,
      "quantity": 500,
      "unit_price": 52.00,
      "notes": "Holiday season increase"
    }
  ]
}

Response 200:
{
  "created": 1,
  "updated": 0,
  "total": 1,
  "message": "Forecasts saved successfully"
}
```

### Import Forecasts from Excel
```http
POST /forecasts/import
Authorization: Bearer {token}
Content-Type: multipart/form-data

cycle_id: 1
file: forecast_data.xlsx

Response 200:
{
  "total_rows": 250,
  "successful": 248,
  "failed": 2,
  "errors": [
    {
      "row": 15,
      "error": "Invalid product code"
    }
  ],
  "import_log_id": 126
}
```

### Submit Forecasts
```http
POST /forecasts/submit
Authorization: Bearer {token}
Content-Type: application/json

{
  "cycle_id": 1,
  "sales_rep_id": 1
}

Response 200:
{
  "message": "Forecasts submitted successfully",
  "submission_id": 50,
  "total_records": 250,
  "validation": {
    "mandatory_complete": true,
    "warnings": []
  }
}
```

### Get Submission Status
```http
GET /forecasts/{cycle_id}/status?sales_rep_id=1
Authorization: Bearer {token}

Response 200:
{
  "cycle_id": 1,
  "sales_rep_id": 1,
  "sales_rep_name": "John Doe",
  "status": "submitted",
  "submitted_at": "2025-10-20T15:30:00Z",
  "total_records": 250,
  "mandatory_complete": true,
  "completion_percent": 100.0,
  "last_updated": "2025-10-20T15:30:00Z"
}
```

---

## Reports

### Get Consolidated Report
```http
GET /reports/consolidated?cycle_id=1&format=json
Authorization: Bearer {token}

Response 200:
{
  "cycle": {
    "id": 1,
    "cycle_name": "Nov 2025"
  },
  "summary": {
    "total_quantity": 50000,
    "total_amount": 2500000.00,
    "customer_count": 150,
    "product_count": 500
  },
  "by_sales_rep": [...],
  "by_customer": [...],
  "by_product_group": [...]
}

GET /reports/consolidated?cycle_id=1&format=excel
Response 200: Excel file download
```

### Get Sales Rep Report
```http
GET /reports/sales-rep/{id}?cycle_id=1&format=excel
Authorization: Bearer {token}

Response 200: Excel file download
```

### Get Comparison Report
```http
GET /reports/comparison?cycle_id=1&compare_to=actual&period=ytd
Authorization: Bearer {token}

Response 200:
{
  "cycle": {...},
  "comparison": [
    {
      "entity": "Customer ABC",
      "forecast": 100000.00,
      "actual": 95000.00,
      "variance": -5000.00,
      "variance_percent": -5.0
    }
  ]
}
```

### Export for Power BI
```http
GET /reports/powerbi-export?cycle_id=1&format=csv
Authorization: Bearer {token}

Response 200: CSV file download optimized for Power BI
```

### Generate Custom Report
```http
POST /reports/generate
Authorization: Bearer {token}
Content-Type: application/json

{
  "report_type": "custom",
  "cycle_id": 1,
  "filters": {
    "sales_rep_ids": [1, 2],
    "product_groups": ["G1", "G2"],
    "customers": [5, 10, 15]
  },
  "format": "excel",
  "include_charts": true
}

Response 200: Excel file download
```

---

## Dashboard

### Get Admin Dashboard Data
```http
GET /dashboard/admin
Authorization: Bearer {token}

Response 200:
{
  "stats": {
    "total_customers": 150,
    "total_products": 500,
    "total_users": 12,
    "active_cycles": 1
  },
  "current_cycle": {
    "id": 1,
    "cycle_name": "Nov 2025",
    "status": "open",
    "submissions": 8,
    "pending": 2
  },
  "sales_trends": [...],
  "top_customers": [...],
  "top_products": [...]
}
```

### Get Sales Rep Dashboard Data
```http
GET /dashboard/sales-rep
Authorization: Bearer {token}

Response 200:
{
  "my_customers": {
    "total": 25,
    "active": 24
  },
  "current_cycle": {
    "id": 1,
    "cycle_name": "Nov 2025",
    "status": "open",
    "my_status": "submitted",
    "submitted_at": "2025-10-20T15:30:00Z"
  },
  "recent_sales": [...],
  "pending_forecasts": [...]
}
```

---

## System Settings (Admin Only)

### Get Settings
```http
GET /settings
Authorization: Bearer {token}

Response 200:
{
  "settings": [
    {
      "id": 1,
      "setting_key": "default_planning_months",
      "setting_value": "16",
      "setting_type": "integer",
      "description": "Number of months for S&OP planning",
      "is_editable": true
    }
  ]
}
```

### Update Setting
```http
PUT /settings/{key}
Authorization: Bearer {token}
Content-Type: application/json

{
  "setting_value": "18"
}

Response 200: Updated setting object
```

---

## Error Responses

All endpoints return consistent error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_id": "abc123"
}
```

---

## Rate Limiting

- **Authentication endpoints**: 5 requests per minute
- **File uploads**: 10 requests per minute
- **General API**: 100 requests per minute
- **Report generation**: 5 requests per minute

---

## Pagination

All list endpoints support pagination:

```http
GET /customers?page=1&limit=50&sort_by=customer_name&sort_order=asc
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 50, max: 100)
- `sort_by`: Field to sort by
- `sort_order`: `asc` or `desc`

---

## Filtering

Most list endpoints support filtering:

```http
GET /customers?search=food&sales_rep_id=1&is_active=true
```

**Common Filter Parameters:**
- `search`: Text search across multiple fields
- `is_active`: Boolean filter
- `start_date` / `end_date`: Date range filters
- Entity-specific IDs for related filtering

---

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `http://localhost:8000/api/docs`
- **ReDoc**: `http://localhost:8000/api/redoc`

These provide:
- Complete endpoint list
- Request/response schemas
- Try-it-out functionality
- Authentication testing
- Schema exploration
