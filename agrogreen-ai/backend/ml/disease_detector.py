# backend/ml/disease_detector.py
"""
Plant Disease Detection using CNN.
Uses intelligent mock classifier for MVP/demo mode.
Can be upgraded to real TensorFlow/PyTorch model.
"""

import random
import os
from PIL import Image
import numpy as np

# Disease database with treatment info
DISEASE_DATABASE = {
    "Tomato Early Blight": {
        "pathogen": "Alternaria solani (Fungus)",
        "confidence_range": (72, 94),
        "symptoms": "Dark brown spots with concentric rings on lower leaves. Yellow halo around spots.",
        "treatment": [
            "🌿 Remove and destroy infected leaves immediately",
            "💊 Spray Mancozeb 2.5g/L or Dithane M-45",
            "🔄 Repeat spray every 7-10 days",
            "💧 Avoid overhead irrigation — use drip irrigation",
        ],
        "prevention": [
            "✅ Use certified disease-free seeds",
            "✅ Crop rotation — don't plant tomato in same field for 3 years",
            "✅ Mulching to prevent soil splash",
            "✅ Plant resistant varieties like Hybrid Navana",
        ],
        "severity": "Moderate",
        "icon": "🍅"
    },
    "Wheat Yellow Rust": {
        "pathogen": "Puccinia striiformis (Fungus)",
        "confidence_range": (78, 96),
        "symptoms": "Yellow-orange stripes running parallel to leaf veins. Powdery rust pustules.",
        "treatment": [
            "💊 Spray Tilt 250 EC (Propiconazole) — 0.5ml/L water",
            "💊 Alternative: Bayleton (Triadimefon) 1g/L",
            "⏰ Apply at early stage for best results",
            "🔄 Repeat after 14 days if needed",
        ],
        "prevention": [
            "✅ Grow rust-resistant varieties (Punjab-2011, Sehar-2006)",
            "✅ Timely sowing — November-December",
            "✅ Monitor fields weekly during January-March",
            "✅ Balanced fertilization — don't over-apply Nitrogen",
        ],
        "severity": "High",
        "icon": "🌾"
    },
    "Cotton Leaf Curl Virus": {
        "pathogen": "Cotton Leaf Curl Virus (CLCV) — spread by Whitefly",
        "confidence_range": (70, 90),
        "symptoms": "Leaf curling upward, dark veins, small leaves, stunted growth.",
        "treatment": [
            "🚫 No cure once infected — remove severely affected plants",
            "🐛 Control whitefly vector: Imidacloprid 200SL (0.5ml/L)",
            "🌿 Apply Neem extract 5% as organic option",
            "⚡ Install yellow sticky traps (10 per acre)",
        ],
        "prevention": [
            "✅ Plant CLCV-resistant varieties: CIM-573, MNH-886",
            "✅ Control whitefly population before planting",
            "✅ Avoid late planting (plant before May 15)",
            "✅ Remove weeds that harbor whitefly",
        ],
        "severity": "Critical",
        "icon": "🌿"
    },
    "Rice Blast": {
        "pathogen": "Magnaporthe oryzae (Fungus)",
        "confidence_range": (74, 92),
        "symptoms": "Diamond-shaped gray lesions on leaves with brown borders. White-gray centers.",
        "treatment": [
            "💊 Spray Beam 75WP (Tricyclazole) — 0.6g/L",
            "💊 Alternative: Fujione (Isoprothiolane) — 1.5ml/L",
            "⏰ Apply at boot leaf stage",
            "🔄 Repeat after 10 days if disease spreads",
        ],
        "prevention": [
            "✅ Use blast-resistant varieties: Irri-9, Shaheen Basmati",
            "✅ Avoid excess Nitrogen fertilizer",
            "✅ Ensure proper field drainage",
            "✅ Crop rotation with non-rice crops",
        ],
        "severity": "High",
        "icon": "🌾"
    },
    "Powdery Mildew": {
        "pathogen": "Various Erysiphe species (Fungus)",
        "confidence_range": (82, 96),
        "symptoms": "White powdery coating on leaves and stems. Leaves may yellow and drop.",
        "treatment": [
            "💊 Spray Sulfur-based fungicide (3g/L water)",
            "💊 Alternative: Carbendazim 1g/L",
            "🌿 Organic: Baking soda spray (5g/L + few drops dish soap)",
            "✂️ Prune heavily infected branches",
        ],
        "prevention": [
            "✅ Ensure good air circulation between plants",
            "✅ Avoid overhead irrigation",
            "✅ Plant in sunny areas — shade promotes disease",
            "✅ Apply preventive sulfur spray in humid weather",
        ],
        "severity": "Moderate",
        "icon": "🍃"
    },
    "Healthy Plant": {
        "pathogen": "None detected",
        "confidence_range": (88, 98),
        "symptoms": "Plant appears healthy with no visible disease symptoms.",
        "treatment": [
            "✅ Continue current management practices",
            "💧 Maintain regular irrigation schedule",
            "🧪 Apply balanced fertilizer as per crop stage",
            "👀 Continue weekly field monitoring",
        ],
        "prevention": [
            "✅ Maintain crop hygiene",
            "✅ Regular scouting for early detection",
            "✅ Keep records of inputs and observations",
            "✅ Plan crop rotation for next season",
        ],
        "severity": "None",
        "icon": "💚"
    }
}


