# SignalForge

> **Micro-Trend Detection & Early Signal Intelligence Platform**

SignalForge is an end-to-end data intelligence platform designed to discover **emerging micro-trends before they become obvious at scale**. It collects and processes social/community signals, converts raw text and metadata into structured features, detects unusual patterns and growing communities, ranks potentially important signals, and presents the results through an interactive dashboard.

The project is designed for a hackathon-scale implementation while keeping a production-oriented architecture: **data ingestion → preprocessing → feature engineering → machine-learning detection → signal ranking → PostgreSQL persistence → API → dashboard → explainable conversational interface**.

---

## Table of Contents

- [1. Problem Statement](#1-problem-statement)
- [2. What SignalForge Does](#2-what-signalforge-does)
- [3. Key Features](#3-key-features)
- [4. System Architecture](#4-system-architecture)
- [5. Technology Stack](#5-technology-stack)
- [6. Machine Learning Approach](#6-machine-learning-approach)
- [7. Data Pipeline](#7-data-pipeline)
- [8. Signal Detection Workflow](#8-signal-detection-workflow)
- [9. Conversational Intelligence](#9-conversational-intelligence)
- [10. Database Design](#10-database-design)
- [11. Project Structure](#11-project-structure)
- [12. Local Development Setup](#12-local-development-setup)
- [13. Configuration](#13-configuration)
- [14. Running the Project](#14-running-the-project)
- [15. API Overview](#15-api-overview)
- [16. ML Training & Inference](#16-ml-training--inference)
- [17. Testing](#17-testing)
- [18. Security & Privacy](#18-security--privacy)
- [19. Reproducibility](#19-reproducibility)
- [20. Future Enhancements](#20-future-enhancements)
- [21. Team Workflow](#21-team-workflow)
- [22. Contributing](#22-contributing)
- [23. License](#23-license)

---

## 1. Problem Statement

The internet produces enormous volumes of conversations, posts, comments, keywords, topics, and community activity every day.

The challenge is not simply finding popular topics.

**The real challenge is identifying weak signals that are growing unusually fast, spreading across communities, or showing early evidence of becoming a meaningful trend.**

Traditional popularity-based systems tend to surface subjects that are already large. SignalForge instead focuses on the transition:

> **Weak signal → emerging pattern → growing micro-trend → potentially significant trend**

The system therefore prioritizes characteristics such as:

- sudden increases in activity
- acceleration over time
- unusual engagement
- cross-community spread
- semantic similarity between conversations
- novelty compared with historical activity
- persistence across multiple time windows
- confidence and explainability

---

## 2. What SignalForge Does

At a high level, SignalForge performs the following operations:

1. **Collects data**
   - Posts
   - Comments
   - Keywords
   - Engagement metrics
   - Community/source information
   - Timestamps
   - Optional metadata

2. **Cleans and normalizes the data**
   - Removes unusable records
   - Normalizes text
   - Handles missing values
   - Standardizes timestamps and metadata

3. **Extracts meaningful features**
   - Frequency
   - Growth rate
   - Engagement velocity
   - Novelty
   - Community diversity
   - Semantic representation
   - Temporal behavior

4. **Detects candidate micro-trends**
   - Statistical anomalies
   - Clusters
   - Rapidly growing topics
   - Cross-community patterns

5. **Ranks detected signals**
   - Combines multiple indicators into a signal score
   - Separates strong candidates from noise

6. **Stores results**
   - Raw/processed data
   - Features
   - Detected trends
   - Scores
   - Explanations
   - Model metadata

7. **Serves results through an API**

8. **Visualizes the intelligence through a dashboard**

9. **Provides an optional conversational layer**
   - "Ask SignalForge"
   - Explain buttons
   - Suggested questions
   - Natural-language dashboard queries

---

## 3. Key Features

### 3.1 Micro-Trend Detection

Identify topics or behavioral patterns that are showing meaningful growth even when their absolute volume is still relatively small.

### 3.2 Trend Velocity

Measure how quickly a signal is changing rather than looking only at its current size.

### 3.3 Cross-Community Spread

Identify signals that are appearing across multiple communities or sources.

Example:

> A topic appearing in 1 community may be niche.  
> The same topic appearing in 6 independent communities within a short period may represent a stronger emerging signal.

### 3.4 Novelty Detection

Compare new signals with historical activity to determine whether a topic is genuinely new or simply recurring.

### 3.5 Signal Ranking

Every detected candidate receives a composite score that can combine:

- growth
- velocity
- engagement
- novelty
- spread
- persistence
- model confidence

### 3.6 Explainable Results

SignalForge should not simply say:

> "This is trending."

It should explain:

> "This signal was ranked highly because its activity increased rapidly over the last two time windows, appeared across multiple communities, and showed above-baseline engagement."

### 3.7 Interactive Dashboard

The dashboard can provide:

- trend cards
- signal scores
- time-series charts
- community distribution
- trend clusters
- growth indicators
- filters
- search
- detailed signal pages

### 3.8 Ask SignalForge

A conversational interface allows users to ask questions about the detected signals.

Example queries:

- "What are the fastest-growing signals?"
- "Why is this signal important?"
- "Which signals are spreading across more than 5 communities?"
- "Show me unusual activity from the last 24 hours."
- "Explain this trend in simple terms."

### 3.9 Suggested Questions

The interface can dynamically suggest useful questions based on the current dashboard context.

### 3.10 Explain Buttons

Each important signal can expose an **Explain** action that translates model outputs into human-readable reasoning.

---

## 4. System Architecture

```text
                     ┌─────────────────────────┐
                     │       Data Sources      │
                     │                         │
                     │ Posts / Comments / APIs │
                     │ Public datasets / Feeds │
                     └────────────┬────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │      Data Ingestion      │
                     │                         │
                     │ Collect → Validate →     │
                     │ Normalize → Store        │
                     └────────────┬────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │  Processing & Features  │
                     │                         │
                     │ Cleaning / NLP / Time   │
                     │ Windows / Aggregation    │
                     └────────────┬────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │      ML Detection       │
                     │                         │
                     │ Clustering / Anomaly    │
                     │ Detection / Similarity  │
                     └────────────┬────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │     Signal Scoring      │
                     │                         │
                     │ Growth + Novelty +      │
                     │ Spread + Engagement     │
                     └────────────┬────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │       PostgreSQL        │
                     │                         │
                     │ Raw Data / Features /   │
                     │ Signals / Predictions   │
                     └────────────┬────────────┘
                                  │
                                  ▼
                     ┌─────────────────────────┐
                     │       Backend API       │
                     │                         │
                     │ REST endpoints / Auth / │
                     │ Query / Explain         │
                     └───────┬─────────┬───────┘
                             │         │
                 ┌───────────┘         └────────────┐
                 ▼                                  ▼
       ┌────────────────────┐             ┌────────────────────┐
       │    Web Dashboard   │             │ Conversational UI  │
       │                    │             │                    │
       │ Charts / Filters   │             │ Ask SignalForge    │
       │ Trend Explorer     │             │ Explain / Queries  │
       └────────────────────┘             └────────────────────┘
```

---

## 5. Technology Stack

The recommended stack is intentionally lightweight enough for a student/hackathon project while being extensible.

### Backend

- **Python**
- **FastAPI** for REST APIs
- **Pydantic** for request/response validation
- **SQLAlchemy** for database interaction
- **Alembic** for database migrations

### Data & ML

- **Pandas** for data manipulation
- **NumPy** for numerical processing
- **scikit-learn** for classical machine learning
- NLP/vectorization libraries as required
- Optional embedding model/API for semantic similarity

### Database

- **PostgreSQL**

PostgreSQL acts as the persistent source of truth for structured application data.

### Frontend

A modern React-based frontend can be used for:

- dashboard
- charts
- trend exploration
- filters
- signal detail views
- conversational UI

### Optional Conversational Layer

The chatbot can use an LLM/API layer for natural-language interpretation while keeping the actual data retrieval and scoring logic in the backend.

**Important:** the chatbot should not independently invent analytics. It should retrieve or transform information that comes from SignalForge's trusted backend.

### Development & Deployment

Recommended:

- Git + GitHub
- Docker / Docker Compose
- `.env` configuration
- pytest
- CI pipeline

---

## 6. Machine Learning Approach

SignalForge does **not require deep learning for the core micro-trend detector**.

For a three-week hackathon implementation, a classical ML/statistical pipeline is more practical, explainable, and easier to debug.

### 6.1 Feature Engineering

Candidate features may include:

| Feature | Purpose |
|---|---|
| `volume` | Amount of activity around a topic |
| `growth_rate` | How quickly activity is increasing |
| `acceleration` | Whether growth itself is increasing |
| `engagement_rate` | Relative interaction level |
| `community_count` | Number of communities where signal appears |
| `community_spread` | Degree of cross-community propagation |
| `novelty_score` | Difference from historical patterns |
| `persistence` | Whether signal survives multiple windows |
| `semantic_similarity` | Similarity between related content |
| `velocity` | Rate of signal movement over time |

### 6.2 Candidate Detection

A practical detector can combine several techniques:

#### A. Statistical / Temporal Detection

Use rolling windows and baseline comparisons to identify unusual growth.

For example:

```text
growth_rate =
    (current_window_volume - previous_window_volume)
    / max(previous_window_volume, 1)
```

A z-score or similar normalization can help identify activity that is unusually high relative to historical behavior.

#### B. Clustering

Group semantically similar posts/topics so that individual posts become larger coherent signals.

Possible algorithms:

- K-Means
- DBSCAN
- HDBSCAN (if included later)

#### C. Anomaly Detection

Use algorithms such as:

- Isolation Forest
- Local Outlier Factor
- statistical anomaly detection

to identify unusual feature combinations.

### 6.3 Composite Signal Score

A practical first version can combine normalized components:

```text
signal_score =
    w1 * growth_score
  + w2 * velocity_score
  + w3 * novelty_score
  + w4 * spread_score
  + w5 * engagement_score
  + w6 * persistence_score
```

The weights should be configurable rather than hard-coded throughout the application.

### 6.4 Why Not Start With PyTorch?

Deep learning can be valuable for advanced semantic modeling, but it should not be introduced merely because the project contains "AI."

The first working version should prioritize:

- reliable data
- useful features
- interpretable scoring
- measurable performance
- fast iteration

A transformer/embedding model can be introduced later if semantic clustering or similarity becomes a bottleneck.

---

## 7. Data Pipeline

The pipeline should separate **raw data** from **processed data**.

### Stage 1 — Collection

Data enters through ingestion scripts or APIs.

Each record should ideally contain:

```json
{
  "source": "example_source",
  "community": "example_community",
  "text": "example post text",
  "timestamp": "2026-08-11T10:30:00Z",
  "engagement": {
    "likes": 10,
    "comments": 4,
    "shares": 2
  }
}
```

### Stage 2 — Validation

Check:

- required fields
- timestamp validity
- text availability
- duplicate records
- malformed metadata

### Stage 3 — Cleaning

Typical operations:

- lowercase/normalize where appropriate
- remove irrelevant markup
- normalize whitespace
- handle URLs and mentions
- remove duplicate content
- handle missing values

### Stage 4 — Aggregation

Convert individual records into time-window statistics.

Example:

```text
5-minute window
15-minute window
1-hour window
6-hour window
24-hour window
```

The exact windows should be configurable.

### Stage 5 — Feature Extraction

Generate model-ready numerical and semantic features.

### Stage 6 — Detection

Run the micro-trend detection pipeline.

### Stage 7 — Persistence

Store:

- detected signals
- scores
- features
- timestamps
- explanations
- model/version metadata

---

## 8. Signal Detection Workflow

A typical execution looks like this:

```text
Raw Posts
   │
   ▼
Clean & Normalize
   │
   ▼
Group Related Content
   │
   ▼
Create Time Windows
   │
   ▼
Calculate Features
   │
   ├── Growth
   ├── Velocity
   ├── Engagement
   ├── Novelty
   ├── Community Spread
   └── Persistence
   │
   ▼
Detect Candidate Signals
   │
   ▼
Rank Candidates
   │
   ▼
Generate Explanation
   │
   ▼
Save to PostgreSQL
   │
   ▼
Expose Through API
   │
   ▼
Dashboard / Ask SignalForge
```

---

## 9. Conversational Intelligence

The chatbot is a **user-experience layer over the analytics platform**, not the primary analytics engine.

### 9.1 Ask SignalForge

Users can ask questions in natural language.

Example:

> "Show me signals spreading across more than 5 communities."

The backend can translate this into a structured query:

```text
community_count > 5
ORDER BY signal_score DESC
```

### 9.2 Explain Button

For a selected signal:

```text
Signal: Topic X

Why it was detected:
- Activity increased 184% in the latest window.
- It appeared in 7 communities.
- Engagement is 2.1× the historical baseline.
- The topic has low historical frequency.
```

### 9.3 Suggested Questions

Examples:

- "What is growing fastest?"
- "What signals are most novel?"
- "Which trends are spreading?"
- "Why is this signal ranked highly?"
- "What changed in the last 24 hours?"

### 9.4 Guardrails

The conversational layer should:

1. retrieve structured data from the backend
2. use controlled query operations
3. avoid direct arbitrary SQL generation
4. avoid exposing database credentials
5. clearly distinguish observed data from generated interpretation
6. refuse to fabricate missing metrics

---

## 10. Database Design

PostgreSQL should be treated as the central persistence layer.

A conceptual schema can contain:

### `sources`

Stores data source metadata.

```text
id
name
type
created_at
```

### `communities`

Stores source communities/topics.

```text
id
source_id
name
metadata
created_at
```

### `posts`

Stores normalized source records.

```text
id
source_id
community_id
external_id
text
timestamp
engagement
created_at
```

### `features`

Stores calculated model features.

```text
id
post_id / cluster_id
growth_score
velocity_score
novelty_score
engagement_score
spread_score
persistence_score
created_at
```

### `signals`

Stores detected micro-trends.

```text
id
label
description
signal_score
confidence
status
first_seen_at
last_seen_at
created_at
```

### `signal_communities`

Maps signals to communities.

```text
signal_id
community_id
mention_count
first_seen_at
last_seen_at
```

### `signal_events`

Stores signal evolution over time.

```text
id
signal_id
timestamp
volume
engagement
community_count
signal_score
```

### `model_runs`

Tracks ML executions.

```text
id
model_name
model_version
parameters
training_data_version
started_at
completed_at
metrics
```

This allows the system to answer not only:

> "What is the signal?"

but also:

> "When did it appear, how did it evolve, and which model generated this result?"

---

## 11. Project Structure

The complete proposed repository structure is documented separately in:

**`PROJECT_STRUCTURE.md`**

The repository should separate:

- application code
- ML code
- data processing
- database/migrations
- frontend
- tests
- configuration
- documentation
- scripts
- deployment

This separation prevents the project from becoming a single large Python/JavaScript codebase.

---

## 12. Local Development Setup

### Prerequisites

Install:

- Git
- Python 3.11+
- Node.js 20+ (if using a React/Next.js frontend)
- PostgreSQL 15+
- Docker Desktop (recommended)

Verify:

```bash
git --version
python --version
node --version
psql --version
docker --version
```

### Clone

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd signalforge
```

### Backend Environment

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**macOS/Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

### Environment Variables

Copy:

```bash
cp .env.example .env
```

Then configure the database and required API credentials.

Never commit `.env`.

---

## 13. Configuration

A typical `.env` file may contain:

```env
APP_ENV=development
APP_DEBUG=true

DATABASE_URL=postgresql://<username>:<password>@localhost:5432/signalforge

API_HOST=0.0.0.0
API_PORT=8000

MODEL_PATH=ml/models/

LLM_API_KEY=<optional>
```

Actual production credentials must never be committed to GitHub.

Use `.env.example` to document required variables without exposing secrets.

---

## 14. Running the Project

### Start PostgreSQL

Using local PostgreSQL:

```bash
sudo systemctl start postgresql
```

Or using Docker:

```bash
docker compose up -d postgres
```

### Run Migrations

```bash
alembic upgrade head
```

### Start Backend

```bash
uvicorn backend.app.main:app --reload
```

The API should then be available at:

```text
http://localhost:8000
```

FastAPI documentation:

```text
http://localhost:8000/docs
```

### Start Frontend

From the frontend directory:

```bash
npm install
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:3000
```

Exact ports can be changed through configuration.

---

## 15. API Overview

The API should expose resource-oriented endpoints.

### Health

```http
GET /api/v1/health
```

### Signals

```http
GET /api/v1/signals
GET /api/v1/signals/{signal_id}
```

### Signal Explanation

```http
GET /api/v1/signals/{signal_id}/explain
```

### Signal Timeline

```http
GET /api/v1/signals/{signal_id}/timeline
```

### Communities

```http
GET /api/v1/communities
```

### Search

```http
GET /api/v1/search?q=...
```

### Natural-Language Query

```http
POST /api/v1/chat/query
```

Example request:

```json
{
  "message": "Show signals spreading across more than 5 communities"
}
```

### ML Execution

```http
POST /api/v1/ml/run
```

In production, long-running ML jobs should preferably be executed asynchronously rather than blocking API requests.

---

## 16. ML Training & Inference

The ML layer should distinguish between:

### Training / Calibration

Used to:

- build baselines
- fit clustering models
- calibrate thresholds
- evaluate candidate detectors
- save model artifacts

### Inference

Used to:

- process new data
- calculate features
- detect signals
- score candidates
- persist predictions

A typical workflow:

```bash
python -m ml.training.train
```

Then:

```bash
python -m ml.inference.run
```

Model artifacts should be versioned and never silently overwritten.

Recommended metadata:

```text
model_name
model_version
training_data_version
feature_version
parameters
metrics
created_at
```

---

## 17. Testing

Testing should exist at multiple levels.

### Unit Tests

Test:

- feature calculations
- scoring
- normalization
- clustering helpers
- validation

Run:

```bash
pytest tests/unit
```

### Integration Tests

Test:

- PostgreSQL interaction
- API endpoints
- ML → database flow

Run:

```bash
pytest tests/integration
```

### API Tests

Verify:

- status codes
- validation
- pagination
- filters
- error handling

### ML Evaluation

Track metrics appropriate to the detection strategy.

For unsupervised detection, useful evaluation approaches include:

- precision of manually reviewed signals
- false-positive rate
- signal persistence
- ranking quality
- cluster coherence
- human evaluation

Because "micro-trend" detection is partly an exploratory task, evaluation should combine quantitative metrics with human review.

---

## 18. Security & Privacy

The project should follow basic security principles from the beginning.

### Never Commit Secrets

Do not commit:

- API keys
- database passwords
- access tokens
- private credentials
- production `.env` files

### Input Validation

All API inputs should be validated using typed schemas.

### Database Security

Use:

- parameterized queries
- least-privilege database users
- controlled migrations

### LLM Security

The conversational layer should not have unrestricted database access.

Instead:

```text
User question
     ↓
Intent / parameter extraction
     ↓
Allowed backend query
     ↓
Structured result
     ↓
Natural-language response
```

---

## 19. Reproducibility

A major goal is that another developer can clone the repository and reproduce the system.

The repository should therefore contain:

- dependency files
- `.env.example`
- database migrations
- seed/sample data
- model configuration
- reproducible scripts
- documented commands
- test suite
- versioned model metadata

For demos, include a small sanitized/sample dataset so that the dashboard can be demonstrated without depending entirely on live external sources.

---

## 20. Future Enhancements

Potential future improvements include:

### Advanced NLP

- transformer embeddings
- semantic topic discovery
- multilingual trend detection
- entity linking
- sentiment/emotion signals

### Advanced Detection

- temporal graph analysis
- graph-based propagation detection
- change-point detection
- online clustering
- streaming inference
- probabilistic trend forecasting

### Product Features

- personalized watchlists
- alerts
- email/Slack notifications
- saved searches
- trend comparison
- signal history
- anomaly maps
- community influence graphs

### Conversational Features

- multi-turn contextual analysis
- natural-language chart generation
- automatic report generation
- conversational drill-down
- "why did this change?" analysis

---

## 21. Team Workflow

For a five-person implementation team, a clean ownership model is recommended:

### Member 1 — ML / Data Science

Owns:

- feature engineering
- detection algorithms
- scoring
- model evaluation

### Member 2 — Backend

Owns:

- FastAPI
- API contracts
- business logic
- integration

### Member 3 — Database / Data Engineering

Owns:

- PostgreSQL
- schema
- migrations
- ingestion
- data pipelines

### Member 4 — Frontend

Owns:

- dashboard
- charts
- filtering
- signal detail pages

### Member 5 — AI UX / Integration / DevOps

Owns:

- Ask SignalForge
- explainability
- frontend/backend integration
- Docker/CI
- demo workflow

These roles can overlap, but each major subsystem should have a clear owner.

---

## 22. Contributing

1. Create a feature branch:

```bash
git checkout -b feature/your-feature
```

2. Make focused changes.

3. Run tests:

```bash
pytest
```

4. Verify formatting/linting.

5. Commit with a meaningful message:

```bash
git commit -m "feat: add signal velocity scoring"
```

6. Push:

```bash
git push origin feature/your-feature
```

7. Open a Pull Request.

### Recommended Commit Prefixes

```text
feat:     new functionality
fix:      bug fix
refactor: code restructuring
docs:     documentation
test:     tests
chore:    tooling/configuration
ml:       machine-learning changes
data:     data pipeline changes
ui:       frontend changes
```

---

## 23. License

Choose and add the appropriate open-source license before publishing the repository.

For a hackathon project, the repository should explicitly state:

- project ownership
- team members
- data-source terms
- third-party API terms
- model/API attribution requirements

---

## Project Status

**Status:** Active development / Hackathon prototype

SignalForge is being developed as a modular prototype with the goal of demonstrating a complete micro-trend intelligence workflow rather than only an isolated machine-learning model.

The core principle is:

> **Detect early. Explain clearly. Explore naturally.**

---

## Acknowledgements

Built as a collaborative project for the **SignalForge micro-trend detection challenge**.

If you use external datasets, APIs, models, libraries, or research papers, add their attribution here before publishing the final repository.
