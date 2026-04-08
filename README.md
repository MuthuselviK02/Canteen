# Smart Canteen Management System

A modern, AI-powered canteen management system that revolutionizes food ordering with real-time queue optimization, intelligent recommendations, and comprehensive analytics.

## 🚀 Features

### **For Customers**
- **Smart Menu Browsing**: Filter menu items by available time constraints
- **AI Recommendations**: Personalized food suggestions based on preferences and behavior
- **Real-time Order Tracking**: Live order status with accurate wait time predictions
- **Queue Management**: See your position in the queue and estimated pickup time

### **For Kitchen Staff**
- **Kitchen Dashboard**: Streamlined order management interface
- **Order Status Management**: Update order status through the preparation workflow
- **Queue Optimization**: Intelligent order sequencing for maximum efficiency
- **Analytics Dashboard**: Real-time insights into kitchen performance

### **For Administrators**
- **User Management**: Role-based access control (USER, STAFF, ADMIN, SUPER_ADMIN)
- **Menu Management**: Add, update, and manage menu items with images
- **Comprehensive Analytics**: Revenue tracking, demand forecasting, and customer insights
- **Predictive Analytics**: AI-powered demand forecasting and churn prediction
- **Billing System**: Complete order billing and invoice management

## 🏗️ Architecture

### **System Architecture Overview**

```
┌─────────────────┐    HTTP/REST API   ┌─────────────────┐
│   Frontend      │ ◄─────────────────►│   Backend       │
│   (React + TS)  │                    │   (FastAPI)     │
│                 │                    │                 │
│ - UI Components │                    │ - API Endpoints │
│ - State Mgmt    │                    │ - Business Logic│
│ - Routing       │                    │ - ML Models     │
└─────────────────┘                    └─────────────────┘
                                                │
                                                ▼
                                        ┌─────────────────┐
                                        │   Database      │
                                        │   (SQLite/PG)   │
                                        │                 │
                                        │ - Users         │
                                        │ - Menu Items    │
                                        │ - Orders        │
                                        │ - Analytics     │
                                        └─────────────────┘
```

### **Backend Architecture (FastAPI)**

```
backend/
├── app/
│   ├── core/                  # Core Configuration
│   │   ├── config.py         # Settings & Environment
│   │   ├── security.py       # JWT & Authentication
│   │   ├── dependencies.py   # Dependency Injection
│   │   └── rate_limit.py     # Rate Limiting 
│   │
│   ├── database/             # Database Layer
│   │   ├── session.py        # DB Session Management
│   │   ├── base.py           # SQLAlchemy Base
│   │   └── migrations/       # Alembic Migrations
│   │
│   ├── models/               # Data Models (SQLAlchemy)
│   │   ├── user.py           # User Model
│   │   ├── menu.py           # Menu Item Model
│   │   ├── order.py          # Order Model
│   │   ├── billing.py        # Billing Model
│   │   └── predictive_analytics.py # ML Models
│   │
│   ├── schemas/              # Pydantic Schemas
│   │   ├── user.py           # User Validation
│   │   ├── order.py          # Order Validation
│   │   ├── menu.py           # Menu Validation
│   │   └── billing.py        # Billing Validation
│   │
│   ├── routers/              # API Endpoints
│   │   ├── auth.py           # Authentication Routes
│   │   ├── menu.py           # Menu Management
│   │   ├── orders.py         # Order Operations
│   │   ├── analytics.py      # Analytics Endpoints
│   │   ├── kitchen.py        # Kitchen Operations
│   │   ├── billing.py        # Billing Routes
│   │   └── ai_recommendations.py # AI Routes
│   │
│   ├── services/             # Business Logic Layer
│   │   ├── auth_service.py   # Authentication Logic
│   │   ├── order_service.py  # Order Management
│   │   ├── menu_service.py   # Menu Operations
│   │   ├── analytics_service.py # Analytics Logic
│   │   ├── ai_recommendation_service.py # AI Engine
│   │   └── predictive_analytics_service.py # ML Service
│   │
│   ├── ml/                   # Machine Learning Modules
│   │   ├── recommendation.py # Recommendation Engine
│   │   ├── demand_forecast.py # Demand Prediction
│   │   └── customer_behavior.py # Behavior Analysis
│   │
│   └── orchestrator/         # Workflow Orchestration
│       └── order_orchestrator.py # Order Flow Management
│
└── main.py                   # FastAPI Application Entry
```