def analyze_image_features(img_array: np.ndarray) -> dict:
    """
    Analyze basic image features to guide disease classification.
    Simple color-based heuristics for demo mode.
    """
    # Normalize
    img_float = img_array.astype(float) / 255.0
    
    # Average color channels
    avg_red = np.mean(img_float[:, :, 0])
    avg_green = np.mean(img_float[:, :, 1])
    avg_blue = np.mean(img_float[:, :, 2])
    
    # Color ratios
    yellow_ness = (avg_red + avg_green) / 2 - avg_blue  # yellow = high R+G, low B
    brown_ness = avg_red - avg_green - avg_blue
    green_dominance = avg_green - (avg_red + avg_blue) / 2
    white_ness = min(avg_red, avg_green, avg_blue)
    
    return {
        "yellow_ness": yellow_ness,
        "brown_ness": brown_ness,
        "green_dominance": green_dominance,
        "white_ness": white_ness,
        "avg_brightness": (avg_red + avg_green + avg_blue) / 3,
    }


def mock_classify(features: dict) -> str:
    """Classify disease based on image features + probability."""
    diseases = list(DISEASE_DATABASE.keys())
    
    # Weight diseases based on color features
    weights = [1.0] * len(diseases)
    
    if features["yellow_ness"] > 0.15:
        weights[1] += 2.0  # Wheat rust (yellow)
    if features["brown_ness"] > 0.05:
        weights[0] += 2.0  # Early blight (brown spots)
    if features["green_dominance"] > 0.05:
        weights[5] += 3.0  # Healthy (green)
    if features["white_ness"] > 0.6:
        weights[4] += 2.0  # Powdery mildew (white)
    if features["avg_brightness"] < 0.3:
        weights[2] += 1.5  # Leaf curl (dark)
    
    # Normalize weights
    total = sum(weights)
    probs = [w / total for w in weights]
    
    return random.choices(diseases, weights=probs, k=1)[0]


def detect_disease(image_path: str) -> dict:
    """
    Main disease detection function.
    
    Args:
        image_path: Path to uploaded plant image
    
    Returns:
        dict with disease info, confidence, treatment, prevention
    """
    try:
        # Load and preprocess image
        img = Image.open(image_path).convert("RGB")
        img_resized = img.resize((224, 224))
        img_array = np.array(img_resized)
        
        # Feature extraction
        features = analyze_image_features(img_array)
        
        # Classification
        disease_name = mock_classify(features)
        disease_info = DISEASE_DATABASE[disease_name]
        
        # Generate confidence
        conf_min, conf_max = disease_info["confidence_range"]
        confidence = round(random.uniform(conf_min, conf_max), 1)
        
        # Build response
        result = {
            "disease": disease_name,
            "pathogen": disease_info["pathogen"],
            "confidence": confidence,
            "severity": disease_info["severity"],
            "icon": disease_info["icon"],
            "symptoms": disease_info["symptoms"],
            "treatment": disease_info["treatment"],
            "prevention": disease_info["prevention"],
            "image_features": {
                "dominant_color": "Green" if features["green_dominance"] > 0.05 else
                                  "Yellow" if features["yellow_ness"] > 0.1 else
                                  "Brown/Dark",
                "brightness": "Bright" if features["avg_brightness"] > 0.5 else "Dark",
            },
            "recommendation": (
                "⚠️ **Immediate action required!**" if disease_info["severity"] == "Critical" else
                "🔔 **Treat within 3-5 days**" if disease_info["severity"] == "High" else
                "ℹ️ **Monitor and treat if spreading**" if disease_info["severity"] == "Moderate" else
                "✅ **Plant is healthy — maintain good practices**"
            ),
            "status": "success"
        }
        
        return result
        
    except Exception as e:
        return {
            "disease": "Analysis Error",
            "confidence": 0,
            "severity": "Unknown",
            "symptoms": "Could not analyze image",
            "treatment": [f"Error: {str(e)}", "Please upload a clear plant image"],
            "prevention": ["Ensure image is well-lit and focused"],
            "status": "error",
            "error": str(e)
        }
