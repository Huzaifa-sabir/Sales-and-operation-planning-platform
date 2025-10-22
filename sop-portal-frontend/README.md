# S&OP Portal - Frontend (MVP)

React TypeScript frontend for the Sales & Operations Planning portal with MongoDB backend.

## 🎉 Frontend is Ready!

The frontend MVP is **complete and running** at: **http://localhost:5173**

## ✅ What's Built

### Core Features
✅ Authentication (Login with JWT)
✅ Layout with sidebar & header
✅ Dashboard (Admin & Sales Rep views)
✅ Protected routes with role-based access
✅ API client with interceptors
✅ Complete TypeScript types
✅ All pages setup (ready for implementation)

### Technologies
- React 18 + TypeScript
- Vite (fast build)
- Ant Design (UI)
- React Router (navigation)
- Zustand (state)
- TanStack Query (data fetching)
- Axios (API client)

## 🚀 Quick Start

```bash
# Start development server
npm run dev

# Build for production
npm run build

# Preview production
npm run preview
```

Visit: **http://localhost:5173**

## 📝 Project Structure

```
src/
├── api/              # API client & endpoints
├── components/       # Reusable components
├── pages/            # Page components
├── store/            # State management
├── types/            # TypeScript types
├── config/           # Constants & config
└── utils/            # Utility functions
```

## 🔐 Mock Login (for testing)

**Admin:**
- Email: admin@example.com
- Password: admin123

**Sales Rep:**
- Email: sales@example.com
- Password: sales123

*(Works once backend is connected)*

## 🎯 Next Steps

1. Connect to backend API
2. Implement Customer page
3. Implement Product page
4. Implement S&OP Cycle management
5. Implement Forecast Entry
6. Add Excel import/export

## 📦 Environment

Create `.env`:
```
VITE_API_URL=http://localhost:8000/api/v1
```

## ✅ Status

**Frontend MVP: COMPLETE** 🎉

All pages are setup and ready for backend integration!

---

Built with React + TypeScript + Ant Design
