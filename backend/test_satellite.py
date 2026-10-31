"""
test_satellite.py - Comprehensive verification of Google Earth Engine integration,
satellite endpoints, zonal calculations, and data provenance.
"""
import sys
import os

# Set UTF-8 encoding for stdout on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_satellite_status():
    print("\n--- 1. Testing GET /api/satellite/status ---")
    response = client.get("/api/satellite/status")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    print("Status response:", data)
    assert "status" in data
    assert "authenticated" in data
    assert "supported_datasets" in data
    dataset_ids = [d["id"] for d in data["supported_datasets"]]
    assert "LANDSAT/LC08/C02/T1_L2" in dataset_ids
    assert "COPERNICUS/S2_SR_HARMONIZED" in dataset_ids
    assert "MODIS/061/MOD11A1" in dataset_ids
    print("✓ Satellite status test passed.")

def test_satellite_city():
    print("\n--- 2. Testing GET /api/satellite/city?city=Chennai ---")
    response = client.get("/api/satellite/city?city=Chennai")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    print("City:", data.get("city"), "Coords:", data.get("coordinates"))
    assert data.get("city") == "Chennai"
    assert "coordinates" in data
    assert "status" in data
    assert "layers" in data
    assert "lst" in data["layers"]
    assert "ndvi" in data["layers"]
    assert "ndwi" in data["layers"]
    assert "ndbi" in data["layers"]
    print("✓ Satellite city endpoint test passed.")

def test_satellite_zones():
    print("\n--- 3. Testing GET /api/satellite/zones?city=Chennai ---")
    response = client.get("/api/satellite/zones?city=Chennai")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data.get("city") == "Chennai"
    assert data.get("zone_count") == 5
    assert len(data.get("zones", [])) == 5
    for z in data["zones"]:
        print(f"Zone: {z['zone_name']} ({z['zone_id']}) - Quality: {z.get('quality_status')}")
        assert "zone_id" in z
        assert "zone_name" in z
        assert "mean_lst_c" in z
        assert "ndvi" in z
        assert "ndwi" in z
        assert "ndbi" in z
        assert "polygon" in z
        assert len(z["polygon"]) >= 5
    print("✓ Satellite zones endpoint test passed.")

def test_single_zone_satellite():
    print("\n--- 4. Testing GET /api/satellite/zones/{zone_id} ---")
    response = client.get("/api/satellite/zones/chennai_zone_1?city=Chennai")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    z = response.json()
    print("Single zone response:", z["zone_name"], "Status:", z.get("quality_status"))
    assert z["zone_id"] == "chennai_zone_1"
    assert "Central Urban Core" in z["zone_name"]
    print("✓ Single zone satellite endpoint test passed.")

def test_satellite_tiles():
    print("\n--- 5. Testing GET /api/satellite/tiles ---")
    response = client.get("/api/satellite/tiles?lat=13.0827&lon=80.2707")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    tiles = data.get("tiles", {})
    print("Tile layers returned:", list(tiles.keys()))
    assert "lst" in tiles
    assert "ndvi" in tiles
    assert "ndwi" in tiles
    assert "ndbi" in tiles
    for k, layer in tiles.items():
        assert "name" in layer
        assert "palette" in layer
        assert "resolution" in layer or "resolution_m" in layer
    print("✓ Satellite tiles test passed.")

def test_city_data_provenance_and_sectors():
    print("\n--- 6. Testing GET /api/city-data provenance & geographic sectors ---")
    response = client.get("/api/city-data?city=Chennai&country=India&lat=13.0827&lon=80.2707")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    
    assert "earth_engine_status" in data
    assert "satellite_layers" in data
    zones = data.get("zones", [])
    assert len(zones) == 5
    
    # Check that sectors are geographically named (no fictional Solaria names)
    zone_names = [z["name"] for z in zones]
    print("Geographic Sector Names:", zone_names)
    assert any("Central" in name for name in zone_names)
    assert any("Northern" in name for name in zone_names)
    assert any("Southern" in name for name in zone_names)
    assert any("Eastern" in name for name in zone_names)
    assert any("Western" in name for name in zone_names)
    
    # Verify explicit data classifications
    for z in zones:
        assert "data_sources" in z, f"Missing data_sources in {z['name']}"
        sources = z["data_sources"]
        assert "satellite_derived" in sources
        assert "weather_api" in sources
        assert "demographic_dataset" in sources
        assert "infrastructure_dataset" in sources
        assert "calculated_estimates" in sources
        assert "satellite_telemetry" in z
        sat = z["satellite_telemetry"]
        assert "mean_lst_c" in sat
        assert "ndvi" in sat
        assert "ndwi" in sat
        assert "ndbi" in sat
    
    print("✓ City data provenance & geographic sectors test passed.")

if __name__ == "__main__":
    test_satellite_status()
    test_satellite_city()
    test_satellite_zones()
    test_single_zone_satellite()
    test_satellite_tiles()
    test_city_data_provenance_and_sectors()
    print("\n🎉 ALL SATELLITE & DATA PROVENANCE TESTS PASSED SUCCESSFULLY! 🎉\n")
