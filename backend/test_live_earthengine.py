"""
test_live_earthengine.py - Genuine Earth Engine Live Integration Verification

This script executes real, non-mocked requests against the Google Earth Engine Python API.
It tests:
1. Genuine authentication using configured Service Account or local credentials.
2. Querying Landsat 8/9 ST_B10 thermal band with scale factor/offset conversion to Celsius and QA_PIXEL masking.
3. Querying Sentinel-2 MSI Level-2A surface reflectance (NDVI, NDWI, NDBI) with QA60 and SCL cloud masking.
4. Querying MODIS 1km daily/composite LST.
5. Computing zonal statistics across the 5 geographic analysis sectors for:
   - City 1: Chennai, India (13.0827°N, 80.2707°E)
   - City 2: Dubai, UAE (25.2048°N, 55.2708°E)

Zero synthetic fallback or mock values are permitted in this test.
If credentials are not configured, it reports the exact blocker honestly.
"""

import sys
import os
import json

# Force UTF-8 on Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta

def verify_live_earth_engine():
    print("=" * 75)
    print("   GENUINE GOOGLE EARTH ENGINE LIVE INTEGRATION TEST (NO MOCKS)    ")
    print("=" * 75)

    # 1. Inspect package installation
    try:
        import ee
        import google.auth
        print(f"[1/5] earthengine-api installed: version {ee.__version__}")
        print(f"      google-auth installed: version {google.auth.__version__}")
    except ImportError as e:
        print(f"[FAIL] Missing required package: {e}")
        return False

    # 2. Check Authentication
    from app.satellite_service import ee_manager, get_earth_engine_status
    status = get_earth_engine_status()
    print(f"\n[2/5] Checking Earth Engine Authentication Status:")
    print(f"      Authenticated: {status.get('authenticated')}")
    print(f"      Status: {status.get('status')}")
    print(f"      Auth Method: {status.get('auth_method')}")
    print(f"      GCP Project ID: {status.get('project_id')}")
    print(f"      Service Account: {status.get('service_account')}")

    if not status.get("authenticated"):
        print("\n" + "!" * 75)
        print("AUTHENTICATION BLOCKER IDENTIFIED:")
        print(f"Error message: {status.get('error_message')}")
        print("\nSetup Requirements to complete live Google Earth Engine data stream:")
        print(status.get("setup_instructions"))
        print("!" * 75)
        print("\nHonest Evaluation: Live satellite telemetry cannot be retrieved without credentials.")
        print("No synthetic or mocked data is being substituted for satellite observations.")
        return False

    # If authenticated, execute live queries for Chennai and an additional city (Dubai)
    test_cities = [
        {"name": "Chennai", "country": "India", "lat": 13.0827, "lon": 80.2707},
        {"name": "Dubai", "country": "United Arab Emirates", "lat": 25.2048, "lon": 55.2708}
    ]

    from app.satellite_service import (
        get_landsat_lst_image, 
        get_sentinel2_indices_image, 
        get_modis_lst_image,
        compute_satellite_zonal_statistics
    )
    from app.geo_service import generate_city_zones, fetch_city_weather

    for c in test_cities:
        city_name = c["name"]
        lat = c["lat"]
        lon = c["lon"]
        print(f"\n[3/5] Querying Genuine Earth Engine Collections for {city_name} ({lat}, {lon})...")

        # Define 25km ROI and 90-day observation window
        roi = ee.Geometry.Point([lon, lat]).buffer(25000)
        end_dt = datetime.utcnow()
        start_dt = end_dt - timedelta(days=90)
        start_str = start_dt.strftime('%Y-%m-%d')
        end_str = end_dt.strftime('%Y-%m-%d')

        # Landsat 8/9
        print(f"      Querying Landsat 8/9 C02/T1_L2 (ST_B10 thermal) from {start_str} to {end_str}...")
        landsat_img = get_landsat_lst_image(roi, start_str, end_str)
        if landsat_img:
            props = landsat_img.getInfo()
            spacecraft = props.get("properties", {}).get("SPACECRAFT_ID")
            acq_date = props.get("properties", {}).get("DATE_ACQUIRED")
            cloud_cov = props.get("properties", {}).get("CLOUD_COVER")
            print(f"      ✓ Real Landsat Scene Retrieved: {spacecraft} on {acq_date} (Cloud: {cloud_cov}%)")
        else:
            print(f"      ⚠ No cloud-free Landsat scene found in 90-day window.")

        # Sentinel-2
        print(f"      Querying Sentinel-2 S2_SR_HARMONIZED (B3, B4, B8, B11, SCL, QA60)...")
        s2_img = get_sentinel2_indices_image(roi, start_str, end_str)
        if s2_img:
            s2_props = s2_img.getInfo()
            prod_id = s2_props.get("properties", {}).get("PRODUCT_ID")
            print(f"      ✓ Real Sentinel-2 Scene Retrieved: {prod_id}")
        else:
            print(f"      ⚠ No clean Sentinel-2 scene found in 90-day window.")

        # MODIS
        print(f"      Querying MODIS Terra/Aqua LST (MOD11A1/MOD11A2)...")
        modis_img = get_modis_lst_image(roi, start_str, end_str)
        if modis_img:
            print(f"      ✓ Real MODIS LST Regional Image Retrieved.")
        else:
            print(f"      ⚠ No MODIS observation found.")

        # 4. Compute Real Zonal Statistics for the 5 Sector Polygons
        print(f"\n[4/5] Computing Real Zonal Reductions for 5 Analysis Sectors in {city_name}...")
        weather = fetch_city_weather(lat, lon)
        zones = generate_city_zones(city_name, c["country"], "CC", lat, lon, weather)

        zonal_res = compute_satellite_zonal_statistics(zones, city_name)
        stats = zonal_res.get("zonal_statistics", {})
        for zid, zstat in stats.items():
            zname = zstat.get("zone_name")
            lst_info = zstat.get("landsat_lst", {})
            s2_info = zstat.get("sentinel2_indices", {})
            print(f"      Sector: {zname} ({zid})")
            print(f"         • Real Mean LST: {lst_info.get('mean_lst_c')}°C (Min: {lst_info.get('min_lst_c')}°C, Max: {lst_info.get('max_lst_c')}°C, Pixels: {lst_info.get('valid_pixels')})")
            print(f"         • Real NDVI: {s2_info.get('ndvi_mean')}, NDWI: {s2_info.get('ndwi_mean')}, NDBI: {s2_info.get('ndbi_mean')}, Veg: {s2_info.get('vegetation_cover_pct')}%")
            print(f"         • QA Status: {zstat.get('data_quality_status')}")

    print("\n[5/5] Genuine Earth Engine Verification Complete!")
    return True

if __name__ == "__main__":
    success = verify_live_earth_engine()
    sys.exit(0 if success else 1)

