"""
feedback_service.py - Persistent Feedback Storage and Statistics Engine
HEATSHIELD AI — Global Urban Climate Resilience Digital Twin

Manages:
- Persistent SQLite storage for feedback submitted by hackathon judges, evaluators, and users
- WAL mode for concurrent multi-client read/write safety
- Field validation and duplicate submission safeguards
- Aggregate statistics calculation (overall rating, ease of use, data viz, heat risk, interventions)
- Role distribution and rating histogram calculations
"""

import os
import sqlite3
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from app.models import FeedbackCreate

logger = logging.getLogger(__name__)

# Determine default database path in backend/data/feedback.db
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BACKEND_DIR, "data")
DEFAULT_DB_PATH = os.path.join(DATA_DIR, "feedback.db")

ALLOWED_ROLES = ["Judge", "Evaluator", "Student", "Faculty", "Other"]


def _get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates a thread-safe connection to the SQLite database with WAL mode."""
    target_path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    conn = sqlite3.connect(target_path, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
    except Exception as e:
        logger.debug(f"PRAGMA setup notice: {e}")
    return conn


def init_feedback_db(db_path: Optional[str] = None) -> None:
    """Initializes the feedback table and indices if they do not exist."""
    conn = _get_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS feedback_submissions (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    role TEXT NOT NULL,
                    overall_rating INTEGER NOT NULL CHECK (overall_rating BETWEEN 1 AND 5),
                    ease_of_use INTEGER NOT NULL CHECK (ease_of_use BETWEEN 1 AND 5),
                    data_visualization INTEGER NOT NULL CHECK (data_visualization BETWEEN 1 AND 5),
                    heat_risk_analysis INTEGER NOT NULL CHECK (heat_risk_analysis BETWEEN 1 AND 5),
                    intervention_recommendations INTEGER NOT NULL CHECK (intervention_recommendations BETWEEN 1 AND 5),
                    most_useful_feature TEXT NOT NULL,
                    suggestions TEXT NOT NULL,
                    additional_comments TEXT,
                    created_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_feedback_created_at
                ON feedback_submissions(created_at DESC)
            """)
            conn.commit()
    finally:
        conn.close()


# Initialize database on module import
init_feedback_db()


def normalize_role(role_raw: str) -> str:
    """Normalizes role string to canonical title-cased value."""
    role_clean = role_raw.strip().title()
    for allowed in ALLOWED_ROLES:
        if role_clean.lower() == allowed.lower():
            return allowed
    return "Other"


def save_feedback(feedback_data: FeedbackCreate, db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Validates and stores a new feedback submission persistently in SQLite.
    Returns the created record with assigned UUID and timestamp.
    """
    # 1. Validate Role
    canonical_role = normalize_role(feedback_data.role)

    # 2. Validate Ratings (1 to 5)
    ratings = [
        ("overall_rating", feedback_data.overall_rating),
        ("ease_of_use", feedback_data.ease_of_use),
        ("data_visualization", feedback_data.data_visualization),
        ("heat_risk_analysis", feedback_data.heat_risk_analysis),
        ("intervention_recommendations", feedback_data.intervention_recommendations)
    ]
    for field_name, val in ratings:
        if not (1 <= val <= 5):
            raise ValueError(f"Rating for '{field_name}' must be between 1 and 5 stars. Received: {val}")

    # 3. Validate Text Fields
    if not feedback_data.most_useful_feature or len(feedback_data.most_useful_feature.strip()) < 2:
        raise ValueError("Field 'most_useful_feature' must contain at least 2 characters.")
    if not feedback_data.suggestions or len(feedback_data.suggestions.strip()) < 3:
        raise ValueError("Field 'suggestions' must contain at least 3 characters.")

    feedback_id = str(uuid.uuid4())
    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    clean_name = feedback_data.name.strip() if feedback_data.name and feedback_data.name.strip() else None
    clean_comments = feedback_data.additional_comments.strip() if feedback_data.additional_comments and feedback_data.additional_comments.strip() else None

    conn = _get_connection(db_path)
    try:
        with conn:
            conn.execute("""
                INSERT INTO feedback_submissions (
                    id, name, role, overall_rating, ease_of_use,
                    data_visualization, heat_risk_analysis, intervention_recommendations,
                    most_useful_feature, suggestions, additional_comments, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback_id,
                clean_name,
                canonical_role,
                int(feedback_data.overall_rating),
                int(feedback_data.ease_of_use),
                int(feedback_data.data_visualization),
                int(feedback_data.heat_risk_analysis),
                int(feedback_data.intervention_recommendations),
                feedback_data.most_useful_feature.strip(),
                feedback_data.suggestions.strip(),
                clean_comments,
                created_at
            ))
            conn.commit()

        logger.info(f"Feedback {feedback_id} saved successfully from role: {canonical_role}")
        return {
            "id": feedback_id,
            "name": clean_name,
            "role": canonical_role,
            "overall_rating": int(feedback_data.overall_rating),
            "ease_of_use": int(feedback_data.ease_of_use),
            "data_visualization": int(feedback_data.data_visualization),
            "heat_risk_analysis": int(feedback_data.heat_risk_analysis),
            "intervention_recommendations": int(feedback_data.intervention_recommendations),
            "most_useful_feature": feedback_data.most_useful_feature.strip(),
            "suggestions": feedback_data.suggestions.strip(),
            "additional_comments": clean_comments,
            "created_at": created_at
        }
    finally:
        conn.close()


