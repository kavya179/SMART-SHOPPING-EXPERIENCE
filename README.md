# Joyory SmartMatch — Smart Shopping Experience

> **Hackathon demo prototype** with verified sample data.  
> Not officially integrated with Joyory.

A full-stack, intelligent beauty and personal-care shopping platform that helps customers discover, understand, compare, and choose products based on their skin profile, preferences, and budget.

---

## 🌟 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 18 + JavaScript (ES6+) + Bootstrap 5 + Glassmorphism CSS3 |
| **Typography** | Google Fonts (*Outfit* & *Plus Jakarta Sans*) |
| **Backend** | Python 3.12 + Django 5.x |
| **API** | Django REST Framework (DRF) |
| **Database** | SQLite (via Django ORM) |
| **ML & NLP** | scikit-learn (TF-IDF + Logistic Regression) + Cosine Similarity |
| **Testing** | Django Test Runner (`products/tests.py` — 26 unit tests) |

---

## 📂 Project Structure

```
SMART-SHOPPING-EXPERIENCE/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── smartmatch/             # Django settings, URLs, WSGI
│   ├── api/                    # Health-check app
│   └── products/               # Product catalog, recommendation & FAQ app
│       ├── models.py           # Product model with INCI, routine & caution fields
│       ├── serializers.py      # DRF serializers
│       ├── views.py            # Catalog, recommendation & FAQ endpoints
│       ├── tests.py            # 26 automated unit tests
│       ├── data/
│       │   └── faq_intent_dataset.json  # Labeled intent training dataset
│       ├── scripts/
│       │   └── train_faq_model.py       # Reproducible ML training script
│       ├── ml_models/
│       │   ├── faq_intent_classifier.joblib  # Trained TF-IDF + Logistic Regression model
│       │   └── faq_semantic_index.joblib     # TF-IDF QA semantic retrieval index
│       ├── services/
│       │   ├── recommender.py   # Rule-based recommendation engine
│       │   └── faq_assistant.py # Hybrid NLP & entity extraction assistant
│       └── management/commands/
│           └── seed_products.py # 12-product multi-category seeder
├── frontend/                   # React SPA
│   ├── public/index.html
│   └── src/
│       ├── components/
│       │   ├── Navbar.js / .css
│       │   ├── Footer.js / .css
│       │   ├── ProductCard.js / .css
│       │   ├── CompareDock.js / .css
│       │   ├── FaqAssistant.js / .css   # Intelligent floating chat assistant
│       │   └── StateDisplay.js / .css
│       ├── context/
│       │   └── ShopContext.js  # Global cart, wishlist, compare & toast state
│       ├── pages/
│       │   ├── HomePage.js / .css
│       │   ├── ProductCatalog.js / .css
│       │   ├── ProductDetail.js / .css
│       │   ├── SmartMatchQuiz.js / .css
│       │   ├── ComparePage.js / .css
│       │   ├── WishlistPage.js / .css
│       │   └── CartPage.js / .css
│       └── services/
│           └── api.js          # Unified API service layer
├── docs/                       # Comprehensive documentation & PDFs
│   ├── Joyory_SmartMatch_Development_Documentation.pdf
│   ├── Joyory_SmartMatch_Development_Documentation.md
│   └── HACKATHON_DELIVERABLES.pdf
├── HACKATHON_DELIVERABLES.md
├── HACKATHON_DELIVERABLES.pdf
└── README.md
```

---

## 🚀 Quick Start (Windows PowerShell / CMD)

### Option A: One-Click Launcher (Recommended)
Simply double-click or run:
```powershell
.\start_joyory.bat
```
This automatically launches both the **Django Backend** (`http://localhost:8000`) and the **React Frontend** (`http://localhost:3000`) in separate windows.

---

### Option B: Manual Startup

#### 1. Terminal 1 — Backend (Django on port 8000)
```powershell
cd backend
.\venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py seed_products

# Run unit tests
python manage.py test

# Start backend server
python manage.py runserver 8000
```

#### 2. Terminal 2 — Frontend (React on port 3000)
```powershell
cd frontend
npm start
```
Visit **`http://localhost:3000`** in your browser.

---

## 🤖 Beauty FAQ Assistant Architecture (Hybrid NLP)

The Beauty FAQ Assistant solves the problem of repetitive, generic answers by combining:
1. **Machine Learning Intent Classifier**: Lightweight `TfidfVectorizer(ngram_range=(1, 2))` + `LogisticRegression` pipeline classifying 14 distinct customer intents (`greeting`, `gratitude`, `farewell`, `usage_instructions`, `ingredients`, `product_purpose`, `safety_and_cautions`, `price_and_discount`, `budget_search`, `availability_and_stock`, `comparison_and_alternatives`, `skin_type_recommendation`, `platform_policy`, `medical_disclaimer_fallback`).
2. **Semantic Question-Answer Retrieval**: TF-IDF cosine similarity index over verified platform questions with a strict similarity threshold to prevent false positives.
3. **Product Entity & Pronoun Context Tracking**: Automatically extracts product context and resolves follow-ups (*"What is its price?"*, *"What are its ingredients?"*) via `context_product_id`.
4. **Live SQLite Catalog Grounding**: Real-time attribute formatting (discounted price calculation, INCI list, routine directions, and budget queries).
5. **Strict Non-Medical Guardrails**: Programmatically intercepts medical treatment queries and attaches clear non-medical disclaimers.

---

## 🔗 REST API Endpoints

| Method | URL | Description |
|---|---|---|
| `GET` | `/api/health/` | Health check |
| `GET` | `/api/products/` | Filterable product catalog (`category`, `search`, `min_price`, `max_price`, `skin_type`, `ordering`) |
| `GET` | `/api/products/<id>/` | Product detail with full INCI, routine, and cautions |
| `GET` | `/api/products/categories/` | Category counts summary |
| `POST` | `/api/recommendations/` | SmartMatch 5-step quiz recommendation engine |
| `POST` | `/api/faq/` | Intelligent Hybrid NLP Product FAQ Assistant |

---

## 🧪 Automated Testing
```powershell
cd backend
.\venv\Scripts\python.exe manage.py test
```
**Result**: **36 / 36 Unit Tests Passing** (100% OK, 0 errors, 0 failures).