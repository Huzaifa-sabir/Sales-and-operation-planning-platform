# MongoDB Atlas User Setup Guide

## Create a New Database User

### Step 1: Go to MongoDB Atlas Dashboard
1. Visit https://cloud.mongodb.com
2. Sign in to your account
3. Select your cluster

### Step 2: Create Database User
1. Click **"Database Access"** in the left sidebar
2. Click **"Add New Database User"**
3. Fill in the details:
   - **Authentication Method**: Password
   - **Username**: `sop_portal_user`
   - **Password**: `SOPPortal123!` (or generate a strong password)
   - **Database User Privileges**: 
     - Select **"Atlas admin"** OR
     - Select **"Read and write to any database"**

### Step 3: Configure Network Access
1. Click **"Network Access"** in the left sidebar
2. Click **"Add IP Address"**
3. Select **"Allow Access from Anywhere"** (0.0.0.0/0)
4. Click **"Confirm"**

### Step 4: Get Connection String
1. Click **"Connect"** on your cluster
2. Select **"Connect your application"**
3. Choose **"Python"** and **"3.6 or later"**
4. Copy the connection string
5. Replace `<password>` with your actual password

### Step 5: Test Connection
Run the test script to verify the connection works.

## Example Connection String Format:
```
mongodb+srv://sop_portal_user:SOPPortal123!@cluster0.4owv6bf.mongodb.net/?retryWrites=true&w=majority
```

## Important Notes:
- Make sure to use a strong password
- Keep the password secure
- The user needs read/write permissions
- Network access must allow your IP or 0.0.0.0/0

