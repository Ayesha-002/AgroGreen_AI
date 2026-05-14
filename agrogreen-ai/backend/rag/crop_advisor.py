# backend/rag/crop_advisor.py
"""
RAG-powered Crop Advisor using LangChain + FAISS + OpenAI
Falls back to intelligent demo mode when API key not set.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import OPENAI_API_KEY, KNOWLEDGE_BASE_DIR, DEMO_MODE

# ─── Demo responses for offline/no-API mode ─────────────────────────────────
DEMO_RESPONSES = {
    "yellow": """🌿 **Yellow Leaves Diagnosis**

Your plant likely has **Nitrogen Deficiency** or **Overwatering** issues.

**Symptoms match:** Yellowing starting from lower/older leaves

**Recommended Treatment:**
1. 🧪 Apply **Urea foliar spray** (2g per liter water) — spray on leaves in morning
2. 💧 Check soil drainage — ensure water doesn't pool around roots
3. 🌱 Add **compost or farmyard manure** to improve soil health
4. ⏰ Irrigate every **3-4 days** (not daily)

**If Fusarium Wilt suspected:**
- Drench soil with **Carbendazim 0.1%** solution
- Remove severely affected plants

**Prevention:** Rotate crops, use disease-resistant varieties next season.

*Source: Pakistan Agriculture Research Council Guidelines*""",

    "wheat": """🌾 **Wheat Farming Guide for Sindh/Punjab**

**Best Time to Sow:** November to December

**Recommended Varieties:**
- Punjab-2011 (high yield, rust resistant)
- Faisalabad-2008 (drought tolerant)
- Galaxy-2013 (good for Sindh conditions)

**Fertilizer Schedule:**
| Stage | Fertilizer | Dose |
|-------|-----------|------|
| Sowing | DAP | 90 kg/acre |
| 21 days | Urea | 1st dose — 50 kg/acre |
| 45 days | Urea | 2nd dose — 50 kg/acre |

**Irrigation:** 4-5 irrigations total
1. Before sowing (rauni)
2. Tillering stage (21 days)
3. Jointing stage (45 days)
4. Heading stage (70 days)
5. Grain filling (90 days)

**Expected Yield:** 45-55 maunds per acre with good management

**Watch for:** Yellow rust — spray Tilt 250 EC if spotted""",

    "tomato": """🍅 **Tomato Cultivation Guide**

**Soil:** Well-drained loamy, pH 6.0–7.0

**Varieties for Pakistan:**
- Roma (processing), Nagina (fresh market), Hybrid F1 varieties

**Fertilizer Plan:**
- Basal: DAP 1 bag + Potash 0.5 bag per acre
- Weekly foliar: NPK 20-20-20 (5g/L water)
- Calcium spray at fruit set stage

**Common Problem — Yellow Leaves:**
- Nitrogen deficiency → Spray Urea 2%
- Fungal — Spray Mancozeb 2.5g/L

**Irrigation:** Drip irrigation best — every 2 days in summer

**Profit Tip:** Sell directly to hotels/restaurants in Karachi for 20-30% better price!""",

    "pest": """🐛 **Pest Management Guide (IPM)**

**Most Common Pests in Pakistan:**

**1. Whitefly** (Tomato, Cotton, Chilies)
- Damage: Curled leaves, sticky honeydew, virus spread
- Control: Imidacloprid 200SL (0.5ml/L) OR Confidor

**2. Bollworm** (Cotton)
- Damage: Bore into bolls, 40-60% yield loss
- Control: Pheromone traps + Cypermethrin spray

**3. Brown Plant Hopper** (Rice)
- Control: Chlorpyrifos or Malathion spray

**4. Aphids** (Multiple crops)
- Control: Dimethoate 40EC (1.5ml/L)

**IPM Strategy (Recommended):**
1. Scout fields twice weekly
2. Use sticky yellow traps
3. Release Trichogramma cards for bollworm
4. Spray only when economic threshold crossed
5. Rotate pesticide groups to prevent resistance

**Organic Option:** Neem extract 5% spray is effective for early infestations.""",

    "default": """🌱 **AgroGreen AI Crop Advisor**

