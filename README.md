# MLOps Price Intelligence Platform

A full-stack, category-agnostic MLOps system that scrapes e-commerce and direct supplier pricing across every product type — from smartphones to engine crankshafts, detergent to industrial glass, house paint to metals. Estimates fair market price ranges (P10–P90 interval) using Machine Learning and exposes predictions via FastAPI and a high-end React dashboard.

## Features

1. **Universal Taxonomy Engine**: Configure categories and dynamic specification parameters via a declarative schema. Zero code changes required to add a new category.
2. **Input Intelligence Layer**: Spell correction and fuzzy brand matching (Levenshtein edit-distance) on input listings. Normalizes specifications to standard SI units (e.g. `mm`, `kg`, `L`) using a rule-based parser.
3. **Quantile Regression Pricing Model**: Estimates fair price distributions (P10, P50, P90) based on category data and spec adjustments (e.g. materials, RAM, storage, purchase volume, etc.).
4. **OEM Factory Intake System**: Direct portal for manufacturers to submit catalog details and bulk pricing tiers directly into the training pipeline database.
5. **Supabase & Local SQLite Fallback**: Automatic local SQLite fallback when Supabase connection details are not configured, enabling zero-config out-of-the-box local and Vercel cloud testing.
6. **Vercel Cloud Support**: Configured with a `vercel.json` rewrite schema to host the Vite + React frontend static site and run python serverless backend functions inside a single monorepo.

---

## Tech Stack

* **Backend**: FastAPI, Uvicorn, Pydantic Settings, Structlog, NumPy, Pandas, Scikit-Learn, XGBoost, PyYAML
* **Frontend**: React (Vite), CSS Custom Properties (Vanilla CSS system)
* **Database**: Supabase / PostgreSQL / SQLite Fallback
* **Deployment**: Vercel (monorepo deployments for frontend + python serverless functions)

---

## Repository Structure

```
project-ml-ops/
├── api/                     # FastAPI endpoint definitions
│   ├── main.py              # Application entry point
│   └── routers/             # Sub-routers for predictions, products, and intake
├── config/                  # App configurations and logging setups
├── db/                      # Database connectors and migrations
├── ml/                      # Machine learning feature extraction & models
│   ├── features/            # Feature matrices and text vectorizers
│   ├── matching/            # Product pairing similarity model
│   └── pricing/             # Distribution quantile pricing model
├── taxonomy/                # Unit normalizers, categories & input corrector logic
├── dashboard/               # Vite + React dashboard frontend application
├── vercel.json              # Vercel deployment build & route mappings
├── pyproject.toml           # Hatchling build system configurations
├── requirements.txt         # Minimal lightweight dependencies lists
└── README.md
```

---

## Local Setup & Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Ingest Seed Data
Run the scraping ingestion runner to seed the SQLite database with 34 realistic cross-platform product records:
```bash
python -m scrapers.run
```

### 3. Run FastAPI Backend
```bash
python -m api.main
```
The API Swagger documentation will be available at: [http://localhost:8000/docs](http://localhost:8000/docs).

### 4. Run Frontend Dashboard
Ensure Node.js is installed locally, navigate to `dashboard/` directory, and run:
```bash
cd dashboard
npm install
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) to view the premium dashboard.

---

## Vercel Deployment

This project is fully structured as a single monorepo compatible with Vercel:
1. Push the code to a GitHub repository.
2. Link the repository to your Vercel Dashboard project.
3. Vercel will auto-detect the root `package.json` and build command, compile the Vite React app into `dashboard/dist`, and deploy the Python Serverless Functions in `/api` automatically.
