# Joyory SmartMatch — Hackathon & HR Presentation Guide

---

## Problem Statement

Beauty product discovery is overwhelming:
- Thousands of products with complex ingredient lists
- Generic recommendations that ignore real skin types and concerns
- No tools to check whether products can be safely used together
- No personalized routine guidance
- No honest catalog analytics for informed buying decisions

**Target users**: Beauty enthusiasts, skincare beginners, anyone who wants confident, data-driven beauty choices.

---

## Solution

**Joyory SmartMatch** is a smart beauty shopping experience that helps users:
1. **Find the right products** — via an AI-style quiz that matches skin type, concern, and budget to real catalog products
2. **Build a complete routine** — AM and PM steps using real products from the database, ordered correctly
3. **Check ingredient safety** — detect conflicts (e.g. Retinol + Vitamin C should be used at different times)
4. **Compare products** — side-by-side with ingredient overlap analysis and a value-for-money score
5. **Understand the catalog** — honest rating analytics across 12 products and 3,000+ reviews

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   FRONTEND (React 18)                    │
│  Pages: Home, Catalog, PDP, Quiz, Compare, Routine,      │
│  Ingredient Checker, Review Insights, Dashboard, FAQ      │
│  State: React Context (cart, wishlist, compare)           │
│  Services: api.js → Fetch to Django REST API             │
└──────────────────────────────┬──────────────────────────┘
                               │ HTTP / JSON
┌──────────────────────────────▼──────────────────────────┐
│           BACKEND (Python 3, Django 4, DRF)              │
│  Products App: views.py, models.py, urls.py              │
│  Services:                                               │
│    ├── Recommender (rule-based, scored matching)         │
│    ├── FaqAssistant (intent + TF-IDF hybrid)             │
│    ├── IngredientChecker (conflict rule database)        │
│    ├── RoutineBuilder (step-by-step, real products)      │
│    └── ReviewAnalyzer (rating distribution, analytics)   │
│  Database: SQLite 3 (12 products, 6 categories)          │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, React Router v6, Context API |
| Styling | Vanilla CSS with CSS Variables (no Tailwind) |
| Backend | Python 3.13, Django 4, Django REST Framework |
| Database | SQLite 3 (via Django ORM) |
| NLP/ML | Rule-based + TF-IDF (no external ML APIs) |
| Startup | `start_joyory.bat` (one-command launcher) |

---

## What Was Built — Feature Map

### Original Features (pre-hackathon session)
- Product catalog with categories
- Basic product detail pages
- Simple recommendation quiz
- Basic FAQ chatbot

### Newly Implemented Features

| Feature | Route | Backend Service | Status |
|---|---|---|---|
| SmartMatch Quiz (upgraded) | `/quiz` | `Recommender` with scoring | ✅ Working |
| FAQ Assistant (upgraded) | floating widget | `FaqAssistant` intent+TF-IDF | ✅ Working |
| Ingredient Safety Checker | `/ingredient-check` | `IngredientChecker` + conflict DB | ✅ Working |
| Beauty Routine Builder | `/routine` | `RoutineBuilder` + real DB products | ✅ Working |
| Product Comparison | `/compare` | Client-side ingredient overlap | ✅ Working |
| Review Insights | `/reviews` | `ReviewAnalyzer` | ✅ Working |
| Unified Dashboard | `/dashboard` | Live API stats aggregated | ✅ Working |
| Wishlist | `/wishlist` | localStorage | ✅ Working |
| Cart | `/cart` | localStorage | ✅ Working |

---

## How Product Matching Works

The `Recommender` service scores each product against the user's quiz answers:

```
Score components (all deterministic, no ML model):
  +30  if skin_type matches exactly
  +15  if concern_tags contains user's concern
  +20  if price ≤ user's budget
  +10  if user's preferred_ingredient in key_ingredients
  +5   if product.is_bestseller
  +5   (rating - 3.0) × 10   [rating bonus, 0-20 range]
  -10  if price > budget
```

Products are ranked by total score. The frontend shows the score as a match percentage.

---

## Database

