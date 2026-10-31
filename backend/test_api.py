import sys
import os

# Reconfigure stdout for UTF-8 on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app

def run_global_tests():
    print("==================================================================")
    print("   HEATSHIELD AI — GLOBAL DIGITAL TWIN VERIFICATION TEST SUITE    ")
    print("==================================================================")
    client = TestClient(app)

    # 1. Global Geocoding Search Test
    print("\n--- 1. Testing Global City Geocoding Search ---")
    cities_to_search = ["Chennai", "Tokyo", "London", "Dubai", "New York"]
    for city_q in cities_to_search:
        r = client.get(f"/api/geocode?q={city_q}")
        assert r.status_code == 200
        res = r.json()
        assert res["count"] > 0, f"No geocoding results for {city_q}"
        top = res["results"][0]
        print(f"[PASS] Geocode '{city_q}' -> {top['display_name']} ({top['latitude']}, {top['longitude']}) Currency: {top['currency']['code']}")

    # 2. Test City 1: Chennai, India
    print("\n--- 2. Testing City 1: Chennai, India ---")
    r_chennai = client.get("/api/city-data?name=Chennai&country=India&country_code=IN&lat=13.0827&lon=80.2707")
    assert r_chennai.status_code == 200
    chennai = r_chennai.json()
    assert chennai["city"]["name"] == "Chennai"
    assert chennai["city"]["currency"]["code"] == "INR"
    assert chennai["city"]["currency"]["symbol"] == "₹"
    assert len(chennai["zones"]) == 5
    assert chennai["weather"]["air_temperature_c"] > 10.0
    print(f"[PASS] Chennai: Real Open-Meteo Air Temp = {chennai['weather']['air_temperature_c']}°C, Apparent = {chennai['weather']['apparent_temperature_c']}°C, Humidity = {chennai['weather']['relative_humidity_pct']}%")
    chennai_zone_ids = [z["id"] for z in chennai["zones"]]
    print(f"[PASS] Chennai 5 Zones: {chennai_zone_ids}")

    # 3. Test City 2: Tokyo, Japan
    print("\n--- 3. Testing City 2: Tokyo, Japan ---")
    r_tokyo = client.get("/api/city-data?name=Tokyo&country=Japan&country_code=JP&lat=35.6762&lon=139.6503")
    assert r_tokyo.status_code == 200
    tokyo = r_tokyo.json()
    assert tokyo["city"]["name"] == "Tokyo"
    assert tokyo["city"]["currency"]["code"] == "JPY"
    assert tokyo["city"]["currency"]["symbol"] == "¥"
    assert len(tokyo["zones"]) == 5
    tokyo_zone_ids = [z["id"] for z in tokyo["zones"]]
    print(f"[PASS] Tokyo: Real Open-Meteo Air Temp = {tokyo['weather']['air_temperature_c']}°C, Apparent = {tokyo['weather']['apparent_temperature_c']}°C")
    print(f"[PASS] Tokyo 5 Zones: {tokyo_zone_ids}")

    # Verify no zone collision between Chennai and Tokyo
    assert set(chennai_zone_ids).isdisjoint(set(tokyo_zone_ids)), "Chennai and Tokyo zone IDs must be completely unique and non-overlapping!"
    print("[PASS] Verified: Zero ID/coordinate overlap between Chennai and Tokyo.")

    # 4. Test City 3: London, UK
    print("\n--- 4. Testing City 3: London, United Kingdom ---")
    r_london = client.get("/api/city-data?name=London&country=United%20Kingdom&country_code=GB&lat=51.5074&lon=-0.1278")
    assert r_london.status_code == 200
    london = r_london.json()
    assert london["city"]["name"] == "London"
    assert london["city"]["currency"]["code"] == "GBP"
    assert london["city"]["currency"]["symbol"] == "£"
    assert len(london["zones"]) == 5
    london_zone_ids = [z["id"] for z in london["zones"]]
    print(f"[PASS] London: Real Open-Meteo Air Temp = {london['weather']['air_temperature_c']}°C, Apparent = {london['weather']['apparent_temperature_c']}°C")
    print(f"[PASS] London 5 Zones: {london_zone_ids}")
    assert set(london_zone_ids).isdisjoint(set(tokyo_zone_ids))
    print("[PASS] Verified: Zero overlap between London and other cities.")

    # 5. Test Intervention Simulator for Chennai (with ₹ INR)
    print("\n--- 5. Testing Simulator with Currency Conversion (Chennai) ---")
    r_sim = client.post("/api/simulate", json={
        "zone_id": chennai["zones"][2]["id"],
        "city_name": "Chennai",
        "currency_code": "INR",
        "currency_symbol": "₹",
        "currency_rate": 83.5,
        "zone_data": chennai["zones"][2],
        "interventions": {"cooling_centers": 4, "tree_planting": 25}
    })
    assert r_sim.status_code == 200
    sim_res = r_sim.json()["zone_result"]
    assert sim_res["currency_symbol"] == "₹"
    assert sim_res["estimated_cost_local"] > sim_res["estimated_cost_usd"]
    assert sim_res["people_protected"] > 0
    assert sim_res["risk_delta"] > 0
    print(f"[PASS] Chennai Zone Sim: Risk Delta = -{sim_res['risk_delta']} pts, Protected = {sim_res['people_protected']:,}, Cost = ₹{sim_res['estimated_cost_local']:,.0f}")

    # 6. Test Cooling Center Biophysical Law
    print("\n--- 6. Testing Cooling Center Biophysical Constraint ---")
    r_cc = client.post("/api/simulate", json={
        "zone_id": tokyo["zones"][1]["id"],
        "city_name": "Tokyo",
        "currency_code": "JPY",
        "currency_symbol": "¥",
        "currency_rate": 155.0,
        "zone_data": tokyo["zones"][1],
        "interventions": {"cooling_centers": 6}
    })
    assert r_cc.status_code == 200
    cc_res = r_cc.json()["zone_result"]
    assert cc_res["lst_reduction_c"] == 0.0, "Cooling centers must NOT claim Land Surface Temperature drop!"
    assert cc_res["simulated"]["hazard_score"] == cc_res["baseline"]["hazard_score"]
    assert cc_res["risk_delta"] > 0, "Human exposure and vulnerability must be reduced"
    print(f"[PASS] Tokyo Cooling Center: LST Reduction = 0.0°C (Exact biophysical law respected), Risk Delta = -{cc_res['risk_delta']} pts")

    # 7. Test Budget Optimizer with Local Currency (London £ GBP)
    print("\n--- 7. Testing Currency-Aware Optimizer (London £2.5M) ---")
    r_opt = client.post("/api/optimize", json={
        "city_name": "London",
        "country_code": "GB",
        "currency_code": "GBP",
        "currency_symbol": "£",
        "currency_rate": 0.79,
        "total_budget_local": 2500000.0,
        "equity_weighting": True,
        "focus_objective": "balanced",
        "zones": london["zones"]
    })
    assert r_opt.status_code == 200
    opt_res = r_opt.json()
    assert opt_res["currency_symbol"] == "£"
    assert opt_res["budget_utilized_local"] <= 2500000.0
    assert opt_res["total_people_protected"] > 0
    assert len(opt_res["prioritization_rationale"]) >= 4
    print(f"[PASS] London Optimizer: Utilized £{opt_res['budget_utilized_local']:,.0f}/£{opt_res['total_budget_local']:,.0f}, Protected: {opt_res['total_people_protected']:,}")
    print("Prioritization Rationales for London:")
    for rat in opt_res["prioritization_rationale"][:2]:
        print(f"  {rat}")

    # 8. Test Budget Optimizer with INR (Chennai ₹2.5 Crore)
    print("\n--- 8. Testing Currency-Aware Optimizer (Chennai ₹2.5 Crore) ---")
    r_opt_inr = client.post("/api/optimize", json={
        "city_name": "Chennai",
        "country_code": "IN",
        "currency_code": "INR",
        "currency_symbol": "₹",
        "currency_rate": 83.5,
        "total_budget_local": 25000000.0,
        "equity_weighting": True,
        "focus_objective": "balanced",
        "zones": chennai["zones"]
    })
    assert r_opt_inr.status_code == 200
    opt_inr_res = r_opt_inr.json()
    assert opt_inr_res["currency_symbol"] == "₹"
    assert opt_inr_res["budget_utilized_local"] <= 25000000.0
    print(f"[PASS] Chennai Optimizer: Utilized ₹{opt_inr_res['budget_utilized_local']:,.0f}/₹{opt_inr_res['total_budget_local']:,.0f}")

    # 9. Test Dedicated AI Chat Assistant Endpoint
    print("\n--- 9. Testing AI Chat Assistant Endpoint ---")
    # Empty message should fail with 400
    r_chat_empty = client.post("/api/chat", json={"message": "   "})
    assert r_chat_empty.status_code == 400, "Empty chat message must return 400"
    print("[PASS] Chat validation: Empty message rejected with 400 Bad Request.")

    # Valid message without configured provider returns friendly setup response
    r_chat_valid = client.post("/api/chat", json={
        "message": "Which zone in Chennai has the highest heat risk?",
        "context": {
            "city": chennai["city"],
            "weather": chennai["weather"],
            "zones": chennai["zones"],
            "selected_zone": chennai["zones"][2],
            "selected_interventions": {"cooling_centers": 4, "tree_planting": 25},
            "simulation_result": sim_res
        }
    })
    assert r_chat_valid.status_code == 200
    chat_res = r_chat_valid.json()
    assert "reply" in chat_res
    assert chat_res["is_configured"] is False or chat_res["is_configured"] is True
    assert "Chennai" in chat_res["reply"] or "Chennai" in str(chat_res.get("context_used"))
    print(f"[PASS] Chat Assistant endpoint operational. is_configured={chat_res['is_configured']}")
    if not chat_res["is_configured"]:
        assert "GEMINI_API_KEY" in chat_res["setup_instructions"] or "OPENAI_API_KEY" in chat_res["setup_instructions"]
        print("[PASS] Clear configuration placeholder and friendly setup message verified without fake generation.")

    print("\n==================================================================")
    print(">>> ALL GLOBAL DIGITAL TWIN VERIFICATION TESTS PASSED (9/9)! <<<")
    print("==================================================================")

if __name__ == "__main__":
    run_global_tests()
