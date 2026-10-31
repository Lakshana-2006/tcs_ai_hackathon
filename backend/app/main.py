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
    FeedbackCreate,
    FeedbackRecord,
    FeedbackSummaryResponse,
)
from app.feedback_service import (
    save_feedback,
    get_all_feedback,
    get_feedback_summary,
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
    get_structured_satellite_records,
    fetch_historical_satellite_series,
    ee_manager
)
from app.dataset_registry import (
    get_all_dataset_provenance,
    get_dataset_provenance_by_id,
    get_spatial_alignment_for_city,
    DATASET_REGISTRY
)
from app.temporal_service import (
    fetch_historical_heat_risk,
    fetch_forecast_heat_risk,
    fetch_climate_projections,
    get_temporal_risk_comparison,
    calculate_zone_risk_for_conditions
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


@app.get("/api/satellite/analysis")
def get_satellite_structured_analysis(
    city: str = Query("Chennai", description="Target city name"),
    zone_id: Optional[str] = Query(None, description="Optional specific zone ID"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    days_back: int = Query(90, ge=7, le=365)
):
    """
    Returns structured satellite observation records matching the exact schema specified in
    Master Prompt Section 6:
    [
      {
        "city": "Chennai",
        "zone": "Central Urban Core",
        "dataset": "LANDSAT/LC08/C02/T1_L2",
        "acquisition_date": "...",
        "land_surface_temperature_c": ...,
        "ndvi": ...,
        "ndwi": ...,
        "ndbi": ...,
        "vegetation_cover_percent": ...,
        "data_status": "available" | "unavailable" | "unconfigured",
        "resolution_meters": 30
      }
    ]
    """
    target_lat = lat or 13.0827
    target_lon = lon or 80.2707
    weather = fetch_city_weather(target_lat, target_lon)
    zones = generate_city_zones(city, "Global", "GL", target_lat, target_lon, weather)

    if zone_id:
        zones = [z for z in zones if z["id"] == zone_id]
        if not zones:
            raise HTTPException(status_code=404, detail=f"Zone '{zone_id}' not found.")

    records = get_structured_satellite_records(zones, city, days_back)
    return {
        "city": city,
        "count": len(records),
        "earth_engine_authenticated": ee_manager.is_initialized,
        "records": records
    }


@app.get("/api/satellite/history")
def get_satellite_history(
    city: str = Query("Chennai", description="Target city name"),
    start_date: str = Query("2024-01-01", description="Start date (YYYY-MM-DD)"),
    end_date: str = Query("2024-06-30", description="End date (YYYY-MM-DD)"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None)
):
    """
    Retrieves historical satellite observations over a user-selected date range.
    Reports honest unconfigured status when Earth Engine credentials are not present.
    """
    target_lat = lat or 13.0827
    target_lon = lon or 80.2707
    weather = fetch_city_weather(target_lat, target_lon)
    zones = generate_city_zones(city, "Global", "GL", target_lat, target_lon, weather)

    return fetch_historical_satellite_series(zones, city, start_date, end_date)


@app.get("/api/satellite/provenance")
def get_satellite_provenance():
    """
    Returns authoritative data provenance, scientific scaling factors,
    and band specifications for all integrated satellite instruments.
    """
    return {
        "system": "HEATSHIELD AI Earth Engine Pipeline",
        "instruments": [
            {
                "instrument": "Landsat 8/9 OLI/TIRS Collection 2 Level-2",
                "dataset_id": "LANDSAT/LC08/C02/T1_L2 + LC09/C02/T1_L2",
                "provider": "USGS / NASA / Google Earth Engine",
                "spatial_resolution": "30m (thermal resampled from 100m)",
                "band_used": "ST_B10 (Surface Temperature)",
                "scaling_formula": "Kelvin = ST_B10 * 0.00341802 + 149.0; Celsius = Kelvin - 273.15",
                "cloud_masking": "QA_PIXEL bitmask: Bit 1 (Dilated Cloud), Bit 2 (Cirrus), Bit 3 (Cloud), Bit 4 (Cloud Shadow)",
                "parameter": "Land Surface Temperature (°C)"
            },
            {
                "instrument": "Sentinel-2 MSI Level-2A Surface Reflectance",
                "dataset_id": "COPERNICUS/S2_SR_HARMONIZED",
                "provider": "European Space Agency (ESA) Copernicus / Google Earth Engine",
                "spatial_resolution": "10m (B2, B3, B4, B8), 20m (B11, SCL)",
                "bands_used": "B2 (Blue), B3 (Green), B4 (Red), B8 (NIR), B11 (SWIR1), QA60, SCL",
                "indices": {
                    "NDVI": "(B8 - B4) / (B8 + B4)",
                    "NDWI": "(B3 - B8) / (B3 + B8)",
                    "NDBI": "(B11 - B8) / (B11 + B8)",
                    "Fractional_Vegetation_Cover_Pct": "((NDVI - 0.15) / (0.70 - 0.15))^2 * 100% (Carlson & Ripley 1997 / Gutman & Ignatov 1998)"
                },
                "cloud_masking": "QA60 (Bits 10, 11) + SCL (Masking shadow=3, cloud_med=8, cloud_high=9, cirrus=10, snow=11)",
                "parameter": "Multispectral vegetation, water, and built-up indices"
            },
            {
                "instrument": "MODIS Terra Land Surface Temperature",
                "dataset_id": "MODIS/061/MOD11A1 / MOD11A2",
                "provider": "NASA LP DAAC / Google Earth Engine",
                "spatial_resolution": "1000m (1 km)",
                "band_used": "LST_Day_1km",
                "scaling_formula": "Celsius = LST_Day_1km * 0.02 - 273.15",
                "parameter": "Regional Land Surface Temperature Baseline (°C)"
            }
        ]
    }


# ==============================================================================
# DATASET INTEGRATION & PROVENANCE REGISTRY ENDPOINTS
# ==============================================================================

@app.get("/api/datasets")
def list_datasets(classification: Optional[str] = Query(None)):
    """
    Returns the complete catalog of integrated and supported datasets with
    authoritative provenance metadata, licensing, spatial resolutions, and processing methods.
    """
    datasets = get_all_dataset_provenance()
    if classification:
        datasets = [d for d in datasets if d.get("classification") == classification]
    return {
        "status": "success",
        "total_datasets": len(datasets),
        "datasets": datasets
    }


@app.get("/api/datasets/spatial-alignment")
def get_spatial_alignment(city: str = Query("Chennai", description="Target city name")):
    """
    Returns documented spatial alignment methodology, administrative boundary mapping,
    and area-weighted intersection cross-references (e.g. GCC 200 Wards / 15 Zones for Chennai).
    """
    return get_spatial_alignment_for_city(city)


@app.get("/api/datasets/{dataset_id}")
def get_dataset_details(dataset_id: str):
    """
    Retrieves full provenance, DOI, provider, and band structure for a specific dataset.
    """
    dataset = get_dataset_provenance_by_id(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found in registry.")
    return dataset


# ==============================================================================
# TEMPORAL HEAT-RISK ANALYSIS ENDPOINTS (PAST, PRESENT, FUTURE, CLIMATE 2050)
# ==============================================================================

@app.get("/api/temporal/past")
def get_past_heat_risk(
    city: str = Query("Chennai", description="Target city name"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    start_date: str = Query("2024-05-15", description="Historical start date (YYYY-MM-DD)"),
    end_date: str = Query("2024-05-22", description="Historical end date (YYYY-MM-DD)")
):
    """
    Retrieves Open-Meteo ERA5 historical reanalysis weather and computes
    historical daily heat-risk trajectories for all 5 city zones using the exact IPCC risk formula.
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

    try:
        data = fetch_historical_heat_risk(city, target_lat, target_lon, zones, start_date, end_date)
        return data
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Historical weather retrieval failed: {str(e)}")


@app.get("/api/temporal/present")
def get_present_heat_risk(
    city: str = Query("Chennai", description="Target city name"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None)
):
    """
    Returns current live weather-based heat risk for all 5 zones from Open-Meteo real-time telemetry.
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

    cur_air = weather.get("air_temperature_c", 30.0)
    cur_app = weather.get("apparent_temperature_c", cur_air + 4.0)

    zone_risks = {}
    for z in zones:
        calc = calculate_zone_risk_for_conditions(z, cur_air, cur_app)
        zone_risks[z["id"]] = {
            "zone_name": z["name"],
            "composite_risk": calc["composite_risk"],
            "hazard_score": calc["hazard_score"],
            "exposure_score": calc["exposure_score"],
            "vulnerability_score": calc["vulnerability_score"],
            "peak_surface_temp_c": calc["peak_surface_temp_c"]
        }

    avg_risk = round(sum(v["composite_risk"] for v in zone_risks.values()) / max(1, len(zone_risks)), 1)

    return {
        "status": "success",
        "city": city,
        "mode": "present",
        "data_source": "Open-Meteo Real-Time Operational API (WMO Weather Stations)",
        "timestamp": weather.get("timestamp", "Live Re-sync"),
        "air_temperature_c": cur_air,
        "apparent_temperature_c": cur_app,
        "relative_humidity_pct": weather.get("relative_humidity_pct", 60.0),
        "wind_speed_kmh": weather.get("wind_speed_kmh", 12.0),
        "average_city_risk": avg_risk,
        "zone_risks": zone_risks
    }


@app.get("/api/temporal/future")
def get_future_heat_risk(
    city: str = Query("Chennai", description="Target city name"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    days: int = Query(7, ge=1, le=14, description="Forecast horizon in days (1-14)")
):
    """
    Returns 7-14 day numerical weather prediction forecast and calculates
    projected daily & hourly heat risk for all 5 zones.
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

    try:
        data = fetch_forecast_heat_risk(city, target_lat, target_lon, zones, forecast_days=days)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Forecast weather retrieval failed: {str(e)}")


@app.get("/api/temporal/climate")
def get_climate_heat_risk(
    city: str = Query("Chennai", description="Target city name"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None),
    model: str = Query("EC_Earth3P_HR", description="CMIP6 Climate Model: EC_Earth3P_HR, MRI_AGCM3_2_S, MPI_ESM1_2_XR")
):
    """
    Retrieves CMIP6 multi-model climate projection scenarios through 2050 from Open-Meteo Climate API.
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

    try:
        data = fetch_climate_projections(city, target_lat, target_lon, zones, model_name=model)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Climate projections retrieval failed: {str(e)}")


@app.get("/api/temporal/compare")
def get_temporal_comparison_route(
    city: str = Query("Chennai", description="Target city name"),
    lat: Optional[float] = Query(None),
    lon: Optional[float] = Query(None)
):
    """
    Synthesizes a comparative temporal profile: Past Heatwave vs Present Live vs Future Forecast vs Climate 2050.
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

    try:
        data = get_temporal_risk_comparison(city, target_lat, target_lon, zones, weather)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Temporal comparison failed: {str(e)}")


# ==============================================================================
# FEEDBACK SESSION ENDPOINTS (JUDGES, EVALUATORS & USERS)
# ==============================================================================

@app.post("/api/feedback", response_model=FeedbackRecord, status_code=201)
def submit_feedback(payload: FeedbackCreate):
    """
    Submits an evaluation or user feedback record into persistent SQLite storage.
    Validates required fields, role, rating ranges (1-5), and text length.
    """
    try:
        record = save_feedback(payload)
        return record
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to persist feedback: {str(e)}")


@app.get("/api/feedback", response_model=List[FeedbackRecord])
def list_feedback(
    limit: int = Query(50, ge=1, le=200, description="Max feedback records to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Retrieves stored feedback records in reverse chronological order for reviewer/evaluator inspection.
    """
    return get_all_feedback(limit=limit, offset=offset)


@app.get("/api/feedback/summary", response_model=FeedbackSummaryResponse)
def get_feedback_statistics():
    """
    Returns aggregated feedback analytics: total submissions, dimensional averages,
    rating distributions, and role breakdowns.
    """
    return get_feedback_summary()

