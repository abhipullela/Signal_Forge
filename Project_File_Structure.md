# SignalForge — Complete Project File Structure

This document defines the recommended **complete repository structure** for SignalForge.

The structure is intentionally modular so that the team can develop the ML pipeline, backend, PostgreSQL database, frontend dashboard, chatbot, tests, and deployment configuration independently without creating a monolithic codebase.

---

## 1. Repository Root

```text
signalforge/
│
├── README.md
├── Project_File_Structure.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Makefile
├── pyproject.toml
│
├── backend/
├── frontend/
├── ml/
├── data/
├── database/
├── scripts/
├── tests/
├── docs/
├── notebooks/
├── configs/
├── deployment/
└── .github/
```

---

# 2. Root-Level Files

## `README.md`

Main GitHub documentation.

Contains:

- project overview
- problem statement
- architecture
- features
- setup instructions
- ML approach
- API overview
- chatbot explanation
- contribution guide

---

## `PROJECT_STRUCTURE.md`

This file.

Documents:

- directory responsibilities
- major modules
- file ownership
- data flow
- development conventions

---

## `LICENSE`

Open-source license selected by the team.

---

## `CONTRIBUTING.md`

Contribution guidelines covering:

- branches
- commits
- pull requests
- testing
- code review

---

## `CHANGELOG.md`

Tracks significant project changes.

Example:

```text
## [0.2.0]

### Added
- Signal scoring
- Explain endpoint

### Changed
- Improved temporal feature extraction
```

---

## `.gitignore`

Must exclude:

```text
.env
.venv/
__pycache__/
*.pyc
node_modules/
dist/
build/
.pytest_cache/
.ipynb_checkpoints/
*.log
ml/models/*.pkl
ml/models/*.joblib
data/raw/*
data/processed/*
```

Keep sample data separately if it is safe to commit.

---

## `.env.example`

Documents required environment variables without containing real secrets.

---

## `docker-compose.yml`

Local multi-service development.

Potential services:

```text
postgres
backend
frontend
```

Optional later:

```text
redis
worker
```

---

## `Makefile`

Convenient commands such as:

```text
make setup
make dev
make test
make lint
make migrate
make seed
make ml
make clean
```

---

## `pyproject.toml`

Python project configuration.

Can contain:

- dependencies
- formatting configuration
- linting configuration
- pytest configuration
- package metadata

---

# 3. Backend

```text
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   │
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       ├── signals.py
│   │       ├── communities.py
│   │       ├── search.py
│   │       ├── chat.py
│   │       └── ml.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py
│   │   ├── base.py
│   │   └── dependencies.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── source.py
│   │   ├── community.py
│   │   ├── post.py
│   │   ├── feature.py
│   │   ├── signal.py
│   │   ├── signal_event.py
│   │   └── model_run.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── source.py
│   │   ├── community.py
│   │   ├── post.py
│   │   ├── signal.py
│   │   ├── search.py
│   │   ├── chat.py
│   │   └── common.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── signal_service.py
│   │   ├── community_service.py
│   │   ├── search_service.py
│   │   ├── explanation_service.py
│   │   └── chat_service.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── signal_repository.py
│   │   ├── community_repository.py
│   │   ├── post_repository.py
│   │   └── model_run_repository.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── pagination.py
│       ├── validators.py
│       └── time.py
│
├── requirements.txt
└── requirements-dev.txt
```

---

# 4. Backend Responsibilities

## `backend/app/main.py`

Application entry point.

Responsibilities:

- create FastAPI application
- register middleware
- register routers
- configure startup/shutdown

---

## `backend/app/api/`

Contains HTTP route definitions.

Routes should remain thin.

Avoid putting complex ML/database logic directly inside route functions.

Preferred flow:

```text
Route
  ↓
Schema validation
  ↓
Service
  ↓
Repository / ML module
  ↓
Database
```

---

## `backend/app/api/v1/signals.py`

Endpoints for:

- list signals
- retrieve signal
- filter signals
- sort by score
- retrieve signal timeline
- retrieve signal explanation

---

## `backend/app/api/v1/chat.py`

Handles:

```text
POST /chat/query
```

