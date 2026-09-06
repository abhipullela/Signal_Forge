"""Risk classification and human-readable evidence explanations."""

from __future__ import annotations

import re

import numpy as np
import pandas as pd

from ml.scoring.normalizer import clamp, normalize_feature

SIGNAL_THRESHOLD = 20.0
MEDIUM_RISK_THRESHOLD = 45.0
HIGH_RISK_THRESHOLD = 70.0
REPRESENTATIVE_POSTS = 5

RISK_KEYWORDS = {
    "misinformation": [
        "fake", "false", "rumor", "rumour", "misinformation",
        "disinformation", "hoax", "fabricated", "unverified",
        "conspiracy", "lie", "lies", "scam", "fraud",
    ],
    "safety": [
        "danger", "dangerous", "unsafe", "warning", "harm",
        "harmful", "injury", "injured", "accident", "risk",
        "hazard", "toxic", "contaminated",
    ],
    "health": [
        "medicine", "medical", "drug", "disease", "symptom",
        "treatment", "hospital", "doctor", "health", "vaccine", "vaccination", "antivaxxer", "anti-vax", "side effect", "infection", "cancer",
    ],
    "security": [
        "hack", "hacked", "hacking", "breach", "leak", "stolen",
        "malware", "virus", "phishing", "attack", "security",
        "exploit", "vulnerability",
    ],
    "financial": [
        "money", "bank", "payment", "price", "stock", "market",
        "investment", "investor", "financial", "loss", "fraud", "scam",
    ],
    "reputational": [
        "boycott", "lawsuit", "complaint", "controversy", "backlash",
        "corruption", "abuse", "bad service", "terrible service",
        "customer complaint", "discrimination",
    ],
}


def normalize_text(value) -> str:
    if pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value).lower()).strip()


def _keyword_pattern(keyword: str) -> re.Pattern:
    """Match whole words/phrases rather than arbitrary substrings."""
    parts = [re.escape(part) for part in keyword.split()]
    pattern = r"\b" + r"\s+".join(parts) + r"\b"
    return re.compile(pattern, re.IGNORECASE)


def detect_risk_keywords(text: str):
    text = normalize_text(text)
    category_hits = {}

    for category, keywords in RISK_KEYWORDS.items():
        hits = [
            keyword
            for keyword in keywords
            if _keyword_pattern(keyword).search(text)
        ]
        if hits:
            category_hits[category] = hits

    if not category_hits:
        return "none", [], 0

    category, hits = max(
        category_hits.items(),
        key=lambda item: len(item[1]),
    )
    return category, hits, len(hits)


def build_representative_text(posts: pd.DataFrame) -> pd.DataFrame:
    posts = posts.copy()
    posts["cluster_id"] = pd.to_numeric(posts["cluster_id"], errors="coerce")
    posts = posts.dropna(subset=["cluster_id"]).copy()
    posts["cluster_id"] = posts["cluster_id"].astype(int)

    title_col = "clean_title" if "clean_title" in posts.columns else (
        "title" if "title" in posts.columns else None
    )
    content_col = "clean_content" if "clean_content" in posts.columns else (
        "content" if "content" in posts.columns else None
    )

    posts["risk_title"] = posts[title_col].map(normalize_text) if title_col else ""
    posts["risk_content"] = posts[content_col].map(normalize_text) if content_col else ""
    posts["risk_text"] = (posts["risk_title"] + " " + posts["risk_content"]).str.strip()

    posts["published_at"] = pd.to_datetime(posts.get("published_at"), errors="coerce", utc=True)
    posts["engagement_value"] = pd.to_numeric(posts.get("score", 0), errors="coerce").fillna(0.0)
    posts["text_length"] = posts["risk_text"].str.len()
    posts = posts[posts["risk_text"].str.len() > 0].copy()
    posts = posts.sort_values(
        ["cluster_id", "published_at", "engagement_value", "text_length"],
        ascending=[True, False, False, False],
    )
    return (
        posts.groupby("cluster_id", sort=False)
        .head(REPRESENTATIVE_POSTS)
        .sort_values(["cluster_id", "published_at"], ascending=[True, False])
        .groupby("cluster_id")["risk_text"]
        .apply(" | ".join)
        .rename("representative_text")
        .reset_index()
    )


def calculate_behavioral_score(row) -> float:
    temporal = clamp(row.get("signal_score", row.get("temporal_signal_score", 0)))
    propagation = clamp(row.get("propagation_score", 0))
    anomaly = normalize_feature(row.get("anomaly", 0), 10)
    persistence = normalize_feature(row.get("persistence", 0), 5)
    communities = normalize_feature(row.get("communities", 1), 5)
    recent_spread = normalize_feature(row.get("recent_community_max", 0), 5)

    return round(clamp(
        0.35 * temporal
        + 0.25 * propagation
        + 0.15 * anomaly
        + 0.15 * persistence
        + 0.05 * communities
        + 0.05 * recent_spread
    ), 2)


def calculate_content_score(row) -> float:
    matches = int(row.get("keyword_score", 0))
    if matches <= 0:
        return 0.0
    if matches == 1:
        return 30.0
    if matches == 2:
        return 60.0
    return 85.0


def calculate_final_risk(row) -> float:
    return round(clamp(
        0.65 * float(row.get("behavioral_risk_score", 0))
        + 0.35 * float(row.get("content_risk_score", 0))
    ), 2)


def classify_risk_type(row) -> str:
    keyword_type = row.get("keyword_risk_type", "none")
    if keyword_type != "none" and int(row.get("keyword_score", 0)) > 0:
        return str(keyword_type)
    return "general"


