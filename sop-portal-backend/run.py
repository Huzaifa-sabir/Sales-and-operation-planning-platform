"""
Run script for the S&OP Portal API
"""
import os
import uvicorn

if __name__ == "__main__":
    # Get port from environment variable (Railway requirement)
    port = int(os.environ.get("PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