Responsible for receiving natural-language questions and passing them to the conversational service.

---

## `backend/app/core/`

Global application configuration.

### `config.py`

Reads:

- environment variables
- database URL
- API settings
- model paths
- LLM configuration

### `security.py`

Authentication/authorization utilities if required.

---

## `backend/app/db/`

Database connection layer.

### `session.py`

Creates SQLAlchemy engine/session.

### `base.py`

Base model declaration.

### `dependencies.py`

FastAPI database dependencies.

---

# 5. Database Models

```text
backend/app/models/
```

SQLAlchemy ORM models.

### `source.py`

Data-source model.

### `community.py`

Community/source grouping.

### `post.py`

Raw/normalized content.

### `feature.py`

Machine-learning features.

### `signal.py`

Detected micro-trend.

### `signal_event.py`

Historical signal measurements.

### `model_run.py`

Tracks ML model executions.

---

# 6. Schemas

```text
backend/app/schemas/
```

Pydantic models.

They define API contracts separately from database models.

For example:

```text
SignalDB model
       ↓
SignalResponse schema
       ↓
JSON response
```

Never expose the entire database object blindly.

---

# 7. Services

```text
backend/app/services/
```

Application/business logic.

### `signal_service.py`

Coordinates:

- filtering
- ranking
- signal retrieval
- signal summaries

### `explanation_service.py`

Creates structured explanations from stored metrics.

### `chat_service.py`

Coordinates conversational queries.

It should not directly execute arbitrary SQL.

Preferred flow:

```text
User
 ↓
Chat service
 ↓
Intent/query parser
 ↓
Allowed query operation
 ↓
Database/service layer
 ↓
Structured result
 ↓
LLM explanation
```

---

# 8. Repositories

Repositories isolate database operations from business logic.

Example:

```text
SignalService
     ↓
SignalRepository
     ↓
PostgreSQL
```

This makes the application easier to test and modify.

---

# 9. Machine Learning Layer

```text
ml/
│
├── __init__.py
│
├── config/
│   ├── feature_config.yaml
│   ├── model_config.yaml
│   └── scoring_config.yaml
│
├── ingestion/
│   ├── __init__.py
│   ├── loaders.py
│   ├── validators.py
│   └── adapters/
│       ├── __init__.py
│       ├── csv_adapter.py
│       ├── json_adapter.py
│       └── api_adapter.py
│
├── preprocessing/
│   ├── __init__.py
│   ├── text_cleaner.py
│   ├── normalizer.py
│   ├── deduplicator.py
│   └── timestamp_processor.py
│
├── features/
│   ├── __init__.py
│   ├── temporal.py
│   ├── growth.py
│   ├── engagement.py
│   ├── novelty.py
│   ├── community_spread.py
│   ├── persistence.py
│   └── embeddings.py
│
├── detection/
│   ├── __init__.py
│   ├── anomaly_detector.py
│   ├── cluster_detector.py
│   ├── temporal_detector.py
│   └── candidate_generator.py
│
├── scoring/
│   ├── __init__.py
│   ├── normalizer.py
│   ├── signal_score.py
│   └── ranking.py
│
├── explanation/
│   ├── __init__.py
│   └── feature_explanations.py
│
├── training/
│   ├── __init__.py
│   ├── train.py
│   ├── evaluate.py
│   └── calibration.py
│
├── inference/
│   ├── __init__.py
│   └── run.py
│
└── models/
    └── .gitkeep
```

---

# 10. ML Module Responsibilities

## `ingestion/`

Brings data into the ML pipeline.

Supports:

- CSV
- JSON
- API responses
- database records

The long-term production path should read processed data from PostgreSQL rather than requiring every model to read files directly.

---

## `preprocessing/`

Cleans raw input.

### `text_cleaner.py`

Handles:

- whitespace
- URLs
- mentions
- normalization
- optional stopword handling

### `deduplicator.py`

Removes duplicate records.

### `timestamp_processor.py`

Creates normalized time representations.

---

# 11. Feature Engineering

```text
ml/features/
```

Each major feature family should have its own module.

### `temporal.py`

Creates:

- time windows
- rolling statistics
- historical baselines

### `growth.py`

Calculates:

- growth rate
- acceleration
- velocity

### `engagement.py`

Calculates:

- engagement rate
- engagement velocity
- normalized engagement

### `novelty.py`

Measures how different a topic is from historical activity.

### `community_spread.py`

Measures:

- community count
- spread
- cross-community appearance

### `persistence.py`

Measures whether a signal continues across multiple windows.

---

# 12. Detection

The detection layer finds candidate signals.

### `temporal_detector.py`

Detects unusual temporal behavior.

### `cluster_detector.py`

Groups semantically related content.

Potential algorithms:

- K-Means
- DBSCAN
- HDBSCAN

### `anomaly_detector.py`

Detects unusual feature combinations.

Potential algorithms:

- Isolation Forest
- Local Outlier Factor

### `candidate_generator.py`

Combines detector outputs into candidate signals.

---

# 13. Signal Scoring

```text
ml/scoring/
```

Converts features into a unified ranking.

Example:

```text
growth
velocity
novelty
spread
engagement
persistence
       ↓
normalized components
       ↓
weighted score
       ↓
ranked signals
```

Keep weights in:

```text
ml/config/scoring_config.yaml
```

rather than scattering constants across Python files.

---

# 14. Frontend

Recommended structure:

```text
frontend/
│
├── package.json
├── package-lock.json
├── tsconfig.json
├── next.config.*
├── public/
│   ├── logo/
│   └── icons/
│
└── src/
    ├── app/
    │   ├── page.*
    │   ├── signals/
    │   │   ├── page.*
    │   │   └── [id]/
    │   │       └── page.*
    │   ├── communities/
    │   │   └── page.*
    │   └── ask/
    │       └── page.*
    │
    ├── components/
    │   ├── dashboard/
    │   │   ├── TrendCard.*
    │   │   ├── SignalTable.*
    │   │   ├── TrendChart.*
    │   │   ├── CommunitySpread.*
    │   │   └── FilterBar.*
    │   │
    │   ├── signals/
    │   │   ├── SignalHeader.*
    │   │   ├── SignalScore.*
    │   │   ├── SignalTimeline.*
    │   │   ├── ExplainButton.*
    │   │   └── CommunityList.*
    │   │
    │   ├── chat/
    │   │   ├── ChatWindow.*
    │   │   ├── ChatMessage.*
    │   │   ├── SuggestedQuestions.*
    │   │   └── QueryInput.*
    │   │
    │   └── ui/
    │       ├── Button.*
    │       ├── Card.*
    │       ├── Modal.*
    │       ├── Badge.*
    │       └── Loading.*
    │
    ├── lib/
    │   ├── api.*
    │   ├── formatters.*
    │   └── utils.*
    │
    ├── hooks/
    │   ├── useSignals.*
    │   ├── useSignal.*
    │   └── useChat.*
    │
    ├── types/
    │   ├── signal.*
    │   ├── community.*
    │   └── chat.*
    │
    └── styles/
        └── globals.*
```

The exact file extension depends on the selected frontend framework.

---

# 15. Dashboard Pages

## `/`

Main dashboard.

Recommended sections:

```text
Header
│
├── System status
├── Time range
└── Search

Key Metrics
│
├── Active signals
├── Fastest growing
├── Most novel
└── Communities affected

Main Analytics
│
├── Trend timeline
├── Top signals
├── Community spread
└── Signal distribution

Ask SignalForge
```

---

## `/signals`

Signal explorer.

Features:

- search
- filtering
- sorting
- score threshold
- time range
- community filter

---

## `/signals/[id]`

Signal detail page.

Display:

- title
- signal score
- confidence
- first seen
- latest activity
- growth
- velocity
- novelty
- engagement
- communities
- timeline
- explanation

---

## `/ask`

Dedicated conversational interface.

---

# 16. Data Directory

```text
data/
│
├── raw/
│   └── .gitkeep
│
├── interim/
│   └── .gitkeep
│
├── processed/
│   └── .gitkeep
│
├── features/
│   └── .gitkeep
│
├── sample/
│   ├── sample_posts.json
│   ├── sample_communities.json
│   └── sample_signals.json
│
└── README.md
```

### Important

