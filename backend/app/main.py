from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

from app.data import ZONES_DATA, INTERVENTIONS_CATALOG, CITY_CENTER, WEIGHTS
from app.models import (
    ZoneSimRequest,
    SimulationResult,
    CitySimulationResponse,
    OptimizeRequest,
    OptimizationResponse,
    WeatherResponse,
    CitySelection,
    ChatRequest,
    ChatResponse,
    SatelliteStatusResponse,
    SatelliteZonesResponse,
)
from app.simulation import simulate_zone_interventions, calculate_composite_risk
from app.optimizer import optimize_budget_allocation
from app.geo_service import (
    geocode_city_search,
    fetch_city_weather,
    generate_city_zones,
    get_currency_for_country,
    FALLBACK_CITIES,
)
from app.ai_service import handle_chat_request
from app.satellite_service import (
    get_earth_engine_status,
    get_earth_engine_tile_urls,
    compute_satellite_zonal_statistics,
    ee_manager
)

app = FastAPI(
    title="HEATSHIELD AI — Global Urban Climate Resilience Digital Twin",
    description="Real-Time Global Urban Heat Risk Modeling, Weather Telemetry, and Policy Simulation",
    version="2.0.0"
)

# Enable CORS for local Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYNTHETIC_NOTICE = (
    "DISCLAIMER: Meteorological air temperatures and humidity are retrieved from real-time "
    "Open-Meteo API. Zone boundaries, demographic counts, vulnerability indices, and intervention "
    "impact response functions are illustrative synthetic demo assumptions for hackathon prototype decision-support. "
    "Not certified for municipal civil engineering."
)


@app.get("/")
def root():
    return {
        "system": "HEATSHIELD AI — Global Urban Climate Resilience Digital Twin",
        "version": "2.0.0",
        "status": "online",
        "notice": SYNTHETIC_NOTICE
    }


@app.get("/api/geocode")
def search_cities(q: str = Query(..., min_length=1, description="City name query")):
    """
    Searches worldwide cities using Open-Meteo Geocoding API with fallback.
    """
    results = geocode_city_search(q)
    return {
        "query": q,
        "count": len(results),
        "results": results,
        "synthetic_notice": SYNTHETIC_NOTICE
    }


