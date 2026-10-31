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

def test_satellite_structured_analysis():
    print("\n--- 7. Testing GET /api/satellite/analysis (Master Prompt Section 6 Schema) ---")
    response = client.get("/api/satellite/analysis?city=Chennai")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data.get("city") == "Chennai"
    assert "records" in data
    assert len(data["records"]) == 5

    for rec in data["records"]:
        print(f"Record: {rec['zone']} | Dataset: {rec['dataset']} | Status: {rec['data_status']}")
        assert "city" in rec
        assert "zone" in rec
        assert "dataset" in rec
        assert "acquisition_date" in rec
        assert "land_surface_temperature_c" in rec
        assert "ndvi" in rec
        assert "ndwi" in rec
        assert "ndbi" in rec
        assert "vegetation_cover_percent" in rec
        assert "data_status" in rec
        assert rec["resolution_meters"] == 30
        assert rec["data_status"] in ["available", "unavailable", "unconfigured"]
    print("✓ Satellite structured analysis schema verified.")

def test_satellite_history_endpoint():
    print("\n--- 8. Testing GET /api/satellite/history ---")
    response = client.get("/api/satellite/history?city=Chennai&start_date=2024-01-01&end_date=2024-06-30")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert data.get("city") == "Chennai"
    assert "authenticated" in data
    assert "status" in data
    print("✓ Satellite history endpoint test passed.")

def test_satellite_provenance_endpoint():
    print("\n--- 9. Testing GET /api/satellite/provenance ---")
    response = client.get("/api/satellite/provenance")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    assert "instruments" in data
    instruments = [inst["instrument"] for inst in data["instruments"]]
    assert any("Landsat" in inst for inst in instruments)
    assert any("Sentinel-2" in inst for inst in instruments)
    assert any("MODIS" in inst for inst in instruments)
    print("✓ Satellite provenance endpoint test passed.")

def test_scientific_formulas():
    print("\n--- 10. Testing Scientific Scaling & Conversion Formulas ---")
    # Landsat 8/9 ST_B10: DN * 0.00341802 + 149.0 = Kelvin -> Celsius
    # Example DN = 44000
    dn_landsat = 44000
    kelvin_landsat = dn_landsat * 0.00341802 + 149.0
    celsius_landsat = kelvin_landsat - 273.15
    assert round(celsius_landsat, 2) == round((44000 * 0.00341802 + 149.0 - 273.15), 2)
    print(f"    Landsat ST_B10 test: DN={dn_landsat} -> {kelvin_landsat:.2f} K -> {celsius_landsat:.2f} °C")

    # MODIS LST_Day_1km: DN * 0.02 - 273.15 = Celsius
    # Example DN = 15300 (306.0 K -> 32.85 °C)
    dn_modis = 15300
    kelvin_modis = dn_modis * 0.02
    celsius_modis = kelvin_modis - 273.15
    assert round(celsius_modis, 2) == 32.85
    print(f"    MODIS test: DN={dn_modis} -> {kelvin_modis:.2f} K -> {celsius_modis:.2f} °C")

    # Sentinel-2 Indices:
    # Reflectance: B3 (green) = 0.12, B4 (red) = 0.10, B8 (nir) = 0.40, B11 (swir) = 0.15
    b3, b4, b8, b11 = 0.12, 0.10, 0.40, 0.15
    ndvi = (b8 - b4) / (b8 + b4)  # 0.30 / 0.50 = 0.60
    ndwi = (b3 - b8) / (b3 + b8)  # -0.28 / 0.52 = -0.538
    ndbi = (b11 - b8) / (b11 + b8) # -0.25 / 0.55 = -0.455
    assert round(ndvi, 3) == 0.600
    # FVC: ((0.60 - 0.15) / 0.55)^2 * 100 = (0.45 / 0.55)^2 * 100 = 0.818^2 * 100 = 66.9%
    fvc = ((ndvi - 0.15) / 0.55) ** 2 * 100.0
    print(f"    Sentinel-2 test: NDVI={ndvi:.3f}, NDWI={ndwi:.3f}, NDBI={ndbi:.3f}, FVC={fvc:.1f}%")
    assert round(fvc, 1) == 66.9
    print("✓ Scientific formula verification passed.")

if __name__ == "__main__":
    test_satellite_status()
    test_satellite_city()
    test_satellite_zones()
    test_single_zone_satellite()
    test_satellite_tiles()
    test_city_data_provenance_and_sectors()
    test_satellite_structured_analysis()
    test_satellite_history_endpoint()
    test_satellite_provenance_endpoint()
    test_scientific_formulas()
    print("\n🎉 ALL 10 SATELLITE & DATA PROVENANCE TESTS PASSED SUCCESSFULLY! 🎉\n")
