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

from api.recommendation_routes import (
    router as recommendation_router
)

from api.workflow_routes import (
    router as workflow_router
)

from api.threshold_routes import (
    router as threshold_router
)

from api.monthly_report_routes import (
    router as monthly_report_router
)


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="AI Report Service",
    description="AI-powered Property Report Service",
    version="1.0.0",
)


# ============================================================
# CORS Configuration
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://aereareport.panzerplayground.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Register API Routers
# ============================================================

# ------------------------------------------------------------
# Summary
# ------------------------------------------------------------

app.include_router(
    summary_router
)


# ------------------------------------------------------------
# AI Chat
#
# This is now the ONLY chatbot endpoint.
#
# /chat/ask
#
# It handles:
#   - Main screen greeting
#   - Module screen greeting
#   - Module buttons
#   - User-selected module
#   - Agentic module routing
#   - Final module agent execution
# ------------------------------------------------------------

app.include_router(
    chat_router
)


# ------------------------------------------------------------
# Anomaly Detection
# ------------------------------------------------------------

app.include_router(
    anomaly_router
)


# ------------------------------------------------------------
# Management Reports
# ------------------------------------------------------------

app.include_router(
    management_report_router
)


# ------------------------------------------------------------
# Recommendations
# ------------------------------------------------------------

app.include_router(
    recommendation_router
)


# ------------------------------------------------------------
# Workflow
# ------------------------------------------------------------

app.include_router(
    workflow_router
)


# ------------------------------------------------------------
# Threshold
# ------------------------------------------------------------

app.include_router(
    threshold_router
)


# ------------------------------------------------------------
# Monthly Reports
# ------------------------------------------------------------

app.include_router(
    monthly_report_router
)


# ============================================================
# Root Endpoint
# ============================================================

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "AI Report Service is running",
    }


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "healthy",
    }


# ============================================================
# Startup Event
# ============================================================

@app.on_event("startup")
async def startup_event():

    print("=" * 60)
    print("AI REPORT SERVICE STARTED")
    print("=" * 60)

    print("CHATBOT: Agentic Chatbot")
    print("CHAT ENDPOINT: /chat/ask")

    print("SUPPORTED MODULES:")
    print(" - Feedback")
    print(" - Facility Bookings")
    print(" - Visitor Management")
    print(" - Financial Reports")
    print(" - Key Collection")
    print(" - Defects")

    print("=" * 60)


# ============================================================
# Shutdown Event
# ============================================================

@app.on_event("shutdown")
async def shutdown_event():

    print("=" * 60)
    print("AI REPORT SERVICE STOPPED")
    print("=" * 60)