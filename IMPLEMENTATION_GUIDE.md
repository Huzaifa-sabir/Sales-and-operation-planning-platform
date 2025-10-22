# S&OP Portal - Implementation Guide

This guide provides step-by-step instructions to implement the S&OP portal.

---

## Prerequisites

### Required Software
- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- **Git** - [Download](https://git-scm.com/downloads)
- **VS Code** (recommended) - [Download](https://code.visualstudio.com/)

### Recommended VS Code Extensions
- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- Prettier - Code formatter
- ESLint
- PostgreSQL
- Thunder Client (API testing)

---

## Phase 1: Project Setup

### Step 1: Create Project Structure

```bash
# Create main project folder
mkdir sop-portal
cd sop-portal

# Initialize git
git init
echo "# S&OP Portal" > README.md

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env
*.log
*.sqlite3

# Node
node_modules/
dist/
build/
.env.local
.env.production

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Uploads
uploads/
temp/
EOF

git add .
git commit -m "Initial commit"
```

---

### Step 2: Setup Backend (Python/FastAPI)

```bash
# Create backend directory
mkdir backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
# FastAPI and server
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0

# Excel processing
pandas==2.2.0
openpyxl==3.1.2
xlsxwriter==3.1.9

# Validation
pydantic==2.5.3
pydantic-settings==2.1.0
email-validator==2.1.0

# CORS
python-cors==1.0.0

# Background tasks (optional for now)
# celery==5.3.4
# redis==5.0.1
EOF

# Install dependencies
pip install -r requirements.txt

# Create requirements-dev.txt for development tools
cat > requirements-dev.txt << 'EOF'
-r requirements.txt
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
black==23.12.1
flake8==7.0.0
mypy==1.8.0
EOF

pip install -r requirements-dev.txt
```

---

### Step 3: Setup PostgreSQL Database

```bash
# Connect to PostgreSQL (adjust based on your installation)
psql -U postgres

# In PostgreSQL shell:
CREATE DATABASE sop_portal;
CREATE USER sop_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE sop_portal TO sop_user;
\q
```

---

### Step 4: Create Backend Project Structure

```bash
# Create directory structure
mkdir -p app/{api/v1,models,schemas,services,utils,core}
mkdir -p alembic/versions
mkdir -p tests

# Create __init__.py files
touch app/__init__.py
touch app/api/__init__.py
touch app/api/v1/__init__.py
touch app/models/__init__.py
touch app/schemas/__init__.py
touch app/services/__init__.py
touch app/utils/__init__.py
touch app/core/__init__.py
touch tests/__init__.py

# Create .env file
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://sop_user:your_secure_password@localhost:5432/sop_portal

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME="S&OP Portal"
DEBUG=True
API_V1_PREFIX=/api/v1

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:5173", "http://localhost:3000"]
EOF

# Create .env.example (without sensitive data)
cat > .env.example << 'EOF'
DATABASE_URL=postgresql://user:password@localhost:5432/sop_portal
SECRET_KEY=change-this-to-a-random-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME="S&OP Portal"
DEBUG=True
API_V1_PREFIX=/api/v1
BACKEND_CORS_ORIGINS=["http://localhost:5173"]
EOF
```

---

### Step 5: Initialize Alembic (Database Migrations)

```bash
# Initialize alembic
alembic init alembic

# This creates:
# - alembic/ directory
# - alembic.ini file
```

Edit `alembic.ini` and update the sqlalchemy.url line:
```ini
# sqlalchemy.url = driver://user:pass@localhost/dbname
# Comment out the above line and use env variable instead
```

Edit `alembic/env.py` to use environment variables and import models:
```python
# Add these imports at the top
from app.core.config import settings
from app.database import Base
from app.models import *  # Import all models

# Update the config.set_main_option line
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Update target_metadata
target_metadata = Base.metadata
```

---

### Step 6: Create Core Backend Files

#### `app/core/config.py`
```python
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # App
    APP_NAME: str = "S&OP Portal"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

#### `app/database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### `app/main.py`
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import auth, users, customers, products

app = FastAPI(
    title=settings.APP_NAME,
    description="Sales & Operations Planning Portal API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "docs": "/api/docs",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX, tags=["auth"])
app.include_router(users.router, prefix=settings.API_V1_PREFIX, tags=["users"])
app.include_router(customers.router, prefix=settings.API_V1_PREFIX, tags=["customers"])
app.include_router(products.router, prefix=settings.API_V1_PREFIX, tags=["products"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

---

### Step 7: Test Backend Setup

```bash
# Make sure you're in backend directory with venv activated
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run the server
uvicorn app.main:app --reload

# Server should start at http://localhost:8000
# API docs at http://localhost:8000/api/docs
```

---

## Phase 2: Frontend Setup (React + TypeScript)

```bash
# Go back to project root
cd ..

# Create frontend with Vite + React + TypeScript
npm create vite@latest frontend -- --template react-ts

cd frontend

# Install dependencies
npm install

# Install additional packages
npm install @tanstack/react-query axios react-router-dom zustand
npm install antd @ant-design/icons
npm install react-hook-form zod @hookform/resolvers
npm install date-fns
npm install recharts
npm install xlsx

# Install dev dependencies
npm install -D @types/node
```

---

### Step 8: Configure Frontend

#### Update `vite.config.ts`
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

#### Create `tsconfig.json` paths
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",

    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

#### Create `.env` file
```bash
cat > .env << 'EOF'
VITE_API_URL=http://localhost:8000/api/v1
EOF

cat > .env.example << 'EOF'
VITE_API_URL=http://localhost:8000/api/v1
EOF
```

---

### Step 9: Create Frontend Structure

```bash
# Create directory structure
mkdir -p src/{api,components/{common,forms,charts},pages/{auth,dashboard,customers,products,sales-history,sop,reports,admin},hooks,store,types,utils,styles,config}

# Create files
touch src/api/axios.ts
touch src/api/auth.ts
touch src/store/authStore.ts
touch src/types/index.ts
touch src/config/constants.ts
```

#### `src/api/axios.ts`
```typescript
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const axiosInstance = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
```

#### `src/App.tsx`
```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ConfigProvider } from 'antd';
import Login from './pages/auth/Login';
import Dashboard from './pages/dashboard/Dashboard';
import Layout from './components/common/Layout';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider theme={{ token: { colorPrimary: '#1890ff' } }}>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={<Layout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<Dashboard />} />
              {/* Add more routes here */}
            </Route>
          </Routes>
        </BrowserRouter>
      </ConfigProvider>
    </QueryClientProvider>
  );
}

export default App;
```

---

### Step 10: Run Frontend

```bash
# In frontend directory
npm run dev

# Frontend should start at http://localhost:5173
```

---

## Phase 3: Database Models Implementation

Now we'll implement the database models based on our schema.

### Create User Model - `app/models/user.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'admin' or 'sales_rep'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
```

### Create Customer Model - `app/models/customer.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String(100), unique=True, nullable=False, index=True)
    customer_name = Column(String(255), nullable=False, index=True)
    sop_customer_name = Column(String(255))
    trim_customer_id = Column(String(100))
    sales_rep_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    city = Column(String(100))
    state = Column(String(50))
    address_1 = Column(String(255))
    address_2 = Column(String(255))
    zip = Column(String(20))
    corporate_group = Column(String(255))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    sales_rep = relationship("User", backref="customers")
```

### Create Product Model - `app/models/product.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    item_code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String, nullable=False)
    group_code = Column(String(50), index=True)
    group_subgroup = Column(String(50))
    group_desc = Column(String(255))
    group_name = Column(String(255))
    group_name2 = Column(String(255))
    manufacturing_location = Column(String(100), index=True)
    production_line = Column(String(100))
    pack_size = Column(Numeric(10, 2))
    weight = Column(Numeric(10, 2))
    uom = Column(String(20), default='CS')
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

Continue with other models following the DATABASE_SCHEMA.md...

---

## Phase 4: Authentication Implementation

This will be covered in the next steps. The key components are:
1. Password hashing (bcrypt)
2. JWT token generation
3. Login endpoint
4. Protected route dependencies

---

## Next Steps

1. Complete all database models
2. Create Pydantic schemas
3. Implement authentication system
4. Create CRUD operations for each entity
5. Implement Excel import/export
6. Build frontend components
7. Connect frontend to backend
8. Testing

---

## Quick Start Commands Summary

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm run dev

# Database migrations
cd backend
alembic revision --autogenerate -m "Initial tables"
alembic upgrade head
```

---

## Troubleshooting

### Common Issues

**Issue**: Cannot connect to database
- Check PostgreSQL is running: `pg_isready`
- Verify credentials in `.env`
- Check database exists: `psql -U postgres -c "\l"`

**Issue**: Module import errors
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

**Issue**: CORS errors in frontend
- Check `BACKEND_CORS_ORIGINS` in backend `.env`
- Verify API URL in frontend `.env`

---

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Ant Design Components](https://ant.design/components/overview/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)

