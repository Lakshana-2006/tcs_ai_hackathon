import math
import requests
from typing import Dict, Any, List, Optional
from app.satellite_service import (
    compute_satellite_zonal_statistics,
    get_earth_engine_status,
    ee_manager
)

# Supported major currencies mapping by country / country_code
CURRENCY_MAP = {
    "IN": {"code": "INR", "symbol": "₹", "name": "Indian Rupee", "rate_per_usd": 83.5, "default_budget": 25000000},
    "JP": {"code": "JPY", "symbol": "¥", "name": "Japanese Yen", "rate_per_usd": 155.0, "default_budget": 500000000},
    "GB": {"code": "GBP", "symbol": "£", "name": "British Pound", "rate_per_usd": 0.79, "default_budget": 2500000},
    "US": {"code": "USD", "symbol": "$", "name": "US Dollar", "rate_per_usd": 1.0, "default_budget": 3500000},
    "AE": {"code": "AED", "symbol": "AED", "name": "UAE Dirham", "rate_per_usd": 3.67, "default_budget": 12000000},
    "EU": {"code": "EUR", "symbol": "€", "name": "Euro", "rate_per_usd": 0.92, "default_budget": 3000000},
    "DE": {"code": "EUR", "symbol": "€", "name": "Euro", "rate_per_usd": 0.92, "default_budget": 3000000},
    "FR": {"code": "EUR", "symbol": "€", "name": "Euro", "rate_per_usd": 0.92, "default_budget": 3000000},
    "ES": {"code": "EUR", "symbol": "€", "name": "Euro", "rate_per_usd": 0.92, "default_budget": 3000000},
    "IT": {"code": "EUR", "symbol": "€", "name": "Euro", "rate_per_usd": 0.92, "default_budget": 3000000},
    "AU": {"code": "AUD", "symbol": "A$", "name": "Australian Dollar", "rate_per_usd": 1.52, "default_budget": 5000000},
    "CA": {"code": "CAD", "symbol": "C$", "name": "Canadian Dollar", "rate_per_usd": 1.38, "default_budget": 4500000},
    "SG": {"code": "SGD", "symbol": "S$", "name": "Singapore Dollar", "rate_per_usd": 1.34, "default_budget": 4500000},
    "BR": {"code": "BRL", "symbol": "R$", "name": "Brazilian Real", "rate_per_usd": 5.70, "default_budget": 18000000},
    "ZA": {"code": "ZAR", "symbol": "R", "name": "South African Rand", "rate_per_usd": 18.2, "default_budget": 60000000},
}

DEFAULT_CURRENCY = {"code": "USD", "symbol": "$", "name": "US Dollar", "rate_per_usd": 1.0, "default_budget": 3500000}

FALLBACK_CITIES = [
    {"name": "Chennai", "country": "India", "country_code": "IN", "admin1": "Tamil Nadu", "latitude": 13.0827, "longitude": 80.2707},
    {"name": "Mumbai", "country": "India", "country_code": "IN", "admin1": "Maharashtra", "latitude": 19.0760, "longitude": 72.8777},
    {"name": "Tokyo", "country": "Japan", "country_code": "JP", "admin1": "Tokyo", "latitude": 35.6762, "longitude": 139.6503},
    {"name": "London", "country": "United Kingdom", "country_code": "GB", "admin1": "England", "latitude": 51.5074, "longitude": -0.1278},
    {"name": "Dubai", "country": "United Arab Emirates", "country_code": "AE", "admin1": "Dubai", "latitude": 25.2048, "longitude": 55.2708},
    {"name": "New York", "country": "United States", "country_code": "US", "admin1": "New York", "latitude": 40.7128, "longitude": -74.0060},
    {"name": "Singapore", "country": "Singapore", "country_code": "SG", "admin1": "Singapore", "latitude": 1.3521, "longitude": 103.8198},
    {"name": "Paris", "country": "France", "country_code": "FR", "admin1": "Île-de-France", "latitude": 48.8566, "longitude": 2.3522},
    {"name": "Sydney", "country": "Australia", "country_code": "AU", "admin1": "New South Wales", "latitude": -33.8688, "longitude": 151.2093},
    {"name": "Cairo", "country": "Egypt", "country_code": "EG", "admin1": "Cairo", "latitude": 30.0444, "longitude": 31.2357},
]


