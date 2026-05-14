# backend/utils/helpers.py
import random
import json
from datetime import datetime, timedelta

def get_demo_weather(city: str = "Karachi") -> dict:
    """Generate realistic demo weather data for Pakistani cities."""
    city_data = {
        "Karachi": {"base_temp": 32, "humidity": 70, "lat": 24.8607, "lon": 67.0011},
        "Lahore": {"base_temp": 28, "humidity": 55, "lat": 31.5204, "lon": 74.3587},
        "Islamabad": {"base_temp": 25, "humidity": 60, "lat": 33.6844, "lon": 73.0479},
        "Hyderabad": {"base_temp": 34, "humidity": 65, "lat": 25.3960, "lon": 68.3578},
        "Multan": {"base_temp": 35, "humidity": 45, "lat": 30.1575, "lon": 71.5249},
        "Faisalabad": {"base_temp": 30, "humidity": 50, "lat": 31.4504, "lon": 73.1350},
    }
    
    data = city_data.get(city, city_data["Karachi"])
    temp = data["base_temp"] + random.uniform(-3, 5)
    humidity = data["humidity"] + random.uniform(-10, 10)
    rain_prob = random.randint(5, 80)
    wind = random.uniform(8, 25)
    
    # Generate 7-day forecast
    forecast = []
    conditions = ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Hot & Dry", "Windy"]
    for i in range(7):
        day = datetime.now() + timedelta(days=i)
        forecast.append({
            "date": day.strftime("%a %d %b"),
            "temp_max": round(temp + random.uniform(-2, 4), 1),
            "temp_min": round(temp - random.uniform(5, 10), 1),
            "condition": random.choice(conditions),
            "rain_prob": random.randint(5, 70),
            "humidity": round(humidity + random.uniform(-5, 5), 1),
        })
    
    # Irrigation recommendation
    if rain_prob > 60:
        irrigation_rec = "🌧️ Skip irrigation — rain expected in the next 24-48 hours."
    elif temp > 38:
        irrigation_rec = "🔥 High heat alert! Irrigate in early morning or evening. Double frequency."
    elif humidity < 40:
        irrigation_rec = "💧 Low humidity detected. Increase irrigation frequency by 20%."
    else:
        irrigation_rec = "✅ Normal irrigation schedule recommended. Monitor soil moisture."
    
    # Planting suggestion
    month = datetime.now().month
    if 10 <= month <= 12:
        planting = "🌾 Ideal time for Rabi crops: Wheat, Mustard, Gram. Start sowing now!"
    elif 4 <= month <= 6:
        planting = "🌿 Kharif season! Plant Rice, Cotton, Maize, Sugarcane."
    elif 2 <= month <= 3:
        planting = "🍅 Good for spring vegetables: Tomato, Cucumber, Pepper seedlings."
    else:
        planting = "🌱 Maintain current crops. Consider soil preparation for next season."
    
    heatwave = temp > 40
    
    return {
        "city": city,
        "temperature": round(temp, 1),
        "feels_like": round(temp + random.uniform(1, 4), 1),
        "humidity": round(humidity, 1),
        "wind_speed": round(wind, 1),
        "rain_probability": rain_prob,
        "condition": random.choice(conditions),
        "uv_index": random.randint(6, 11),
        "pressure": random.randint(1005, 1020),
        "visibility": random.randint(5, 15),
        "heatwave_alert": heatwave,
        "irrigation_recommendation": irrigation_rec,
        "planting_suggestion": planting,
        "forecast": forecast,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "lat": data["lat"],
        "lon": data["lon"],
    }


def get_demo_green_zones() -> dict:
    """Return demo GeoJSON data for green space optimization."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [67.0650, 24.9056]},
                "properties": {
                    "name": "Clifton Rooftop Farm Zone",
                    "type": "rooftop_farming",
                    "score": 92,
                    "area_sqm": 5000,
                    "suggestion": "High-rise buildings ideal for rooftop vegetable gardens",
                    "co2_saved": "12 tonnes/year",
                    "icon": "🏢"
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [67.0300, 24.8800]},
                "properties": {
                    "name": "Lyari River Tree Corridor",
                    "type": "tree_plantation",
                    "score": 88,
                    "area_sqm": 25000,
                    "suggestion": "Plant native trees: Neem, Peepal, Shisham along riverbank",
                    "co2_saved": "45 tonnes/year",
                    "icon": "🌳"
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [67.1100, 24.9200]},
                "properties": {
                    "name": "Gulshan Urban Park",
                    "type": "urban_park",
                    "score": 85,
                    "area_sqm": 15000,
                    "suggestion": "Convert vacant land to community park with food forest",
                    "co2_saved": "28 tonnes/year",
                    "icon": "🌿"
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [67.0800, 24.8500]},
                "properties": {
                    "name": "SITE Area Smart Irrigation",
                    "type": "smart_irrigation",
                    "score": 78,
                    "area_sqm": 8000,
                    "suggestion": "Install drip irrigation system for industrial green belts",
                    "co2_saved": "8 tonnes/year",
                    "icon": "💧"
                }
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [67.0200, 24.9400]},
                "properties": {
                    "name": "North Karachi Agroforestry",
                    "type": "agroforestry",
                    "score": 95,
                    "area_sqm": 50000,
                    "suggestion": "Large-scale tree plantation with intercropping potential",
                    "co2_saved": "95 tonnes/year",
                    "icon": "🌲"
                }
            },
        ]
    }


def get_demo_iot_data() -> dict:
    """Mock IoT sensor dashboard data."""
    return {
        "sensors": [
            {
                "id": "S001",
                "location": "Field A - Wheat",
                "soil_moisture": round(random.uniform(35, 65), 1),
                "soil_temp": round(random.uniform(22, 30), 1),
                "air_temp": round(random.uniform(28, 38), 1),
                "humidity": round(random.uniform(40, 70), 1),
                "irrigation_status": random.choice(["Active", "Idle", "Scheduled"]),
                "battery": random.randint(60, 100),
                "last_reading": "2 mins ago"
            },
            {
                "id": "S002",
                "location": "Field B - Cotton",
                "soil_moisture": round(random.uniform(30, 60), 1),
                "soil_temp": round(random.uniform(24, 32), 1),
                "air_temp": round(random.uniform(30, 40), 1),
                "humidity": round(random.uniform(35, 65), 1),
                "irrigation_status": random.choice(["Active", "Idle", "Scheduled"]),
                "battery": random.randint(45, 90),
                "last_reading": "5 mins ago"
            },
            {
                "id": "S003",
                "location": "Greenhouse - Tomatoes",
                "soil_moisture": round(random.uniform(50, 75), 1),
                "soil_temp": round(random.uniform(20, 26), 1),
                "air_temp": round(random.uniform(24, 32), 1),
                "humidity": round(random.uniform(60, 85), 1),
                "irrigation_status": "Active",
                "battery": random.randint(70, 100),
                "last_reading": "1 min ago"
            },
        ],
        "alerts": [
            {"type": "warning", "message": "Field A soil moisture dropping below threshold", "time": "10 mins ago"},
            {"type": "info", "message": "Irrigation scheduled for Field B at 6:00 AM", "time": "1 hour ago"},
            {"type": "success", "message": "Greenhouse irrigation completed successfully", "time": "2 hours ago"},
        ]
    }