### **Frontend Architecture (React)**

```
frontend/
├── src/
│   ├── components/           # Reusable UI Components
│   │   ├── ui/              # shadcn/ui Base Components
│   │   │   ├── button.tsx   # Button Component
│   │   │   ├── card.tsx     # Card Component
│   │   │   ├── input.tsx    # Input Component
│   │   │   └── ...          # More UI Components
│   │   │
│   │   ├── layout/          # Layout Components
│   │   │   ├── Header.tsx   # Navigation Header
│   │   │   ├── Sidebar.tsx  # Sidebar Navigation
│   │   │   └── Footer.tsx   # Page Footer
│   │   │
│   │   ├── auth/            # Authentication Components
│   │   │   ├── Login.tsx    # Login Form
│   │   │   ├── Register.tsx # Registration Form
│   │   │   └── Profile.tsx  # User Profile
│   │   │
│   │   ├── menu/            # Menu Components
│   │   │   ├── MenuCard.tsx # Menu Item Card
│   │   │   ├── MenuFilter.tsx # Menu Filters
│   │   │   └── Cart.tsx     # Shopping Cart
│   │   │
│   │   ├── kitchen/         # Kitchen Components
│   │   │   ├── OrderCard.tsx # Kitchen Order View
│   │   │   ├── StatusBadge.tsx # Order Status
│   │   │   └── KitchenDashboard.tsx # Main Dashboard
│   │   │
│   │   ├── admin/           # Admin Components
│   │   │   ├── UserManagement.tsx # User CRUD
│   │   │   ├── MenuManagement.tsx # Menu CRUD
│   │   │   └── Analytics.tsx # Analytics Dashboard
│   │   │
│   │   ├── ai/              # AI Components
│   │   │   └── AIRecommendations.tsx # AI Suggestions
│   │   │
│   │   └── billing/         # Billing Components
│   │       ├── OrderBilling.tsx # Order Billing
│   │       └── BillingDashboard.tsx # Billing Analytics
│   │
│   ├── pages/               # Route Components
│   │   ├── Index.tsx        # Landing Page
│   │   ├── Login.tsx        # Login Page
│   │   ├── Register.tsx     # Registration Page
│   │   ├── Menu.tsx         # Menu Page
│   │   ├── Orders.tsx       # Orders Page
│   │   ├── Kitchen.tsx      # Kitchen Dashboard
│   │   └── Admin.tsx        # Admin Dashboard
│   │
│   ├── contexts/            # React Context (State Management)
│   │   ├── AuthContext.tsx  # Authentication State
│   │   ├── OrderContext.tsx # Order Management State
│   │   └── AIRecommendationContext.tsx # AI State
│   │
│   ├── hooks/               # Custom React Hooks
│   │   ├── useAuth.ts       # Authentication Hook
│   │   ├── useOrders.ts     # Orders Hook
│   │   └── use-toast.ts     # Toast Notifications
│   │
│   ├── utils/               # Utility Functions
│   │   ├── istTime.ts       # IST Time Conversion
│   │   ├── api.ts           # API Helper Functions
│   │   └── constants.ts     # App Constants
│   │
│   ├── types/               # TypeScript Type Definitions
│   │   ├── auth.ts          # Auth Types
│   │   ├── order.ts         # Order Types
│   │   └── menu.ts          # Menu Types
│   │
│   ├── lib/                 # Library Configurations
│   │   └── utils.ts         # Utility Functions
│   │
│   ├── styles/              # Global Styles
│   │   ├── globals.css      # Global CSS
│   │   └── components.css   # Component Styles
│   │
│   ├── App.tsx              # Main App Component
│   ├── main.tsx             # Application Entry Point
│   └── vite-env.d.ts        # Vite Type Definitions
│
├── public/                  # Static Assets
│   ├── images/              # Image Assets
│   └── icons/               # Icon Assets
│
├── package.json             # Dependencies & Scripts
├── vite.config.ts           # Vite Configuration
├── tailwind.config.ts       # Tailwind CSS Configuration
└── tsconfig.json            # TypeScript Configuration
```

### **Data Flow Architecture**

