# SignalForge ML Plan

## Objective

Detect emerging micro-trends that demonstrate unusual growth,
novelty, engagement, persistence, or cross-community spread.

---

## Initial Approach

SignalForge will initially use classical ML, statistical
techniques, and pretrained language models rather than
requiring deep learning.

### Stage 1 — Semantic Clustering

Group related posts/topics based on semantic similarity.

Process:

- text preprocessing
- sentence embeddings
- clustering
- cluster validation

Initial approaches:

- Sentence Transformers
- HDBSCAN
- cosine similarity

---

### Stage 2 — Temporal Analysis

Measure how each semantic cluster changes over time.

Calculate:

- volume
- growth rate
- velocity
- acceleration
- rolling averages
- historical baseline

---

### Stage 3 — Anomaly Detection

Identify clusters demonstrating unusually high activity
relative to their historical behavior.

Potential approaches:

- statistical anomaly detection
- z-score
- rolling baseline deviation
- EWMA
- Isolation Forest

---

### Stage 4 — Signal Scoring

Combine multiple indicators into an overall signal score.

Potential score:

signal_score =
w1 * growth +
w2 * velocity +
w3 * novelty +
w4 * spread +
w5 * engagement +
w6 * persistence

Weights will be calibrated during experimentation.

---

### Stage 5 — Propagation Analysis

Determine whether emerging signals are spreading across
communities or platforms.

Calculate:

- community spread
- author spread
- cross-community activity
- cross-platform activity
- propagation score

Potential approach:

- NetworkX
- graph-based propagation analysis

---

### Stage 6 — Risk Classification

Classify high-value emerging signals based on their content
and behavior.

Potential outputs:

- risk type
- severity
- justification

Initial approach:

- LLM-based classification
- manual validation of flagged signals

---

### Stage 7 — Alert Generation

Generate explainable alerts for strong emerging signals.

Each alert should contain:

- topic/cluster
- signal score
- growth and velocity
- propagation information
- risk classification
- explanation
- source posts

Alerts must be traceable back to the original posts.

---

## Deep Learning

Deep learning is not required for the first MVP.

Pretrained models will initially be used primarily for
semantic embeddings.

Potential future uses:

- fine-tuned semantic embeddings
- multilingual understanding
- advanced topic discovery
- trend forecasting
- learned signal scoring