**Engine**: SQLite 3 (file: `backend/db.sqlite3`)
**Tables used**: `products_product` (12 products), `api_product` (legacy)
**Key fields per product**: name, brand, category, price, discount_percent, rating, review_count, skin_type, concern_tags, key_ingredients, usage_instructions, image_url, availability, is_bestseller

**What does NOT exist in the database**:
- Individual review text (no `Review` model)
- User accounts (no registration/login)
- Order history
- Cart persistence (localStorage only)

---

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/products/` | GET | List with search, filter, sort, pagination |
| `/api/products/{id}/` | GET | Product detail |
| `/api/products/categories/` | GET | Distinct categories |
| `/api/products/recommend/` | POST | Scored product matching |
| `/api/products/faq/` | POST | Intent-based FAQ |
| `/api/products/ingredient-check/` | POST | Ingredient conflict analysis |
| `/api/products/routine/` | POST | AM/PM routine generation |
| `/api/products/review-insights/` | GET | Catalog rating analytics |

---

## Testing Summary

- **73 backend tests executed** — all pass
- **0 test failures** at final run
- Tests cover: model logic, API endpoints, recommendation engine, FAQ, ingredient checker, routine builder, review analyzer

See `docs/TESTING_REPORT.md` for the full breakdown.

---

## Known Limitations

| Limitation | Honest Disclosure |
|---|---|
| No review text | Only rating numbers & review counts stored. No sentiment analysis possible. |
| Small catalog | 12 products. Routine Builder may show "not found" for less common product types. |
| No user auth | No login. Cart/wishlist stored in browser only. |
| SQLite | Suitable for development/demo. Not production-ready for concurrent users. |
| No HTTPS locally | Production security headers not configured (expected for dev). |
| No model training | All matching is deterministic rule-based — no trained model. |

---

## Demo Script (for Judges / HR)

> **"Let me walk you through Joyory SmartMatch — a smart beauty shopping experience I built for this hackathon."**

**1. Start at the Dashboard** (`/dashboard`)
> "This is the unified dashboard. The numbers here — products, review count, average rating — all come live from the SQLite database. No fake data."

**2. Run the Quiz** (`/quiz`)
> "The SmartMatch Quiz asks four questions. Let me select oily skin, acne concern, budget ₹600, and I prefer Niacinamide. The backend scores every product and returns these match percentages. The algorithm is transparent — it's a weighted rule system, not a black box."

**3. Check Ingredient Safety** (`/ingredient-check`)
> "Now suppose I want to use Vitamin C serum in the morning and Retinol at night. Let me check those together. You can see — Vitamin C and Retinol have a medium-severity conflict because Vitamin C works at low pH while Retinol degrades in acidic environments. The checker recommends using them at different times."

**4. Build a Routine** (`/routine`)
> "For oily skin with acne concern — the Routine Builder generates a step-by-step AM and PM routine using real products from our catalog. Step 3 found our Niacinamide Gel. Steps with no matching product show an honest 'not found' with a tip instead of a fake product."

**5. Compare Two Products** (`/compare`)
> "I'll add two products to compare. Side-by-side we see ratings, value score — that's rating divided by price, a fair measure of bang for your rupee — and an ingredient overlap analysis. This one gets the Best Pick badge."

**6. Review Insights** (`/reviews`)
> "This page honestly shows what we know — 12 products, 3,278 total reviews, average rating 4.37. I'll be transparent: we don't store individual review text, so we can't do sentiment analysis. What we CAN show is rating distribution, per-category trends, and which products have the most confidence behind their ratings."

**7. Close with Architecture**
> "Everything runs locally with one command: `.\start_joyory.bat`. Backend on port 8000, frontend on 3000. Django REST Framework handles all APIs, React handles the UI. 73 automated tests all pass."

---

## Future Improvements

1. Add a `Review` model with text body → enable real sentiment analysis
2. User authentication → persistent cart, wishlists, purchase history
3. Expand catalog → more product types (toner, eye cream, SPF) for better routine coverage
4. PostgreSQL → production-grade database
5. Product image upload → admin panel for content management
6. Comparison export → PDF or email
