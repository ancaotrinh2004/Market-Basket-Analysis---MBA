# Market Basket Analysis
A complete end-to-end Market Basket Analysis system using **FP-Growth algorithm** to generate intelligent product recommendations. Built with modern data stack: **dbt**, **FastAPI**, and **Streamlit**.

![System Architecture](docs/architecture.svg)

## 📋 Table of Contents
- [Overview](#-overview)
- [Repository Struture](#repository-structure)
- [Features](#-features)
- [Tech Stack](#️-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage Guide](#-usage-guide)
- [Configuration](#️-configuration)
---

## 🎯 Overview

This system analyzes transaction data to discover product associations and provide personalized recommendations. It helps businesses:

- 📊 Understand customer buying patterns
- 🎯 Generate real-time product recommendations
- 💡 Optimize product placement and bundling
- 📈 Increase cross-selling opportunities
- 🔍 Discover hidden product relationships

### Key Metrics
- **Algorithm**: FP-Growth (10-100x faster than Apriori)
- **Performance**: Sub-second recommendations for 1M+ transactions
- **Accuracy**: Lift-based ranking ensures relevant suggestions
- **Scalability**: Horizontal scaling with Docker
---
## 📁Repository Structure

```bash
Market-Basket-Analysis/
├── backend
│   ├── app
│   │   ├── routers
│   │   ├── config.py
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── models.py
│   ├── Dockerfile
│   └── requirements.txt
├── data
│   └── basket_analysis.csv
├── dbt
│   └── mba_dbt
│       ├── analyses
│       ├── macros
│       ├── models
│       ├── seeds
│       ├── snapshots
│       ├── tests
│       ├── dbt_project.yml
│       └── README.md
├── frontend
│   ├── pages
│   │   ├── Analytics.py
│   │   ├── Recommendations.py
│   │   ├── Rules_Explorer.py
│   │   └── Search.py
│   ├── utils
│   │   ├── api_client.py
│   │   └── visualizations.py
│   ├── app.py
│   ├── config.py
│   ├── Dockerfile
│   └── requirements.txt
├── notebook
│   └── eda.ipynb
├── postgres_init
│   └── init.sql
├── scripts
│   └── fp_growth.py
├── docker-compose.yml
└── README.md
```
---
## ✨ Features

### 🎯 Recommendation Engine
- Real-time product recommendations based on cart items
- Configurable confidence and lift thresholds
- Batch processing support
- Multi-item association analysis

### 📊 Analytics Dashboard
- Interactive visualizations (Plotly)
- Distribution analysis (confidence, lift, support)
- Top items and patterns discovery
- Quadrant analysis for rule quality

### 🔍 Rules Explorer
- Browse and filter association rules
- Search by product name
- Export to CSV
- Detailed metric explanations

### 🔎 Search Functionality
- Find rules containing specific items
- View antecedent/consequent relationships
- Quick search suggestions
- Pattern insights

---
## 🛠️ Tech Stack

### Data Processing
- **dbt**: Data transformation
- **PostgreSQL**: Database
### Backend
- **FastAPI**: RestAPI framework
- **SQLAlchemy**: ORM
- **Pydantic**: Datavalidation
- **Uvicorn**: Web server
### Frontend
- **Streamlit**: UI framework
### DevOps
- **Docker - Docker compose**: Containerization
## 📦 Prerequisites

- **Python** 3.11+
- **PostgreSQL** 15+
- **Docker** & **Docker Compose** (optional, for containerized deployment)
- **Git**
- **Conda**
## 🚀 Installation

### Method 1: Local Installation (Development)

#### 1. Clone Repository
```bash
git clone https://github.com/ancaotrinh2004/Market-Basket-Analysis---MBA.git
cd Market-Basket-Analysis---MBA
```

#### 2. Create Virtual Environment
```bash
conda create -n mba python==3.11
conda activate mba
```

#### 3. Install Dependencies

**dbt:**
```bash
cd mba_dbt
pip install dbt-postgres
```

**Backend:**
```bash
cd ../backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd ../frontend
pip install -r requirements.txt
```

#### 4. Setup Database
```bash
# Create PostgreSQL database
createdb mba_db

# Or using psql
psql -U postgres -c "CREATE DATABASE mba_db;"
```

#### 5. Configure Environment Variables

**Create `.env` files:**

`mba_dbt/profiles.yml`:
```yaml
mba_dbt:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      port: 5432
      user: your_user
      password: your_password
      dbname: mba_db
      schema: public
      threads: 4
```

`backend/.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/mba_db
API_TITLE=MBA Recommendation API
API_VERSION=1.0.0
CORS_ORIGINS=["http://localhost:8501"]
```

`frontend/.env`:
```bash
API_URL=http://localhost:8000
APP_TITLE=MBA Recommender System
```

---

### Method 2: Docker Installation (Production)

#### 1. Clone Repository
```bash
git clone https://github.com/ancaotrinh2004/Market-Basket-Analysis---MBA.git
cd Market-Basket-Analysis---MBA
```

#### 2. Configure Environment
Edit `docker-compose.yml` if needed (ports, credentials, etc.)

#### 3. Build and Run
```bash
docker-compose up --build -d
```

#### 4. Access Services
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5433
---

## ⚡ Quick Start

### Step 1: Load Data
```bash
cd mba_dbt

# Load seed data
dbt seed

# Run transformations
dbt run
```

### Step 2: Generate Rules
```bash
# From project root
python scripts/fp_growth.py --min-support 0.01 --min-confidence 0.1 --min-lift 1.0
```

### Step 3: Start Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Start Frontend
```bash
cd frontend
streamlit run app.py
```

### Step 5: Access Application

Open browser: **http://localhost:8501**

---

## 📖 Usage Guide

### 1. Home Page
- View system status (API, Database)
- Check overall statistics
- Quick start guide

### 2. Recommendations Page

**Get Recommendations:**
1. Select items from dropdown (your cart)
2. Adjust settings:
   - Number of recommendations (1-20)
   - Minimum confidence threshold
   - Minimum lift threshold
3. Click "Get Recommendations"
4. View ranked suggestions with metrics
5. Download results as CSV

**Example:**
```
Cart: [Milk, Bread]
→ Recommendations: Butter (Lift: 2.5), Eggs (Lift: 2.1), Cheese (Lift: 1.8)
```

### 3. Rules Explorer

**Browse Rules:**
1. Set filters (confidence, lift, support)
2. Choose max results (50-1000)
3. Click "Load Rules"
4. Sort and filter table
5. Export to CSV

### 4. Analytics Dashboard

**View Insights:**
- Key metrics overview
- Top 30 items frequency chart
- Distribution histograms (confidence, lift, support)
- Confidence vs Lift scatter plot
- Quadrant analysis
- Top 20 rules by lift

### 5. Search

**Find Rules:**
1. Enter product name
2. Click search or select from suggestions
3. View results in 3 tabs:
   - **As Antecedent**: What's bought AFTER
   - **As Consequent**: What's bought BEFORE
   - **All Results**: Complete list
4. Download search results

## ⚙️ Configuration

### dbt Configuration

`mba_dbt/dbt_project.yml`:
```yaml
name: 'mba_dbt'
version: '1.0.0'
profile: 'mba_dbt'

models:
  mba_dbt:
    staging:
      +materialized: view
    marts:
      +materialized: table

seeds:
  mba_dbt:
    basket_analysis:
      +alias: raw_basket
      +quote: false
```

### FP-Growth Parameters

Adjust in `scripts/fp_growth.py`:
```python
python scripts/fp_growth.py \
  --min-support 0.01 \     # Minimum support (1%)
  --min-confidence 0.1 \   # Minimum confidence (10%)
  --min-lift 1.0 \         # Minimum lift
  --table-name fp_growth_rules
```

### API Configuration

`backend/app/config.py`:
```python
class Settings(BaseSettings):
    database_url: str
    api_title: str = "MBA Recommendation API"
    api_version: str = "1.0.0"
    cors_origins: List[str] = ["*"]
```

### UI Configuration

`frontend/config.py`:
```python
API_URL = "http://localhost:8000"
APP_TITLE = "MBA Recommender System"
```

