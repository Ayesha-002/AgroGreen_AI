# 🌱 AgroGreen AI

> **AI-Powered Smart Farming & Urban Green Planning Platform for Pakistan**

[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg)](https://fastapi.tiangolo.com)
[![Gradio](https://img.shields.io/badge/Gradio-4.37-orange.svg)](https://gradio.app)
[![LangChain](https://img.shields.io/badge/LangChain-0.2-blue.svg)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 What is AgroGreen AI?

AgroGreen AI is a multi-agent AI platform that helps:

- 🌾 **Farmers** improve crop production with AI-powered advisors
- 🏙️ **Cities** optimize green spaces using GIS and AI
- 🌍 **Communities** fight climate change with impact prediction

Built as a hackathon MVP — **demo-ready in under 5 hours!**

---

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Setup

```bash
git clone https://github.com/your-org/agrogreen-ai
cd agrogreen-ai
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # Linux/Mac
# OR
venv\Scripts\activate        # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your API keys (optional — works in DEMO_MODE without them!)
```

### 5. Run the Platform

```bash
# Run Gradio frontend (recommended for demo)
python run.py

# Or run both backend + frontend
python run.py --mode both

# Or run FastAPI only
python run.py --mode backend
```

### 6. Open in Browser

- **Gradio UI:** http://localhost:7860
- **FastAPI Docs:** http://localhost:8000/docs

> ✅ **Works in DEMO MODE without any API keys!** All features have intelligent fallbacks.

---

## 📁 Project Structure

```
agrogreen-ai/
├── 🔧 config/
│   └── settings.py              # Environment config
├── 🧠 backend/
│   ├── main.py                  # FastAPI application
│   ├── agents/
│   │   └── agents.py            # Multi-agent system
│   ├── rag/
│   │   └── crop_advisor.py      # LangChain RAG pipeline
│   ├── ml/
│   │   └── disease_detector.py  # CNN disease detection
│   └── utils/
│       └── helpers.py           # Weather, IoT, maps utils
├── 🎨 frontend/
│   └── app.py                   # Gradio UI (9 tabs!)
├── 📊 data/
│   ├── datasets/
│   │   └── market_prices.csv    # Pakistan crop price data
│   └── knowledge_base/
│       └── agriculture_kb.txt   # RAG knowledge base
├── run.py                       # Main launcher
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🤖 Multi-Agent Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER (Farmer / City Planner)         │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                   GRADIO FRONTEND                        │
│           (9 Tabs: Dashboard → Funding Finder)          │
└──────────────────────────┬──────────────────────────────┘
                           │ HTTP / Direct Call
┌──────────────────────────▼──────────────────────────────┐
│                   FASTAPI BACKEND                        │
│              (REST API + Agent Router)                  │
└──┬────────┬────────┬──────────┬──────────┬─────────────┘
   │        │        │          │          │
   ▼        ▼        ▼          ▼          ▼
🌤️ Weather  🤖 RAG   🔬 CNN    📈 Market  🌍 Impact
 Agent    Chatbot  Detector   Agent     Predictor
   │        │                   │
   ▼        ▼                   ▼
OpenWeather OpenAI           CSV Dataset
  API      + FAISS
```

---

## 🌟 Features

| # | Feature | Technology | Status |
|---|---------|-----------|--------|
| 1 | 🌤️ Smart Weather Advisor | OpenWeather API + AI | ✅ Demo Ready |
| 2 | 🤖 AI Crop Chatbot (RAG) | LangChain + FAISS + GPT | ✅ Demo Ready |
| 3 | 🔬 Plant Disease Detection | CNN + Image Analysis | ✅ Demo Ready |
| 4 | 📈 Market Price Advisor | CSV + Pandas + Charts | ✅ Demo Ready |
| 5 | 🗺️ GreenLens Maps | Leaflet.js + GeoJSON | ✅ Demo Ready |
| 6 | 🌍 Environmental Impact | Math Models + AI | ✅ Demo Ready |
| 7 | 📡 IoT Monitor Dashboard | Mock Sensors | ✅ Demo Ready |
| 8 | 💰 Funding Finder | Curated Database | ✅ Demo Ready |

---

## 🔑 API Keys (Optional)

The platform runs in **DEMO MODE** without any API keys.

To enable real AI:

1. **OpenAI API Key** → [platform.openai.com](https://platform.openai.com)
   - Enables: Real RAG chatbot, GPT responses
   
2. **OpenWeather API Key** → [openweathermap.org](https://openweathermap.org/api)
   - Enables: Live weather data

Add both to your `.env` file and set `DEMO_MODE=false`.

---

## 🛠️ API Documentation

FastAPI auto-generates docs at: **http://localhost:8000/docs**

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/weather?city=Karachi` | Weather + farming advisory |
| POST | `/chat` | AI crop advisor chatbot |
| POST | `/detect-disease` | Plant disease detection |
| GET | `/market-prices` | Crop prices in Pakistan |
| GET | `/green-zones` | Urban green space data |
| POST | `/impact-analysis` | Environmental impact calc |
| GET | `/iot-data` | IoT sensor readings |
| GET | `/funding` | Funding opportunities |

---

## 🌱 Knowledge Base (RAG)

The chatbot is trained on `data/knowledge_base/agriculture_kb.txt` covering:

- Wheat, Rice, Cotton, Sugarcane, Tomato cultivation
- Pakistani-specific recommendations (varieties, timing, markets)
- Disease diagnosis and treatment
- Pest management (IPM)
- Irrigation techniques
- Climate change adaptation
- Urban farming

**To add more knowledge:** Edit the `.txt` file and restart the app.

---

## 🗺️ Supported Cities

Weather, market prices, and maps available for:
- 📍 Karachi
- 📍 Lahore
- 📍 Islamabad
- 📍 Hyderabad
- 📍 Multan
- 📍 Faisalabad

---

## 🔮 Future Improvements

1. **Real-time market prices** via Pakistan Agriculture Dept. API
2. **Satellite imagery** integration via Google Earth Engine
3. **Urdu voice assistant** using OpenAI Whisper
4. **SMS alerts** via Twilio for remote farmers
5. **TensorFlow plant disease model** with 20k+ training images
6. **Drone-based field analysis** integration
7. **Weather forecast ML model** trained on Pakistan meteorological data
8. **Blockchain crop provenance** tracking
9. **Mobile app** via Gradio's mobile-responsive interface

---

## 🏆 Hackathon Notes

This MVP was built in **< 5 hours** with:
- Modular architecture for fast extension
- Demo mode for offline/no-API usage
- Intelligent fallbacks for every feature
- Production-like code quality

---

## 🤝 Contributing

1. Fork the repo
2. Add knowledge base data to `data/knowledge_base/`
3. Add new agents in `backend/agents/agents.py`
4. Add new UI tabs in `frontend/app.py`

---

## 📄 License

MIT License — Free to use for agricultural development.

---

**Built with ❤️ for Pakistan's 8 million farmers and growing cities.**
