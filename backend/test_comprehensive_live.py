import sys
import os
import requests
import json
import time

# Ensure UTF-8 output on Windows
if sys.platform.startswith("win"):
    sys.stdout.reconfigure(encoding="utf-8")

BACKEND_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"

def main():
    print("=" * 72)
    print("   HEATSHIELD AI — COMPREHENSIVE LIVE SYSTEM VERIFICATION TEST   ")
    print("=" * 72)

    test_results = {}

    # -------------------------------------------------------------
    # 1. Startup & Health Checks
    # -------------------------------------------------------------
    print("\n[CHECK 1] Verifying Backend & Frontend Live Availability...")
    try:
        r_fe = requests.get(FRONTEND_URL, timeout=5)
        assert r_fe.status_code == 200, f"Frontend status: {r_fe.status_code}"
        assert "<div id=\"root\"></div>" in r_fe.text
        print(f"  ✓ Frontend online at {FRONTEND_URL} (HTTP 200 OK, HTML loaded)")
        test_results["Frontend Startup"] = "PASS"
    except Exception as e:
        print(f"  ✗ Frontend failed: {e}")
        test_results["Frontend Startup"] = f"FAIL: {e}"

    try:
        r_be = requests.get(f"{BACKEND_URL}/", timeout=5)
        assert r_be.status_code == 200, f"Backend status: {r_be.status_code}"
        root_data = r_be.json()
        assert root_data["status"] == "online"
        print(f"  ✓ Backend online at {BACKEND_URL} (HTTP 200 OK, System online)")
        test_results["Backend Startup"] = "PASS"
    except Exception as e:
        print(f"  ✗ Backend failed: {e}")
        test_results["Backend Startup"] = f"FAIL: {e}"

    # -------------------------------------------------------------
    # 2. City Search (Geocoding)
    # -------------------------------------------------------------
    print("\n[CHECK 2] Testing Worldwide Geocoding Search (Chennai, Tokyo, London, Dubai)...")
    cities_test = [
        {"q": "Chennai", "expect_country": "India", "curr": "INR"},
        {"q": "Tokyo", "expect_country": "Japan", "curr": "JPY"},
        {"q": "London", "expect_country": "United Kingdom", "curr": "GBP"},
        {"q": "Dubai", "expect_country": "United Arab Emirates", "curr": "AED"}
    ]

    geocoded_cities = {}
    search_all_pass = True

    for c in cities_test:
        try:
            r = requests.get(f"{BACKEND_URL}/api/geocode?q={c['q']}", timeout=6)
            assert r.status_code == 200
            data = r.json()
            assert data["count"] > 0, f"No results for {c['q']}"
            top = data["results"][0]
            assert c["expect_country"].lower() in top["country"].lower(), f"Expected {c['expect_country']}, got {top['country']}"
            assert top["currency"]["code"] == c["curr"], f"Expected {c['curr']}, got {top['currency']['code']}"
            geocoded_cities[c["q"]] = top
            print(f"  ✓ Search '{c['q']}': Found '{top['display_name']}' at ({top['latitude']}, {top['longitude']}), Currency: {top['currency']['symbol']} {top['currency']['code']}")
        except Exception as e:
            print(f"  ✗ Search '{c['q']}' failed: {e}")
            search_all_pass = False

    test_results["Global City Search"] = "PASS" if search_all_pass else "FAIL"

    # -------------------------------------------------------------
    # 3. Dynamic City Coordinates & 5 Zones Generation
    # -------------------------------------------------------------
    print("\n[CHECK 3] Verifying Dynamic Map Coordinates & 5 Unique Zones per City...")
    city_data_cache = {}
    zone_gen_pass = True

    city_coords = [
        {"name": "Chennai", "country": "India", "country_code": "IN", "lat": 13.0827, "lon": 80.2707},
        {"name": "Tokyo", "country": "Japan", "country_code": "JP", "lat": 35.6762, "lon": 139.6503},
        {"name": "London", "country": "United Kingdom", "country_code": "GB", "lat": 51.5074, "lon": -0.1278},
        {"name": "Dubai", "country": "United Arab Emirates", "country_code": "AE", "lat": 25.2048, "lon": 55.2708}
    ]

    for item in city_coords:
        try:
            params = {
                "name": item["name"],
                "country": item["country"],
                "country_code": item["country_code"],
                "lat": item["lat"],
                "lon": item["lon"]
            }
            r = requests.get(f"{BACKEND_URL}/api/city-data", params=params, timeout=6)
            assert r.status_code == 200
            res = r.json()
            city_data_cache[item["name"]] = res

            zones = res["zones"]
            assert len(zones) == 5, f"Expected 5 zones, got {len(zones)}"

            # Verify zone coordinates are within ~5km of city center
            city_slug = item["name"].lower()
            for z in zones:
                assert city_slug in z["id"], f"Zone ID {z['id']} should contain city slug {city_slug}"
                assert len(z["polygon"]) >= 4, f"Zone polygon should have >= 4 coordinates"
                c_lat, c_lon = z["centroid"]
                assert abs(c_lat - item["lat"]) < 0.15, f"Zone centroid latitude {c_lat} too far from city lat {item['lat']}"
                assert abs(c_lon - item["lon"]) < 0.15, f"Zone centroid longitude {c_lon} too far from city lon {item['lon']}"

            print(f"  ✓ {item['name']}: 5 Zones generated around ({item['lat']}°, {item['lon']}°): {[z['short_name'] for z in zones]}")
        except Exception as e:
            print(f"  ✗ {item['name']} zone generation failed: {e}")
            zone_gen_pass = False

    test_results["Dynamic 5-Zone Generation"] = "PASS" if zone_gen_pass else "FAIL"

    # -------------------------------------------------------------
    # 4. Open-Meteo Real Weather Telemetry
    # -------------------------------------------------------------
    print("\n[CHECK 4] Verifying Real Open-Meteo Weather Telemetry & Attributions...")
    weather_pass = True

    for name, cdata in city_data_cache.items():
        w = cdata["weather"]
        try:
            assert "air_temperature_c" in w
            assert "relative_humidity_pct" in w
            assert "apparent_temperature_c" in w
            assert "timestamp" in w
            assert w["data_source"] == "Open-Meteo Global Weather API"
            assert "Not land-surface temperature" in w["measurement_notice"]
            assert -20.0 <= w["air_temperature_c"] <= 55.0, f"Unrealistic temperature: {w['air_temperature_c']}"
            print(f"  ✓ {name}: Air Temp = {w['air_temperature_c']}°C, Feels Like = {w['apparent_temperature_c']}°C, Humidity = {w['relative_humidity_pct']}%, Condition: '{w['condition']}' [{w['timestamp']}]")
        except Exception as e:
            print(f"  ✗ {name} weather check failed: {e}")
            weather_pass = False

    test_results["Real Weather & Attribution"] = "PASS" if weather_pass else "FAIL"

    # -------------------------------------------------------------
    # 5. Synthetic Data Transparency & Labeling
    # -------------------------------------------------------------
    print("\n[CHECK 5] Checking Synthetic Assumption Labeling & Disclaimers...")
    synthetic_pass = True
    for name, cdata in city_data_cache.items():
        try:
            assert "synthetic_notice" in cdata
            assert "synthetic demo assumptions" in cdata["synthetic_notice"].lower()
            assert "not certified" in cdata["synthetic_notice"].lower()
        except Exception as e:
            print(f"  ✗ Synthetic disclaimer missing for {name}: {e}")
            synthetic_pass = False

    if synthetic_pass:
        print("  ✓ All API responses explicitly label population, vulnerability, and risk metrics as synthetic demo assumptions.")
    test_results["Synthetic Data Disclaimers"] = "PASS" if synthetic_pass else "FAIL"

    # -------------------------------------------------------------
    # 6. Zone Selection & Intervention Simulation
    # -------------------------------------------------------------
    print("\n[CHECK 6] Testing Intervention Simulator & Biophysical Constraints...")
    sim_pass = True

    # Test 6a: Cooling Centres ONLY reduce exposure and vulnerability (0.0°C LST drop)
    tokyo_z2 = city_data_cache["Tokyo"]["zones"][1]
    tokyo_curr = city_data_cache["Tokyo"]["city"]["currency"]
    try:
        r_sim_cc = requests.post(f"{BACKEND_URL}/api/simulate", json={
            "zone_id": tokyo_z2["id"],
            "city_name": "Tokyo",
            "currency_code": tokyo_curr["code"],
            "currency_symbol": tokyo_curr["symbol"],
            "currency_rate": tokyo_curr["rate_per_usd"],
            "zone_data": tokyo_z2,
            "interventions": {"cooling_centers": 5}
        }, timeout=6)
        assert r_sim_cc.status_code == 200
        res_cc = r_sim_cc.json()["zone_result"]

        assert res_cc["lst_reduction_c"] == 0.0, "Cooling centers MUST have 0.0°C LST reduction!"
        assert res_cc["simulated"]["hazard_score"] == res_cc["baseline"]["hazard_score"]
        assert res_cc["risk_delta"] > 0
        assert res_cc["people_protected"] > 0
        assert res_cc["currency_symbol"] == "¥"
        print(f"  ✓ Cooling Centers Rule Verified (Tokyo): LST Drop = {res_cc['lst_reduction_c']}°C, Exposure/Risk Delta = -{res_cc['risk_delta']} pts, Protected = {res_cc['people_protected']:,}, Cost = ¥{res_cc['estimated_cost_local']:,.0f}")
    except Exception as e:
        print(f"  ✗ Cooling centers simulation failed: {e}")
        sim_pass = False

    # Test 6b: Physical cooling (Tree planting + Cool roofs) in Chennai
    chennai_z3 = city_data_cache["Chennai"]["zones"][2]
    chennai_curr = city_data_cache["Chennai"]["city"]["currency"]
    try:
        r_sim_phys = requests.post(f"{BACKEND_URL}/api/simulate", json={
            "zone_id": chennai_z3["id"],
            "city_name": "Chennai",
            "currency_code": chennai_curr["code"],
            "currency_symbol": chennai_curr["symbol"],
            "currency_rate": chennai_curr["rate_per_usd"],
            "zone_data": chennai_z3,
            "interventions": {"tree_planting": 30, "cool_roofs": 40}
        }, timeout=6)
        assert r_sim_phys.status_code == 200
        res_phys = r_sim_phys.json()["zone_result"]

        assert res_phys["lst_reduction_c"] > 1.0, "Physical interventions must reduce LST"
        assert res_phys["simulated"]["hazard_score"] < res_phys["baseline"]["hazard_score"]
        assert res_phys["uncertainty"]["low"] <= res_phys["uncertainty"]["expected"] <= res_phys["uncertainty"]["high"]
        print(f"  ✓ Physical Cooling Verified (Chennai): LST Drop = -{res_phys['lst_reduction_c']}°C, Hazard = {res_phys['baseline']['hazard_score']} -> {res_phys['simulated']['hazard_score']}, 90% CI = [{res_phys['uncertainty']['low']} to {res_phys['uncertainty']['high']}], Cost = ₹{res_phys['estimated_cost_local']:,.0f}")
    except Exception as e:
        print(f"  ✗ Physical cooling simulation failed: {e}")
        sim_pass = False

    test_results["Intervention Simulation & Biophysical Rules"] = "PASS" if sim_pass else "FAIL"

    # -------------------------------------------------------------
    # 7. Currency-Aware Budget Optimization
    # -------------------------------------------------------------
    print("\n[CHECK 7] Testing Currency-Aware Budget Optimizer & Prioritization...")
    opt_pass = True

    opt_tests = [
        {"city": "Chennai", "code": "INR", "sym": "₹", "rate": 83.5, "budget": 25000000.0},
        {"city": "Tokyo", "code": "JPY", "sym": "¥", "rate": 155.0, "budget": 500000000.0},
        {"city": "London", "code": "GBP", "sym": "£", "rate": 0.79, "budget": 2500000.0},
        {"city": "Dubai", "code": "AED", "sym": "AED", "rate": 3.67, "budget": 12000000.0}
    ]

    for ot in opt_tests:
        try:
            cdata = city_data_cache[ot["city"]]
            payload = {
                "city_name": ot["city"],
                "country_code": cdata["city"]["country_code"],
                "currency_code": ot["code"],
                "currency_symbol": ot["sym"],
                "currency_rate": ot["rate"],
                "total_budget_local": ot["budget"],
                "equity_weighting": True,
                "focus_objective": "balanced",
                "zones": cdata["zones"]
            }
            r_opt = requests.post(f"{BACKEND_URL}/api/optimize", json=payload, timeout=6)
            assert r_opt.status_code == 200
            res = r_opt.json()

            assert res["currency_symbol"] == ot["sym"]
            assert res["budget_utilized_local"] <= ot["budget"]
            assert res["total_people_protected"] > 0
            assert len(res["prioritization_rationale"]) >= 3

            # Verify allocations are for current city's zones only
            for zid in res["allocations_by_zone"]:
                assert ot["city"].lower() in zid, f"Cross-contamination: zone {zid} in {ot['city']} optimizer!"

            print(f"  ✓ {ot['city']} Optimizer: Utilized {ot['sym']}{res['budget_utilized_local']:,.0f} of {ot['sym']}{ot['budget']:,.0f} ({ot['code']}), Protected = {res['total_people_protected']:,}, Risk Reduction = -{res['risk_reduction_pct']}%")
        except Exception as e:
            print(f"  ✗ {ot['city']} optimizer failed: {e}")
            opt_pass = False

    test_results["Budget Optimizer & Rationale"] = "PASS" if opt_pass else "FAIL"

    # -------------------------------------------------------------
    # 8. Repeated City Switching & Zero-Stale-Data Verification
    # -------------------------------------------------------------
    print("\n[CHECK 8] Testing Rapid Sequential Switching: Chennai -> Tokyo -> London -> Dubai -> Chennai...")
    switch_order = ["Chennai", "Tokyo", "London", "Dubai", "Chennai"]
    stale_pass = True

    for i in range(len(switch_order)):
        c_name = switch_order[i]
        c_meta = next(c for c in city_coords if c["name"] == c_name)
        try:
            r = requests.get(f"{BACKEND_URL}/api/city-data", params=c_meta, timeout=6)
            assert r.status_code == 200
            data = r.json()

            # Confirm city name
            assert data["city"]["name"] == c_name
            current_slug = c_name.lower()

            # Confirm all 5 zone IDs strictly match current city slug
            zone_ids = [z["id"] for z in data["zones"]]
            for zid in zone_ids:
                assert zid.startswith(current_slug), f"Stale zone ID detected: {zid} when active city is {c_name}!"

            # If previous city was different, confirm zero IDs from previous city linger
            if i > 0:
                prev_slug = switch_order[i - 1].lower()
                for zid in zone_ids:
                    assert not zid.startswith(prev_slug), f"Stale zone ID from previous city {prev_slug} found: {zid}"

            print(f"  ✓ Switch #{i+1} to {c_name}: Active zones strictly {zone_ids[:2]}... (Zero stale data from {switch_order[i-1] if i > 0 else 'initial'})")
        except Exception as e:
            print(f"  ✗ Switching step #{i+1} failed: {e}")
            stale_pass = False

    test_results["Zero-Stale-Data City Switching"] = "PASS" if stale_pass else "FAIL"

    # -------------------------------------------------------------
    # Final Summary Report
    # -------------------------------------------------------------
    print("\n" + "=" * 72)
    print("                    FINAL VERIFICATION REPORT                    ")
    print("=" * 72)
    all_passed = True
    for feat, status in test_results.items():
        print(f"  {feat:<45} : {status}")
        if status != "PASS":
            all_passed = False

    print("=" * 72)
    if all_passed:
        print(">>> ALL 8 CORE TEST SUITES PASSED WITH 100% SUCCESS <<<")
    else:
        print(">>> SOME CHECKS FAILED — REVIEW DETAILS ABOVE <<<")
    print("=" * 72)

if __name__ == "__main__":
    main()