@app.get("/api/weather")
def get_weather(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Retrieves real-time global weather from Open-Meteo.
    """
    weather = fetch_city_weather(lat, lon)
    return weather


@app.get("/api/city-data")
def get_city_data(
    name: str = Query("Chennai", description="City name"),
    country: str = Query("India", description="Country name"),
    country_code: str = Query("IN", description="ISO 2-letter country code"),
    lat: float = Query(13.0827, description="Latitude"),
    lon: float = Query(80.2707, description="Longitude")
):
    """
    Generates unified city telemetry:
    1. Real-time Open-Meteo weather
    2. Dynamic 5 microclimate analysis zones centered around the city's coordinates
    3. Currency configuration (INR, JPY, GBP, USD, AED, EUR, etc.)
    4. Citywide KPI summary
    """
    # 1. Fetch real weather
    weather = fetch_city_weather(lat, lon)

    # 2. Generate 5 unique illustrative zones
    zones = generate_city_zones(name, country, country_code, lat, lon, weather)

    # 3. Currency
    curr = get_currency_for_country(country_code)

    # 4. Compute citywide KPIs
    total_pop = sum(z["population"] for z in zones)
    zone_risks = [z["baseline_risk"] for z in zones]
    high_risk_zones = sum(1 for r in zone_risks if r >= 65.0)
    max_peak_temp = max(z["baseline_hazard"]["peak_surface_temp_c"] for z in zones)
    max_lst_anomaly = max(z["baseline_hazard"]["lst_anomaly_c"] for z in zones)
    avg_risk = round(sum(zone_risks) / len(zone_risks), 1)

    exposed_pop = sum(
        z["population"]
        for z in zones
        if z["baseline_risk"] >= 50.0
    )

    return {
        "city": {
            "name": name,
            "country": country,
            "country_code": country_code,
            "latitude": lat,
            "longitude": lon,
            "currency": curr
        },
        "weather": weather,
        "kpis": {
            "city_name": name,
            "country": country,
            "total_population": total_pop,
            "high_risk_zones_count": high_risk_zones,
            "total_zones": len(zones),
            "exposed_population": exposed_pop,
            "peak_surface_temp_c": max_peak_temp,
            "max_lst_anomaly_c": max_lst_anomaly,
            "average_baseline_risk": avg_risk,
            "default_budget_local": curr["default_budget"],
            "currency_symbol": curr["symbol"],
            "currency_code": curr["code"],
            "risk_weights": WEIGHTS
        },
        "zones": zones,
        "weights": WEIGHTS,
        "earth_engine_status": get_earth_engine_status(),
        "satellite_layers": get_earth_engine_tile_urls(lat, lon).get("tiles", {}),
        "synthetic_notice": SYNTHETIC_NOTICE
    }


@app.get("/api/kpis")
def get_kpis(
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    country_code: Optional[str] = None
):
    """
    Returns city-wide summary KPIs. If city coordinates provided, returns dynamic city KPIs.
    """
    if lat is not None and lon is not None:
        city_name = city or "Selected City"
        country = "Global"
        code = country_code or "US"
        weather = fetch_city_weather(lat, lon)
        zones = generate_city_zones(city_name, country, code, lat, lon, weather)
        curr = get_currency_for_country(code)

        total_pop = sum(z["population"] for z in zones)
        zone_risks = [z["baseline_risk"] for z in zones]
        high_risk_zones = sum(1 for r in zone_risks if r >= 65.0)
        max_peak_temp = max(z["baseline_hazard"]["peak_surface_temp_c"] for z in zones)
        max_lst_anomaly = max(z["baseline_hazard"]["lst_anomaly_c"] for z in zones)
        avg_risk = round(sum(zone_risks) / len(zone_risks), 1)
        exposed_pop = sum(z["population"] for z in zones if z["baseline_risk"] >= 50.0)

        return {
            "city_name": city_name,
            "country": country,
            "total_population": total_pop,
            "high_risk_zones_count": high_risk_zones,
            "total_zones": len(zones),
            "exposed_population": exposed_pop,
            "peak_surface_temp_c": max_peak_temp,
            "max_lst_anomaly_c": max_lst_anomaly,
            "average_baseline_risk": avg_risk,
            "default_budget_local": curr["default_budget"],
            "currency_symbol": curr["symbol"],
            "currency_code": curr["code"],
            "risk_weights": WEIGHTS,
            "synthetic_notice": SYNTHETIC_NOTICE
        }

    # Default Solaria Metro baseline
    total_pop = sum(z["population"] for z in ZONES_DATA.values())
    zone_risks = [
        calculate_composite_risk(
            z["baseline_hazard"]["hazard_score"],
            z["baseline_exposure"]["exposure_score"],
            z["baseline_vulnerability"]["vulnerability_score"]
        )
        for z in ZONES_DATA.values()
    ]
    high_risk_zones = sum(1 for r in zone_risks if r >= 65.0)
    max_peak_temp = max(z["baseline_hazard"]["peak_surface_temp_c"] for z in ZONES_DATA.values())
    max_lst_anomaly = max(z["baseline_hazard"]["lst_anomaly_c"] for z in ZONES_DATA.values())
    avg_risk = round(sum(zone_risks) / len(zone_risks), 1)

    exposed_pop = sum(
        z["population"]
        for z in ZONES_DATA.values()
        if calculate_composite_risk(
            z["baseline_hazard"]["hazard_score"],
            z["baseline_exposure"]["exposure_score"],
            z["baseline_vulnerability"]["vulnerability_score"]
        ) >= 50.0
    )

    return {
        "city_name": "Solaria Metropolitan District",
        "total_population": total_pop,
        "high_risk_zones_count": high_risk_zones,
        "total_zones": len(ZONES_DATA),
        "exposed_population": exposed_pop,
        "peak_surface_temp_c": max_peak_temp,
        "max_lst_anomaly_c": max_lst_anomaly,
        "average_baseline_risk": avg_risk,
        "default_budget_local": 3500000.0,
        "currency_symbol": "$",
        "currency_code": "USD",
        "risk_weights": WEIGHTS,
        "synthetic_notice": SYNTHETIC_NOTICE
    }


@app.get("/api/zones")
def get_all_zones(
    city: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    country_code: Optional[str] = None
):
    """
    Returns zones. If city coordinates provided, dynamically returns the 5 zones for that city.
    """
    if lat is not None and lon is not None:
        city_name = city or "Selected City"
        country = "Global"
        code = country_code or "US"
        weather = fetch_city_weather(lat, lon)
        zones = generate_city_zones(city_name, country, code, lat, lon, weather)
        return {
            "city_center": {"lat": lat, "lng": lon, "zoom": 12},
            "weights": WEIGHTS,
            "zones": zones,
            "synthetic_notice": SYNTHETIC_NOTICE
        }

    results = []
    for zid, z in ZONES_DATA.items():
        h = z["baseline_hazard"]["hazard_score"]
        e = z["baseline_exposure"]["exposure_score"]
        v = z["baseline_vulnerability"]["vulnerability_score"]
        risk = calculate_composite_risk(h, e, v)

        results.append({
            "id": z["id"],
            "name": z["name"],
            "short_name": z["short_name"],
            "type": z["type"],
            "centroid": z["centroid"],
            "polygon": z["polygon"],
            "population": z["population"],
            "daytime_commuters": z["daytime_commuters"],
            "area_km2": z["area_km2"],
            "baseline_risk": risk,
            "baseline_hazard": z["baseline_hazard"],
            "baseline_exposure": z["baseline_exposure"],
            "baseline_vulnerability": z["baseline_vulnerability"],
            "vulnerability_factors": z["vulnerability_factors"],
            "recommended_priorities": z["recommended_priorities"]
        })

    return {
        "city_center": CITY_CENTER,
        "weights": WEIGHTS,
        "zones": results,
        "synthetic_notice": SYNTHETIC_NOTICE
    }


@app.get("/api/interventions")
def get_interventions_catalog():
    """
    Returns metadata for all available heat resilience interventions.
    """
    return {
        "interventions": list(INTERVENTIONS_CATALOG.values()),
        "synthetic_notice": SYNTHETIC_NOTICE
    }


@app.post("/api/simulate")
def run_simulation(request: ZoneSimRequest):
    """
    Simulates selected interventions on a specific zone or across all zones.
    Accepts dynamic zone snapshot and currency conversion.
    """
    rate = request.currency_rate if request.currency_rate and request.currency_rate > 0 else 1.0
    sym = request.currency_symbol or "$"
    city = request.city_name or "Global Metro"

    if request.zone_id or request.zone_data:
        zid = request.zone_id or (request.zone_data.get("id") if request.zone_data else "zone_1")
        result = simulate_zone_interventions(
            zone_id=zid,
            interventions=request.interventions,
            zone_data=request.zone_data,
            city_name=city,
            currency_symbol=sym,
            currency_rate=rate
        )
        return {
            "mode": "single_zone",
            "zone_result": result,
            "synthetic_notice": SYNTHETIC_NOTICE
        }
    else:
        # Default city-wide simulation
        zone_results: List[SimulationResult] = []
        total_cost_usd = 0.0
        total_cost_local = 0.0
        total_people = 0
        total_risk_red_pct = 0.0
        total_lst_red = 0.0

        for zid in ZONES_DATA:
            res = simulate_zone_interventions(
                zone_id=zid,
                interventions=request.interventions,
                city_name=city,
                currency_symbol=sym,
                currency_rate=rate
            )
            zone_results.append(res)
            total_cost_usd += res.estimated_cost_usd
            total_cost_local += res.estimated_cost_local
            total_people += res.people_protected
            total_risk_red_pct += res.risk_reduction_pct
            total_lst_red += res.lst_reduction_c

        count = len(zone_results)
        return CitySimulationResponse(
            city_name=city,
            currency_symbol=sym,
            total_cost_local=round(total_cost_local, 2),
            total_cost_usd=round(total_cost_usd, 2),
            total_people_protected=total_people,
            avg_risk_reduction_pct=round(total_risk_red_pct / count, 1) if count else 0.0,
            avg_lst_reduction_c=round(total_lst_red / count, 2) if count else 0.0,
            zone_results=zone_results,
            synthetic_notice=SYNTHETIC_NOTICE
        )


@app.post("/api/optimize", response_model=OptimizationResponse)
def run_optimizer(request: OptimizeRequest):
    """
    Optimizes intervention selection under a budget cap in local currency.
    """
    return optimize_budget_allocation(request)


@app.post("/api/chat", response_model=ChatResponse)
def chat_with_assistant(request: ChatRequest):
    """
    Dedicated AI Chat Assistant endpoint for HEATSHIELD AI.
    Answers queries grounded in real-time city telemetry, 5 analysis zones,
    active zone profile, and current What-If intervention simulator results.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        return handle_chat_request(request)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process AI chat request: {str(e)}")


# ==============================================================================
# SATELLITE & GOOGLE EARTH ENGINE API ENDPOINTS
# ==============================================================================

@app.get("/api/satellite/status", response_model=SatelliteStatusResponse)
def get_satellite_connection_status():
    """
    Returns Google Earth Engine authentication status, configured project,
    and dataset availability.
    """
    return get_earth_engine_status()


@app.get("/api/satellite/city")
def get_city_satellite_summary(
    city: str = Query(..., description="Target city name"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None)
):
    """
    Returns satellite metadata, observation windows, and available raster layers for the city.
    """
    status = get_earth_engine_status()
    target_lat = lat
    target_lon = lon
    if target_lat is None or target_lon is None:
        matches = geocode_city_search(city)
        if matches:
            target_lat = matches[0]["latitude"]
            target_lon = matches[0]["longitude"]
        else:
            target_lat = 13.0827
            target_lon = 80.2707

    tiles = get_earth_engine_tile_urls(target_lat, target_lon)
    return {
        "city": city,
        "coordinates": [target_lat, target_lon],
        "earth_engine_status": status,
        "layers": tiles.get("tiles", {}),
        "status": tiles.get("status", "unconfigured"),
        "observation_window": tiles.get("observation_window")
    }


@app.get("/api/satellite/zones")
def get_satellite_zones(
    city: str = Query(..., description="Target city name"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None)
):
    """
    Returns satellite-derived zonal statistics for the 5 zones of the selected city:
    - Landsat 8/9 Surface Temperature (ST_B10: mean, min, max in °C)
    - Sentinel-2 Multispectral Indices (NDVI, NDWI, NDBI, vegetation cover %)
    - MODIS LST Regional Baseline (1000m)
    - Acquisition dates, pixel counts, and cloud cover.
    """
    target_lat = lat
    target_lon = lon
    if target_lat is None or target_lon is None:
        matches = geocode_city_search(city)
        if matches:
            target_lat = matches[0]["latitude"]
            target_lon = matches[0]["longitude"]
        else:
            target_lat = 13.0827
            target_lon = 80.2707

    weather = fetch_city_weather(target_lat, target_lon)
    zones = generate_city_zones(city, "Global", "GL", target_lat, target_lon, weather)
    
    if ee_manager.is_initialized:
        res = compute_satellite_zonal_statistics(zones, city)
        zonal_stats = res.get("zonal_statistics", {})
        zone_list = []
        for z in zones:
            zs = zonal_stats.get(z["id"], {})
            lst = zs.get("landsat_lst", {})
            s2 = zs.get("sentinel2_indices", {})
            zone_list.append({
                "zone_id": z["id"],
                "zone_name": z["name"],
                "mean_lst_c": lst.get("mean_lst_c"),
                "min_lst_c": lst.get("min_lst_c"),
                "max_lst_c": lst.get("max_lst_c"),
                "ndvi": s2.get("ndvi_mean"),
                "ndwi": s2.get("ndwi_mean"),
                "ndbi": s2.get("ndbi_mean"),
                "vegetation_cover_pct": s2.get("vegetation_cover_pct"),
                "valid_pixel_count": lst.get("valid_pixels", 0),
                "satellite_name": lst.get("satellite", "Landsat 8/9"),
                "dataset_name": lst.get("dataset", "LANDSAT/LC08/C02/T1_L2"),
                "quality_status": zs.get("data_quality_status", "VALID_OBSERVATION"),
                "polygon": z.get("polygon", [])
            })
        res["city"] = city
        res["zone_count"] = len(zones)
        res["zones"] = zone_list
        return res
    else:
        zone_list = []
        for z in zones:
            tele = z.get("satellite_telemetry", {})
            zone_list.append({
                "zone_id": z["id"],
                "zone_name": z["name"],
                "mean_lst_c": tele.get("mean_lst_c"),
                "min_lst_c": tele.get("min_lst_c"),
                "max_lst_c": tele.get("max_lst_c"),
                "ndvi": tele.get("ndvi"),
                "ndwi": tele.get("ndwi"),
                "ndbi": tele.get("ndbi"),
                "vegetation_cover_pct": tele.get("vegetation_cover_pct"),
                "valid_pixel_count": tele.get("valid_pixel_count", 0),
                "satellite_name": tele.get("satellite_name", "Standby"),
                "dataset_name": tele.get("dataset_name", "Standby"),
                "quality_status": tele.get("quality_status", "CREDENTIALS_REQUIRED"),
                "polygon": z.get("polygon", [])
            })
        return {
            "authenticated": False,
            "status": "unconfigured",
            "city": city,
            "city_name": city,
            "zone_count": len(zones),
            "zones": zone_list,
            "message": "Earth Engine credentials not configured in backend/.env",
            "setup_instructions": get_earth_engine_status().get("setup_instructions"),
            "zonal_statistics": {z["id"]: z.get("satellite_telemetry") for z in zones}
        }


@app.get("/api/satellite/zones/{zone_id}")
def get_single_zone_satellite(
    zone_id: str,
    city: Optional[str] = Query(None),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None)
):
    """
    Retrieves satellite statistics for a specific zone by ID.
    """
    c_name = city or "Current City"
    target_lat = lat or 13.0827
    target_lon = lon or 80.2707
    weather = fetch_city_weather(target_lat, target_lon)
    zones = generate_city_zones(c_name, "Global", "GL", target_lat, target_lon, weather)
    matching = next((z for z in zones if z["id"] == zone_id), None)
    if not matching:
        raise HTTPException(status_code=404, detail=f"Zone '{zone_id}' not found.")
    
    return {
        "zone_id": zone_id,
        "zone_name": matching["name"],
        "satellite_telemetry": matching.get("satellite_telemetry"),
        "satellite_data": matching.get("satellite_data"),
        "is_real_satellite": matching.get("is_real_satellite", False),
        "data_quality_status": matching.get("data_quality_status")
    }


@app.get("/api/satellite/tiles")
def get_satellite_tiles(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude"),
    layer: str = Query("lst", description="Layer name: lst, ndvi, ndwi, ndbi")
):
    """
    Returns the real Earth Engine Leaflet Tile URL for the requested raster layer.
    """
    tiles_data = get_earth_engine_tile_urls(lat, lon)
    return tiles_data