Do not commit large or private raw datasets.

Use:

```text
data/raw/
```

for local/private source data.

Use:

```text
data/sample/
```

for small sanitized datasets that demonstrate the application.

---

# 17. Database

```text
database/
│
├── migrations/
│   ├── README.md
│   └── versions/
│       └── <migration_files>
│
├── seeds/
│   ├── seed_sources.sql
│   ├── seed_communities.sql
│   └── seed_demo_data.sql
│
├── schema/
│   └── schema.md
│
└── queries/
    ├── analytics.sql
    ├── signal_queries.sql
    └── dashboard_queries.sql
```

---

# 18. Database Migrations

Use Alembic for schema evolution.

Example:

```text
migration 001
    ↓
sources
communities
posts

migration 002
    ↓
features

migration 003
    ↓
signals
signal_events

migration 004
    ↓
model_runs
```

Never manually modify production schema without recording the change as a migration.

---

# 19. Scripts

```text
scripts/
│
├── setup.sh
├── setup.ps1
├── seed_database.py
├── ingest_data.py
├── run_pipeline.py
├── run_ml.py
├── export_demo_data.py
└── health_check.py
```

Scripts should provide simple entry points for common workflows.

---

# 20. Tests

```text
tests/
│
├── unit/
│   ├── test_features.py
│   ├── test_scoring.py
│   ├── test_detection.py
│   ├── test_preprocessing.py
│   └── test_explanations.py
│
├── integration/
│   ├── test_database.py
│   ├── test_pipeline.py
│   └── test_signal_flow.py
│
├── api/
│   ├── test_health.py
│   ├── test_signals.py
│   ├── test_search.py
│   └── test_chat.py
│
└── fixtures/
    ├── sample_posts.json
    ├── sample_signals.json
    └── sample_features.json
```

---

# 21. Notebooks

```text
notebooks/
│
├── 01_data_exploration.ipynb
├── 02_feature_exploration.ipynb
├── 03_trend_detection_experiments.ipynb
├── 04_model_evaluation.ipynb
└── 05_demo_analysis.ipynb
```

Notebooks are for experimentation and analysis.

Core production logic should remain in `ml/`.

---

# 22. Configuration

```text
configs/
│
├── development.yaml
├── testing.yaml
├── production.yaml
└── demo.yaml
```

These files should contain non-secret configuration.

Secrets belong in environment variables or a secret-management system.

---

# 23. Documentation

```text
docs/
│
├── architecture/
│   ├── system-architecture.md
│   ├── data-flow.md
│   └── ml-architecture.md
│
├── api/
│   └── api-reference.md
│
├── database/
│   ├── schema.md
│   └── relationships.md
│
├── ml/
│   ├── feature-engineering.md
│   ├── detection-methodology.md
│   ├── scoring.md
│   └── evaluation.md
│
├── chatbot/
│   ├── architecture.md
│   ├── query-flow.md
│   └── guardrails.md
│
└── deployment/
    └── deployment-guide.md
```

---

# 24. Deployment

```text
deployment/
│
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── ml.Dockerfile
│
├── nginx/
│   └── nginx.conf
│
└── production/
    └── README.md
```

For the hackathon, Docker Compose may be sufficient.

A production deployment can later move to:

```text
Frontend
    ↓
Reverse Proxy
    ↓
Backend API
    ↓
PostgreSQL

ML Worker
    ↓
PostgreSQL
```

---

# 25. GitHub Actions

```text
.github/
│
├── workflows/
│   ├── ci.yml
│   ├── backend-tests.yml
│   └── frontend-checks.yml
│
├── ISSUE_TEMPLATE/
│   ├── bug_report.md
│   └── feature_request.md
│
└── pull_request_template.md
```

### CI should ideally run:

```text
Install dependencies
       ↓
Lint
       ↓
Unit tests
       ↓
API tests
       ↓
Frontend checks
       ↓
Build
```

---

# 26. Complete Final Tree

The repository should eventually look approximately like this:

