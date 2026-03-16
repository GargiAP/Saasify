# Saasify — AI-Powered Startup Idea Evaluation

**Live Demo:** https://saasify-umber.vercel.app/

Saasify is an ML-powered decision support system that helps founders evaluate startup ideas. Enter any idea and get a structured, data-driven analysis in under 30 seconds.

---

## What it does

| Feature | Description |
|---|---|
| Semantic similarity search | Finds the most similar real products from a corpus of 352 SaaS products |
| Market gap analysis | Detects what competitors are missing and where opportunities exist |
| Viability scoring | XGBoost regression model predicts a 0-100 viability score |
| SHAP explainability | Shows exactly which features are helping or hurting the score |
| LLM report | Llama 3 generates an investor-style analysis report |

---

## System Architecture
```
User Idea Input
      ↓
Groq Llama 3 (idea preprocessing → structured JSON)
      ↓
Keyword Similarity Search (352 real SaaS products)
      ↓
┌─────────────────────┬──────────────────────┐
│   Gap Analysis      │   Viability Scorer   │
│   (market gaps +    │   (XGBoost R²=0.94   │
│    opportunities)   │    + SHAP)           │
└─────────────────────┴──────────────────────┘
      ↓
Groq Llama 3 (synthesize → investor-style report)
      ↓
Next.js Dashboard
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Data collection | Product Hunt GraphQL API | Real SaaS product corpus |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | Semantic text understanding |
| Vector search | FAISS (local) / keyword search (production) | Fast similarity search |
| ML model | XGBoost Regressor | Best for tabular feature data |
| Explainability | SHAP TreeExplainer | Per-prediction feature attribution |
| LLM | Groq Llama 3 (llama-3.1-8b-instant) | Fast, free, high quality |
| Backend | FastAPI + Python | Async, auto docs, production-ready |
| Frontend | Next.js + Tailwind CSS | Fast, modern, responsive |
| Deployment | Vercel (frontend) + Render (backend) | Free tier, auto-deploy on push |

---

## ML Pipeline Details

### Data — 352 real SaaS products
Scraped from Product Hunt API via GraphQL pagination. Each product includes name, tagline, description, vote count, topics, and creation date. Data cleaned, deduplicated, and stored as CSV corpus.

### Feature Engineering — 7 engineered features
| Feature | How computed |
|---|---|
| competition_density | Average similarity to nearest neighbors |
| novelty_score | 1 - competition_density |
| market_growth | Keyword matching against high-growth topics |
| pain_severity | Pain indicator words in description |
| monetization_signal | Business/pricing keywords in description |
| description_quality | Length + specificity + action words |
| topic_diversity | Number of topic categories |

### Viability Model — XGBoost Regressor
- Target: domain-informed weighted formula (pain × 0.25 + growth × 0.20 + monetization × 0.20 + quality × 0.15 + novelty × 0.10 - competition × 0.15)
- R² score: 0.941
- MAE: 0.84 points on 0-100 scale
- Explainability: SHAP TreeExplainer for per-prediction feature attribution

---

## Project Structure
```
saasify/
├── frontend/                    # Next.js dashboard
│   ├── app/
│   │   ├── page.tsx             # Landing page with idea input
│   │   ├── analyze/page.tsx     # Results dashboard
│   │   └── api/analyze/         # Next.js API route → ML service
│   ├── services/mlService.ts    # API service layer
│   └── types/analysis.ts        # TypeScript interfaces
│
├── ml-service/                  # FastAPI ML backend
│   ├── app.py                   # Full ML service (local dev)
│   ├── app_lite.py              # Lightweight service (production)
│   ├── scraper.py               # Product Hunt data collection
│   ├── embeddings.py            # FAISS index builder
│   ├── gap_analysis.py          # KeyBERT gap detection
│   ├── llm_service.py           # Groq LLM integration
│   ├── prepare_training_data.py # Feature engineering pipeline
│   ├── train_model.py           # XGBoost training + SHAP
│   ├── data/
│   │   ├── products.csv         # Raw scraped data
│   │   └── products_clean.csv   # Cleaned corpus
│   ├── models/
│   │   ├── viability_model.pkl  # Trained XGBoost model
│   │   ├── shap_explainer.pkl   # SHAP TreeExplainer
│   │   ├── embeddings.pkl       # Product embeddings
│   │   └── metrics.json         # Model evaluation metrics
│   └── Dockerfile               # Container for deployment
│
└── NOTES.md                     # Detailed build documentation
```

---

## Running Locally

### Prerequisites
- Python 3.11
- Node.js 18+

### Backend
```bash
git clone https://github.com/GargiAP/Saasify.git
cd Saasify

python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Mac/Linux

pip install -r ml-service/requirements.txt

echo "GROQ_API_KEY=your_key_here" > ml-service/.env

cd ml-service
uvicorn app:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
echo "NEXT_PUBLIC_ML_SERVICE_URL=http://localhost:8000" > .env.local
npm run dev
```

Open `http://localhost:3000`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check + model metrics |
| POST | `/analyze` | Full idea analysis pipeline |
| POST | `/feedback` | Save user feedback |
| GET | `/metrics` | Model evaluation metrics |

### Sample request
```bash
curl -X POST https://saasify-ml-service.onrender.com/analyze \
  -H "Content-Type: application/json" \
  -d '{"idea": "an AI tool that helps developers automate code reviews"}'
```

---

## Key Engineering Decisions

**Why XGBoost over neural networks?**
XGBoost is interpretable, fast to train, and works better on tabular feature data. Compatible with SHAP for per-prediction explanations — critical for our use case where users need to understand why their score is what it is.

**Why formula-derived targets?**
Real outcome labels like revenue and retention are not publicly available. Product Hunt votes are noisy proxies — 64% of products have zero votes regardless of quality. A domain-informed formula encodes startup research knowledge and gives the model meaningful signal to learn from.

**Why Groq Llama 3 over GPT-4?**
Groq's inference is 10x faster than OpenAI at comparable quality for structured extraction tasks. Free tier with 14,400 requests/day is sufficient for development and demo usage.

**Why FAISS for similarity search?**
FAISS scales to millions of vectors with sub-millisecond search. Even at 352 products it is the right tool — no code changes needed to scale to 500,000 products.

---

## Resume Description

Built an ML-powered startup idea evaluation system: scraped 352 real SaaS products via Product Hunt GraphQL API, engineered 7 features from raw text, trained XGBoost regression model (R²=0.94) with SHAP explainability, and integrated Groq Llama 3 for structured idea analysis and report generation. Deployed as FastAPI + Next.js application on Render + Vercel with CI/CD via GitHub.

---

## Author

**Gargi Pratapwar**
[GitHub](https://github.com/GargiAP) • [LinkedIn](your-linkedin-here)
