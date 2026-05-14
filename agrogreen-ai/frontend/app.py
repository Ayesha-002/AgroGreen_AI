# frontend/app.py
"""
AgroGreen AI — Gradio Frontend
Beautiful green-themed multi-tab dashboard for smart farming.
"""

import os
import sys
import json
import random
import tempfile
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr
import pandas as pd
import numpy as np

from config.settings import DATASETS_DIR
from backend.utils.helpers import get_demo_weather, get_demo_green_zones, get_demo_iot_data
from backend.agents.agents import WeatherAgent, MarketAgent, ImpactAgent, FundingAgent
from backend.ml.disease_detector import detect_disease
from backend.rag.crop_advisor import get_advisor

# ─── Custom CSS ───────────────────────────────────────────────────────────────
CUSTOM_CSS = """
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');

:root {
    --green-900: #5a3f7d;
    --green-800: #6b4d8a;
    --green-700: #7c5a97;
    --green-600: #8d67a4;
    --green-500: #9e74b1;
    --green-400: #af81be;
    --green-300: #c9a8d4;
    --green-100: #e8ddf1;
    --green-50: #f5f0fa;
    --yellow: #f59e0b;
    --blue: #3b82f6;
    --red: #ef4444;
    --bg: #faf8fd;
    --card: #ffffff;
    --text: #1f2937;
    --muted: #6b7280;
    --border: #e8ddf1;
    --shadow: 0 4px 24px rgba(122,90,151,0.10);
}

* { font-family: 'Plus Jakarta Sans', sans-serif; }

body, .gradio-container { 
    background: linear-gradient(135deg, #faf8fd 0%, #f5f0fa 50%, #faf8fd 100%) !important;
    min-height: 100vh;
}

/* ── Header ── */
.agrogreen-header {
    background: linear-gradient(135deg, #5a3f7d 0%, #7c5a97 50%, #6b4d8a 100%);
    border-radius: 20px;
    padding: 28px 36px;
    margin-bottom: 24px;
    color: white;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 8px 32px rgba(90,63,125,0.3);
    position: relative;
    overflow: hidden;
}
.agrogreen-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(207,163,255,0.15) 0%, transparent 70%);
    border-radius: 50%;
}
.header-logo { font-size: 52px; }
.header-title { 
    font-size: 30px; 
    font-weight: 800; 
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: -0.5px;
}
.header-subtitle { font-size: 14px; opacity: 0.8; margin-top: 4px; }
.header-badge {
    background: rgba(207,163,255,0.2);
    border: 1px solid rgba(207,163,255,0.4);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 12px;
    color: #af81be;
    margin-left: auto;
}

/* ── Cards ── */
.metric-card {
    background: white;
    border-radius: 16px;
    padding: 20px 24px;
    box-shadow: var(--shadow);
    border: 1px solid var(--border);
    transition: transform 0.2s, box-shadow 0.2s;
}
.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(122,90,151,0.15);
}
.metric-icon { font-size: 32px; margin-bottom: 8px; }
.metric-value { 
    font-size: 28px; 
    font-weight: 700; 
    color: #7c5a97;
    font-family: 'Space Grotesk', sans-serif;
}
.metric-label { font-size: 13px; color: var(--muted); margin-top: 4px; }

/* ── Tabs ── */
.tab-nav button {
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px 18px !important;
    border-radius: 10px !important;
    transition: all 0.2s !important;
}
.tab-nav button.selected {
    background: linear-gradient(135deg, #7c5a97, #8d67a4) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(122,90,151,0.3) !important;
}

/* ── Buttons ── */
.gr-button-primary, button.primary {
    background: linear-gradient(135deg, #7c5a97, #8d67a4) !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 12px 24px !important;
    transition: all 0.2s !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(122,90,151,0.25) !important;
}
.gr-button-primary:hover, button.primary:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(122,90,151,0.35) !important;
}

/* ── Chat ── */
.chatbot-container .message.bot {
    background: linear-gradient(135deg, #faf8fd, #f5f0fa) !important;
    border: 1px solid #e8ddf1 !important;
    border-radius: 16px !important;
    padding: 16px !important;
}

/* ── Status badges ── */
.badge-success { 
    display: inline-block;
    background: #e8ddf1; color: #7c5a97; 
    border-radius: 20px; padding: 3px 12px; 
    font-size: 12px; font-weight: 600;
}
.badge-warning { 
    display: inline-block;
    background: #fef3c7; color: #d97706; 
    border-radius: 20px; padding: 3px 12px; 
    font-size: 12px; font-weight: 600;
}
.badge-danger { 
    display: inline-block;
    background: #fee2e2; color: #dc2626; 
    border-radius: 20px; padding: 3px 12px; 
    font-size: 12px; font-weight: 600;
}

/* ── Section headers ── */
.section-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #6b4d8a;
    border-left: 4px solid #9e74b1;
    padding-left: 14px;
    margin: 20px 0 14px 0;
}

/* ── Map container ── */
.map-frame { 
    border-radius: 16px !important; 
    overflow: hidden !important; 
    border: 2px solid var(--border) !important;
    box-shadow: var(--shadow) !important;
}

/* ── General containers ── */
.gr-box, .gr-panel { 
    border-radius: 16px !important;
    border: 1px solid var(--border) !important;
}

/* ── Fix: Examples text always visible ── */
.gr-samples-table td,
.gr-samples-table button,
.gr-samples-table tr td button,
.examples-holder table td,
table.gr-samples-table td button,
.gr-form .gr-examples button,
div[class*="examples"] button,
div[class*="examples"] td {
    color: #1f2937 !important;
}
div[class*="examples"] button:hover,
div[class*="examples"] td:hover {
    color: #7c5a97 !important;
    background: #faf8fd !important;
}
"""

# ─── HTML Templates ───────────────────────────────────────────────────────────

def build_header():
    return """
    <div class="agrogreen-header">
        <div class="header-logo">🌱</div>
        <div>
            <div class="header-title">AgroGreen AI</div>
            <div class="header-subtitle">AI-Powered Smart Farming & Urban Green Planning Platform</div>
        </div>
        <div class="header-badge">🤖 AI Powered • 🇵🇰 Pakistan</div>
    </div>
    """

