# backend/agents/agents.py
"""
Multi-Agent System for AgroGreen AI
Each agent handles a specific domain.
"""

import random
import math
from datetime import datetime


class WeatherAgent:
    """Fetches and interprets weather data for farming decisions."""
    
    name = "🌤️ Weather Fetcher"
    
    @staticmethod
    def get_sms_alerts(weather: dict) -> list:
        alerts = []
        if weather.get("heatwave_alert"):
            alerts.append({
                "type": "heatwave",
                "icon": "🔥",
                "title": "Heatwave Alert!",
                "message": f"Temperature {weather['temperature']}°C. Irrigate crops early morning. Protect livestock.",
                "priority": "HIGH"
            })
        if weather.get("rain_probability", 0) > 70:
            alerts.append({
                "type": "rain",
                "icon": "🌧️",
                "title": "Rain Alert",
                "message": f"{weather['rain_probability']}% chance of rain. Delay irrigation. Harvest ripe crops.",
                "priority": "MEDIUM"
            })
        if not alerts:
            alerts.append({
                "type": "normal",
                "icon": "✅",
                "title": "Normal Conditions",
                "message": "Weather is favorable for farming operations today.",
                "priority": "LOW"
            })
        return alerts


class MarketAgent:
    """Analyzes crop market prices and provides trading recommendations."""
    
    name = "📈 Market Advisor"
    
    @staticmethod
    def get_profit_prediction(crop: str, quantity_kg: float, city: str, price_per_kg: float) -> dict:
        """Calculate profit prediction for a crop sale."""
        # Costs (estimated per kg)
        cost_estimates = {
            "wheat": 45, "rice": 80, "cotton": 320,
            "tomato": 55, "sugarcane": 15
        }
        cost_per_kg = cost_estimates.get(crop, 50)
        
        gross_revenue = quantity_kg * price_per_kg
        total_cost = quantity_kg * cost_per_kg
        net_profit = gross_revenue - total_cost
        roi = ((net_profit / total_cost) * 100) if total_cost > 0 else 0
        
        # Best market recommendation
        city_premiums = {
            "Islamabad": 1.08, "Karachi": 1.05, "Lahore": 1.03, "Hyderabad": 1.0
        }
        best_city = max(city_premiums, key=city_premiums.get)
        best_price = price_per_kg * city_premiums[best_city]
        best_profit = quantity_kg * best_price - total_cost
        
        return {
            "crop": crop,
            "quantity_kg": quantity_kg,
            "current_price": price_per_kg,
            "gross_revenue": round(gross_revenue, 2),
            "estimated_cost": round(total_cost, 2),
            "net_profit": round(net_profit, 2),
            "roi_percent": round(roi, 1),
            "best_market": best_city,
            "best_price": round(best_price, 2),
            "best_profit": round(best_profit, 2),
            "advice": (
                f"💰 Sell in {best_city} for PKR {best_price:.0f}/kg — "
                f"saves you PKR {(best_profit - net_profit):.0f} extra!"
                if best_city != city else
                f"✅ You're already in the best market! Good timing."
            )
        }
    
    @staticmethod
    def get_timing_advice(crop: str) -> str:
        month = datetime.now().month
        advice = {
            "wheat": {
                3: "⏳ Just harvested — store 2-3 months for better prices (May-June peak)",
                4: "📦 Store wheat now. Prices will rise 15-20% by June.",
                5: "📈 Good selling window opening. Monitor prices daily.",
                6: "🎯 PEAK SEASON — sell now for maximum profit!",
            },
            "rice": {
                10: "🌾 Fresh harvest — dry properly before selling. Wait 2-3 weeks.",
                11: "📦 Store basmati for export prices. Regular rice — sell now.",
                12: "💰 Good time to sell. Export demand is high.",
            },
            "tomato": {
                "default": "🍅 Tomato is perishable — sell within 2-3 days of harvest. Consider processing."
            },
            "cotton": {
                10: "🌿 Fresh picked — clean and grade properly.",
                11: "📈 Good prices now. Sell after ginning for better rates.",
                12: "🎯 Peak cotton trading season. Negotiate with ginners.",
            }
        }
        
        crop_advice = advice.get(crop, {})
        return crop_advice.get(month, crop_advice.get("default", 
               f"📊 Monitor {crop} prices in your nearest mandi daily for best decisions."))


