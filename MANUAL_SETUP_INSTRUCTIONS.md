# 🚀 Manual Backend Setup & Testing Instructions

## 📋 **Step-by-Step Instructions**

### **Step 1: Start Backend**
1. Open Command Prompt or PowerShell
2. Navigate to: `D:\Heavy\sop-portal-backend`
3. Run: `python working_backend.py`
   - OR double-click: `START_BACKEND.bat`

**Expected Output:**
```
🚀 Starting S&OP Portal Backend...
🌐 CORS enabled for all origins
🔐 Test Login: admin@heavygarlic.com / admin123
📡 Server will run on: http://localhost:8000
📚 API Docs: http://localhost:8000/docs
==================================================
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### **Step 2: Verify Backend is Running**
Open browser and go to: http://localhost:8000/health

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

### **Step 3: Start Frontend**
1. Open new Command Prompt/PowerShell
2. Navigate to: `D:\Heavy\sop-portal-frontend`
3. Run: `npm run dev`

**Expected Output:**
```
VITE v7.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  press h + enter to show help
```

### **Step 4: Test Integration**
1. Open: http://localhost:5173
2. Click "Sign In"
3. Enter credentials:
   - **Email**: `admin@heavygarlic.com`
   - **Password**: `admin123`
4. Click "Sign In"

**Expected Result:**
- ✅ No CORS errors
- ✅ No 500 errors
- ✅ Login successful
- ✅ Redirect to dashboard

### **Step 5: Run Automated Test (Optional)**
Double-click: `TEST_INTEGRATION.bat` in the root directory

This will:
- Test backend health
- Test CORS configuration
- Test login endpoint
- Open frontend in browser

---

## 🔧 **Troubleshooting**

### **Backend Won't Start**
- Check if port 8000 is already in use
- Make sure Python is installed
- Check for any error messages in console

### **CORS Errors**
- Backend is configured to allow all origins (`*`)
- Should work with any frontend port

### **Login Fails**
- Check backend console for login attempts
- Verify credentials: `admin@heavygarlic.com` / `admin123`
- Check browser console for errors

### **Frontend Won't Start**
- Make sure Node.js is installed
- Run `npm install` if needed
- Check for port conflicts (try different port)

---

## 📊 **What's Fixed**

✅ **CORS Configuration**: Backend allows all origins  
✅ **Login Endpoint**: Working with correct request format  
✅ **Error Handling**: Frontend handles errors gracefully  
✅ **Response Format**: Backend returns correct JSON structure  
✅ **Authentication**: JWT token generation working  

---

## 🎯 **Test Credentials**

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@heavygarlic.com | admin123 |

---

## 📁 **Files Created**

- `sop-portal-backend/working_backend.py` - Simple working backend
- `sop-portal-backend/START_BACKEND.bat` - Easy start script
- `TEST_INTEGRATION.bat` - Automated test script
- `MANUAL_SETUP_INSTRUCTIONS.md` - This file

---

## 🚀 **Quick Start Commands**

**Terminal 1 (Backend):**
```bash
cd D:\Heavy\sop-portal-backend
python working_backend.py
```

**Terminal 2 (Frontend):**
```bash
cd D:\Heavy\sop-portal-frontend
npm run dev
```

**Test:**
- Open: http://localhost:5173
- Login: admin@heavygarlic.com / admin123

---

**Status**: ✅ Ready for Testing  
**Last Updated**: October 18, 2025
