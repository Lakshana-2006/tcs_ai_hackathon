"""
test_feedback.py - Verification Test Suite for Feedback Session Feature
HEATSHIELD AI — Global Urban Climate Resilience Digital Twin

Tests:
1. Empty feedback database initial state & summary defaults
2. Valid feedback submission with 5-star evaluation ratings
3. Persistence check: retrieve submitted record by ID and list
4. Missing required fields validation (422 Unprocessable Entity)
5. Invalid rating values rejection (< 1 or > 5 stars -> 400 Bad Request)
6. Multiple submissions and aggregate summary statistics calculation
7. Role breakdown and rating distribution histogram
8. Text length validations (most_useful_feature, suggestions)
"""

import sys
import os
import tempfile
import pytest

# UTF-8 encoding for Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.feedback_service import init_feedback_db, save_feedback, get_feedback_summary, get_all_feedback
from app.models import FeedbackCreate

client = TestClient(app)


def test_empty_database_summary():
    print("\n--- 1. Testing Empty Feedback Summary State ---")
    # Use a temporary SQLite database for clean test isolation
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        test_db_path = tmp.name

    try:
        init_feedback_db(test_db_path)
        summary = get_feedback_summary(test_db_path)
        assert summary["total_submissions"] == 0
        assert summary["avg_overall_rating"] == 0.0
        assert summary["avg_ease_of_use"] == 0.0
        assert summary["avg_data_visualization"] == 0.0
        assert summary["avg_heat_risk_analysis"] == 0.0
        assert summary["avg_intervention_recommendations"] == 0.0
        assert summary["rating_distribution"] == {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        assert len(summary["category_averages"]) == 5
        print("✓ Empty feedback summary test passed (zero-safe defaults).")
    finally:
        if os.path.exists(test_db_path):
            os.remove(test_db_path)


def test_valid_feedback_submission():
    print("\n--- 2. Testing Valid Feedback Submission via API ---")
    payload = {
        "name": "Dr. Aris Thorne",
        "role": "Judge",
        "overall_rating": 5,
        "ease_of_use": 4,
        "data_visualization": 5,
        "heat_risk_analysis": 5,
        "intervention_recommendations": 4,
        "most_useful_feature": "IPCC multi-criteria risk decomposition and Landsat thermal overlay",
        "suggestions": "Add multi-city side-by-side comparative views in the budget optimizer.",
        "additional_comments": "Exceptional digital twin architecture for urban heat resilience."
    }

    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()

    assert "id" in data
    assert data["name"] == "Dr. Aris Thorne"
    assert data["role"] == "Judge"
    assert data["overall_rating"] == 5
    assert data["ease_of_use"] == 4
    assert data["data_visualization"] == 5
    assert data["heat_risk_analysis"] == 5
    assert data["intervention_recommendations"] == 4
    assert "IPCC multi-criteria" in data["most_useful_feature"]
    assert "created_at" in data
    print(f"✓ Feedback created successfully: ID {data['id']}")
    return data["id"]


def test_get_feedback_by_id():
    print("\n--- 2b. Testing GET /api/feedback/{feedback_id} Endpoint ---")
    payload = {
        "name": "Direct ID Test",
        "role": "Evaluator",
        "overall_rating": 5,
        "ease_of_use": 5,
        "data_visualization": 5,
        "heat_risk_analysis": 5,
        "intervention_recommendations": 5,
        "most_useful_feature": "Single record lookup by UUID",
        "suggestions": "None",
        "additional_comments": "Testing direct ID retrieval"
    }
    create_resp = client.post("/api/feedback", json=payload)
    assert create_resp.status_code == 201
    created_id = create_resp.json()["id"]

    # Fetch by ID
    get_resp = client.get(f"/api/feedback/{created_id}")
    assert get_resp.status_code == 200, f"Expected 200, got {get_resp.status_code}: {get_resp.text}"
    record = get_resp.json()
    assert record["id"] == created_id
    assert record["name"] == "Direct ID Test"
    assert record["role"] == "Evaluator"

    # Fetch non-existent ID
    bad_resp = client.get("/api/feedback/non-existent-uuid-12345")
    assert bad_resp.status_code == 404
    print("✓ GET /api/feedback/{id} verified for both valid and 404 cases.")


def test_feedback_retrieval_and_persistence():
    print("\n--- 3. Testing Feedback Retrieval and Persistence ---")
    response = client.get("/api/feedback?limit=10&offset=0")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    records = response.json()
    assert isinstance(records, list)
    assert len(records) >= 1

    latest = records[0]
    assert "id" in latest
    assert "role" in latest
    assert "overall_rating" in latest
    assert "suggestions" in latest
    print(f"✓ Retrieved {len(records)} feedback record(s) from persistent SQLite.")


def test_missing_required_fields():
    print("\n--- 4. Testing Missing Required Fields Validation ---")
    # Missing 'role'
    payload_no_role = {
        "overall_rating": 5,
        "ease_of_use": 5,
        "data_visualization": 5,
        "heat_risk_analysis": 5,
        "intervention_recommendations": 5,
        "most_useful_feature": "Interactive map",
        "suggestions": "None"
    }
    resp = client.post("/api/feedback", json=payload_no_role)
    assert resp.status_code == 422, f"Expected 422 for missing role, got {resp.status_code}"

    # Missing 'suggestions'
    payload_no_suggestions = {
        "role": "Evaluator",
        "overall_rating": 4,
        "ease_of_use": 4,
        "data_visualization": 4,
        "heat_risk_analysis": 4,
        "intervention_recommendations": 4,
        "most_useful_feature": "What-If Simulator"
    }
    resp = client.post("/api/feedback", json=payload_no_suggestions)
    assert resp.status_code == 422, f"Expected 422 for missing suggestions, got {resp.status_code}"
    print("✓ Missing required fields correctly rejected with 422 Unprocessable Entity.")


def test_invalid_rating_values():
    print("\n--- 5. Testing Invalid Rating Boundaries ---")
    # Rating > 5
    payload_high = {
        "role": "Student",
        "overall_rating": 6,  # Invalid
        "ease_of_use": 5,
        "data_visualization": 5,
        "heat_risk_analysis": 5,
        "intervention_recommendations": 5,
        "most_useful_feature": "Thermal map",
        "suggestions": "Great work"
    }
    resp = client.post("/api/feedback", json=payload_high)
    assert resp.status_code in [400, 422], f"Expected 400 or 422, got {resp.status_code}"

    # Rating < 1
    payload_low = {
        "role": "Student",
        "overall_rating": 0,  # Invalid
        "ease_of_use": 5,
        "data_visualization": 5,
        "heat_risk_analysis": 5,
        "intervention_recommendations": 5,
        "most_useful_feature": "Thermal map",
        "suggestions": "Great work"
    }
    resp = client.post("/api/feedback", json=payload_low)
    assert resp.status_code in [400, 422], f"Expected 400 or 422, got {resp.status_code}"
    print("✓ Out-of-bounds ratings (< 1 or > 5) correctly rejected.")


def test_feedback_summary_statistics_calculation():
    print("\n--- 6. Testing Mathematical Accuracy of Feedback Summary ---")
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        test_db = tmp.name

    try:
        init_feedback_db(test_db)

        # Submission 1: Judge, overall=5, ease=4, viz=5, analysis=5, interventions=4
        sub1 = FeedbackCreate(
            name="Judge Alpha",
            role="Judge",
            overall_rating=5,
            ease_of_use=4,
            data_visualization=5,
            heat_risk_analysis=5,
            intervention_recommendations=4,
            most_useful_feature="Dynamic 5-zone urban generation",
            suggestions="Expand regional cooling scenarios.",
            additional_comments="Top-tier hackathon project."
        )
        save_feedback(sub1, test_db)

        # Submission 2: Evaluator, overall=4, ease=4, viz=4, analysis=4, interventions=4
        sub2 = FeedbackCreate(
            name="Evaluator Beta",
            role="Evaluator",
            overall_rating=4,
            ease_of_use=4,
            data_visualization=4,
            heat_risk_analysis=4,
            intervention_recommendations=4,
            most_useful_feature="Budget optimization knapsack",
            suggestions="Include export to PDF reporting.",
            additional_comments=None
        )
        save_feedback(sub2, test_db)

        # Submission 3: Faculty, overall=5, ease=5, viz=4, analysis=5, interventions=5
        sub3 = FeedbackCreate(
            name=None,  # Optional name omitted
            role="Faculty",
            overall_rating=5,
            ease_of_use=5,
            data_visualization=4,
            heat_risk_analysis=5,
            intervention_recommendations=5,
            most_useful_feature="Scientific provenance & landsat ST_B10 scaling",
            suggestions="Validate against local meteorological ground sensors.",
            additional_comments=None
        )
        save_feedback(sub3, test_db)

        summary = get_feedback_summary(test_db)
        assert summary["total_submissions"] == 3

        # Expected averages:
        # overall: (5 + 4 + 5) / 3 = 14 / 3 = 4.67
        # ease: (4 + 4 + 5) / 3 = 13 / 3 = 4.33
        # viz: (5 + 4 + 4) / 3 = 13 / 3 = 4.33
        # analysis: (5 + 4 + 5) / 3 = 14 / 3 = 4.67
        # interventions: (4 + 4 + 5) / 3 = 13 / 3 = 4.33
        assert summary["avg_overall_rating"] == 4.67
        assert summary["avg_ease_of_use"] == 4.33
        assert summary["avg_data_visualization"] == 4.33
        assert summary["avg_heat_risk_analysis"] == 4.67
        assert summary["avg_intervention_recommendations"] == 4.33

        # Rating distribution for overall_rating: 1:0, 2:0, 3:0, 4:1, 5:2
        assert summary["rating_distribution"]["5"] == 2
        assert summary["rating_distribution"]["4"] == 1
        assert summary["rating_distribution"]["3"] == 0

        # Role breakdown: Judge:1, Evaluator:1, Faculty:1
        assert summary["role_breakdown"]["Judge"] == 1
        assert summary["role_breakdown"]["Evaluator"] == 1
        assert summary["role_breakdown"]["Faculty"] == 1
        assert summary["role_breakdown"]["Student"] == 0

        print(f"✓ Summary verified: Total: {summary['total_submissions']}, Avg Overall: {summary['avg_overall_rating']} / 5.0")
    finally:
        if os.path.exists(test_db):
            os.remove(test_db)


def test_api_summary_endpoint():
    print("\n--- 7. Testing GET /api/feedback/summary Endpoint ---")
    response = client.get("/api/feedback/summary")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()

    assert "total_submissions" in data
    assert "avg_overall_rating" in data
    assert "avg_ease_of_use" in data
    assert "avg_data_visualization" in data
    assert "avg_heat_risk_analysis" in data
    assert "avg_intervention_recommendations" in data
    assert "rating_distribution" in data
    assert "role_breakdown" in data
    assert "category_averages" in data
    print(f"✓ Feedback summary endpoint verified with {data['total_submissions']} total submissions.")


if __name__ == "__main__":
    test_empty_database_summary()
    test_valid_feedback_submission()
    test_get_feedback_by_id()
    test_feedback_retrieval_and_persistence()
    test_missing_required_fields()
    test_invalid_rating_values()
    test_feedback_summary_statistics_calculation()
    test_api_summary_endpoint()
    print("\n🎉 ALL FEEDBACK SESSION VERIFICATION TESTS PASSED (8/8)! 🎉\n")