def get_currency_for_country(country_code: Optional[str]) -> Dict[str, Any]:
    if not country_code:
        return DEFAULT_CURRENCY
    code_upper = country_code.upper()
    return CURRENCY_MAP.get(code_upper, DEFAULT_CURRENCY)


def geocode_city_search(query: str) -> List[Dict[str, Any]]:
    """
    Searches worldwide cities using Open-Meteo Geocoding API with fallback.
    """
    q = query.strip()
    if not q:
        return []

    results = []
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={requests.utils.quote(q)}&count=8&language=en&format=json"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json().get("results", [])
            for item in data:
                c_code = item.get("country_code", "US")
                curr = get_currency_for_country(c_code)
                results.append({
                    "id": f"{item.get('name', 'City').lower().replace(' ', '_')}_{item.get('id', '')}",
                    "name": item.get("name"),
                    "country": item.get("country", ""),
                    "country_code": c_code,
                    "admin1": item.get("admin1", ""),
                    "latitude": round(item.get("latitude"), 4),
                    "longitude": round(item.get("longitude"), 4),
                    "timezone": item.get("timezone", "UTC"),
                    "population": item.get("population", 0),
                    "display_name": f"{item.get('name')}, {item.get('admin1') + ', ' if item.get('admin1') else ''}{item.get('country')}",
                    "currency": curr
                })
    except Exception as e:
        print(f"Geocoding API network issue: {e}. Falling back to internal directory.")

    if not results:
        q_lower = q.lower()
        matched = [c for c in FALLBACK_CITIES if q_lower in c["name"].lower() or q_lower in c["country"].lower()]
        for item in (matched if matched else FALLBACK_CITIES[:4]):
            curr = get_currency_for_country(item["country_code"])
            results.append({
                "id": f"{item['name'].lower()}_fallback",
                "name": item["name"],
                "country": item["country"],
                "country_code": item["country_code"],
                "admin1": item["admin1"],
                "latitude": item["latitude"],
                "longitude": item["longitude"],
                "timezone": "UTC",
                "population": 2500000,
                "display_name": f"{item['name']}, {item['admin1']}, {item['country']}",
                "currency": curr
            })

    return results


def fetch_city_weather(latitude: float, longitude: float) -> Dict[str, Any]:
    """
    Retrieves real-time global weather from Open-Meteo for the selected coordinates.
    """
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}&"
            f"current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m&"
            f"timezone=auto"
        )
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            raw = resp.json().get("current", {})
            temp = raw.get("temperature_2m", 25.0)
            rh = raw.get("relative_humidity_2m", 50.0)
            app_temp = raw.get("apparent_temperature", temp)
            time_str = raw.get("time", "latest")

            code = raw.get("weather_code", 0)
            desc_map = {
                0: "Clear Sky", 1: "Mainly Clear", 2: "Partly Cloudy", 3: "Overcast",
                45: "Foggy", 51: "Light Drizzle", 61: "Slight Rain", 63: "Moderate Rain",
                65: "Heavy Rain", 80: "Rain Showers", 95: "Thunderstorm"
            }
            condition = desc_map.get(code, "Clear to Partly Cloudy")

            return {
                "status": "success",
                "air_temperature_c": round(temp, 1),
                "relative_humidity_pct": round(rh, 1),
                "apparent_temperature_c": round(app_temp, 1),
                "wind_speed_kmh": round(raw.get("wind_speed_10m", 10.0), 1),
                "precipitation_mm": round(raw.get("precipitation", 0.0), 1),
                "condition": condition,
                "timestamp": time_str,
                "data_source": "Open-Meteo Global Weather API",
                "measurement_notice": "Air temperature measured at 2m reference height. Not land-surface temperature."
            }
    except Exception as e:
        print(f"Weather API error: {e}")

    return {
        "status": "fallback",
        "air_temperature_c": 28.5,
        "relative_humidity_pct": 62.0,
        "apparent_temperature_c": 31.8,
        "wind_speed_kmh": 12.0,
        "precipitation_mm": 0.0,
        "condition": "Sensors Offline (Fallback Mode)",
        "timestamp": "Latest Cached",
        "data_source": "Open-Meteo (Offline Cache)",
        "measurement_notice": "Air temperature fallback approximation."
    }