def build_weather_card(data: dict) -> str:
    heatwave_html = '<div class="badge-danger">🔥 HEATWAVE ALERT</div>' if data.get("heatwave_alert") else ""
    forecast_rows = ""
    for f in data.get("forecast", [])[:5]:
        emoji = "☀️" if "Sunny" in f["condition"] else "🌧️" if "Rain" in f["condition"] else "⛅"
        forecast_rows += f"""
        <tr style="border-bottom:1px solid #e8ddf1;">
            <td style="padding:8px 6px;font-weight:600;">{f['date']}</td>
            <td style="padding:8px 6px;">{emoji} {f['condition']}</td>
            <td style="padding:8px 6px;color:#ef4444;">{f['temp_max']}°C</td>
            <td style="padding:8px 6px;color:#3b82f6;">{f['temp_min']}°C</td>
            <td style="padding:8px 6px;">💧 {f['rain_prob']}%</td>
        </tr>"""
    
    return f"""
    <div style="padding:4px">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;">
            <span style="font-size:48px">🌤️</span>
            <div>
                <div style="font-size:48px;font-weight:800;color:#7c5a97;font-family:'Space Grotesk',sans-serif">{data['temperature']}°C</div>
        </div>
        
        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;">
            <div class="metric-card">
                <div class="metric-icon">💧</div>
                <div class="metric-value">{data['humidity']}%</div>
                <div class="metric-label">Humidity</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">🌬️</div>
                <div class="metric-value">{data['wind_speed']}</div>
                <div class="metric-label">Wind km/h</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">🌧️</div>
                <div class="metric-value">{data['rain_probability']}%</div>
                <div class="metric-label">Rain Chance</div>
            </div>
            <div class="metric-card">
                <div class="metric-icon">☀️</div>
                <div class="metric-value">{data['uv_index']}</div>
                <div class="metric-label">UV Index</div>
            </div>
        </div>
        
        <div style="background:linear-gradient(135deg,#f5f0fa,#e8ddf1);border-radius:14px;padding:16px;margin-bottom:16px;border:1px solid #c9a8d4;">
            <div style="font-weight:700;color:#7c5a97;margin-bottom:6px;">💧 Irrigation Advisory</div>
            <div style="color:#5a3f7d;">{data['irrigation_recommendation']}</div>
        </div>
        
        <div style="background:linear-gradient(135deg,#f0e8f9,#e8ddf1);border-radius:14px;padding:16px;margin-bottom:20px;border:1px solid #d4c1e8;">
            <div style="font-weight:700;color:#7c5a97;margin-bottom:6px;">🌱 Planting Suggestion</div>
            <div style="color:#5a3f7d;">{data['planting_suggestion']}</div>
        </div>
        
        <div style="font-weight:700;font-size:16px;color:#7c5a97;margin-bottom:12px;font-family:'Space Grotesk',sans-serif;">📅 7-Day Forecast</div>
        <table style="width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.06);">
            <thead>
                <tr style="background:linear-gradient(135deg,#7c5a97,#8d67a4);color:white;">
                    <th style="padding:10px 6px;text-align:left;font-weight:600;">Date</th>
                    <th style="padding:10px 6px;text-align:left;font-weight:600;">Condition</th>
                    <th style="padding:10px 6px;text-align:left;font-weight:600;">Max</th>
                    <th style="padding:10px 6px;text-align:left;font-weight:600;">Min</th>
                    <th style="padding:10px 6px;text-align:left;font-weight:600;">Rain</th>
                </tr>
            </thead>
            <tbody>{forecast_rows}</tbody>
        </table>
    </div>"""


def build_disease_result(result: dict) -> str:
    if result.get("status") == "error":
        return f'<div style="color:red;padding:20px;">❌ Error: {result.get("error")}</div>'
    
    severity_colors = {
        "Critical": "#ef4444", "High": "#f97316", 
        "Moderate": "#f59e0b", "None": "#7c5a97"
    }
    color = severity_colors.get(result.get("severity", "Moderate"), "#f59e0b")
    
    treatments = "".join([f'<li style="margin:6px 0;color:#1f2937;">{t}</li>' for t in result.get("treatment", [])])
    preventions = "".join([f'<li style="margin:6px 0;color:#1f2937;">{p}</li>' for p in result.get("prevention", [])])
    
    return f"""
    <div style="padding:4px">
        <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;background:white;border-radius:16px;padding:20px;box-shadow:0 4px 16px rgba(0,0,0,0.08);">
            <div style="font-size:56px">{result.get('icon','🌿')}</div>
            <div style="flex:1">
                <div style="font-size:22px;font-weight:800;color:#1f2937;font-family:'Space Grotesk',sans-serif">{result.get('disease','Unknown')}</div>
                <div style="color:#6b7280;font-size:13px;margin:4px 0">{result.get('pathogen','')}</div>
                <div style="display:flex;gap:10px;margin-top:8px;align-items:center;">
                    <div style="background:linear-gradient(135deg,#7c5a97,#8d67a4);color:white;border-radius:20px;padding:4px 14px;font-size:13px;font-weight:600;">
                        🎯 {result.get('confidence',0)}% Confidence
                    </div>
                    <div style="background:{color}20;color:{color};border-radius:20px;padding:4px 14px;font-size:13px;font-weight:600;border:1px solid {color}40;">
                        ⚠️ {result.get('severity','Unknown')} Severity
                    </div>
                </div>
            </div>
        </div>
        
        <div style="background:#fef9c3;border-radius:14px;padding:14px;margin-bottom:14px;border-left:4px solid #f59e0b;color:#1f2937;">
            <strong style="color:#92400e;">📋 Symptoms:</strong> <span style="color:#1f2937;">{result.get('symptoms','')}</span>
        </div>
        
        <div style="margin-bottom:14px;background:#f5f0fa;border-radius:14px;padding:16px;border:1px solid #e8ddf1;">
            <div style="font-weight:700;color:#7c5a97;font-size:15px;margin-bottom:10px;">💊 Treatment Plan</div>
            <ul style="margin:0;padding-left:20px;color:#1f2937;">{treatments}</ul>
        </div>
        
        <div style="background:#eff6ff;border-radius:14px;padding:16px;border:1px solid #bfdbfe;">
            <div style="font-weight:700;color:#1d4ed8;font-size:15px;margin-bottom:10px;">🛡️ Prevention</div>
            <ul style="margin:0;padding-left:20px;color:#1f2937;">{preventions}</ul>
        </div>
        
        <div style="margin-top:14px;padding:14px;background:linear-gradient(135deg,#5a3f7d,#7c5a97);color:white;border-radius:14px;text-align:center;font-weight:600;">
            {result.get('recommendation','')}
        </div>
    </div>"""


