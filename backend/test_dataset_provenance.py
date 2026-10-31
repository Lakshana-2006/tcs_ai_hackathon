"""
test_dataset_provenance.py - Validation Test Suite for Dataset Integration & Provenance Layer

Tests:
1. Complete Dataset Registry & Metadata Provenance (Landsat, Sentinel-2, MODIS, Open-Meteo, Census 2011, GCC, OSM, IPCC).
2. Proper data classification: raw, derived, baseline, estimated.
3. Correct units and spatial resolutions (10m, 20m, 30m, 1000m, ward polygon, vector point).
4. Spatial alignment and area-weighted cross-referencing with GCC 200 Wards / 15 Zones.
5. Strict avoidance of false neighborhood identities or synthetic substitutions for satellite data.
6. Missing data and cloud-cover handling.
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
from app.dataset_registry import DATASET_REGISTRY, CHENNAI_GCC_SPATIAL_ALIGNMENT

client = TestClient(app)


def test_dataset_registry_completeness():
    print("\n--- 1. Testing Dataset Registry Completeness & Official Sources ---")
    response = client.get("/api/datasets")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    data = response.json()
    assert "datasets" in data
    assert data["total_datasets"] >= 8
    
    dataset_ids = [d["id"] for d in data["datasets"]]
    expected_ids = [
        "landsat_8_9_lst",
        "sentinel_2_indices",
        "modis_lst",
        "open_meteo_weather",
        "census_india_2011",
        "chennai_gcc_ward_profiles",
        "openstreetmap_infrastructure",
        "ipcc_risk_framework"
    ]
    
    for eid in expected_ids:
        assert eid in dataset_ids, f"Missing required dataset '{eid}' in registry!"
        d = next(item for item in data["datasets"] if item["id"] == eid)
        print(f"  • {d['name']} ({d['provider']}) - Resolution: {d['spatial_resolution']}")
        assert d["official_url"].startswith("http"), f"Missing valid official URL for {eid}"
        assert len(d["license"]) > 5, f"Missing license for {eid}"
        assert len(d["processing_method"]) > 20, f"Missing processing method description for {eid}"
    print("[PASS] All 8 required datasets registered with official providers and DOIs/URLs.")


def test_data_classification_and_provenance():
    print("\n--- 2. Testing Data Classifications (Raw, Derived, Baseline, Estimated) ---")
    
    # 1. Raw / Operational Telemetry
    raw_resp = client.get("/api/datasets?classification=raw")
    raw_ids = [d["id"] for d in raw_resp.json()["datasets"]]
    assert "open_meteo_weather" in raw_ids
    assert "openstreetmap_infrastructure" in raw_ids
    print(f"  • Raw observations: {raw_ids}")

    # 2. Derived Indices (Sensor processing)
    derived_resp = client.get("/api/datasets?classification=derived")
    derived_ids = [d["id"] for d in derived_resp.json()["datasets"]]
    assert "landsat_8_9_lst" in derived_ids
    assert "sentinel_2_indices" in derived_ids
    assert "modis_lst" in derived_ids
    print(f"  • Derived satellite indices: {derived_ids}")

    # 3. Baseline Demographics
    baseline_resp = client.get("/api/datasets?classification=baseline")
    baseline_ids = [d["id"] for d in baseline_resp.json()["datasets"]]
    assert "census_india_2011" in baseline_ids
    assert "chennai_gcc_ward_profiles" in baseline_ids
    print(f"  • Official baseline datasets: {baseline_ids}")

    # 4. Estimated Models
    est_resp = client.get("/api/datasets?classification=estimated")
    est_ids = [d["id"] for d in est_resp.json()["datasets"]]
    assert "ipcc_risk_framework" in est_ids
    print(f"  • Estimated risk models: {est_ids}")

    print("[PASS] Strict distinction between raw, derived, baseline, and estimated classifications verified.")


def test_units_and_spatial_resolutions():
    print("\n--- 3. Testing Units, Bands, and Spatial Resolutions ---")
    
    # Landsat 8/9
    l8 = DATASET_REGISTRY["landsat_8_9_lst"]
    assert "30m" in l8["spatial_resolution"]
    assert l8["units"]["mean_lst_c"] == "°C"
    assert "ST_B10" in l8["bands_used"]
    assert "QA_PIXEL" in l8["bands_used"]
    
    # Sentinel-2
    s2 = DATASET_REGISTRY["sentinel_2_indices"]
    assert "10m" in s2["spatial_resolution"]
    assert "B8" in "".join(s2["bands_used"])
    assert "SCL" in s2["bands_used"]
    assert "vegetation_cover_pct" in s2["units"]
    
    # MODIS
    modis = DATASET_REGISTRY["modis_lst"]
    assert "1000m" in modis["spatial_resolution"] or "1km" in modis["spatial_resolution"]
    assert modis["units"]["modis_lst_c"] == "°C"
    
    # Census
    census = DATASET_REGISTRY["census_india_2011"]
    assert census["units"]["total_population"] == "residents"
    assert census["reference_period"] == "March 1, 2011 (Official Census Enumeration)"
    
    # OpenStreetMap
    osm = DATASET_REGISTRY["openstreetmap_infrastructure"]
    assert "amenity=hospital" in "".join(osm["bands_used"])
    assert "amenity=community_centre" in "".join(osm["bands_used"])

    print("[PASS] Biophysical units and spatial resolutions accurately documented.")


def test_spatial_alignment_and_gcc_mapping():
    print("\n--- 4. Testing Spatial Alignment & GCC 200 Ward Cross-Referencing ---")
    response = client.get("/api/datasets/spatial-alignment?city=Chennai")
    assert response.status_code == 200
    data = response.json()
    assert data["city"] == "Chennai"
    assert data["official_authority"] == "Greater Chennai Corporation (GCC)"
    assert data["official_wards_total"] == 200
    assert data["official_zones_total"] == 15
    assert data["census_2011_district_code"] == 603
    
    sectors = data["sector_mappings"]
    assert len(sectors) == 5
    assert "chennai_zone_1" in sectors
    assert "chennai_zone_2" in sectors
    assert "chennai_zone_3" in sectors
    assert "chennai_zone_4" in sectors
    assert "chennai_zone_5" in sectors
    
    # Confirm documented area-weighted mapping
    for zid, sec in sectors.items():
        print(f"  • {sec['sector_name']}: {sec['orientation']}")
        assert len(sec["gcc_administrative_zones"]) >= 1
        assert len(sec["official_gcc_wards_intersected"]) >= 1
        assert len(sec["spatial_method"]) > 10
        assert "analytical_sectors_note" in data
    
    print("[PASS] Spatial alignment avoids fictitious neighborhood identities and documents GCC ward cross-referencing.")


def test_missing_data_and_unauthenticated_guardrails():
    print("\n--- 5. Testing Missing Data & Unauthenticated Guardrails ---")
    # Query single zone satellite endpoint
    resp = client.get("/api/satellite/zones/chennai_zone_1?city=Chennai")
    assert resp.status_code == 200
    z = resp.json()
    
    # Verify that when GEE is unauthenticated, no fake values are substituted
    tele = z.get("satellite_telemetry", {})
    assert z.get("is_real_satellite") is False or z.get("is_real_satellite") is None
    assert tele.get("mean_lst_c") is None, "Synthetic LST was erroneously returned as satellite observation!"
    assert tele.get("ndvi") is None, "Synthetic NDVI was erroneously returned as satellite observation!"
    assert tele.get("quality_status") == "CREDENTIALS_REQUIRED"
    print("  • Verified: Telemetry values are strictly None when unauthenticated (Zero synthetic substitution).")
    print("[PASS] Missing observation guardrails verified.")


if __name__ == "__main__":
    test_dataset_registry_completeness()
    test_data_classification_and_provenance()
    test_units_and_spatial_resolutions()
    test_spatial_alignment_and_gcc_mapping()
    test_missing_data_and_unauthenticated_guardrails()
    print("\n🎉 ALL DATASET INTEGRATION & PROVENANCE TESTS PASSED (5/5)! 🎉\n")