I'm your AI-powered farming assistant trained on Pakistani agriculture knowledge!

**I can help you with:**
- 🌾 Crop cultivation guides (Wheat, Rice, Cotton, Sugarcane, Vegetables)
- 🦠 Plant disease diagnosis and treatment
- 🐛 Pest identification and management
- 💧 Irrigation scheduling
- 🧪 Fertilizer recommendations
- 💰 Market timing and profit tips
- 🌿 Organic and sustainable farming

**Try asking me:**
- "My tomato leaves are turning yellow"
- "How to grow wheat in Sindh?"
- "What fertilizer for cotton?"
- "How to control whitefly?"
- "Best time to sell rice?"

*Powered by Pakistan Agriculture Research Council knowledge base*"""
}


class CropAdvisor:
    """
    RAG-based Crop Advisor.
    Uses OpenAI + FAISS when API key available, falls back to demo responses.
    """
    
    def __init__(self):
        self.chain = None
        self.initialized = False
        self._try_init_rag()
    
    def _try_init_rag(self):
        """Try to initialize the RAG pipeline."""
        if not OPENAI_API_KEY or DEMO_MODE:
            print("[CropAdvisor] Running in DEMO mode (no API key or DEMO_MODE=true)")
            return
        
        try:
            from langchain_openai import OpenAIEmbeddings, ChatOpenAI
            from langchain_community.vectorstores import FAISS
            from langchain_community.document_loaders import TextLoader
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            from langchain.chains import RetrievalQA
            from langchain.prompts import PromptTemplate
            
            kb_path = os.path.join(KNOWLEDGE_BASE_DIR, "agriculture_kb.txt")
            loader = TextLoader(kb_path, encoding="utf-8")
            docs = loader.load()
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_documents(docs)
            
            embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            vectorstore = FAISS.from_documents(chunks, embeddings)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
            
            llm = ChatOpenAI(
                openai_api_key=OPENAI_API_KEY,
                model_name="gpt-3.5-turbo",
                temperature=0.5,
                max_tokens=600
            )
            
            prompt = PromptTemplate(
                input_variables=["context", "question"],
                template="""You are AgroGreen AI, an expert Pakistani agriculture advisor.
Answer based on the context provided. Include specific recommendations for Pakistan.
Use emojis and formatting. Answer in the same language as the question (English or Urdu).

Context: {context}

Farmer's Question: {question}

Expert Answer:"""
            )
            
            self.chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=retriever,
                chain_type_kwargs={"prompt": prompt}
            )
            self.initialized = True
            print("[CropAdvisor] RAG pipeline initialized successfully!")
            
        except Exception as e:
            print(f"[CropAdvisor] RAG init failed: {e}. Using demo mode.")
    
    def get_demo_response(self, query: str) -> str:
        """Return intelligent demo response based on keywords."""
        q = query.lower()
        if any(w in q for w in ["yellow", "پیلا", "پیلے"]):
            return DEMO_RESPONSES["yellow"]
        elif any(w in q for w in ["wheat", "گندم"]):
            return DEMO_RESPONSES["wheat"]
        elif any(w in q for w in ["tomato", "ٹماٹر"]):
            return DEMO_RESPONSES["tomato"]
        elif any(w in q for w in ["pest", "insect", "whitefly", "bollworm", "کیڑا"]):
            return DEMO_RESPONSES["pest"]
        else:
            return DEMO_RESPONSES["default"]
    
    def chat(self, message: str, history: list = None) -> str:
        """Process a farming question and return expert answer."""
        if not message.strip():
            return "Please ask me a farming question!"
        
        if self.initialized and self.chain:
            try:
                result = self.chain.invoke({"query": message})
                return result.get("result", self.get_demo_response(message))
            except Exception as e:
                print(f"[CropAdvisor] Chain error: {e}")
                return self.get_demo_response(message)
        else:
            return self.get_demo_response(message)


# Singleton instance
_advisor = None

def get_advisor():
    global _advisor
    if _advisor is None:
        _advisor = CropAdvisor()
    return _advisor