def build_market_table(prices: list) -> str:
    crop_icons = {"wheat": "🌾", "rice": "🍚", "cotton": "🌿", "tomato": "🍅", "sugarcane": "🌱"}
    trend_icons = {"up": "📈", "down": "📉", "stable": "➡️"}
    rows = ""
    for p in prices:
        icon = crop_icons.get(p["crop"], "🌾")
        trend = p.get("trend", "stable")
        trend_icon = trend_icons.get(trend, "➡️")
        trend_html = f'<span style="color:#9e74b1">{trend_icon}</span>' if trend == "up" else \
                     f'<span style="color:#ef4444">{trend_icon}</span>' if trend == "down" else \
                     f'<span style="color:#6b7280">{trend_icon}</span>'
        rows += f"""
        <tr style="border-bottom:1px solid #e8ddf1;">
            <td style="padding:12px 10px;">{icon} <strong>{p['crop'].title()}</strong></td>
            <td style="padding:12px 10px;">📍 {p['city']}</td>
            <td style="padding:12px 10px;font-size:18px;font-weight:700;color:#7c5a97;font-family:'Space Grotesk',sans-serif;">PKR {p['price_per_kg']}</td>
            <td style="padding:12px 10px;">{trend_html} {p['trend'].title()}</td>
        </tr>"""
    
    return f"""
    <table style="width:100%;border-collapse:collapse;background:white;border-radius:14px;overflow:hidden;box-shadow:0 4px 16px rgba(0,0,0,0.08);">
        <thead>
            <tr style="background:linear-gradient(135deg,#7c5a97,#8d67a4);color:black;">
                <th style="padding:14px 10px;text-align:left;font-weight:700;">Crop</th>
                <th style="padding:14px 10px;text-align:left;font-weight:700;">Market</th>
                <th style="padding:14px 10px;text-align:left;font-weight:700;">Price/kg</th>
                <th style="padding:14px 10px;text-align:left;font-weight:700;">Trend</th>
            </tr>
        </thead>
        <tbody>{rows}</tbody>
    </table>"""


def build_impact_card(result: dict) -> str:
    before = result.get("before_after", {})
    funding = result.get("funding_opportunities", [])
    funding_html = "".join([f"""
        <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 14px;background:white;border-radius:10px;margin-bottom:8px;border:1px solid #e8ddf1;">
            <div><strong>{f['name']}</strong> — {f['amount']}</div>
            <div style="background:#e8ddf1;color:#7c5a97;border-radius:20px;padding:3px 10px;font-size:12px;font-weight:700;">{f['match']} match</div>
        </div>""" for f in funding[:3]])
    
    return f"""
    <div style="padding:4px">
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;margin-bottom:20px;">
            <div class="metric-card" style="text-align:center;">
                <div style="font-size:36px">🌿</div>
                <div class="metric-value">{result.get('co2_saved_tonnes',0)} t</div>
                <div class="metric-label">CO₂ Saved/Year</div>
                <div style="font-size:11px;color:#6b7280;margin-top:4px">{result.get('co2_equivalent','')}</div>
            </div>
            <div class="metric-card" style="text-align:center;">
                <div style="font-size:36px">🌡️</div>
                <div class="metric-value">{result.get('temperature_reduction',0)}°C</div>
                <div class="metric-label">Temp Reduction</div>
            </div>
            <div class="metric-card" style="text-align:center;">
                <div style="font-size:36px">💧</div>
                <div class="metric-value">{result.get('water_saved_readable','')}</div>
                <div class="metric-label">Water Saved</div>
            </div>
            <div class="metric-card" style="text-align:center;">
                <div style="font-size:36px">🌳</div>
                <div class="metric-value">{result.get('trees_equivalent',0)}</div>
                <div class="metric-label">Tree Equivalent</div>
            </div>
        </div>
        
        <div style="background:linear-gradient(135deg,#5a3f7d,#7c5a97);border-radius:16px;padding:20px;margin-bottom:20px;color:white;text-align:center;">
            <div style="font-size:14px;opacity:0.8;margin-bottom:6px;">🌍 Sustainability Score</div>
            <div style="font-size:56px;font-weight:800;font-family:'Space Grotesk',sans-serif">{result.get('sustainability_score',0)}<span style="font-size:24px">/100</span></div>
            <div style="font-size:13px;opacity:0.7;margin-top:6px;">💰 Carbon Credits: ${result.get('carbon_credits_usd',0):,.0f} USD potential</div>
        </div>
        
        <div style="font-weight:700;font-size:16px;color:#7c5a97;margin-bottom:12px;font-family:'Space Grotesk',sans-serif;">💰 Matching Funding Opportunities</div>
        {funding_html}
    </div>"""


