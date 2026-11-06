# 🥗 AI Nutrition Assistant — Powered by IBM Granite

> The Smartest AI Nutrition Assistant — personalised, adaptive, and powered by **IBM Granite** on **watsonx.ai (Lite)**.

---

## 🌟 Features

| Feature | Description |
|---------|-------------|
| 💬 **Chat with NutriGenius** | Conversational AI nutrition expert with memory across turns |
| 📅 **7-Day Meal Plan Generator** | Personalised meal plans with calories, macros & explanations |
| 🔍 **Food Analyzer** | Deep nutritional breakdown from text description, photo, or label |
| 🔄 **Smart Food Swaps** | Goal-aligned healthier alternatives with taste-match scores |
| 🧠 **Nutrition Encyclopedia** | Plain-English explanations of any nutrition concept |
| 📈 **Progress Coach** | Adaptive feedback loop — share your experience, get a refined plan |

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.11+
- IBM Cloud account (Free Lite tier): [cloud.ibm.com/registration](https://cloud.ibm.com/registration)
- watsonx.ai project (Free): [dataplatform.cloud.ibm.com](https://dataplatform.cloud.ibm.com)

### 2. Clone & Install

```bash
git clone <repo-url>
cd "Nutrition Agent_3"
pip install -r requirements.txt
```

### 3. Configure IBM Credentials

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:
```
IBM_API_KEY=your_actual_ibm_cloud_api_key
WATSONX_PROJECT_ID=your_actual_project_id
WATSONX_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-3-3-8b-instruct
```

#### Getting your credentials:
1. **IBM_API_KEY**: [IBM Cloud Console → IAM → API Keys](https://cloud.ibm.com/iam/apikeys) → Create
2. **WATSONX_PROJECT_ID**: Open your watsonx.ai project → Manage → General → Project ID
3. **WATSONX_URL**: Use `https://us-south.ml.cloud.ibm.com` for US South (adjust for your region)

### 4. Run the App

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🏗️ Project Structure

```
Nutrition Agent_3/
├── app.py                      # Main Streamlit application (all UI tabs)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── utils/
│   ├── __init__.py
│   ├── granite_client.py       # IBM watsonx.ai / Granite REST client
│   ├── nutrition_agent.py      # Core AI agent orchestrator
│   ├── food_analyzer.py        # Food description & label analysis
│   └── swap_recommender.py     # Smart food swap engine
└── README.md
```

---

## 🔧 IBM Granite Integration

The app uses IBM Granite `3.3 8B Instruct` via the watsonx.ai REST API:

```
POST /ml/v1/text/generation?version=2023-05-29
Authorization: Bearer <IAM Token>
```

Authentication uses IBM Cloud IAM token exchange (API key → Bearer token).
The `GraniteClient` in `utils/granite_client.py` handles:
- IAM token acquisition and refresh
- Prompt construction with system persona
- Conversation history management
- Graceful demo-mode fallback when credentials are not configured

**Granite model parameters used:**
| Parameter | Value |
|-----------|-------|
| Decoding | Sampling |
| Max tokens | 1024–2000 (task-dependent) |
| Temperature | 0.7 |
| Top-k | 50 |
| Top-p | 0.9 |
| Repetition penalty | 1.1 |

---

## 🎨 Architecture

```
User Input (text / image / label)
         │
         ▼
    Streamlit UI (app.py)
         │
         ▼
  NutritionAgent / FoodAnalyzer / SwapRecommender
         │
         ▼
    GraniteClient (utils/granite_client.py)
         │
    IBM IAM Token Exchange
         │
         ▼
  watsonx.ai REST API
  (IBM Granite 3.3 8B Instruct)
         │
         ▼
    Structured AI Response → Streamlit UI
```

---

## 📋 User Profile Fields

The sidebar collects:
- **Demographics**: Name, age, gender, weight, height
- **Health goal**: Weight loss, muscle gain, diabetes management, etc.
- **Activity level**: Sedentary → Extremely active
- **Dietary preference**: Vegetarian, vegan, keto, halal, etc.
- **Cultural cuisine preferences**
- **Allergies & intolerances**
- **Medical conditions**

The profile is used to contextualise every AI response, auto-calculate BMI and TDEE.

---

## ⚠️ Medical Disclaimer

This AI assistant provides **general nutrition information only**. It is not a substitute for professional medical or dietetic advice. Always consult a registered dietitian or physician for clinical nutrition decisions.

---

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web UI framework |
| `ibm-watsonx-ai` | Official IBM SDK (optional; REST API used directly) |
| `python-dotenv` | Environment variable loading |
| `requests` | IBM IAM + watsonx.ai REST calls |
| `Pillow` | Image processing for food photo uploads |
| `pandas` | Data handling |
| `plotly` | Charts and visualisations |

---

## 🔐 Security Notes

- Never commit your `.env` file — it's already in `.gitignore`
- Use `.env.example` as the template
- IBM API keys can be rotated at [cloud.ibm.com/iam/apikeys](https://cloud.ibm.com/iam/apikeys)
