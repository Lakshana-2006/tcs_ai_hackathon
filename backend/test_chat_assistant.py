import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ai_service import build_system_context_prompt

client = TestClient(app)

def test_chat_empty_message():
    response = client.post("/api/chat", json={"message": "   "})
    assert response.status_code == 400
    assert "Message cannot be empty" in response.json()["detail"]

def test_chat_unconfigured_setup_message():
    context_data = {
        "city": {
            "name": "Tokyo",
            "country": "Japan",
            "currency": {"code": "JPY", "symbol": "¥", "rate_per_usd": 155.0}
        },
        "weather": {
            "air_temperature_c": 22.5,
            "apparent_temperature_c": 22.0,
            "condition": "Clear sky"
        },
        "zones": [
            {"id": "tokyo_zone_1", "name": "Zone 1 — Otemachi / Ginza", "baseline_risk": 58.2, "population": 85000},
            {"id": "tokyo_zone_2", "name": "Zone 2 — Shinjuku High-Rise", "baseline_risk": 71.4, "population": 160000}
        ],
        "selected_zone": {
            "id": "tokyo_zone_2",
            "name": "Zone 2 — Shinjuku High-Rise",
            "baseline_risk": 71.4,
            "population": 160000
        },
        "selected_interventions": {"cool_roofs": 35.0},
        "simulation_result": {
            "zone_name": "Zone 2 — Shinjuku High-Rise",
            "risk_delta": 4.5,
            "risk_reduction_pct": 6.3,
            "lst_reduction_c": 1.58,
            "people_protected": 25200,
            "estimated_cost_local": 67812500,
            "estimated_cost_usd": 437500
        }
    }

    response = client.post("/api/chat", json={
        "message": "Which zone has the highest heat risk?",
        "context": context_data
    })
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    # When no key is set, it must return setup instructions and friendly message, not fake generation
    assert data["is_configured"] is False
    assert "GEMINI_API_KEY" in data["setup_instructions"]
    assert "Tokyo" in data["reply"]
    assert "Zone 2" in data["reply"]

def test_system_prompt_builder():
    context_data = {
        "city": {"name": "Chennai", "country": "India", "currency": {"symbol": "₹", "code": "INR"}},
        "weather": {"air_temperature_c": 32.0, "apparent_temperature_c": 38.0, "relative_humidity_pct": 70, "condition": "Humid"},
        "zones": [
            {
                "id": "chennai_zone_3",
                "name": "Zone 3 — Historic Commercial Core",
                "baseline_risk": 78.5,
                "population": 140000,
                "baseline_hazard": {"hazard_score": 85.0},
                "baseline_exposure": {"exposure_score": 88.0},
                "baseline_vulnerability": {"vulnerability_score": 62.0}
            }
        ],
        "selected_zone": {
            "id": "chennai_zone_3",
            "name": "Zone 3 — Historic Commercial Core",
            "baseline_risk": 78.5,
            "population": 140000,
            "baseline_hazard": {"hazard_score": 85.0, "lst_anomaly_c": 4.5, "tree_canopy_pct": 8.0, "impervious_surface_pct": 85.0},
            "baseline_exposure": {"exposure_score": 88.0, "pop_density_per_km2": 24000, "outdoor_labor_ratio": 42.0},
            "baseline_vulnerability": {"vulnerability_score": 62.0, "social_vulnerability_index": 0.78, "lack_of_ac_pct": 68.0, "elderly_pct": 14.5},
            "recommended_priorities": ["tree_planting", "cool_roofs"]
        },
        "simulation_result": {
            "risk_delta": 8.2,
            "risk_reduction_pct": 10.4,
            "lst_reduction_c": 2.1,
            "people_protected": 35000,
            "estimated_cost_local": 25000000,
            "estimated_cost_usd": 299401
        }
    }

    prompt = build_system_context_prompt(context_data)
    assert "Chennai" in prompt
    assert "32.0°C" in prompt
    assert "Zone 3" in prompt
    assert "78.5/100" in prompt
    assert "8.2 pts" in prompt
    assert "Cooling Hubs" in prompt  # Biophysical rule
    print("[PASS] System prompt builder accurately constructs ground-truth dashboard context.")

if __name__ == "__main__":
    test_chat_empty_message()
    test_chat_unconfigured_setup_message()
    test_system_prompt_builder()
    print("ALL CHAT ASSISTANT TESTS PASSED!")

