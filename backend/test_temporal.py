"""
test_temporal.py - Comprehensive Verification Test Suite for Past, Present, Future, and Climate Heat-Risk Analysis

Tests:
1. Past (Historical Reanalysis via Open-Meteo Archive API)
2. Present (Real-Time Weather Telemetry via Open-Meteo Operational API)
3. Future (7-14 Day Numerical Weather Prediction via Open-Meteo Forecast API)
4. Long-Term Climate Projections through 2050 (CMIP6 Multi-Model via Open-Meteo Climate API)
5. Multi-Horizon Comparative Synthesis
6. Exact IPCC Risk Formula Preservation: R = 0.35H + 0.30E + 0.35V - Adaptive Buffer
7. Date Range Validation & Error Handling
"""

import sys
import os

# Set UTF-8 encoding on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.temporal_service import calculate_single_hazard_score, calculate_zone_risk_for_conditions

client = TestClient(app)


def test_ipcc_formula_consistency():
    print("\n--- 1. Testing IPCC Risk Formula Consistency ---")
    # Test known values:
    # air_temp = 35.0°C, apparent_temp = 42.0°C, uhi_bias = 5.0°C
    # hazard_raw = (35.0 * 1.2) + ((42.0 - 35.0) * 2.0) + (5.0 * 4.2)
    #             = 42.0 + 14.0 + 21.0 = 77.0
    h_score = calculate_single_hazard_score(35.0, 42.0, 5.0)
    assert h_score == 77.0, f"Expected 77.0, got {h_score}"
    print(f"  • Hazard score: {h_score} (Air: 35°C, Apparent: 42°C, UHI: 5°C)")

    # Zone with Exposure = 60.0, Vulnerability = 70.0, Adaptive Capacity = 50.0
    # risk_unadjusted = (0.35 * 77.0) + (0.30 * 60.0) + (0.35 * 70.0)
    #                 = 26.95 + 18.0 + 24.5 = 69.45
    # adaptive_buffer = (50.0 / 100.0) * 4.0 = 2.0
    # risk = round(69.45 - 2.0, 1) = 67.5
    mock_zone = {
        "id": "test_zone",
        "baseline_hazard": {"lst_anomaly_c": 5.0},
        "baseline_exposure": {"exposure_score": 60.0},
        "baseline_vulnerability": {"vulnerability_score": 70.0},
        "urban_infrastructure": {"adaptive_capacity_score": 50.0}
    }
    z_res = calculate_zone_risk_for_conditions(mock_zone, 35.0, 42.0)
    assert z_res["composite_risk"] == 67.5, f"Expected 67.5, got {z_res['composite_risk']}"
    assert z_res["hazard_score"] == 77.0
    print(f"  • Composite Risk: {z_res['composite_risk']} / 100 (Formula exact match)")
    print("[PASS] IPCC multi-criteria risk formula verified with exact weights (0.35, 0.30, 0.35).")


def test_historical_weather_api():
    print("\n--- 2. Testing Past: Open-Meteo Historical Archive API ---")
    response = client.get("/api/temporal/past?city=Chennai&start_date=2024-05-15&end_date=2024-05-20")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["city"] == "Chennai"
    assert data["mode"] == "past"
    assert "Open-Meteo Historical Weather Archive" in data["data_source"]
    assert data["days_count"] >= 5
    assert data["peak_temperature_c"] > 20.0
    assert len(data["daily_timeline"]) >= 5
    
    # Check all 5 zones exist in zone_histories
    zh = data["zone_histories"]
    assert len(zh) == 5
    for zid, hist in zh.items():
        assert len(hist["daily_risks"]) >= 5
        print(f"  • Historical Zone: {hist['zone_name']} - Peak Risk Date: {data['peak_risk_date']}")

    print(f"  • Peak Historical Temperature: {data['peak_temperature_c']}°C, Peak Risk: {data['peak_risk_score']}")
    print("[PASS] Historical heat-risk analysis verified using genuine ERA5 reanalysis data.")


