# backend/main.py
"""
AgroGreen AI — FastAPI Backend
Provides all AI-powered API endpoints for the platform.
"""

import os
import sys
import json
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import pandas as pd

from config.settings import DATASETS_DIR, DEMO_MODE
from backend.utils.helpers import get_demo_weather, get_demo_green_zones, get_demo_iot_data
from backend.agents.agents import WeatherAgent, MarketAgent, ImpactAgent, FundingAgent
from backend.ml.disease_detector import detect_disease

# ─── App Setup ────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AgroGreen AI API",
    description="AI-Powered Smart Farming & Urban Green Planning Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request/Response Models ──────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    history: Optional[list] = []

class ImpactRequest(BaseModel):
    area_hectares: float = 1.0
    action_type: str = "tree_plantation"
    num_trees: int = 100
    crop_type: str = "vegetables"

class ProfitRequest(BaseModel):
    crop: str
    quantity_kg: float
    city: str
    price_per_kg: float


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "app": "AgroGreen AI",
        "status": "running",
        "version": "1.0.0",
        "demo_mode": DEMO_MODE,
        "endpoints": [
            "/weather", "/chat", "/detect-disease",
            "/market-prices", "/green-zones", "/impact-analysis",
            "/iot-data", "/funding", "/docs"
        ]
    }


@app.get("/weather")
def get_weather(city: str = Query(default="Karachi")):
    """Get weather data and farming recommendations for a Pakistani city."""
    try:
        weather = get_demo_weather(city)
        alerts = WeatherAgent.get_sms_alerts(weather)
        weather["alerts"] = alerts
        return JSONResponse(content=weather)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
def chat(request: ChatRequest):
    """AI-powered crop advisor chatbot using RAG pipeline."""
    try:
        from backend.rag.crop_advisor import get_advisor
        advisor = get_advisor()
        response = advisor.chat(request.message, request.history)
        return {"response": response, "status": "success"}
    except Exception as e:
        return {"response": f"Error: {str(e)}", "status": "error"}


@app.post("/detect-disease")
async def detect_plant_disease(file: UploadFile = File(...)):
    """Upload plant image and detect disease using AI."""
    try:
        # Save uploaded file temporarily
        suffix = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Run detection
        result = detect_disease(tmp_path)
        
        # Cleanup
        os.unlink(tmp_path)
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market-prices")
def get_market_prices(
    crop: Optional[str] = None,
    city: Optional[str] = None
):
    """Get crop market prices with trends."""
    try:
        csv_path = os.path.join(DATASETS_DIR, "market_prices.csv")
        df = pd.read_csv(csv_path)
        
        if crop:
            df = df[df["crop"] == crop.lower()]
        if city:
            df = df[df["city"] == city]
        
        # Latest prices (most recent date)
        latest = df.groupby(["crop", "city"]).last().reset_index()
        
        # Summary stats
        summary = []
        for _, row in latest.iterrows():
            summary.append({
                "crop": row["crop"],
                "city": row["city"],
                "price_per_kg": row["price_per_kg"],
                "unit": "PKR",
                "trend": row["trend"],
                "trend_icon": "📈" if row["trend"] == "up" else "📉" if row["trend"] == "down" else "➡️"
            })
        
        # Chart data (time series)
        chart_data = {}
        for crop_name in df["crop"].unique():
            crop_df = df[df["crop"] == crop_name].groupby("date")["price_per_kg"].mean()
            chart_data[crop_name] = {
                "dates": crop_df.index.tolist(),
                "prices": [round(p, 2) for p in crop_df.values.tolist()]
            }
        
        # Market timing advice
        timing = {}
        for c in df["crop"].unique():
            timing[c] = MarketAgent.get_timing_advice(c)
        
        return {
            "prices": summary,
            "chart_data": chart_data,
            "market_advice": timing,
            "last_updated": "2024-03-01",
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/profit-calculator")
def calculate_profit(request: ProfitRequest):
    """Calculate profit prediction for crop sale."""
    try:
        result = MarketAgent.get_profit_prediction(
            request.crop, request.quantity_kg,
            request.city, request.price_per_kg
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/green-zones")
def get_green_zones():
    """Get green space optimization recommendations with GeoJSON data."""
    try:
        data = get_demo_green_zones()
        return JSONResponse(content=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/impact-analysis")
def analyze_impact(request: ImpactRequest):
    """Calculate environmental impact of green initiatives."""
    try:
        result = ImpactAgent.calculate_impact(
            request.area_hectares,
            request.action_type,
            request.num_trees,
            request.crop_type
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/iot-data")
def get_iot_data():
    """Get mock IoT sensor data for farm monitoring."""
    try:
        return JSONResponse(content=get_demo_iot_data())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/funding")
def get_funding(project_type: str = "general", budget: str = "medium"):
    """Get funding opportunities for agricultural projects."""
    try:
        opportunities = FundingAgent.find_funding(project_type, budget)
        return {"opportunities": opportunities, "count": len(opportunities)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    from config.settings import APP_HOST, APP_PORT
    uvicorn.run("backend.main:app", host=APP_HOST, port=APP_PORT, reload=True)
