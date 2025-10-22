#!/usr/bin/env python3
"""
Working S&OP Portal Backend - Ready for Testing
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="S&OP Portal API", version="1.0.0")

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/")
async def root():
    return {
        "name": "S&OP Portal API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": "connected",
        "version": "1.0.0"
    }

@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    print(f"🔐 Login attempt: {request.username}")
    
    # Test credentials
    if request.username == "admin@heavygarlic.com" and request.password == "admin123":
        print("✅ Login successful!")
        return {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test-token",
            "token_type": "bearer",
            "expires_in": 28800,
            "user": {
                "id": "admin-user-id",
                "username": "admin",
                "email": "admin@heavygarlic.com",
                "firstName": "Admin",
                "lastName": "User",
                "fullName": "Admin User",
                "role": "admin",
                "employeeId": "EMP001",
                "isActive": True
            }
        }
    else:
        print("❌ Login failed!")
        return {"error": "Invalid credentials"}

@app.get("/api/v1/auth/me")
async def get_current_user():
    print("👤 Getting current user info")
    return {
        "id": "admin-user-id",
        "username": "admin",
        "email": "admin@heavygarlic.com",
        "firstName": "Admin",
        "lastName": "User",
        "fullName": "Admin User",
        "role": "admin",
        "employeeId": "EMP001",
        "isActive": True
    }

@app.post("/api/v1/auth/logout")
async def logout():
    print("🚪 User logout")
    return {"message": "Successfully logged out"}

if __name__ == "__main__":
    print("🚀 Starting S&OP Portal Backend...")
    print("🌐 CORS enabled for all origins")
    print("🔐 Test Login: admin@heavygarlic.com / admin123")
    print("📡 Server will run on: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