def build_iot_card(data: dict) -> str:
    sensors_html = ""
    for s in data.get("sensors", []):
        moisture = s["soil_moisture"]
        status_color = "#9e74b1" if s["irrigation_status"] == "Active" else "#f59e0b"
        sensors_html += f"""
        <div class="metric-card" style="margin-bottom:12px;">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                <div>
                    <div style="font-weight:700;color:#1f2937;">📡 {s['location']}</div>
                    <div style="font-size:12px;color:#6b7280;">Sensor #{s['id']} • {s['last_reading']}</div>
                </div>
                <div style="background:{status_color}20;color:{status_color};border-radius:20px;padding:4px 12px;font-size:12px;font-weight:600;">
                    ⚡ {s['irrigation_status']}
                </div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px;text-align:center;">
                <div style="background:#faf8fd;border-radius:10px;padding:10px;">
                    <div style="font-size:18px">💧</div>
                    <div style="font-weight:700;color:#7c5a97;font-size:16px">{moisture}%</div>
                    <div style="font-size:11px;color:#6b7280;">Soil Moisture</div>
                </div>
                <div style="background:#fffbeb;border-radius:10px;padding:10px;">
                    <div style="font-size:18px">🌡️</div>
                    <div style="font-weight:700;color:#d97706;font-size:16px">{s['soil_temp']}°</div>
                    <div style="font-size:11px;color:#6b7280;">Soil Temp</div>
                </div>
                <div style="background:#eff6ff;border-radius:10px;padding:10px;">
                    <div style="font-size:18px">☁️</div>
                    <div style="font-weight:700;color:#3b82f6;font-size:16px">{s['air_temp']}°</div>
                    <div style="font-size:11px;color:#6b7280;">Air Temp</div>
                </div>
                <div style="background:#f5f3ff;border-radius:10px;padding:10px;">
                    <div style="font-size:18px">🔋</div>
                    <div style="font-weight:700;color:#7c3aed;font-size:16px">{s['battery']}%</div>
                    <div style="font-size:11px;color:#6b7280;">Battery</div>
                </div>
            </div>
        </div>"""
    
    alerts_html = ""
    for a in data.get("alerts", []):
        icon = "⚠️" if a["type"] == "warning" else "✅" if a["type"] == "success" else "ℹ️"
        bg = "#fef3c7" if a["type"] == "warning" else "#e8ddf1" if a["type"] == "success" else "#eff6ff"
        alerts_html += f'<div style="background:{bg};border-radius:10px;padding:10px 14px;margin-bottom:8px;">{icon} <strong>{a["message"]}</strong> <span style="color:#9ca3af;font-size:12px">— {a["time"]}</span></div>'
    
    return f"""
    <div style="padding:4px">
        <div style="font-weight:700;font-size:16px;color:#7c5a97;margin-bottom:14px;font-family:'Space Grotesk',sans-serif;">📡 Live IoT Sensor Readings</div>
        {sensors_html}
        <div style="font-weight:700;font-size:16px;color:#7c5a97;margin:14px 0 10px;font-family:'Space Grotesk',sans-serif;">🔔 System Alerts</div>
        {alerts_html}
    </div>"""


