# Render Environment Variable Setup

## 🔧 How to Fix CORS on Render

The `.env` file is ignored by git (for security), so the CORS fix needs to be set in Render's environment variables.

### Step 1: Go to Render Dashboard
1. Open [Render Dashboard](https://dashboard.render.com)
2. Click on your backend service: `sales-and-operation-planning-platform-1`

### Step 2: Set Environment Variable
1. Click on **"Environment"** tab
2. Click **"Add Environment Variable"**
3. Set the following:
   - **Key**: `CORS_ORIGINS`
   - **Value**: `http://localhost:5173,http://localhost:5174,http://localhost:3000,https://soptest.netlify.app`
4. Click **"Save Changes"**

### Step 3: Redeploy
1. Go to **"Deploys"** tab
2. Click **"Manual Deploy"** → **"Deploy latest commit**
3. Wait for deployment to complete

### Step 4: Test
1. Go to [https://soptest.netlify.app](https://soptest.netlify.app)
2. Check browser console - should see no CORS errors
3. Test login and reports functionality

## 🎯 Expected Result
After setting the environment variable and redeploying, the CORS errors should be resolved and the frontend should work properly with the backend.

## 📋 Alternative: Check Current Environment Variables
You can also check what environment variables are currently set in Render:
1. Go to **"Environment"** tab
2. Look for existing `CORS_ORIGINS` variable
3. If it exists, update it with the new value
4. If it doesn't exist, add it as described above

