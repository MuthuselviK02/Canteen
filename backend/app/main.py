from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings

from app.database.session import engine, SessionLocal
from app.database.base import Base

# Import all models to ensure they're registered with SQLAlchemy
from app.models import user, menu, order, order_item, billing, inventory
from app.models.inventory import Inventory, InventoryLog, InventoryStockUpdate
from app.models.predictive_analytics import (
    PreparationTimePrediction, QueueForecast, QueueActual,
    PeakHourPrediction, DemandForecast, CustomerBehaviorPattern,
    ChurnPrediction, RevenueForecast, PredictiveModel
)
from app.models.user import User

# Routers
from app.routers import (
    auth,
    menu,
    orders,
    admin_menu,
    admin_staff,
    admin_inventory,
    admin_kpi,
    kitchen,
    analytics,
    auth_me,
    ai_recommendations,
    predictive_analytics,
    test_predictive,
    billing,
    categories,
)
from app.routers import inventory_dashboard

# Seeding
from app.seed.admin_seed import seed_admin

# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
)

# -----------------------------
# CORS (Frontend Access)
# -----------------------------
cors_origins = settings.get_cors_origins()
print(f"CORS Origins: {cors_origins}")  # Debug line

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["OPTIONS", "GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["Content-Type", "Authorization"],
)

# -----------------------------
# Database Initialization
# -----------------------------
Base.metadata.create_all(bind=engine)

# -----------------------------
# Startup Event (Admin Seed)
# -----------------------------
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        seed_admin(db)
        
        # Initialize production queue manager
        from app.services.production_queue_manager import production_queue_manager
        production_queue_manager.start_background_updates()
        print("Production queue manager initialized and started")
        
    finally:
        db.close()

# -----------------------------
# Shutdown Event
# -----------------------------
@app.on_event("shutdown")
def shutdown_event():
    try:
        # Stop production queue manager
        from app.services.production_queue_manager import production_queue_manager
        production_queue_manager.stop_background_updates()
        print("Production queue manager stopped")
    except Exception as e:
        print(f"Error stopping production queue manager: {e}")

# -----------------------------
# API Routers
# -----------------------------
app.include_router(auth.router)
app.include_router(menu.router)
app.include_router(categories.router)
app.include_router(orders.router)

app.include_router(admin_menu.router)
app.include_router(admin_staff.router)
app.include_router(admin_inventory.router)
app.include_router(admin_kpi.router)
app.include_router(analytics.router)

app.include_router(kitchen.router)
app.include_router(auth_me.router)
app.include_router(ai_recommendations.router)
app.include_router(predictive_analytics.router)
app.include_router(test_predictive.router)
app.include_router(billing.router)
app.include_router(inventory_dashboard.router)

# -----------------------------
# Static File Serving
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# -----------------------------
# Health Check
# -----------------------------
@app.get("/")
async def root():
    return {"message": "Smart Canteen API", "status": "running", "version": "1.0.0", "health_check": "/health"}

@app.get("/test-endpoint")
async def test_endpoint():
    """Simple test endpoint to verify server is working"""
    return {"message": "Server is working!", "status": "success"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.options("/api/auth/login")
async def options_login(request: Request):
    print("OPTIONS request headers:", request.headers)
    return {"message": "Preflight request logged"}