def generate_city_zones(
    city_name: str,
    country: str,
    country_code: str,
    lat: float,
    lon: float,
    weather: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Generates 5 illustrative analysis zones mathematically centered around the selected city coordinates.
    Includes all requested heat & environmental, population & vulnerability, and infrastructure parameters.
    """
    rad_lat = math.radians(lat)
    cos_lat = max(0.2, math.cos(rad_lat))
    deg_per_km_lat = 1.0 / 111.0
    deg_per_km_lon = 1.0 / (111.0 * cos_lat)

    current_air_temp = weather.get("air_temperature_c", 28.0)
    apparent_temp = weather.get("apparent_temperature_c", current_air_temp)
    humidity = weather.get("relative_humidity_pct", 55.0)
    weather_time = weather.get("timestamp", "latest")
    weather_source = weather.get("data_source", "Open-Meteo Global Weather API")

    city_slug = city_name.lower().replace(" ", "_").replace("-", "_")

    # Geographically defined spatial analysis sectors around the geocoded city coordinates
    spatial_sectors = [
        {
            "suffix": "zone_1",
            "name": f"{city_name} — Central Urban Core Sector",
            "short_name": "Central Core",
            "type": "Dense Commercial & Urban Core",
            "d_lat_km": 0.0,
            "d_lon_km": 0.0,
            "radius_km": 2.0,
            "canopy_cover": 10.5,
            "elderly_pct": 14.5,
            "children_pct": 7.2,
            "outdoor_worker_pct": 18.0,
            "poverty_rate": 16.5,
            "ac_penetration": 84.0,
            "pop": 145000,
            "commuters": 95000,
            "area_km2": 5.2,
            "building_density": "Very High (88% Built Footprint)",
            "water_availability": "Adequate (Pressurized Municipal Grid & Hydrants)",
            "hospital_availability": "4 Major Hospitals (920 Acute Beds • 24/7 Heat Triage)",
            "cooling_facility_availability": "3 Operational Facilities (HVAC Transit Hubs)",
            "land_use_classification": "Commercial / High-Rise Office & Transit Concourse",
            "power_demand": "165 MW (High Peak A/C Strain)",
            "adaptive_capacity_score": 68.0,
            "adaptive_capacity_rating": "Moderate-High (Hospital infrastructure, high AC)",
            "drivers": [
                "Intense urban canyon geometry with concentrated heat retention",
                "High density of pedestrian commuters and outdoor transit hubs",
                "Predominantly impervious paved surfaces with sparse shade canopy"
            ],
            "priorities": ["cool_roofs", "green_corridors", "tree_planting"]
        },
        {
            "suffix": "zone_2",
            "name": f"{city_name} — Northern Urban Sector",
            "short_name": "Northern Sector",
            "type": "Northern Freight & Manufacturing Corridor",
            "d_lat_km": 3.6,
            "d_lon_km": 0.4,
            "radius_km": 2.4,
            "canopy_cover": 7.0,
            "elderly_pct": 9.5,
            "children_pct": 7.5,
            "outdoor_worker_pct": 44.0,
            "poverty_rate": 27.0,
            "ac_penetration": 52.0,
            "pop": 72000,
            "commuters": 52000,
            "area_km2": 8.5,
            "building_density": "High (76% Impervious Industrial Yards & Warehouses)",
            "water_availability": "Constrained (Industrial Greywater • Low Hydrant Density)",
            "hospital_availability": "1 Urgent Care Clinic (35 Beds)",
            "cooling_facility_availability": "0 Dedicated Facilities (Critical Worker Sanctuary Gap)",
            "land_use_classification": "Industrial Logistics & Transportation Hub",
            "power_demand": "220 MW (Industrial Baseload & HVAC Exhaust)",
            "adaptive_capacity_score": 38.0,
            "adaptive_capacity_rating": "Deficient (Zero cooling shelters, high outdoor labor)",
            "drivers": [
                "Extensive dark metal roofs and paved asphalt logistics yards",
                "High concentration of outdoor labor workforce during daytime peak heat",
                "Low vegetative shading contributing to nocturnal thermal storage"
            ],
            "priorities": ["cool_roofs", "permeable_pavements", "cooling_centers"]
        },
        {
            "suffix": "zone_3",
            "name": f"{city_name} — Southern Mixed Sector",
            "short_name": "Southern Sector",
            "type": "Dense Residential & Commercial District",
            "d_lat_km": -3.6,
            "d_lon_km": -0.5,
            "radius_km": 2.3,
            "canopy_cover": 12.0,
            "elderly_pct": 28.5,
            "children_pct": 13.5,
            "outdoor_worker_pct": 24.0,
            "poverty_rate": 34.0,
            "ac_penetration": 42.0,
            "pop": 182000,
            "commuters": 30000,
            "area_km2": 6.8,
            "building_density": "Extremely Dense (Narrow Streets • 90% Ground Coverage)",
            "water_availability": "Vulnerable (Aging Municipal Mains • Intermittent Supply)",
            "hospital_availability": "1 Community Clinic (60 Beds • Surge Deficit)",
            "cooling_facility_availability": "1 Community Center (250 capacity • Overburdened)",
            "land_use_classification": "Dense Mixed Residential & Street Commerce",
            "power_demand": "92 MW (Aging Transformer Infrastructure)",
            "adaptive_capacity_score": 26.0,
            "adaptive_capacity_rating": "Critically Deficient (High senior density, 58% lack AC)",
            "drivers": [
                "Highest demographic vulnerability: 28.5% elderly residents and high poverty",
                "Uninsulated housing stock with severe deficit in mechanical cooling",
                "Critical priority for emergency medical cooling hub deployment"
            ],
            "priorities": ["cooling_centers", "tree_planting", "cool_roofs"]
        },
        {
            "suffix": "zone_4",
            "name": f"{city_name} — Eastern Sector",
            "short_name": "Eastern Sector",
            "type": "Eastern Coastal / Corridor Sector",
            "d_lat_km": 0.6,
            "d_lon_km": 4.0,
            "radius_km": 2.4,
            "canopy_cover": 23.0,
            "elderly_pct": 16.0,
            "children_pct": 9.0,
            "outdoor_worker_pct": 15.0,
            "poverty_rate": 15.5,
            "ac_penetration": 82.0,
            "pop": 96000,
            "commuters": 34000,
            "area_km2": 7.2,
            "building_density": "Moderate (60% Built Footprint)",
            "water_availability": "Abundant (Pressurized Municipal Infrastructure)",
            "hospital_availability": "2 General Hospitals (380 Acute Beds)",
            "cooling_facility_availability": "2 Waterfront Civic Hubs (800 capacity)",
            "land_use_classification": "Mixed Waterfront Promenade & Residential Sector",
            "power_demand": "74 MW (Moderate Residential Load)",
            "adaptive_capacity_score": 72.0,
            "adaptive_capacity_rating": "Substantial (Moderate natural ventilation buffer)",
            "drivers": [
                "Benefits from local water breeze and maritime thermal moderation",
                "Localized heat retention along unshaded commercial arterial roads",
                "Balanced socio-economic adaptive capacity with reliable healthcare"
            ],
            "priorities": ["tree_planting", "green_corridors"]
        },
        {
            "suffix": "zone_5",
            "name": f"{city_name} — Western Sector",
            "short_name": "Western Sector",
            "type": "Western Suburban & Park Buffer",
            "d_lat_km": -0.5,
            "d_lon_km": -4.0,
            "radius_km": 2.6,
            "canopy_cover": 41.0,
            "elderly_pct": 12.0,
            "children_pct": 13.5,
            "outdoor_worker_pct": 8.0,
            "poverty_rate": 8.5,
            "ac_penetration": 94.0,
            "pop": 78000,
            "commuters": 45000,
            "area_km2": 9.5,
            "building_density": "Low-Moderate (34% Built Footprint • Campus Style)",
            "water_availability": "High (Municipal & Reclaimed Stormwater Systems)",
            "hospital_availability": "1 Academic Medical Center (450 State-of-the-Art Beds)",
            "cooling_facility_availability": "4 Modern Civic Hubs (2,200 capacity)",
            "land_use_classification": "Low-Density Residential & Suburban Parklands",
            "power_demand": "56 MW (Modern Energy Efficiency Standards)",
            "adaptive_capacity_score": 86.0,
            "adaptive_capacity_rating": "Resilient (High canopy, modern infrastructure)",
            "drivers": [
                "Substantial natural vegetation cover (41%) providing evapotranspirative shade",
                "Modern building envelopes with high thermal efficiency and cooling",
                "Serves as benchmark baseline resilience zone for the urban area"
            ],
            "priorities": ["green_corridors", "permeable_pavements"]
        }
    ]

    zones: List[Dict[str, Any]] = []

    for sector in spatial_sectors:
        zid = f"{city_slug}_{sector['suffix']}"
        c_lat = lat + (sector["d_lat_km"] * deg_per_km_lat)
        c_lon = lon + (sector["d_lon_km"] * deg_per_km_lon)

        r_lat = sector["radius_km"] * deg_per_km_lat
        r_lon = sector["radius_km"] * deg_per_km_lon

        # Generate realistic 8-vertex organic polygon around the sector centroid
        angles = [0.0, 0.785, 1.571, 2.356, 3.142, 3.927, 4.712, 5.498]
        radii_offsets = [1.0, 0.88, 1.05, 0.92, 1.02, 0.85, 0.98, 1.06]
        polygon = []
        for i, a in enumerate(angles):
            scale = radii_offsets[i % len(radii_offsets)]
            p_lat = round(c_lat + r_lat * scale * math.sin(a), 4)
            p_lon = round(c_lon + r_lon * scale * math.cos(a), 4)
            polygon.append([p_lat, p_lon])

        # Baseline environmental approximations (used when GEE is offline or unconfigured)
        fallback_uhi = 3.5 if sector["suffix"] == "zone_1" else (4.2 if sector["suffix"] == "zone_2" else (3.8 if sector["suffix"] == "zone_3" else (1.8 if sector["suffix"] == "zone_4" else 0.8)))

        density = int(sector["pop"] / sector["area_km2"])
        exposure_raw = (density / 450.0) + (sector["outdoor_worker_pct"] * 0.75) + (sector["commuters"] / 4000.0)
        exposure_score = round(max(15.0, min(95.0, exposure_raw)), 1)

        canopy_deficit = 100.0 - sector["canopy_cover"]
        ac_deficit = 100.0 - sector["ac_penetration"]
        svi_score = round((sector["poverty_rate"] * 1.2) + (sector["elderly_pct"] * 1.5), 1)

        vuln_raw = (
            (canopy_deficit * 0.32) +
            (sector["elderly_pct"] * 0.30) +
            (sector["poverty_rate"] * 0.22) +
            (ac_deficit * 0.16)
        )
        vuln_score = round(max(15.0, min(95.0, vuln_raw)), 1)

        hazard_raw = (
            (current_air_temp * 1.2) +
            ((apparent_temp - current_air_temp) * 2.0) +
            (fallback_uhi * 4.2)
        )
        hazard_score = round(max(15.0, min(96.0, hazard_raw)), 1)

        risk_unadjusted = (0.35 * hazard_score) + (0.30 * exposure_score) + (0.35 * vuln_score)
        adaptive_buffer = (sector["adaptive_capacity_score"] / 100.0) * 4.0
        risk = round(max(10.0, min(98.0, risk_unadjusted - adaptive_buffer)), 1)

        elderly_count = int(sector["pop"] * (sector["elderly_pct"] / 100.0))
        children_count = int(sector["pop"] * (sector["children_pct"] / 100.0))
        outdoor_count = int(sector["pop"] * (sector["outdoor_worker_pct"] / 100.0))

        zone_dict = {
            "id": zid,
            "city": city_name,
            "country": country,
            "country_code": country_code,
            "name": sector["name"],
            "short_name": sector["short_name"],
            "type": sector["type"],
            "centroid": [round(c_lat, 4), round(c_lon, 4)],
            "polygon": polygon,
            "population": sector["pop"],
            "daytime_commuters": sector["commuters"],
            "area_km2": sector["area_km2"],
            "baseline_risk": risk,
            "is_real_satellite": False,
            "satellite_status": "UNAUTHENTICATED (Setup Required)",
            "data_quality_status": "UNAUTHENTICATED_DEMO_BASELINE",
            "data_source_labels": {
                "environmental": "Open-Meteo Real-time API",
                "satellite": "Google Earth Engine (Unconfigured in backend/.env)",
                "demographic": "Municipal Demographic Estimate (Synthetic Baseline)",
                "infrastructure": "Municipal Infrastructure Survey (Synthetic Baseline)",
                "risk_score": "Calculated IPCC Composite Multi-Criteria Index"
            },
            "data_sources": {
                "satellite_derived": "Google Earth Engine (Landsat 8/9 ST_B10, Sentinel-2 MSI, MODIS)",
                "weather_api": "Open-Meteo Real-Time Weather API",
                "demographic_dataset": "Municipal Demographic & Census Baseline",
                "infrastructure_dataset": "Municipal Infrastructure Survey",
                "calculated_estimates": "Calculated Multi-Criteria Risk Model"
            },
            "satellite_telemetry": {
                "mean_lst_c": None,
                "min_lst_c": None,
                "max_lst_c": None,
                "ndvi": None,
                "ndwi": None,
                "ndbi": None,
                "vegetation_cover_pct": None,
                "valid_pixel_count": 0,
                "satellite_name": "Landsat / Sentinel-2 / MODIS",
                "dataset_name": "Standby (Awaiting GEE Setup)",
                "acquisition_date": None,
                "processing_date": None,
                "cloud_cover_pct": None,
                "quality_status": "CREDENTIALS_REQUIRED"
            },
            "baseline_hazard": {
                "air_temperature_c": current_air_temp,
                "apparent_temperature_c": apparent_temp,
                "relative_humidity_pct": humidity,
                "lst_anomaly_c": fallback_uhi,
                "peak_surface_temp_c": round(apparent_temp + fallback_uhi * 1.35, 1),
                "hazard_score": hazard_score,
                "extreme_heat_days": int(max(8, min(65, 12 + fallback_uhi * 4))),
                "weather_timestamp": weather_time,
                "weather_data_source": weather_source,
                "satellite_verified": False,
                "satellite_source": "Pending Earth Engine Authentication"
            },
            "baseline_exposure": {
                "population_density_sqkm": density,
                "outdoor_worker_pct": sector["outdoor_worker_pct"],
                "outdoor_worker_count": outdoor_count,
                "transit_commuter_density": "High" if sector["commuters"] > 60000 else "Moderate",
                "building_density": sector["building_density"],
                "exposure_score": exposure_score,
                "data_source": "Municipal Demographic Estimate"
            },
            "baseline_vulnerability": {
                "elderly_pct": sector["elderly_pct"],
                "elderly_count": elderly_count,
                "children_pct": sector["children_pct"],
                "children_count": children_count,
                "poverty_rate_pct": sector["poverty_rate"],
                "canopy_cover_pct": sector["canopy_cover"],
                "canopy_deficit_pct": round(canopy_deficit, 1),
                "ac_penetration_pct": sector["ac_penetration"],
                "svi_score": svi_score,
                "vulnerability_score": vuln_score,
                "data_source": "Municipal Demographic Estimate"
            },
            "heat_environmental": {
                "air_temperature_c": current_air_temp,
                "relative_humidity_pct": humidity,
                "apparent_temperature_c": apparent_temp,
                "tree_canopy_cover_pct": sector["canopy_cover"],
                "building_density": sector["building_density"],
                "water_availability": sector["water_availability"],
                "data_source_weather": weather_source,
                "data_source_satellite": "Google Earth Engine",
                "timestamp": weather_time,
                "temperature_is_measured": True
            },
            "population_vulnerability": {
                "total_population": sector["pop"],
                "elderly_population": {
                    "count": elderly_count,
                    "pct": sector["elderly_pct"],
                    "data_source": "Municipal Census / Estimate"
                },
                "children_population": {
                    "count": children_count,
                    "pct": sector["children_pct"],
                    "data_source": "Municipal Census / Estimate"
                },
                "outdoor_workers": {
                    "count": outdoor_count,
                    "pct": sector["outdoor_worker_pct"],
                    "data_source": "Labor Survey / Estimate"
                },
                "low_income_population": {
                    "count": int(sector["pop"] * (sector["poverty_rate"] / 100.0)),
                    "pct": sector["poverty_rate"],
                    "data_source": "Municipal Census / Estimate"
                },
                "ac_access": {
                    "has_ac_pct": sector["ac_penetration"],
                    "lacks_ac_pct": round(ac_deficit, 1),
                    "data_source": "Housing Survey / Estimate"
                },
                "social_vulnerability_index": svi_score
            },
            "urban_infrastructure": {
                "land_use_classification": sector["land_use_classification"],
                "building_density": sector["building_density"],
                "water_availability": sector["water_availability"],
                "hospital_availability": sector["hospital_availability"],
                "cooling_facilities": sector["cooling_facility_availability"],
                "power_grid_strain": sector["power_demand"],
                "adaptive_capacity_score": sector["adaptive_capacity_score"],
                "adaptive_capacity_rating": sector["adaptive_capacity_rating"],
                "data_source": "Municipal Infrastructure Survey (Synthetic Baseline)"
            },
            "recommended_priorities": sector["priorities"],
            "key_drivers": sector["drivers"],
            "satellite_data": None
        }

        zones.append(zone_dict)

    # If Earth Engine is initialized, attempt to query real satellite zonal stats
    if ee_manager.is_initialized:
        try:
            sat_stats = compute_satellite_zonal_statistics(zones, city_name)
            if sat_stats.get("authenticated") and sat_stats.get("zonal_statistics"):
                z_map = sat_stats["zonal_statistics"]
                city_lst_values = [v["landsat_lst"]["mean_lst_c"] for v in z_map.values() if v.get("landsat_lst", {}).get("mean_lst_c") is not None]
                city_mean_lst = sum(city_lst_values) / len(city_lst_values) if city_lst_values else None

                for z in zones:
                    zid = z["id"]
                    if zid in z_map:
                        s_record = z_map[zid]
                        z["satellite_data"] = s_record
                        z["is_real_satellite"] = True
                        z["satellite_status"] = "AUTHENTICATED_LIVE"
                        z["data_quality_status"] = s_record.get("data_quality_status", "VALID_OBSERVATION")
                        z["data_source_labels"]["satellite"] = f"{s_record['landsat_lst']['satellite']} & {s_record['sentinel2_indices']['satellite']}"

                        # Update baseline hazard with real satellite temperature
                        real_lst = s_record["landsat_lst"]["mean_lst_c"]
                        if real_lst is not None:
                            z["baseline_hazard"]["mean_surface_lst_c"] = real_lst
                            z["baseline_hazard"]["min_surface_lst_c"] = s_record["landsat_lst"]["min_lst_c"]
                            z["baseline_hazard"]["max_surface_lst_c"] = s_record["landsat_lst"]["max_lst_c"]
                            z["baseline_hazard"]["peak_surface_temp_c"] = s_record["landsat_lst"]["max_lst_c"]
                            if city_mean_lst is not None:
                                z["baseline_hazard"]["lst_anomaly_c"] = round(real_lst - city_mean_lst, 2)

                            # Recalculate hazard score with real satellite LST
                            haz_calc = (
                                (current_air_temp * 1.1) +
                                ((apparent_temp - current_air_temp) * 1.8) +
                                (abs(z["baseline_hazard"]["lst_anomaly_c"]) * 4.5)
                            )
                            z["baseline_hazard"]["hazard_score"] = round(max(15.0, min(98.0, haz_calc)), 1)
                            z["baseline_hazard"]["satellite_verified"] = True
                            z["baseline_hazard"]["satellite_source"] = s_record["landsat_lst"]["satellite"]
                            z["baseline_hazard"]["observation_date"] = s_record["landsat_lst"]["acquisition_date"]

                        # Update vegetation with real Sentinel-2 NDVI & vegetation coverage
                        real_veg = s_record["sentinel2_indices"]["vegetation_cover_pct"]
                        if real_veg is not None:
                            z["baseline_vulnerability"]["canopy_cover_pct"] = real_veg
                            z["baseline_vulnerability"]["canopy_deficit_pct"] = round(100.0 - real_veg, 1)
                            z["baseline_vulnerability"]["ndvi_mean"] = s_record["sentinel2_indices"]["ndvi_mean"]
                            z["baseline_vulnerability"]["ndbi_mean"] = s_record["sentinel2_indices"]["ndbi_mean"]
                            z["baseline_vulnerability"]["ndwi_mean"] = s_record["sentinel2_indices"]["ndwi_mean"]

                        # Update composite risk score with real satellite environmental inputs
                        r_raw = (0.35 * z["baseline_hazard"]["hazard_score"]) + (0.30 * z["baseline_exposure"]["exposure_score"]) + (0.35 * z["baseline_vulnerability"]["vulnerability_score"])
                        z["baseline_risk"] = round(max(10.0, min(98.0, r_raw - adaptive_buffer)), 1)

        except Exception as e:
            print(f"Satellite enrichment issue for {city_name}: {e}")

    return zones