```text
signalforge/
│
├── README.md
├── PROJECT_STRUCTURE.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Makefile
├── pyproject.toml
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── health.py
│   │   │       ├── signals.py
│   │   │       ├── communities.py
│   │   │       ├── search.py
│   │   │       ├── chat.py
│   │   │       └── ml.py
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── repositories/
│   │   └── utils/
│   ├── requirements.txt
│   └── requirements-dev.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── lib/
│   │   ├── types/
│   │   └── styles/
│   ├── package.json
│   └── tsconfig.json
│
├── ml/
│   ├── config/
│   ├── ingestion/
│   ├── preprocessing/
│   ├── features/
│   ├── detection/
│   ├── scoring/
│   ├── explanation/
│   ├── training/
│   ├── inference/
│   └── models/
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   ├── features/
│   ├── sample/
│   └── README.md
│
├── database/
│   ├── migrations/
│   ├── seeds/
│   ├── schema/
│   └── queries/
│
├── scripts/
│   ├── setup.sh
│   ├── setup.ps1
│   ├── seed_database.py
│   ├── ingest_data.py
│   ├── run_pipeline.py
│   ├── run_ml.py
│   ├── export_demo_data.py
│   └── health_check.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── api/
│   └── fixtures/
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_exploration.ipynb
│   ├── 03_trend_detection_experiments.ipynb
│   ├── 04_model_evaluation.ipynb
│   └── 05_demo_analysis.ipynb
│
├── configs/
│   ├── development.yaml
│   ├── testing.yaml
│   ├── production.yaml
│   └── demo.yaml
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── database/
│   ├── ml/
│   ├── chatbot/
│   └── deployment/
│
├── deployment/
│   ├── docker/
│   ├── nginx/
│   └── production/
│
└── .github/
    ├── workflows/
    │   ├── ci.yml
    │   ├── backend-tests.yml
    │   └── frontend-checks.yml
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   └── feature_request.md
    └── pull_request_template.md
```

---

# 27. Data Flow Across the Repository

The most important relationship is:

```text
data/
  ↓
ml/ingestion/
  ↓
ml/preprocessing/
  ↓
ml/features/
  ↓
ml/detection/
  ↓
ml/scoring/
  ↓
backend/app/services/
  ↓
database/
  ↓
backend/app/api/
  ↓
frontend/
```

The conversational layer sits above the same trusted backend:

```text
User
  ↓
frontend/components/chat/
  ↓
POST /api/v1/chat/query
  ↓
backend/app/api/v1/chat.py
  ↓
backend/app/services/chat_service.py
  ↓
backend/app/services/search_service.py
  ↓
PostgreSQL
  ↓
Structured results
  ↓
Explanation / LLM layer
  ↓
Chat response
```

---

# 28. Important Architectural Rule

Do **not** allow every component to access every other component.

Use clear boundaries:

```text
Frontend
   ↓
API
   ↓
Services
   ↓
Repositories / ML
   ↓
Database
```

and:

```text
Data
   ↓
ML pipeline
   ↓
Signals
   ↓
Database
```

This makes the system:

- easier to debug
- easier to test
- easier to demonstrate
- easier to scale
- easier for five team members to work on simultaneously

---

# 29. Hackathon MVP vs Full Structure

You do **not** need to implement every file immediately.

For the first working MVP, prioritize:

```text
backend/
frontend/
ml/
database/
data/sample/
tests/
README.md
docker-compose.yml
.env.example
```

Then add:

```text
chat/
docs/
deployment/
CI
advanced ML
```

as the core pipeline becomes stable.

The objective should be:

> **A small number of working modules connected end-to-end is more valuable than a large number of empty folders.**

---

# 30. Recommended Implementation Order

Build in this order:

```text
1. PostgreSQL
      ↓
2. Database schema + migrations
      ↓
3. Sample dataset
      ↓
4. Data ingestion
      ↓
5. Preprocessing
      ↓
6. Feature engineering
      ↓
7. Micro-trend detection
      ↓
8. Signal scoring
      ↓
9. Save signals to PostgreSQL
      ↓
10. FastAPI
      ↓
11. Dashboard
      ↓
12. Explain functionality
      ↓
13. Ask SignalForge
      ↓
14. Tests
      ↓
15. Docker + deployment
      ↓
16. Final polish/demo
```

This ordering minimizes integration risk and gives the team a usable system early.