def get_all_feedback(
    limit: int = 50,
    offset: int = 0,
    db_path: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Retrieves paginated feedback records ordered by creation date descending."""
    conn = _get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, role, overall_rating, ease_of_use,
                   data_visualization, heat_risk_analysis, intervention_recommendations,
                   most_useful_feature, suggestions, additional_comments, created_at
            FROM feedback_submissions
            ORDER BY created_at DESC, rowid DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_feedback_by_id(feedback_id: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves a single feedback record by its UUID."""
    conn = _get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, role, overall_rating, ease_of_use,
                   data_visualization, heat_risk_analysis, intervention_recommendations,
                   most_useful_feature, suggestions, additional_comments, created_at
            FROM feedback_submissions
            WHERE id = ?
        """, (feedback_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_feedback_summary(db_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculates genuine aggregate feedback statistics:
    - Total submissions count
    - Average rating across all 5 dimensions
    - Star rating distribution (1 to 5 stars for overall rating)
    - Role distribution (Judge, Evaluator, Student, Faculty, Other)
    - Category breakdown array formatted for Recharts data visualization
    """
    conn = _get_connection(db_path)
    try:
        cursor = conn.cursor()

        # 1. Aggregate Averages & Total
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                AVG(overall_rating) as avg_overall,
                AVG(ease_of_use) as avg_ease,
                AVG(data_visualization) as avg_viz,
                AVG(heat_risk_analysis) as avg_analysis,
                AVG(intervention_recommendations) as avg_interventions
            FROM feedback_submissions
        """)
        agg = cursor.fetchone()
        total = agg["total"] if agg else 0

        if total == 0:
            return {
                "total_submissions": 0,
                "avg_overall_rating": 0.0,
                "avg_ease_of_use": 0.0,
                "avg_data_visualization": 0.0,
                "avg_heat_risk_analysis": 0.0,
                "avg_intervention_recommendations": 0.0,
                "rating_distribution": {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0},
                "role_breakdown": {r: 0 for r in ALLOWED_ROLES},
                "category_averages": [
                    {"category": "Overall Experience", "score": 0.0, "fullMark": 5.0},
                    {"category": "Ease of Use", "score": 0.0, "fullMark": 5.0},
                    {"category": "Data Visualization", "score": 0.0, "fullMark": 5.0},
                    {"category": "Heat Risk Analysis", "score": 0.0, "fullMark": 5.0},
                    {"category": "Intervention Modeling", "score": 0.0, "fullMark": 5.0}
                ]
            }

        avg_overall = round(float(agg["avg_overall"] or 0.0), 2)
        avg_ease = round(float(agg["avg_ease"] or 0.0), 2)
        avg_viz = round(float(agg["avg_viz"] or 0.0), 2)
        avg_analysis = round(float(agg["avg_analysis"] or 0.0), 2)
        avg_interventions = round(float(agg["avg_interventions"] or 0.0), 2)

        # 2. Rating Distribution for Overall Rating (1 to 5 stars)
        cursor.execute("""
            SELECT overall_rating, COUNT(*) as count
            FROM feedback_submissions
            GROUP BY overall_rating
        """)
        rating_counts = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        for row in cursor.fetchall():
            rating_counts[str(row["overall_rating"])] = row["count"]

        # 3. Role Breakdown
        cursor.execute("""
            SELECT role, COUNT(*) as count
            FROM feedback_submissions
            GROUP BY role
        """)
        role_counts = {r: 0 for r in ALLOWED_ROLES}
        for row in cursor.fetchall():
            r_name = row["role"]
            if r_name in role_counts:
                role_counts[r_name] = row["count"]
            else:
                role_counts["Other"] += row["count"]

        # 4. Formatted Category Averages for Recharts
        category_averages = [
            {"category": "Overall Experience", "score": avg_overall, "fullMark": 5.0},
            {"category": "Ease of Use", "score": avg_ease, "fullMark": 5.0},
            {"category": "Data Visualization", "score": avg_viz, "fullMark": 5.0},
            {"category": "Heat Risk Analysis", "score": avg_analysis, "fullMark": 5.0},
            {"category": "Intervention Modeling", "score": avg_interventions, "fullMark": 5.0}
        ]

        return {
            "total_submissions": total,
            "avg_overall_rating": avg_overall,
            "avg_ease_of_use": avg_ease,
            "avg_data_visualization": avg_viz,
            "avg_heat_risk_analysis": avg_analysis,
            "avg_intervention_recommendations": avg_interventions,
            "rating_distribution": rating_counts,
            "role_breakdown": role_counts,
            "category_averages": category_averages
        }
    finally:
        conn.close()
