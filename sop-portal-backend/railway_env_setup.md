# Railway Environment Variables Setup

## Required Environment Variables for Railway

Go to your Railway project dashboard → Variables tab and add these:

### Database Configuration
```
MONGODB_URL=mongodb+srv://huzaifasabir289_db_user:4SLjzoPzm00pQNNv@cluster0.4owv6bf.mongodb.net/sop_portal?retryWrites=true&w=majority
MONGODB_DB_NAME=sop_portal
```

### JWT Configuration
```
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Server Configuration
```
PORT=8000
HOST=0.0.0.0
```

### CORS Configuration
```
CORS_ORIGINS=https://your-frontend-domain.vercel.app,http://localhost:5173
```

## Steps to Set Variables in Railway:

1. Go to https://railway.app
2. Click on your project
3. Click on the backend service
4. Go to "Variables" tab
5. Click "New Variable" for each variable above
6. Replace `YOUR_ACTUAL_PASSWORD` with your actual MongoDB Atlas password
7. Save each variable

## After Setting Variables:

1. Railway will automatically redeploy
2. Your backend will connect to MongoDB Atlas
3. Test the API endpoints to ensure everything works