def classify_severity(row) -> str:
    signal = float(row.get("signal_score", row.get("temporal_signal_score", 0)))
    risk_score = float(row.get("risk_score", 0))
    keyword_score = int(row.get("keyword_score", 0))
    propagation = float(row.get("propagation_score", 0))
    risk_type = str(row.get("risk_type", "general"))

    if signal < SIGNAL_THRESHOLD:
        return "LOW"
    if (
        risk_score >= HIGH_RISK_THRESHOLD
        and (keyword_score >= 2 or propagation >= 60)
        and risk_type != "general"
    ):
        return "HIGH"
    if risk_score >= MEDIUM_RISK_THRESHOLD:
        return "MEDIUM"
    return "LOW"


def calculate_confidence(row) -> float:
    behavioral = float(row.get("behavioral_risk_score", 0))
    keyword_evidence = normalize_feature(float(row.get("keyword_score", 0)), 3)
    propagation = float(row.get("propagation_score", 0))
    return round(clamp(
        0.50 * behavioral + 0.25 * keyword_evidence + 0.25 * propagation
    ), 2)


def generate_justification(row) -> str:
    risk_type = str(row.get("risk_type", "general"))
    severity = str(row.get("severity", "LOW"))
    risk_score = float(row.get("risk_score", 0))
    signal = float(row.get("signal_score", row.get("temporal_signal_score", 0)))
    propagation = float(row.get("propagation_score", 0))
    persistence = float(row.get("persistence", 0))
    communities = int(float(row.get("communities", 1)))
    keyword_hits = str(row.get("keyword_hits", ""))

    reasons = []
    if signal >= 60:
        reasons.append(f"strong temporal signal ({signal:.1f}/100)")
    elif signal >= 40:
        reasons.append(f"moderate temporal signal ({signal:.1f}/100)")
    elif signal >= 20:
        reasons.append(f"emerging temporal activity ({signal:.1f}/100)")

    if propagation >= 60:
        reasons.append(f"strong cross-community propagation ({propagation:.1f}/100)")
    elif propagation >= 20:
        reasons.append(f"cross-community propagation ({propagation:.1f}/100)")
    if communities > 1:
        reasons.append(f"activity across {communities} communities")
    if persistence >= 3:
        reasons.append(f"persistent activity across {persistence:.0f} windows")
    elif persistence > 0:
        reasons.append(f"activity persisted for {persistence:.0f} windows")
    if keyword_hits:
        content_score = float(row.get("content_risk_score", 0))
        reasons.append(
            f"content indicators: {keyword_hits} (content score {content_score:.1f}/100)"
        )
    if not reasons:
        reasons.append("limited behavioral and content-based evidence")

    return (
        f"{severity} {risk_type} signal (risk score {risk_score:.1f}/100): "
        + "; ".join(reasons)
        + "."
    )


def classify_risk(
    temporal: pd.DataFrame,
    propagation: pd.DataFrame,
    posts: pd.DataFrame,
) -> pd.DataFrame:
    """Merge evidence and return one risk classification per cluster."""
    if temporal.empty:
        return pd.DataFrame()

    df = temporal.copy()
    df["cluster_id"] = pd.to_numeric(df["cluster_id"], errors="coerce")
    propagation = propagation.copy()
    propagation["cluster_id"] = pd.to_numeric(propagation["cluster_id"], errors="coerce")

    df = df.dropna(subset=["cluster_id"]).copy()
    propagation = propagation.dropna(subset=["cluster_id"]).copy()
    df["cluster_id"] = df["cluster_id"].astype(int)
    propagation["cluster_id"] = propagation["cluster_id"].astype(int)

    df = df.merge(propagation, on="cluster_id", how="left", suffixes=("", "_prop"))
    representative = build_representative_text(posts)
    df = df.merge(representative, on="cluster_id", how="left")
    df["representative_text"] = df["representative_text"].fillna("")

    risk_results = df["representative_text"].map(detect_risk_keywords)
    df["keyword_risk_type"] = risk_results.map(lambda x: x[0])
    df["keyword_hits"] = risk_results.map(lambda x: ", ".join(x[1]))
    df["keyword_score"] = risk_results.map(lambda x: x[2])

    numeric_columns = [
        "signal_score", "propagation_score", "growth_rate", "velocity",
        "acceleration", "engagement", "anomaly", "persistence",
        "communities", "cross_community", "cross_source",
        "community_spread_rate", "propagation_velocity",
        "recent_community_max", "recent_community_growth",
        "recent_windows_active", "source_count",
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df["behavioral_risk_score"] = df.apply(calculate_behavioral_score, axis=1)
    df["content_risk_score"] = df.apply(calculate_content_score, axis=1)
    df["risk_score"] = df.apply(calculate_final_risk, axis=1)
    df["risk_type"] = df.apply(classify_risk_type, axis=1)
    df["severity"] = df.apply(classify_severity, axis=1)
    df["risk_confidence"] = df.apply(calculate_confidence, axis=1)
    df["justification"] = df.apply(generate_justification, axis=1)

    columns = [
        "cluster_id", "risk_type", "severity", "risk_score", "risk_confidence",
        "justification", "keyword_risk_type", "keyword_hits", "keyword_score",
        "content_risk_score", "behavioral_risk_score", "signal_score",
        "growth_rate", "velocity", "acceleration", "engagement", "anomaly",
        "persistence", "communities", "cross_community", "cross_source",
        "community_spread_rate", "propagation_velocity", "recent_community_max",
        "recent_community_growth", "recent_windows_active", "propagation_score",
        "representative_text",
    ]
    return (
        df[[c for c in columns if c in df.columns]]
        .sort_values(["risk_score", "signal_score"], ascending=False)
        .reset_index(drop=True)
    )