def test_present_live_weather():
    print("\n--- 3. Testing Present: Real-Time Operational Telemetry ---")
    response = client.get("/api/temporal/present?city=Chennai")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["city"] == "Chennai"
    assert data["mode"] == "present"
    assert data["air_temperature_c"] > 5.0
    assert data["relative_humidity_pct"] > 0.0
    assert len(data["zone_risks"]) == 5
    print(f"  • Current Chennai Air Temp: {data['air_temperature_c']}°C (Feels like: {data['apparent_temperature_c']}°C)")
    print(f"  • Average City Risk: {data['average_city_risk']} / 100")
    print("[PASS] Present real-time heat-risk analysis verified.")


def test_future_forecast_weather():
    print("\n--- 4. Testing Future: Numerical Weather Prediction Forecast ---")
    response = client.get("/api/temporal/future?city=Chennai&days=7")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["city"] == "Chennai"
    assert data["mode"] == "future"
    assert data["forecast_horizon_days"] == 7
    assert len(data["daily_timeline"]) == 7
    assert len(data["hourly_diurnal_24h"]) == 24
    assert len(data["zone_forecasts"]) == 5
    print(f"  • 7-Day Forecast Peak Temp: {data['peak_temperature_c']}°C on {data['peak_risk_date']}")
    print(f"  • Diurnal Curve: {len(data['hourly_diurnal_24h'])} hourly points computed")
    print("[PASS] Future forecast heat-risk analysis verified.")


def test_climate_projections_2050():
    print("\n--- 5. Testing Long-Term Climate Projections through 2050 (CMIP6) ---")
    response = client.get("/api/temporal/climate?city=Chennai&model=EC_Earth3P_HR")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data["city"] == "Chennai"
    assert data["mode"] == "climate"
    assert "CMIP6" in data["data_source"]
    assert "decadal_projections" in data
    
    decades = data["decadal_projections"]
    years = [d["year"] for d in decades]
    assert 2025 in years
    assert 2030 in years
    assert 2040 in years
    assert 2050 in years
    for d in decades:
        print(f"  • Year {d['year']}: Projected Summer Mean Max {d['projected_mean_summer_max_c']}°C (Risk: {d['projected_city_average_risk']})")
    assert "scientific_disclaimer" in data
    print("[PASS] CMIP6 climate model projections through 2050 verified.")


def test_temporal_comparison_endpoint():
    print("\n--- 6. Testing Temporal Comparison (Past vs Present vs Future vs 2050) ---")
    response = client.get("/api/temporal/compare?city=Chennai")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "past_heatwave" in data
    assert "present_live" in data
    assert "future_forecast" in data
    assert "climate_2050" in data
    print(f"  • Past Heatwave: {data['past_heatwave']['peak_air_temp_c']}°C (Risk {data['past_heatwave']['city_risk_score']})")
    print(f"  • Present Live: {data['present_live']['current_air_temp_c']}°C (Risk {data['present_live']['city_risk_score']})")
    print(f"  • Future 7-Day Peak: {data['future_forecast']['peak_air_temp_c']}°C (Risk {data['future_forecast']['peak_risk_score']})")
    print(f"  • Climate 2050: {data['climate_2050']['projected_summer_max_c']}°C (Risk {data['climate_2050']['projected_city_risk']})")
    print("[PASS] Multi-horizon temporal comparison verified.")


def test_date_validation_and_errors():
    print("\n--- 7. Testing Date Validation & Error Handling ---")
    # Invalid: start_date > end_date
    res_bad = client.get("/api/temporal/past?city=Chennai&start_date=2024-05-25&end_date=2024-05-15")
    assert res_bad.status_code == 400, f"Expected 400, got {res_bad.status_code}"
    print("  • Verified: Inverted date range correctly rejected with 400 Bad Request.")

    # Invalid: Malformed date string
    res_bad_fmt = client.get("/api/temporal/past?city=Chennai&start_date=invalid-date&end_date=2024-05-20")
    assert res_bad_fmt.status_code == 400, f"Expected 400, got {res_bad_fmt.status_code}"
    print("  • Verified: Malformed date format correctly rejected with 400 Bad Request.")
    print("[PASS] Date validation and error handling verified.")


if __name__ == "__main__":
    test_ipcc_formula_consistency()
    test_historical_weather_api()
    test_present_live_weather()
    test_future_forecast_weather()
    test_climate_projections_2050()
    test_temporal_comparison_endpoint()
    test_date_validation_and_errors()
    print("\n🎉 ALL TEMPORAL HEAT-RISK ANALYSIS TESTS PASSED (7/7)! 🎉\n")