def build_map_html(zones_geojson: dict) -> str:
    """Build Leaflet.js map with green zone markers wrapped in an iframe."""
    features_json = json.dumps(zones_geojson)
    type_colors = {
        "rooftop_farming": "#f59e0b",
        "tree_plantation": "#9e74b1",
        "urban_park": "#3b82f6",
        "smart_irrigation": "#6366f1",
        "agroforestry": "#7c5a97"
    }
    colors_json = json.dumps(type_colors)
    
    map_inner = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
    body {{ margin:0; font-family:'Segoe UI',sans-serif; }}
    #map {{ height:100vh; width:100%; }}
    .legend {{ background:white; padding:12px 16px; border-radius:10px; box-shadow:0 2px 12px rgba(0,0,0,0.15); font-size:12px; line-height:1.8; }}
    .legend-item {{ display:flex; align-items:center; gap:8px; }}
    .legend-dot {{ width:12px; height:12px; border-radius:50%; }}
    .custom-popup .leaflet-popup-content-wrapper {{ border-radius:14px; box-shadow:0 8px 32px rgba(0,0,0,0.15); border:none; }}
    .popup-content {{ padding:4px; }}
    .popup-title {{ font-weight:700; font-size:14px; color:#7c5a97; margin-bottom:6px; }}
    .popup-stat {{ display:flex; justify-content:space-between; font-size:12px; padding:4px 0; border-bottom:1px solid #faf8fd; }}
</style>
</head>
<body>
<div id="map"></div>
<script>
const map = L.map('map').setView([24.8607, 67.0011], 12);
L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    attribution: '© OpenStreetMap contributors'
}}).addTo(map);

const data = {features_json};
const colors = {colors_json};

data.features.forEach(f => {{
    const props = f.properties;
    const coords = f.geometry.coordinates;
    const color = colors[props.type] || '#7c5a97';
    const score = props.score;
    
    const marker = L.circleMarker([coords[1], coords[0]], {{
        radius: 8 + (score / 15),
        fillColor: color,
        color: 'white',
        weight: 2,
        opacity: 1,
        fillOpacity: 0.85
    }}).addTo(map);
    
    marker.bindPopup(`
        <div class="popup-content">
            <div class="popup-title">${{props.icon}} ${{props.name}}</div>
            <div class="popup-stat"><span>🌿 Type</span><strong>${{props.type.replace('_',' ').toUpperCase()}}</strong></div>
            <div class="popup-stat"><span>📊 Green Score</span><strong>${{props.score}}/100</strong></div>
            <div class="popup-stat"><span>📐 Area</span><strong>${{props.area_sqm.toLocaleString()}} m²</strong></div>
            <div class="popup-stat"><span>🌍 CO₂ Saved</span><strong>${{props.co2_saved}}</strong></div>
            <div style="margin-top:8px;background:#faf8fd;border-radius:8px;padding:8px;font-size:12px;color:#7c5a97;">${{props.suggestion}}</div>
        </div>
    `, {{className: 'custom-popup', maxWidth: 280}});
}});

const legend = L.control({{position: 'bottomright'}});
legend.onAdd = () => {{
    const div = L.DomUtil.create('div', 'legend');
    div.innerHTML = `
        <div style="font-weight:700;margin-bottom:8px;color:#7c5a97;">🗺️ Zone Types</div>
        <div class="legend-item"><div class="legend-dot" style="background:#f59e0b"></div>Rooftop Farming</div>
        <div class="legend-item"><div class="legend-dot" style="background:#9e74b1"></div>Tree Plantation</div>
        <div class="legend-item"><div class="legend-dot" style="background:#3b82f6"></div>Urban Park</div>
        <div class="legend-item"><div class="legend-dot" style="background:#6366f1"></div>Smart Irrigation</div>
        <div class="legend-item"><div class="legend-dot" style="background:#7c5a97"></div>Agroforestry</div>
    `;
    return div;
}};
legend.addTo(map);
</script>
</body>
</html>"""
    
    import base64
    encoded = base64.b64encode(map_inner.encode('utf-8')).decode('utf-8')
    return f'<iframe src="data:text/html;base64,{encoded}" width="100%" height="480px" style="border:none;border-radius:16px;box-shadow:0 4px 24px rgba(5,150,105,0.10);"></iframe>'


def build_funding_cards(opportunities: list) -> str:
    type_colors = {"Grant": "#9e74b1", "Loan + Grant": "#3b82f6", "Research Grant": "#8b5cf6",
                   "Government Grant": "#f59e0b", "Subsidized Loan": "#6366f1", "Grant + Technical Support": "#ec4899"}
    
    cards = ""
    for opp in opportunities:
        color = type_colors.get(opp["type"], "#9e74b1")
        cards += f"""
        <div style="background:white;border-radius:16px;padding:20px;border:1px solid #e8ddf1;box-shadow:0 4px 16px rgba(0,0,0,0.06);margin-bottom:14px;transition:transform 0.2s;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px;">
                <div>
                    <div style="font-size:24px;margin-bottom:6px">{opp['icon']}</div>
                    <div style="font-weight:700;font-size:16px;color:#1f2937;font-family:'Space Grotesk',sans-serif">{opp['name']}</div>
                </div>
                <div style="background:{color}15;color:{color};border-radius:20px;padding:4px 12px;font-size:12px;font-weight:700;border:1px solid {color}30;">{opp['type']}</div>
            </div>
            <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;font-size:13px;margin-bottom:12px;">
                <div><span style="color:#6b7280;">💰 Amount:</span> <strong>{opp['amount']}</strong></div>
                <div><span style="color:#6b7280;">⏰ Deadline:</span> <strong>{opp['deadline']}</strong></div>
                <div style="grid-column:1/-1"><span style="color:#6b7280;">🎯 Focus:</span> <strong>{opp['focus']}</strong></div>
                <div style="grid-column:1/-1"><span style="color:#6b7280;">✅ Eligible:</span> {opp['eligibility']}</div>
            </div>
            <a href="{opp['url']}" target="_blank" style="display:inline-block;background:linear-gradient(135deg,#7c5a97,#8d67a4);color:white;padding:8px 18px;border-radius:10px;font-size:13px;font-weight:600;text-decoration:none;">
                🔗 Apply Now →
            </a>
        </div>"""
    
    return f'<div style="padding:4px">{cards}</div>'


# ─── Action Functions ─────────────────────────────────────────────────────────

def fetch_weather(city):
    data = get_demo_weather(city)
    return build_weather_card(data)

def chat_fn(message, history):
    if not message.strip():
        return history, ""
    advisor = get_advisor()
    response = advisor.chat(message, history)
    history = history or []
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": response})
    return history, ""

def run_disease_detection(image):
    if image is None:
        return '<div style="padding:40px;text-align:center;color:#6b7280;font-size:16px;">📤 Please upload a plant image to analyze</div>'
    
    # Save image temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        from PIL import Image as PILImage
        if isinstance(image, np.ndarray):
            PILImage.fromarray(image.astype(np.uint8)).save(tmp.name)
        else:
            import shutil
            shutil.copy(image, tmp.name)
        tmp_path = tmp.name
    
    result = detect_disease(tmp_path)
    try:
        os.unlink(tmp_path)
    except:
        pass
    
    return build_disease_result(result)

def fetch_market_prices(selected_crop, selected_city):
    try:
        csv_path = os.path.join(DATASETS_DIR, "market_prices.csv")
        df = pd.read_csv(csv_path)
        
        # Ensure required columns exist
        if "trend" not in df.columns:
            df["trend"] = "stable"
        
        if selected_crop != "All Crops":
            df = df[df["crop"] == selected_crop.lower()]
        if selected_city != "All Cities":
            df = df[df["city"] == selected_city]
        
        latest = df.groupby(["crop", "city"]).last().reset_index()
        prices = latest.to_dict("records")
        table_html = build_market_table(prices)
        
        # Profit advice
        advice_list = []
        for crop in df["crop"].unique():
            advice = MarketAgent.get_timing_advice(crop)
            advice_list.append(f"<div style='margin-bottom:8px;background:#faf8fd;border-radius:10px;padding:10px 14px;border-left:3px solid #9e74b1;'><strong>{crop.title()}:</strong> {advice}</div>")
        
        advice_html = f"""
        <div style="padding:4px">
            <div style="font-weight:700;font-size:16px;color:#7c5a97;margin-bottom:12px;font-family:'Space Grotesk',sans-serif;">⏰ Market Timing Advice</div>
            {''.join(advice_list)}
        </div>"""
        
        return table_html, advice_html
        
    except Exception as e:
        return f"<p>Error: {e}</p>", ""

def calculate_profit(crop, qty, city, price):
    if not all([crop, qty, city, price]):
        return '<div style="padding:20px;color:#6b7280;">Please fill all fields to calculate profit.</div>'
    
    result = MarketAgent.get_profit_prediction(crop.lower(), float(qty), city, float(price))
    
    profit_color = "#9e74b1" if result["net_profit"] > 0 else "#ef4444"
    
    return f"""
    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;padding:4px;">
        <div class="metric-card" style="text-align:center;border-top:3px solid #9e74b1;">
            <div class="metric-icon">💰</div>
            <div class="metric-value" style="color:{profit_color};">PKR {result['net_profit']:,.0f}</div>
            <div class="metric-label">Net Profit</div>
        </div>
        <div class="metric-card" style="text-align:center;border-top:3px solid #3b82f6;">
            <div class="metric-icon">📈</div>
            <div class="metric-value" style="color:#3b82f6;">{result['roi_percent']}%</div>
            <div class="metric-label">ROI</div>
        </div>
        <div class="metric-card" style="text-align:center;">
            <div class="metric-icon">💵</div>
            <div class="metric-value">PKR {result['gross_revenue']:,.0f}</div>
            <div class="metric-label">Gross Revenue</div>
        </div>
        <div class="metric-card" style="text-align:center;">
            <div class="metric-icon">🏭</div>
            <div class="metric-value">PKR {result['estimated_cost']:,.0f}</div>
            <div class="metric-label">Estimated Cost</div>
        </div>
        <div class="metric-card" style="grid-column:1/-1;background:linear-gradient(135deg,#f0fdf4,#d1fae5);border:1px solid #a7f3d0;">
            <div style="font-size:16px;color:#047857;font-weight:700;">{result['advice']}</div>
        </div>
    </div>"""

def run_impact_analysis(area, action_type, num_trees, crop_type):
    result = ImpactAgent.calculate_impact(
        float(area), action_type, int(num_trees), crop_type
    )
    return build_impact_card(result)

def refresh_iot():
    return build_iot_card(get_demo_iot_data())

def load_green_map():
    zones = get_demo_green_zones()
    return build_map_html(zones)

def load_funding():
    opportunities = FundingAgent.find_funding()
    return build_funding_cards(opportunities)


# ─── Build Dashboard ──────────────────────────────────────────────────────────

def build_dashboard_summary() -> str:
    weather = get_demo_weather("Karachi")
    return f"""
    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:24px;">
        <div class="metric-card" style="border-top:3px solid #10b981;text-align:center;">
            <div class="metric-icon">🌡️</div>
            <div class="metric-value">{weather['temperature']}°C</div>
            <div class="metric-label">Karachi Temp</div>
        </div>
        <div class="metric-card" style="border-top:3px solid #3b82f6;text-align:center;">
            <div class="metric-icon">🌧️</div>
            <div class="metric-value">{weather['rain_probability']}%</div>
            <div class="metric-label">Rain Chance</div>
        </div>
        <div class="metric-card" style="border-top:3px solid #f59e0b;text-align:center;">
            <div class="metric-icon">🌾</div>
            <div class="metric-value">PKR 70</div>
            <div class="metric-label">Wheat Price/kg</div>
        </div>
        <div class="metric-card" style="border-top:3px solid #8b5cf6;text-align:center;">
            <div class="metric-icon">🌍</div>
            <div class="metric-value">82/100</div>
            <div class="metric-label">Eco Score</div>
        </div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;">
        <div style="background:linear-gradient(135deg,#064e3b,#047857);color:white;border-radius:16px;padding:20px;">
            <div style="font-size:28px;margin-bottom:8px;">🤖</div>
            <div style="font-weight:700;font-size:15px;margin-bottom:4px;">AI Crop Advisor</div>
            <div style="font-size:13px;opacity:0.8;">Ask anything about your crops — powered by RAG + OpenAI</div>
        </div>
        <div style="background:linear-gradient(135deg,#1e3a8a,#1d4ed8);color:white;border-radius:16px;padding:20px;">
            <div style="font-size:28px;margin-bottom:8px;">🔬</div>
            <div style="font-weight:700;font-size:15px;margin-bottom:4px;">Disease Detector</div>
            <div style="font-size:13px;opacity:0.8;">Upload plant photo for instant AI disease diagnosis</div>
        </div>
        <div style="background:linear-gradient(135deg,#78350f,#d97706);color:white;border-radius:16px;padding:20px;">
            <div style="font-size:28px;margin-bottom:8px;">📈</div>
            <div style="font-weight:700;font-size:15px;margin-bottom:4px;">Market Advisor</div>
            <div style="font-size:13px;opacity:0.8;">Real-time crop prices across Pakistan's major markets</div>
        </div>
    </div>"""


# ─── Main Gradio App ──────────────────────────────────────────────────────────

with gr.Blocks(
    css=CUSTOM_CSS,
    title="🌱 AgroGreen AI — Smart Farming Platform",
    theme=gr.themes.Base(
        primary_hue=gr.themes.colors.green,
        secondary_hue=gr.themes.colors.emerald,
        neutral_hue=gr.themes.colors.slate,
        font=[gr.themes.GoogleFont("Plus Jakarta Sans"), "sans-serif"],
    )
) as app:
    
    # ── Header ──
    gr.HTML(build_header())
    
    with gr.Tabs(elem_classes=["tab-nav"]):
        
        # ── Tab 1: Dashboard ──────────────────────────────────────────────────
        with gr.TabItem("🏠 Dashboard"):
            gr.HTML('<div class="section-title">📊 Live Platform Overview</div>')
            dashboard_html = gr.HTML(build_dashboard_summary())
            
            gr.HTML("""
            <div style="background:linear-gradient(135deg,#f0fdf4,#ecfdf5);border-radius:16px;padding:20px;margin-top:16px;border:1px solid #d1fae5;">
                <div style="font-weight:700;font-size:16px;color:#047857;margin-bottom:10px;font-family:'Space Grotesk',sans-serif;">
                    🌟 Platform Features
                </div>
                <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:10px;font-size:13px;color:#065f46;">
                    <div>🌤️ Smart Weather Advisor</div>
                    <div>🤖 RAG Crop Chatbot</div>
                    <div>🔬 Disease Detection AI</div>
                    <div>📈 Market Price Tracker</div>
                    <div>🗺️ GreenLens Maps</div>
                    <div>🌍 Impact Calculator</div>
                    <div>📡 IoT Dashboard</div>
                    <div>💰 Funding Finder</div>
                </div>
            </div>""")
        
        # ── Tab 2: Weather ────────────────────────────────────────────────────
        with gr.TabItem("🌤️ Weather"):
            gr.HTML('<div class="section-title">🌤️ Smart Weather Advisor</div>')
            with gr.Row():
                city_input = gr.Dropdown(
                    choices=["Karachi", "Lahore", "Islamabad", "Hyderabad", "Multan", "Faisalabad"],
                    value="Karachi", label="📍 Select City", scale=2
                )
                weather_btn = gr.Button("🔄 Get Weather & Advisory", variant="primary", scale=1)
            
            weather_output = gr.HTML(label="Weather Report")
            gr.HTML("""
            <div style="background:linear-gradient(135deg,#f0fdf4,#ecfdf5);border-radius:14px;padding:18px 22px;margin-top:14px;border:1px solid #d1fae5;">
                <div style="font-weight:700;font-size:15px;color:#047857;margin-bottom:12px;font-family:'Space Grotesk',sans-serif;">🌾 Seasonal Farming Calendar</div>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;font-size:13px;">
                    <div style="background:white;border-radius:10px;padding:12px;border:1px solid #d1fae5;">
                        <div style="font-weight:700;color:#065f46;margin-bottom:6px;">🌱 Rabi Season (Oct–Mar)</div>
                        <div style="color:#374151;">Wheat, Mustard, Chickpea, Barley. Sow when soil temp &lt; 25°C.</div>
                    </div>
                    <div style="background:white;border-radius:10px;padding:12px;border:1px solid #d1fae5;">
                        <div style="font-weight:700;color:#065f46;margin-bottom:6px;">☀️ Kharif Season (Apr–Sep)</div>
                        <div style="color:#374151;">Rice, Cotton, Sugarcane, Maize. Plant after last frost, needs 30°C+.</div>
                    </div>
                    <div style="background:white;border-radius:10px;padding:12px;border:1px solid #d1fae5;">
                        <div style="font-weight:700;color:#065f46;margin-bottom:6px;">💧 Irrigation Tips</div>
                        <div style="color:#374151;">Irrigate early morning (5–7 AM) or evening (6–8 PM) to minimise evaporation.</div>
                    </div>
                </div>
            </div>""")
            
            weather_btn.click(fetch_weather, inputs=[city_input], outputs=[weather_output])
            app.load(lambda: fetch_weather("Karachi"), outputs=[weather_output])
        
        # ── Tab 3: AI Chatbot ─────────────────────────────────────────────────
        with gr.TabItem("🤖 AI Advisor"):
            gr.HTML('<div class="section-title">🤖 AI Crop Advisor — RAG Powered</div>')
            gr.HTML('<div style="background:#f0fdf4;border-radius:12px;padding:12px 16px;border:1px solid #d1fae5;margin-bottom:14px;font-size:13px;color:#065f46;">💡 Ask in <strong>English or Urdu</strong>. Try: "میری ٹماٹر کی پتیاں پیلی ہو رہی ہیں" or "How to grow wheat in Sindh?"</div>')
            
            chatbot = gr.Chatbot(
                label="🌱 AgroGreen AI Advisor",
                height=420,
                type="messages",
                avatar_images=("👨‍🌾", "🌱"),
                show_copy_button=True,
            )
            
            with gr.Row():
                chat_input = gr.Textbox(
                    placeholder="Ask about crops, diseases, fertilizers, irrigation...",
                    label="Your Question",
                    scale=4
                )
                chat_btn = gr.Button("Send 📤", variant="primary", scale=1)
            
            with gr.Row():
                gr.Examples(
                    examples=[
                        ["My tomato leaves are turning yellow — what should I do?"],
                        ["How to grow wheat in Sindh? Best variety and fertilizer?"],
                        ["How to control whitefly on cotton?"],
                        ["What is the best time to sell wheat for maximum profit?"],
                        ["گندم کی کاشت کیسے کریں؟"],
                        ["How to do organic farming in Pakistan?"],
                    ],
                    inputs=[chat_input],
                )
            
            chat_btn.click(chat_fn, inputs=[chat_input, chatbot], outputs=[chatbot, chat_input])
            chat_input.submit(chat_fn, inputs=[chat_input, chatbot], outputs=[chatbot, chat_input])
        
        # ── Tab 4: Disease Detection ──────────────────────────────────────────
        with gr.TabItem("🔬 Disease Detection"):
            gr.HTML('<div class="section-title">🔬 AI Plant Disease Detector</div>')
            
            with gr.Row():
                with gr.Column(scale=1):
                    image_input = gr.Image(
                        label="📸 Upload Plant Image",
                        type="numpy",
                        sources=["upload", "webcam"],
                        height=280
                    )
                    detect_btn = gr.Button("🔍 Analyze Disease", variant="primary")
                    gr.HTML('<div style="font-size:12px;color:#6b7280;padding:8px;text-align:center;">Supports: JPG, PNG, WEBP • Works with leaf, stem, fruit images</div>')
                
                with gr.Column(scale=2):
                    disease_output = gr.HTML(
                        '<div style="padding:60px;text-align:center;color:#9ca3af;font-size:16px;">📸 Upload a plant image and click Analyze to detect diseases</div>'
                    )
            
            detect_btn.click(run_disease_detection, inputs=[image_input], outputs=[disease_output])
        
        # ── Tab 5: Market Prices ──────────────────────────────────────────────
        with gr.TabItem("📈 Market Prices"):
            gr.HTML('<div class="section-title">📈 Crop Market Price Advisor</div>')
            
            with gr.Row():
                crop_filter = gr.Dropdown(
                    choices=["All Crops", "Wheat", "Rice", "Cotton", "Tomato", "Sugarcane"],
                    value="All Crops", label="🌾 Filter by Crop", scale=1
                )
                city_filter = gr.Dropdown(
                    choices=["All Cities", "Karachi", "Lahore", "Islamabad", "Hyderabad"],
                    value="All Cities", label="📍 Filter by City", scale=1
                )
                market_btn = gr.Button("📊 Load Market Prices", variant="primary", scale=1)
            
            market_table = gr.HTML()
            market_advice = gr.HTML()
            
            gr.HTML('<div class="section-title" style="margin-top:20px;">💰 Profit Calculator</div>')
            with gr.Row():
                pc_crop = gr.Dropdown(["Wheat", "Rice", "Cotton", "Tomato", "Sugarcane"], label="Crop", value="Wheat")
                pc_qty = gr.Number(label="Quantity (kg)", value=1000)
                pc_city = gr.Dropdown(["Karachi", "Lahore", "Islamabad", "Hyderabad"], label="Target Market", value="Karachi")
                pc_price = gr.Number(label="Expected Price (PKR/kg)", value=70)
            
            pc_btn = gr.Button("💰 Calculate Profit", variant="primary")
            profit_output = gr.HTML()
            
            market_btn.click(fetch_market_prices, inputs=[crop_filter, city_filter], outputs=[market_table, market_advice])
            pc_btn.click(calculate_profit, inputs=[pc_crop, pc_qty, pc_city, pc_price], outputs=[profit_output])
            app.load(lambda: fetch_market_prices("All Crops", "All Cities"), outputs=[market_table, market_advice])
        
        # ── Tab 6: GreenLens Map ──────────────────────────────────────────────
        with gr.TabItem("🗺️ GreenLens Map"):
            gr.HTML('<div class="section-title">🗺️ Urban Green Space Optimizer</div>')
            gr.HTML('<div style="background:#f0fdf4;border-radius:12px;padding:12px 16px;border:1px solid #d1fae5;margin-bottom:14px;font-size:13px;color:#065f46;">🌍 Interactive map showing AI-recommended green zones for Karachi. Click markers for details.</div>')
            
            map_html_output = gr.HTML()
            refresh_map_btn = gr.Button("🔄 Refresh Map", variant="primary", scale=0)
            
            app.load(load_green_map, outputs=[map_html_output])
            refresh_map_btn.click(load_green_map, outputs=[map_html_output])
        
        # ── Tab 7: Environmental Impact ───────────────────────────────────────
        with gr.TabItem("🌍 Eco Impact"):
            gr.HTML('<div class="section-title">🌍 Environmental Impact Predictor</div>')
            
            with gr.Row():
                with gr.Column(scale=1):
                    impact_area = gr.Number(label="Area (hectares)", value=2.0)
                    impact_action = gr.Dropdown(
                        choices=["tree_plantation", "rooftop_farming", "urban_park", "agroforestry", "drip_irrigation"],
                        value="tree_plantation",
                        label="🌿 Green Action Type"
                    )
                    impact_trees = gr.Number(label="Number of Trees (if applicable)", value=200)
                    impact_crop = gr.Dropdown(
                        choices=["vegetables", "fruit_trees", "herbs", "grains"],
                        value="vegetables", label="Crop Type"
                    )
                    impact_btn = gr.Button("🌍 Calculate Impact", variant="primary")
                
                with gr.Column(scale=2):
                    impact_output = gr.HTML()
            
            impact_btn.click(
                run_impact_analysis,
                inputs=[impact_area, impact_action, impact_trees, impact_crop],
                outputs=[impact_output]
            )
            app.load(
                lambda: run_impact_analysis(2.0, "tree_plantation", 200, "vegetables"),
                outputs=[impact_output]
            )
        
        # ── Tab 8: IoT Dashboard ──────────────────────────────────────────────
        with gr.TabItem("📡 IoT Monitor"):
            gr.HTML('<div class="section-title">📡 Real-Time Farm IoT Monitor</div>')
            gr.HTML("""
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px;">
                <div style="background:linear-gradient(135deg,#064e3b,#047857);color:white;border-radius:14px;padding:16px;text-align:center;">
                    <div style="font-size:28px;margin-bottom:4px;">📡</div>
                    <div style="font-size:22px;font-weight:700;font-family:'Space Grotesk',sans-serif;">3</div>
                    <div style="font-size:12px;opacity:0.8;">Active Sensors</div>
                </div>
                <div style="background:linear-gradient(135deg,#1e3a8a,#1d4ed8);color:white;border-radius:14px;padding:16px;text-align:center;">
                    <div style="font-size:28px;margin-bottom:4px;">💧</div>
                    <div style="font-size:22px;font-weight:700;font-family:'Space Grotesk',sans-serif;">52%</div>
                    <div style="font-size:12px;opacity:0.8;">Avg Soil Moisture</div>
                </div>
                <div style="background:linear-gradient(135deg,#78350f,#d97706);color:white;border-radius:14px;padding:16px;text-align:center;">
                    <div style="font-size:28px;margin-bottom:4px;">🌡️</div>
                    <div style="font-size:22px;font-weight:700;font-family:'Space Grotesk',sans-serif;">31°C</div>
                    <div style="font-size:12px;opacity:0.8;">Avg Air Temp</div>
                </div>
                <div style="background:linear-gradient(135deg,#4c1d95,#7c3aed);color:white;border-radius:14px;padding:16px;text-align:center;">
                    <div style="font-size:28px;margin-bottom:4px;">🔋</div>
                    <div style="font-size:22px;font-weight:700;font-family:'Space Grotesk',sans-serif;">85%</div>
                    <div style="font-size:12px;opacity:0.8;">Avg Battery</div>
                </div>
            </div>""")
            with gr.Row():
                iot_output = gr.HTML()
            iot_refresh_btn = gr.Button("🔄 Refresh Sensor Data", variant="primary")
            
            iot_refresh_btn.click(refresh_iot, outputs=[iot_output])
            app.load(refresh_iot, outputs=[iot_output])
        
        # ── Tab 9: Funding Finder ─────────────────────────────────────────────
        with gr.TabItem("💰 Funding Finder"):
            gr.HTML('<div class="section-title">💰 Agricultural Funding & Grants</div>')
            gr.HTML('<div style="background:#fffbeb;border-radius:12px;padding:12px 16px;border:1px solid #fde68a;margin-bottom:14px;font-size:13px;color:#92400e;">💡 AI-matched funding opportunities for Pakistani farmers and green initiatives. Click "Apply Now" to visit official sources.</div>')
            
            funding_output = gr.HTML()
            app.load(load_funding, outputs=[funding_output])
    
    # ── Footer ──
    gr.HTML("""
    <div style="text-align:center;padding:20px;color:#6b7280;font-size:13px;margin-top:16px;border-top:1px solid #d1fae5;">
        🌱 <strong>AgroGreen AI</strong> — Built for Pakistan's Farmers & Cities &nbsp;|&nbsp; 
        🤖 Powered by OpenAI + LangChain + FAISS &nbsp;|&nbsp;
        🏆 Hackathon MVP v1.0
    </div>""")


if __name__ == "__main__":
    from config.settings import GRADIO_PORT
    app.launch(
        server_name="0.0.0.0",
        server_port=GRADIO_PORT,
        share=False,
        show_error=True
    )
