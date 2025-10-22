#!/usr/bin/env python3
"""
Minimal working backend for S&OP Portal
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="S&OP Portal API")

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
    return {"message": "S&OP Portal API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "cors": "enabled"}

@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
    print(f"Login attempt: {request.username}")
    
    # Simple test login
    if request.username == "admin@heavygarlic.com" and request.password == "admin123":
        return {
            "access_token": "test-jwt-token-12345",
            "token_type": "bearer",
            "expires_in": 28800,
            "user": {
                "id": "test-user-id",
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
        return {"error": "Invalid credentials"}

@app.get("/api/v1/auth/me")
async def get_current_user():
    return {
        "id": "test-user-id",
        "username": "admin",
        "email": "admin@heavygarlic.com",
        "firstName": "Admin",
        "lastName": "User",
        "fullName": "Admin User",
        "role": "admin",
        "employeeId": "EMP001",
        "isActive": True
    }

if __name__ == "__main__":
    print("Starting minimal S&OP Portal backend...")
    print("CORS enabled for all origins")
    print("Login: admin@heavygarlic.com / admin123")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