```
┌─────────────┐    API Request   ┌─────────────┐    Database     ┌─────────────┐
│   Frontend  │ ───────────────► │   Backend   │ ──────────────► │  Database   │
│             │                  │             │                 │             │
│ - User      │ ◄─────────────── │ - FastAPI   │ ◄────────────── │ - SQLite/   │
│   Actions   │   API Response   │   Routes    │   Query Result  │   PostgreSQL│
│ - State     │                  │ - Business  │                 │             │
│   Updates   │                  │   Logic     │                 │             │
└─────────────┘                  └─────────────┘                 └─────────────┘
        │                                │                              │
        │                                │                              │
        ▼                                ▼                              ▼
  ┌─────────────┐                ┌─────────────┐                ┌─────────────┐
  │ React State │                │ ML Models   │                │ Data Models │
  │ Management  │                │ - AI Recs   │                │ - Users     │
  │ - Context   │                │ - Forecast  │                │ - Orders    │
  │ - Hooks     │                │ - Analytics │                │ - Menu      │
  └─────────────┘                └─────────────┘                └─────────────┘
```

### **Security Architecture**

```
┌─────────────────────────────────────────────────────────────────┐
│                        Security Layers                          │
├─────────────────────────────────────────────────────────────────┤
│  Frontend Security                                              │
│  ├─ Protected Routes (Role-based)                               │
│  ├─ Input Validation (Zod)                                      │
│  ├─ XSS Prevention                                              │
│  └─ Secure Storage (localStorage for tokens)                    │
├─────────────────────────────────────────────────────────────────┤
│  API Security                                                   │
│  ├─ JWT Authentication                                          │
│  ├─ CORS Configuration                                          │
│  ├─ Rate Limiting                                               │
│  ├─ Input Validation (Pydantic)                                 │
│  └─ SQL Injection Prevention (SQLAlchemy)                       │
├─────────────────────────────────────────────────────────────────┤
│  Backend Security                                               │
│  ├─ Password Hashing (bcrypt)                                   │
│  ├─ Environment Variables                                       │
│  ├─ Role-based Access Control                                   │
│  └─ Secure Headers                                              │
└─────────────────────────────────────────────────────────────────┘
```

### **Technology Integration**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│                 │    │                 │    │                 │
│ React 18        │    │ FastAPI         │    │ SQLite/PG       │
│ TypeScript      │    │ Python 3.11     │    │ SQLAlchemy      │
│ Tailwind CSS    │    │ SQLAlchemy      │    │ Alembic         │
│ Radix UI        │    │ Pydantic        │    │                 │
│ React Query     │    │ JWT Auth        │    │                 │
│ React Router    │    │ Scikit-learn    │    │                 │
│                 │    │ Pandas          │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                        ┌─────────────────┐
                        │   Deployment    │
                        │                 │
                        │ Vercel          │
                        │ Nginx           │
                        │ CI/CD           │
                        └─────────────────┘
```

### **Backend (FastAPI)**
- **Framework**: FastAPI with Python 3.11
- **Database**: SQLite with SQLAlchemy ORM (configurable to PostgreSQL)
- **Authentication**: JWT-based with role-based access control
- **ML/AI**: Scikit-learn for predictive analytics and recommendations
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### **Frontend (React)**
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and building
- **UI Library**: Radix UI + Tailwind CSS + shadcn/ui components
- **State Management**: React Context for Auth, Orders, and AI Recommendations
- **Routing**: React Router v6 with protected routes

## 🛠️ Tech Stack

### **Backend**
- FastAPI 0.110.0
- SQLAlchemy 2.0.25
- Pydantic 2.6.1
- Python-jose (JWT)
- Scikit-learn 1.4.0
- Pandas 2.2.0
- Uvicorn (ASGI server)

### **Frontend**
- React 18.3.1
- TypeScript 5.8.3
- Vite 5.4.19
- Tailwind CSS 3.4.17
- Radix UI components
- React Query (TanStack Query)
- Framer Motion

### **DevOps**
- Alembic (Database migrations)
- Vercel (Frontend deployment ready)

## 📦 Installation

### **Prerequisites**
- Python 3.11+
- Node.js 18+
- Node.js 18+

### **Backend Setup**

1. **Clone the repository**
```bash
git clone <repository-url>
cd smartcanteen/backend
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Initialize database**
```bash
# The database will be created automatically on first run
# For migrations:
alembic upgrade head
```

