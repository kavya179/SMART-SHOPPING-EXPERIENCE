# Joyory SmartMatch — Smart Shopping Experience

> **Hackathon demo prototype** with sample data.  
> Not officially integrated with Joyory.

A full-stack web application that helps customers discover, understand, compare, and choose beauty & personal-care products based on their needs, preferences, and budget.

## Tech Stack

| Layer      | Technology                          |
|------------|-------------------------------------|
| Frontend   | React 18 + JavaScript + Bootstrap 5 |
| Backend    | Python + Django 4.2                 |
| API        | Django REST Framework               |
| Database   | SQLite (via Django ORM)             |
| Matching   | Python rule-based logic (Phase 3+)  |

## Project Structure

```
SMART-SHOPPING-EXPERIENCE/
├── backend/                    # Django project
│   ├── manage.py
│   ├── requirements.txt
│   ├── smartmatch/             # Django settings, URLs, WSGI
│   ├── api/                    # Health-check API app
│   └── products/               # Product catalog app (Phase 2)
│       ├── models.py           # Product model
│       ├── serializers.py      # DRF serializers
│       ├── views.py            # List, detail, search, filter
│       ├── admin.py            # Django admin config
│       ├── tests.py            # Unit tests
│       └── management/commands/
│           └── seed_products.py  # Sample data seeder
├── frontend/                   # React app
│   ├── public/index.html       # Bootstrap 5 via CDN
│   └── src/
│       ├── App.js              # Landing page
│       └── components/
│           └── ConnectionTest.js
├── README.md
└── .gitignore
```

## Quick Start (Windows PowerShell)

### Terminal 1 — Backend (Django on port 8000)

```powershell
cd SMART-SHOPPING-EXPERIENCE\backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_products       # Load 12 sample products
python manage.py runserver
```

### Terminal 2 — Frontend (React on port 3000)

```powershell
cd SMART-SHOPPING-EXPERIENCE\frontend
npm install
npm start
```

## API Endpoints

| Method | URL                              | Description                    |
|--------|----------------------------------|--------------------------------|
| GET    | `/api/health/`                   | Health check                   |
| GET    | `/api/products/`                 | List all products (filterable) |
| GET    | `/api/products/<id>/`            | Product detail                 |
| GET    | `/api/products/categories/`      | List categories with counts    |

### Filtering & Search

| Parameter    | Example                             | Description              |
|-------------|--------------------------------------|--------------------------|
| `category`   | `?category=skincare`                | Filter by category       |
| `skin_type`  | `?skin_type=oily`                   | Filter by skin type      |
| `min_price`  | `?min_price=300`                    | Minimum price            |
| `max_price`  | `?max_price=800`                    | Maximum price            |
| `search`     | `?search=vitamin`                   | Search name/brand/desc   |
| `concern`    | `?concern=acne`                     | Filter by concern tag    |
| `bestseller` | `?bestseller=true`                  | Only bestsellers         |
| `new`        | `?new=true`                         | Only new arrivals        |
| `ordering`   | `?ordering=-rating`                 | Sort (price, rating, name) |

## Verification

1. **Backend health check**: http://localhost:8000/api/health/
2. **Product list**: http://localhost:8000/api/products/
3. **Frontend**: http://localhost:3000 → click "Test Health" and "Fetch Products"
4. **Django admin**: http://localhost:8000/admin/ (create superuser first: `python manage.py createsuperuser`)
5. **Run tests**: `python manage.py test products api --verbosity=2`

## Seeding & Resetting Data

```powershell
# Seed sample products (idempotent — won't duplicate)
python manage.py seed_products

# Clear and reseed
python manage.py seed_products --clear
```

## Completed Phases

- [x] **Phase 1**: Project scaffolding, Django + React setup, API health check, CORS
- [x] **Phase 2**: Product model, migrations, sample catalog, CRUD API, search/filter, admin, tests
- [ ] **Phase 3**: Recommendation engine, user preferences (upcoming)