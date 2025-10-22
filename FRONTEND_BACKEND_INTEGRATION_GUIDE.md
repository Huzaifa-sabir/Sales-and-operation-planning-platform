# Frontend-Backend Integration Guide
## S&OP Portal - Complete API Integration

**Last Updated**: 2025-10-18
**Backend**: http://localhost:8000
**Frontend**: http://localhost:3000
**API Docs**: http://localhost:8000/api/docs

---

## Table of Contents
1. [Authentication](#authentication)
2. [API Endpoints by Feature](#api-endpoints-by-feature)
3. [Request/Response Examples](#requestresponse-examples)
4. [Error Handling](#error-handling)
5. [State Management](#state-management)
6. [Environment Setup](#environment-setup)

---

## Authentication

### Login Flow
```javascript
// 1. Login
const login = async (email, password) => {
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password })
  });

  const data = await response.json();
  // Store token
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('user', JSON.stringify(data.user));

  return data;
};

// 2. Get Current User
const getCurrentUser = async () => {
  const token = localStorage.getItem('access_token');
  const response = await fetch('http://localhost:8000/api/v1/auth/me', {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return response.json();
};

// 3. Logout
const logout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user');
  window.location.href = '/login';
};
```

### Protected API Calls
```javascript
const apiCall = async (endpoint, options = {}) => {
  const token = localStorage.getItem('access_token');

  const response = await fetch(`http://localhost:8000${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers
    }
  });

  if (response.status === 401) {
    logout();
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'API Error');
  }

  return response.json();
};
```

---

## API Endpoints by Feature

### 1. Users Management
```javascript
// List users
GET /api/v1/users?skip=0&limit=20
const getUsers = () => apiCall('/api/v1/users');

// Create user (admin only)
POST /api/v1/users
const createUser = (userData) => apiCall('/api/v1/users', {
  method: 'POST',
  body: JSON.stringify(userData)
});

// Update user
PUT /api/v1/users/{user_id}
const updateUser = (userId, userData) => apiCall(`/api/v1/users/${userId}`, {
  method: 'PUT',
  body: JSON.stringify(userData)
});

// Delete user
DELETE /api/v1/users/{user_id}
const deleteUser = (userId) => apiCall(`/api/v1/users/${userId}`, {
  method: 'DELETE'
});
```

### 2. Customers Management
```javascript
// List customers
GET /api/v1/customers?skip=0&limit=20
const getCustomers = () => apiCall('/api/v1/customers');

// Get customer by ID
GET /api/v1/customers/{customer_id}
const getCustomer = (customerId) => apiCall(`/api/v1/customers/${customerId}`);

// Create customer
POST /api/v1/customers
const createCustomer = (data) => apiCall('/api/v1/customers', {
  method: 'POST',
  body: JSON.stringify(data)
});

// Update customer
PUT /api/v1/customers/{customer_id}
const updateCustomer = (customerId, data) => apiCall(`/api/v1/customers/${customerId}`, {
  method: 'PUT',
  body: JSON.stringify(data)
});
```

### 3. Products Management
```javascript
// List products
GET /api/v1/products?skip=0&limit=20
const getProducts = () => apiCall('/api/v1/products');

// Search products
GET /api/v1/products/search?q=searchTerm
const searchProducts = (query) => apiCall(`/api/v1/products/search?q=${query}`);

// Create product
POST /api/v1/products
const createProduct = (data) => apiCall('/api/v1/products', {
  method: 'POST',
  body: JSON.stringify(data)
});
```

### 4. S&OP Cycles
```javascript
// List cycles
GET /api/v1/sop/cycles?status=OPEN
const getCycles = (status) => apiCall(`/api/v1/sop/cycles${status ? `?status=${status}` : ''}`);

// Get active cycle
GET /api/v1/sop/cycles/active
const getActiveCycle = () => apiCall('/api/v1/sop/cycles/active');

// Create cycle (admin only)
POST /api/v1/sop/cycles
const createCycle = (data) => apiCall('/api/v1/sop/cycles', {
  method: 'POST',
  body: JSON.stringify(data)
});

// Open cycle
PUT /api/v1/sop/cycles/{cycle_id}/open
const openCycle = (cycleId) => apiCall(`/api/v1/sop/cycles/${cycleId}/open`, {
  method: 'PUT'
});

// Close cycle
PUT /api/v1/sop/cycles/{cycle_id}/close
const closeCycle = (cycleId) => apiCall(`/api/v1/sop/cycles/${cycleId}/close`, {
  method: 'PUT'
});
```

### 5. Forecasts
```javascript
// List forecasts for cycle
GET /api/v1/forecasts?cycleId={cycle_id}
const getForecasts = (cycleId) => apiCall(`/api/v1/forecasts?cycleId=${cycleId}`);

// Create forecast
POST /api/v1/forecasts
const createForecast = (data) => apiCall('/api/v1/forecasts', {
  method: 'POST',
  body: JSON.stringify({
    cycleId: data.cycleId,
    customerId: data.customerId,
    productId: data.productId,
    monthlyForecasts: data.monthlyForecasts,
    useCustomerPrice: true
  })
});

// Submit forecast
POST /api/v1/forecasts/{forecast_id}/submit
const submitForecast = (forecastId) => apiCall(`/api/v1/forecasts/${forecastId}/submit`, {
  method: 'POST'
});

// Bulk import forecasts
POST /api/v1/forecasts/bulk-import
const bulkImportForecasts = async (file, cycleId) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('cycleId', cycleId);

  const token = localStorage.getItem('access_token');
  const response = await fetch('http://localhost:8000/api/v1/forecasts/bulk-import', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  return response.json();
};
```

### 6. Reports
```javascript
// Generate report
POST /api/v1/reports/generate
const generateReport = (reportType, format, filters) => apiCall('/api/v1/reports/generate', {
  method: 'POST',
  body: JSON.stringify({
    reportType,  // "sales_summary", "forecast_vs_actual", etc.
    format,      // "EXCEL" or "PDF"
    filters: filters || {}
  })
});

// List user's reports
GET /api/v1/reports?skip=0&limit=20
const getReports = () => apiCall('/api/v1/reports');

// Download report
GET /api/v1/reports/{report_id}/download
const downloadReport = async (reportId) => {
  const token = localStorage.getItem('access_token');
  const response = await fetch(`http://localhost:8000/api/v1/reports/${reportId}/download`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `report_${reportId}.xlsx`;
  a.click();
};
```

### 7. Settings (Admin Only)
```javascript
// Get public settings (no auth)
GET /settings/public
const getPublicSettings = async () => {
  const response = await fetch('http://localhost:8000/api/v1/settings/public');
  return response.json();
};

// List all settings (admin)
GET /settings
const getSettings = () => apiCall('/api/v1/settings');

// Update setting
PUT /settings/{key}
const updateSetting = (key, value) => apiCall(`/api/v1/settings/${key}`, {
  method: 'PUT',
  body: JSON.stringify({ value })
});
```

### 8. Audit Logs (Admin Only)
```javascript
// List audit logs
GET /api/v1/audit-logs?skip=0&limit=100
const getAuditLogs = () => apiCall('/api/v1/audit-logs');

// Get my activity
GET /api/v1/audit-logs/my-activity?days=30
const getMyActivity = () => apiCall('/api/v1/audit-logs/my-activity?days=30');

// Get critical events
GET /api/v1/audit-logs/critical-events?hours=24
const getCriticalEvents = () => apiCall('/api/v1/audit-logs/critical-events?hours=24');
```

---

## Request/Response Examples

### Create Forecast Example
```javascript
// Request
POST /api/v1/forecasts
{
  "cycleId": "507f1f77bcf86cd799439011",
  "customerId": "CUST001",
  "productId": "PROD001",
  "useCustomerPrice": true,
  "monthlyForecasts": [
    {
      "year": 2025,
      "month": 1,
      "monthLabel": "2025-01",
      "quantity": 1000,
      "isFuture": true
    },
    {
      "year": 2025,
      "month": 2,
      "monthLabel": "2025-02",
      "quantity": 1200,
      "isFuture": true
    }
    // ... 12 months minimum required
  ]
}

// Response
{
  "id": "507f1f77bcf86cd799439012",
  "cycleId": "507f1f77bcf86cd799439011",
  "customerId": "CUST001",
  "productId": "PROD001",
  "status": "draft",
  "totalQuantity": 2200,
  "totalRevenue": 44000.00,
  "createdAt": "2025-10-18T12:00:00Z"
}
```

### Generate Report Example
```javascript
// Request
POST /api/v1/reports/generate
{
  "reportType": "sales_summary",
  "format": "EXCEL",
  "filters": {
    "startDate": "2024-01-01",
    "endDate": "2024-12-31"
  }
}

// Response (202 Accepted)
{
  "reportId": "507f1f77bcf86cd799439013",
  "status": "PENDING",
  "message": "Report generation started. Check status using the reportId.",
  "downloadUrl": null
}

// After generation completes
GET /api/v1/reports/507f1f77bcf86cd799439013
{
  "id": "507f1f77bcf86cd799439013",
  "reportType": "sales_summary",
  "format": "EXCEL",
  "status": "COMPLETED",
  "fileName": "sales_summary_507f1f77bcf86cd799439013.xlsx",
  "downloadUrl": "/api/v1/reports/507f1f77bcf86cd799439013/download",
  "createdAt": "2025-10-18T12:00:00Z"
}
```

---

## Error Handling

### Standard Error Response
```javascript
{
  "detail": "Error message here"
}
```

### Common HTTP Status Codes
- `200 OK` - Success
- `201 Created` - Resource created
- `202 Accepted` - Request accepted (async operation)
- `204 No Content` - Success with no response body
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing/invalid token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Handling Example
```javascript
try {
  const data = await apiCall('/api/v1/forecasts', {
    method: 'POST',
    body: JSON.stringify(forecastData)
  });

  showSuccess('Forecast created successfully');
  return data;

} catch (error) {
  if (error.message.includes('Rate limit')) {
    showError('Too many requests. Please wait a moment.');
  } else if (error.message.includes('Unauthorized')) {
    logout();
  } else {
    showError(error.message);
  }
}
```

---

## State Management

### React Context Example
```javascript
// AuthContext.js
import { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token'));

  useEffect(() => {
    if (token) {
      getCurrentUser().then(setUser);
    }
  }, [token]);

  const login = async (email, password) => {
    const data = await loginAPI(email, password);
    setToken(data.access_token);
    setUser(data.user);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('access_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
```

---

## Environment Setup

### Frontend .env
```bash
REACT_APP_API_URL=http://localhost:8000
REACT_APP_API_V1_PREFIX=/api/v1
```

### Backend .env
```bash
# Database
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=sop_portal

# JWT
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480

# SMTP (for email notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@sopportal.com
FROM_NAME=S&OP Portal

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

---

## Complete API Endpoint List

### Authentication
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/change-password` - Change password

### Users
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

### Products
- `GET /api/v1/products` - List products
- `POST /api/v1/products` - Create product
- `GET /api/v1/products/{id}` - Get product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `GET /api/v1/products/search` - Search products

### Pricing Matrix
- `GET /api/v1/matrix` - List pricing
- `POST /api/v1/matrix` - Create pricing
- `PUT /api/v1/matrix/{id}` - Update pricing
- `DELETE /api/v1/matrix/{id}` - Delete pricing

### Sales History
- `GET /api/v1/sales-history` - List sales
- `POST /api/v1/sales-history` - Create sale
- `GET /api/v1/sales-history/monthly/{year}/{month}` - Monthly sales
- `GET /api/v1/sales-history/analytics` - Sales analytics

### S&OP Cycles
- `GET /api/v1/sop/cycles` - List cycles
- `POST /api/v1/sop/cycles` - Create cycle
- `GET /api/v1/sop/cycles/active` - Get active cycle
- `GET /api/v1/sop/cycles/{id}` - Get cycle
- `PUT /api/v1/sop/cycles/{id}` - Update cycle
- `PUT /api/v1/sop/cycles/{id}/open` - Open cycle
- `PUT /api/v1/sop/cycles/{id}/close` - Close cycle
- `DELETE /api/v1/sop/cycles/{id}` - Delete cycle

### Forecasts
- `GET /api/v1/forecasts` - List forecasts
- `POST /api/v1/forecasts` - Create forecast
- `GET /api/v1/forecasts/{id}` - Get forecast
- `PUT /api/v1/forecasts/{id}` - Update forecast
- `POST /api/v1/forecasts/{id}/submit` - Submit forecast
- `DELETE /api/v1/forecasts/{id}` - Delete forecast
- `POST /api/v1/forecasts/bulk-import` - Bulk import
- `GET /api/v1/forecasts/cycle/{id}/template` - Download template

### Reports
- `POST /api/v1/reports/generate` - Generate report
- `GET /api/v1/reports` - List reports
- `GET /api/v1/reports/{id}` - Get report
- `GET /api/v1/reports/{id}/download` - Download report
- `DELETE /api/v1/reports/{id}` - Delete report

### Settings (Admin)
- `GET /api/v1/settings/public` - Public settings
- `GET /api/v1/settings` - List settings
- `GET /api/v1/settings/{key}` - Get setting
- `POST /api/v1/settings` - Create setting
- `PUT /api/v1/settings/{key}` - Update setting
- `DELETE /api/v1/settings/{key}` - Delete setting

### Audit Logs (Admin)
- `GET /api/v1/audit-logs` - List logs
- `GET /api/v1/audit-logs/my-activity` - My activity
- `GET /api/v1/audit-logs/critical-events` - Critical events
- `GET /api/v1/audit-logs/statistics` - Statistics

### Health & Docs
- `GET /` - API info
- `GET /health` - Health check
- `GET /api/docs` - Swagger UI
- `GET /api/openapi.json` - OpenAPI spec

---

## Rate Limiting
- Default: 60 requests per minute per user/IP
- Headers returned:
  - `X-RateLimit-Limit: 60`
  - `X-RateLimit-Remaining: 45`
  - `X-RateLimit-Reset: 60`

---

## WebSocket Support (Future)
For real-time notifications, consider adding WebSocket support for:
- Forecast submission notifications
- Cycle status changes
- Report generation completion

---

**END OF INTEGRATION GUIDE**
