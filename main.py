from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.summary_routes import (
    router as summary_router
)

from api.chat_routes import (
    router as chat_router
)

from api.anomaly_routes import (
    router as anomaly_router
)

from api.management_report_routes import (
    router as management_report_router
)

app = FastAPI(
    title="AI Report Service",
    description="AI-powered Property Report Service",
    version="1.0.0"
)

# ----------------------------------------
# CORS Configuration
# ----------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aereareport.panzerplayground.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------
# Register Routers
# ----------------------------------------

app.include_router(
    summary_router
)

app.include_router(
    chat_router
)

app.include_router(
    anomaly_router
)

app.include_router(
    management_report_router
)

# ----------------------------------------
# Root Endpoint
# ----------------------------------------

@app.get("/")
async def root():

    return {
        "status": "success",
        "message": "AI Report Service is running"
    }

# ----------------------------------------
# Health Check
# ----------------------------------------

@app.get("/health")
async def health():

    return {
        "status": "healthy"
    }

# ----------------------------------------
# Startup Event
# ----------------------------------------

@app.on_event("startup")
async def startup_event():

    print("=" * 60)
    print("AI REPORT SERVICE STARTED")
    print("=" * 60)

# ----------------------------------------
# Shutdown Event
# ----------------------------------------

@app.on_event("shutdown")
async def shutdown_event():

    print("=" * 60)
    print("AI REPORT SERVICE STOPPED")
    print("=" * 60)