class ImpactAgent:
    """Calculates environmental impact of green initiatives."""
    
    name = "🌍 Impact Predictor"
    
    @staticmethod
    def calculate_impact(area_hectares: float, action_type: str, 
                         num_trees: int = 0, crop_type: str = "vegetables") -> dict:
        """Calculate environmental impact metrics."""
        
        # CO2 sequestration rates (tonnes/year)
        co2_rates = {
            "tree_plantation": num_trees * 0.022,  # ~22kg per tree per year
            "rooftop_farming": area_hectares * 2.5,
            "urban_park": area_hectares * 8.0,
            "agroforestry": area_hectares * 15.0,
            "drip_irrigation": area_hectares * 1.5,
        }
        
        co2_saved = co2_rates.get(action_type, area_hectares * 5.0)
        
        # Temperature reduction (urban heat island effect)
        temp_reduction = min(area_hectares * 0.3, 3.5)
        
        # Water saved (drip vs flood irrigation)
        water_saved_liters = area_hectares * 3000000 * 0.4  # 40% water saving
        
        # Air quality improvement (AQI points)
        aqi_improvement = min(area_hectares * 5 + num_trees * 0.1, 35)
        
        # Biodiversity score
        biodiversity = min(30 + area_hectares * 10 + num_trees * 0.05, 95)
        
        # Economic value
        carbon_credits = co2_saved * 15  # $15 per tonne CO2
        food_value_usd = area_hectares * 2000 * 0.3  # $2000/ha food value, 30% urban uplift
        
        # Sustainability score (0-100)
        sustainability = min(
            40 + (co2_saved * 2) + (temp_reduction * 5) + (aqi_improvement * 0.5),
            98
        )
        
        return {
            "co2_saved_tonnes": round(co2_saved, 2),
            "co2_equivalent": f"= driving {int(co2_saved * 4000)} km less per year",
            "temperature_reduction": round(temp_reduction, 2),
            "water_saved_liters": int(water_saved_liters),
            "water_saved_readable": f"{water_saved_liters/1000000:.1f} million liters/year",
            "aqi_improvement": round(aqi_improvement, 1),
            "biodiversity_score": round(biodiversity, 1),
            "sustainability_score": round(sustainability, 1),
            "carbon_credits_usd": round(carbon_credits, 2),
            "food_value_usd": round(food_value_usd, 2),
            "trees_equivalent": int(co2_saved / 0.022),
            "before_after": {
                "co2_before": round(co2_saved * 1.0, 2),
                "co2_after": round(co2_saved * 0.15, 2),
                "temp_before": 38.0,
                "temp_after": round(38.0 - temp_reduction, 1),
                "aqi_before": 185,
                "aqi_after": round(185 - aqi_improvement, 1),
                "biodiversity_before": 25.0,
                "biodiversity_after": round(biodiversity, 1),
            },
            "funding_opportunities": [
                {"name": "GCF Pakistan Climate Fund", "amount": "$500K - $2M", "match": "95%"},
                {"name": "USAID Green Cities Grant", "amount": "$100K - $500K", "match": "88%"},
                {"name": "World Bank Urban Resilience", "amount": "$1M - $5M", "match": "82%"},
                {"name": "KfW Germany Green Finance", "amount": "€250K - €1M", "match": "75%"},
            ]
        }


class FundingAgent:
    """Finds funding opportunities for green agriculture projects."""
    
    name = "💰 Funding Finder"
    
    FUNDING_DB = [
        {
            "name": "Green Climate Fund (GCF)",
            "type": "Grant",
            "amount": "$500K — $50M",
            "focus": "Climate adaptation, sustainable agriculture",
            "eligibility": "Government bodies, NGOs, Private sector",
            "deadline": "Rolling applications",
            "url": "https://www.greenclimate.fund",
            "match_keywords": ["climate", "agriculture", "green", "sustainable"],
            "icon": "🌍"
        },
        {
            "name": "USAID Agricultural Development",
            "type": "Grant + Technical Support",
            "amount": "$50K — $2M",
            "focus": "Smallholder farmers, food security, Pakistan",
            "eligibility": "NGOs, Cooperatives, Farmer groups",
            "deadline": "Quarterly calls",
            "url": "https://www.usaid.gov/pakistan",
            "match_keywords": ["farmer", "food", "smallholder", "Pakistan"],
            "icon": "🇺🇸"
        },
        {
            "name": "World Bank Climate-Smart Agriculture",
            "type": "Loan + Grant",
            "amount": "$1M — $100M",
            "focus": "Large-scale agricultural transformation",
            "eligibility": "Government, Large cooperatives",
            "deadline": "Annual cycle",
            "url": "https://www.worldbank.org",
            "match_keywords": ["large scale", "government", "transformation"],
            "icon": "🏦"
        },
        {
            "name": "PARC Research Grants",
            "type": "Research Grant",
            "amount": "PKR 500K — 5M",
            "focus": "Agricultural research and innovation in Pakistan",
            "eligibility": "Researchers, Universities, Agri startups",
            "deadline": "March & September",
            "url": "https://www.parc.gov.pk",
            "match_keywords": ["research", "innovation", "university", "startup"],
            "icon": "🔬"
        },
        {
            "name": "Punjab Urban Greening Initiative",
            "type": "Government Grant",
            "amount": "PKR 1M — 20M",
            "focus": "Urban tree plantation, park development",
            "eligibility": "Local governments, Community organizations",
            "deadline": "June annually",
            "url": "https://www.punjab.gov.pk",
            "match_keywords": ["urban", "trees", "plantation", "city"],
            "icon": "🌳"
        },
        {
            "name": "Agri Fintech Pakistan (ZTBL)",
            "type": "Subsidized Loan",
            "amount": "PKR 50K — 5M",
            "focus": "Farm equipment, irrigation, seed financing",
            "eligibility": "Individual farmers with land title",
            "deadline": "Open year-round",
            "url": "https://www.ztbl.com.pk",
            "match_keywords": ["loan", "equipment", "irrigation", "farmer"],
            "icon": "🏧"
        },
    ]
    
    @staticmethod
    def find_funding(project_type: str = "general", budget: str = "medium") -> list:
        """Return relevant funding opportunities."""
        return FundingAgent.FUNDING_DB