6. **Run the backend server**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Frontend Setup**

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
# or
yarn install
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API URL
```

4. **Run the development server**
```bash
npm run dev
# or
yarn dev
```

The application will be available at:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs


## 📱 Usage

### **Default Admin Account**
After first run, an admin account is created automatically:
- Email: `admin@canteen.com`
- Password: `admin123`

### **User Roles**

1. **USER**: Can browse menu, place orders, and track their orders
2. **STAFF**: Can access kitchen dashboard and manage order statuses
3. **ADMIN**: Full access to user management, menu management, and analytics
4. **SUPER_ADMIN**: Complete system control

### **Key Workflows**

#### **Customer Flow**
1. Register/Login to the system
2. Browse menu with time-based filtering
3. Add items to cart with AI recommendations
4. Place order and receive queue position
5. Track order status in real-time
6. Receive notification when order is ready

#### **Kitchen Staff Flow**
1. Login with staff credentials
2. View pending orders in queue
3. Update order status through preparation workflow
4. Monitor kitchen analytics and performance
5. Mark orders as ready for pickup

#### **Admin Flow**
1. Login with admin credentials
2. Manage users and roles
3. Update menu items and prices
4. View comprehensive analytics
5. Monitor system performance and revenue

## 🔧 Configuration

### **Environment Variables**

**Backend (.env):**
```env
DATABASE_URL=sqlite:///./canteen.db
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:8000
```

### **Database Configuration**

The system uses SQLite by default for development. For production:

1. **PostgreSQL Setup:**
```env
DATABASE_URL=postgresql://user:password@localhost/canteen_db
```

2. **Run migrations:**
```bash
alembic upgrade head
```

## 🧪 Testing

### **Backend Tests**
```bash
cd backend
python -m pytest
```

### **Frontend Tests**
```bash
cd frontend
npm test
# or
yarn test
```

### **IST Time Conversion Tests**
```bash
# Test IST time conversion utilities
node test_ist_conversion.js
# Open in browser
open test_ist.html
```

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### **Key API Endpoints**

#### **Authentication**
- `POST /api/auth/login` - User login
- `POST /api/auth/register` - User registration
- `GET /api/auth/me` - Get current user info

#### **Menu**
- `GET /api/menu/` - Get all menu items

#### **Orders**
- `POST /api/orders/` - Create new order
- `GET /api/orders/` - Get user orders
- `PUT /api/orders/{id}/status` - Update order status

#### **Analytics**
- `GET /api/analytics/dashboard` - Get dashboard analytics
- `GET /api/analytics/predictive` - Get predictive analytics

## 🌟 Key Features Deep Dive

### **AI-Powered Recommendations**
The system uses machine learning to provide personalized food recommendations based on:
- User order history
- Time of day
- Popular items
- Dietary preferences

### **Predictive Analytics**
Advanced analytics including:
- Demand forecasting for inventory planning
- Customer churn prediction
- Revenue forecasting
- Peak hour predictions

### **Real-time Queue Management**
- Dynamic queue position calculation
- Accurate wait time predictions
- Order status tracking in real-time
- Kitchen workflow optimization

### **IST Time Management**
Centralized Indian Standard Time handling:
- UTC to IST conversion
- Consistent time formatting
- Dynamic time calculations
- Timezone-aware order tracking

## 🚀 Deployment

### **Production Deployment**

**Backend:**
Run the FastAPI application using a production-grade ASGI server like Gunicorn with Uvicorn workers.

**Frontend (Vercel):**
1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### **Environment-Specific Configurations**

**Development:**
- SQLite database
- Hot reload enabled
- Debug logging
- CORS for local development

**Production:**
- PostgreSQL database
- Optimized builds
- Error logging
- Security headers
- Rate limiting

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the ISC License - see the package.json file for details.

##  Support

For support and questions:
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`
- Review the test files for usage examples

## Version History

- **v1.0.0** - Initial release with core features
- AI-powered recommendations
- Real-time queue management
- Comprehensive analytics
- Role-based access control
- IST time management

---

**Built with using FastAPI, React, and modern web technologies**
