#!/usr/bin/env python3
"""
Simple test server to verify CORS and login functionality
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="S&OP Portal API - Test")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

@app.get("/")
async def root():
    return {"message": "S&OP Portal API - Test Server", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy", "cors": "enabled"}

@app.post("/api/v1/auth/login")
async def login(request: LoginRequest):
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

if __name__ == "__main__":
    import uvicorn
    print("Starting simple test server on http://localhost:8000")
    print("CORS enabled for localhost:5173 and localhost:5174")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
