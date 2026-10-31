"""
dataset_registry.py - Documented Dataset Integration & Provenance Layer for HEATSHIELD AI

Provides authoritative metadata, official URLs, licensing, resolutions, processing methods,
and spatial alignment cross-referencing for:
1. Landsat 8/9 Collection 2 Level-2 (LST via ST_B10)
2. Sentinel-2 Harmonized Level-2A (NDVI, NDWI, NDBI)
3. MODIS Terra/Aqua LST (MOD11A1 / MOD11A2)
4. Open-Meteo Global Numerical Weather API
5. Census of India 2011 Primary Census Abstract (Chennai District 603)
6. Greater Chennai Corporation (GCC) 200 Wards / 15 Zones Dataset
7. OpenStreetMap Infrastructure (Hospitals, Cooling Hubs, Parks, Roads)
8. IPCC AR5/AR6 Climate Risk Assessment Framework
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

# ==============================================================================
# OFFICIAL DATASET REGISTRY
# ==============================================================================

DATASET_REGISTRY: Dict[str, Dict[str, Any]] = {
    "landsat_8_9_lst": {
        "id": "landsat_8_9_lst",
        "name": "Landsat 8 & 9 Collection 2 Tier 1 Level-2 Land Surface Temperature",
        "provider": "U.S. Geological Survey (USGS) & NASA",
        "dataset_identifier": "LANDSAT/LC08/C02/T1_L2 & LANDSAT/LC09/C02/T1_L2",
        "official_url": "https://developers.google.com/earth-engine/datasets/catalog/LANDSAT_LC08_C02_T1_L2",
        "doi": "10.5066/P9OGBGM6",
        "spatial_resolution": "30m (Thermal band ST_B10 resampled from native 100m)",
        "temporal_resolution": "16 days (8 days combined Landsat 8 + 9)",
        "geographic_coverage": "Global terrestrial landmass (-60°S to +84°N)",
        "reference_period": "Rolling 90-day observation window to present",
        "bands_used": ["ST_B10", "QA_PIXEL"],
        "processing_method": (
            "Atmospherically corrected surface temperature. Applied USGS scale factor "
            "(0.00341802) and offset (149.0) to convert ST_B10 digital numbers to Kelvin, "
            "then subtracted 273.15 for Celsius. QA_PIXEL bitmask applied to remove dilated clouds "
            "(bit 1), clouds (bit 3), and cloud shadows (bit 4)."
        ),
        "license": "Public Domain (USGS / NASA Open Data Policy)",
        "classification": "derived",  # raw, derived, baseline, estimated
        "availability_status": "INTEGRATED_REQUIRES_GEE_AUTH",
        "units": {
            "mean_lst_c": "°C",
            "min_lst_c": "°C",
            "max_lst_c": "°C"
        }
    },
    "sentinel_2_indices": {
        "id": "sentinel_2_indices",
        "name": "Sentinel-2 MSI Level-2A Harmonized Surface Reflectance",
        "provider": "European Space Agency (ESA) Copernicus Programme",
        "dataset_identifier": "COPERNICUS/S2_SR_HARMONIZED",
        "official_url": "https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S2_SR_HARMONIZED",
        "doi": "10.5270/S2_-u76j335",
        "spatial_resolution": "10m (B2, B3, B4, B8) and 20m (B11, SCL)",
        "temporal_resolution": "5 days (Sentinel-2A + Sentinel-2B combined)",
        "geographic_coverage": "Global terrestrial surface from -56°S to +84°N",
        "reference_period": "Rolling 90-day observation window to present",
        "bands_used": ["B3 (Green)", "B4 (Red)", "B8 (NIR)", "B11 (SWIR1)", "QA60", "SCL"],
        "processing_method": (
            "Sen2Cor bottom-of-atmosphere surface reflectance scaled by 10,000. Cloud & shadow "
            "masking via combined QA60 bitmask (bits 10 & 11) and Level-2A Scene Classification "
            "Layer (SCL values 3=shadow, 8=med cloud, 9=high cloud, 10=cirrus). "
            "NDVI = (B8 - B4)/(B8 + B4); NDWI = (B3 - B8)/(B3 + B8); NDBI = (B11 - B8)/(B11 + B8). "
            "Vegetation canopy fraction calculated as zonal pixels with NDVI >= 0.35. "
            "Biophysical constraint: Sentinel-2 does not provide thermal LST."
        ),
        "license": "Copernicus Open Access Sentinel Data Terms",
        "classification": "derived",
        "availability_status": "INTEGRATED_REQUIRES_GEE_AUTH",
        "units": {
            "ndvi": "Index ratio (-1.0 to +1.0)",
            "ndwi": "Index ratio (-1.0 to +1.0)",
            "ndbi": "Index ratio (-1.0 to +1.0)",
            "vegetation_cover_pct": "%"
        }
    },
    "modis_lst": {
        "id": "modis_lst",
        "name": "MODIS Terra/Aqua Daily & 8-Day Land Surface Temperature (MOD11A1 / MOD11A2)",
        "provider": "NASA Land Processes Distributed Active Archive Center (LP DAAC)",
        "dataset_identifier": "MODIS/061/MOD11A1 & MODIS/061/MOD11A2",
        "official_url": "https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MOD11A1",
        "doi": "10.5067/MODIS/MOD11A1.061",
        "spatial_resolution": "1000m (1km grid)",
        "temporal_resolution": "Daily (MOD11A1) / 8-day composite (MOD11A2)",
        "geographic_coverage": "Global daily coverage",
        "reference_period": "2000-present rolling daily",
        "bands_used": ["LST_Day_1km", "QC_Day"],
        "processing_method": (
            "Split-window generalized algorithm retrieving daytime skin temperature. "
            "Digital number scaled by 0.02 to Kelvin, converted to Celsius. Provides regional "
            "thermal baseline and wide-swath validation for high-resolution Landsat scenes."
        ),
        "license": "NASA Open Earth Science Data Policy",
        "classification": "derived",
        "availability_status": "INTEGRATED_REQUIRES_GEE_AUTH",
        "units": {
            "modis_lst_c": "°C"
        }
    },
    "open_meteo_weather": {
        "id": "open_meteo_weather",
        "name": "Open-Meteo Global Numerical Weather Prediction Telemetry",
        "provider": "Open-Meteo GmbH (integrating DWD ICON, NOAA GFS, ECMWF IFS models)",
        "dataset_identifier": "API:open-meteo:v1/forecast",
        "official_url": "https://open-meteo.com/en/docs",
        "doi": "N/A (Operational Weather API)",
        "spatial_resolution": "~11km regional NWP grid with bilinear point coordinate interpolation",
        "temporal_resolution": "Hourly updates with 7-day forward horizon",
        "geographic_coverage": "Global coordinates (90°S to 90°N)",
        "reference_period": "Live Real-Time / Current Hour",
        "bands_used": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "wind_speed_10m",
            "precipitation"
        ],
        "processing_method": (
            "Standard WMO 2-meter air temperature and relative humidity telemetry. "
            "Apparent temperature computed via Steadman comprehensive Heat Index formula "
            "incorporating vapor pressure and ambient wind cooling."
        ),
        "license": "Creative Commons Attribution 4.0 International (CC-BY 4.0)",
        "classification": "raw",
        "availability_status": "OPERATIONAL_LIVE",
        "units": {
            "air_temperature_c": "°C",
            "relative_humidity_pct": "%",
            "apparent_temperature_c": "°C",
            "wind_speed_kmh": "km/h"
        }
    },
    "census_india_2011": {
        "id": "census_india_2011",
        "name": "Census of India 2011 — Primary Census Abstract (PCA) Chennai District",
        "provider": "Office of the Registrar General & Census Commissioner, Ministry of Home Affairs, Government of India",
        "dataset_identifier": "GOI:CENSUS:2011:PCA:TAMILNADU:DISTRICT_603",
        "official_url": "https://censusindia.gov.in/census.website/data/census-tables",
        "doi": "Census of India 2011 Series 34 Part XII-B",
        "spatial_resolution": "District aggregate (District Code 603 Chennai: 175 km² pre-expansion jurisdiction)",
        "temporal_resolution": "Decennial national census",
        "geographic_coverage": "Chennai District, Tamil Nadu, India (Coordinates ~13.08°N, 80.27°E)",
        "reference_period": "March 1, 2011 (Official Census Enumeration)",
        "bands_used": [
            "TOT_P (Total Population: 4,646,732)",
            "P_06 (Child Pop 0-6: 459,824 • 9.90%)",
            "P_SC (Scheduled Caste: 779,278 • 16.78%)",
            "P_LIT (Literate Population: 3,776,276 • 90.18%)",
            "TOT_WORK_P (Total Workers: 1,817,288 • 39.1%)",
            "MARGWORK_P (Marginal Workers: 147,764 • Informal Labor Proxy)"
        ],
        "processing_method": (
            "Official district totals and demographic ratios. Pediatric vulnerability extracted from "
            "P_06; senior vulnerability (>60 years) synthesized from Tamil Nadu State Age Cohort Tables "
            "(10.4% senior baseline); informal/outdoor labor estimated from Marginal and Construction "
            "Worker categories in Primary Census Abstract."
        ),
        "license": "Government Open Data License - India (GODL)",
        "classification": "baseline",
        "availability_status": "OFFICIALLY_INTEGRATED_BASELINE",
        "units": {
            "total_population": "residents",
            "child_pct": "%",
            "elderly_pct": "%",
            "literacy_rate": "%"
        }
    },
    "chennai_gcc_ward_profiles": {
        "id": "chennai_gcc_ward_profiles",
        "name": "Greater Chennai Corporation (GCC) 200 Ward Administrative Boundary Dataset",
        "provider": "Greater Chennai Corporation (GCC) & Tamil Nadu Urban Infrastructure Financial Services (TNUDF)",
        "dataset_identifier": "GCC:200WARDS:15ZONES:ADMINISTRATIVE_BOUNDARIES",
        "official_url": "https://chennaicorporation.gov.in/gcc/",
        "doi": "GCC Special Projects & Revenue Administration Records 2011-2022",
        "spatial_resolution": "Ward polygons (200 administrative wards across 15 zones, 426 km² post-expansion)",
        "temporal_resolution": "Administrative ward delimitations post-2011 expansion",
        "geographic_coverage": "Metropolitan Chennai municipal limits",
        "reference_period": "2011-2022 Delimitation Baseline",
        "bands_used": [
            "Zone_No (1 to 15)",
            "Zone_Name (Thiruvottiyur to Sholinganallur)",
            "Ward_No (1 to 200)",
            "Area_SqKm",
            "Population_2011_Census"
        ],
        "processing_method": (
            "Spatial cross-reference between GCC 15 administrative zones and the 5 analytical sectors. "
            "The analytical sectors are continuous spatial envelopes rather than individual legal wards. "
            "Zone-level population densities are mapped to corresponding spatial sectors via area-weighted "
            "geographic intersection (e.g. Northern Sector intersects GCC Zones 1-4; Central Urban Core "
            "intersects GCC Zones 5, 8, 9; Southern Sector intersects GCC Zones 13-15)."
        ),
        "license": "Government of Tamil Nadu Open Access / GCC Public Records",
        "classification": "baseline",
        "availability_status": "DOCUMENTED_SPATIAL_CROSSREFERENCE",
        "units": {
            "ward_count": "wards (1-200)",
            "zone_count": "administrative zones (1-15)",
            "total_area_km2": "426 km²"
        }
    },
    "openstreetmap_infrastructure": {
        "id": "openstreetmap_infrastructure",
        "name": "OpenStreetMap Urban Critical Infrastructure & Environmental Assets",
        "provider": "OpenStreetMap Contributors & Overpass API / Geofabrik",
        "dataset_identifier": "OSM:PLANET:URBAN_INFRASTRUCTURE:VECTOR",
        "official_url": "https://www.openstreetmap.org/copyright",
        "doi": "OpenStreetMap Foundation Open Data Archive",
        "spatial_resolution": "High-precision vector coordinates (points, lines, polygons; 1m-5m accuracy)",
        "temporal_resolution": "Continuous community crowd-sourced commits (2024-2026)",
        "geographic_coverage": "Global coverage for any geocoded city coordinates",
        "reference_period": "Latest OpenStreetMap Planet Snapshot",
        "bands_used": [
            "amenity=hospital | healthcare=hospital",
            "amenity=community_centre | leisure=community_centre",
            "leisure=park | landuse=recreation_ground | leisure=garden",
            "highway=primary | highway=secondary | highway=trunk",
            "natural=water | waterway=river | water=reservoir"
        ],
        "processing_method": (
            "Overpass QL geospatial bounding box queries centered on city and sector polygons. "
            "Counts and tags aggregated per sector polygon to calculate hospital availability, "
            "emergency cooling shelter density, and impervious road network fractions."
        ),
        "license": "Open Data Commons Open Database License (ODbL) 1.0",
        "classification": "raw",
        "availability_status": "INTEGRATED_WITH_OFFLINE_CACHE",
        "units": {
            "hospital_count": "facilities",
            "cooling_facility_count": "facilities",
            "parks_area_km2": "km²"
        }
    },
    "ipcc_risk_framework": {
        "id": "ipcc_risk_framework",
        "name": "IPCC AR5/AR6 Urban Climate Risk Multi-Criteria Assessment Framework",
        "provider": "Intergovernmental Panel on Climate Change (WMO & UNEP)",
        "dataset_identifier": "IPCC:AR6:WGII:CHAPTER_6_CITIES_INFRASTRUCTURE",
        "official_url": "https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-6/",
        "doi": "10.1017/9781009325844.008",
        "spatial_resolution": "Zonal spatial multi-criteria evaluation",
        "temporal_resolution": "Sixth Assessment Report (AR6) Scientific Baseline (2022-present)",
        "geographic_coverage": "Global Urban Settlements",
        "reference_period": "IPCC Assessment Cycle 6",
        "bands_used": [
            "Hazard (H): Air Temp, Apparent Heat Index, LST Anomaly",
            "Exposure (E): Population Density, Outdoor Workforce, Building Density",
            "Vulnerability (V): Senior Residents, Children, Poverty, A/C Deficit, SVI",
            "Adaptive Capacity (AC): Hospital Access, Cooling Havens, Grid Stability"
        ],
        "processing_method": (
            "Composite multi-criteria formula: Risk = (0.35 * Hazard) + (0.30 * Exposure) + "
            "(0.35 * Vulnerability) - Adaptive Capacity Buffer. Normalizes heterogeneous telemetry "
            "into a 0-100 actionable climate resilience index."
        ),
        "license": "United Nations / WMO / UNEP Scientific Open Reference",
        "classification": "estimated",
        "availability_status": "OPERATIONAL_MODEL",
        "units": {
            "composite_risk_score": "Score (0 - 100)"
        }
    }
}


# ==============================================================================
# SPATIAL ALIGNMENT DOCUMENTATION (CHENNAI & GLOBAL SECTOR MAPPING)
# ==============================================================================

CHENNAI_GCC_SPATIAL_ALIGNMENT: Dict[str, Any] = {
    "city": "Chennai",
    "state": "Tamil Nadu",
    "country": "India",
    "coordinates": [13.0827, 80.2707],
    "official_authority": "Greater Chennai Corporation (GCC)",
    "official_wards_total": 200,
    "official_zones_total": 15,
    "census_2011_district_code": 603,
    "analytical_sectors_note": (
        "The HEATSHIELD AI digital twin employs 5 geographically defined spatial analysis sectors "
        "radiating outward from Chennai's urban center. These sectors are deliberate spatial analysis envelopes "
        "rather than single administrative wards. Ward-level census counts are aggregated using an "
        "area-weighted intersection method across overlapping GCC administrative zones."
    ),
    "sector_mappings": {
        "chennai_zone_1": {
            "sector_name": "Chennai — Central Urban Core Sector",
            "orientation": "Center (Radius 2.2 km)",
            "gcc_administrative_zones": [
                {"zone_no": 5, "zone_name": "Royapuram (Central Commercial / Port)"},
                {"zone_no": 8, "zone_name": "Anna Nagar (Dense Commercial Core)"},
                {"zone_no": 9, "zone_name": "Teynampet (CBD & Institutional Hub)"}
            ],
            "official_gcc_wards_intersected": ["Wards 50-62, 94-108, 110-126"],
            "census_2011_basis": "District 603 High Density Commercial PCA",
            "spatial_method": "Geometric centroid intersection with GCC Zones 5, 8, 9"
        },
        "chennai_zone_2": {
            "sector_name": "Chennai — Northern Urban Sector",
            "orientation": "North (+3.6 km North)",
            "gcc_administrative_zones": [
                {"zone_no": 1, "zone_name": "Thiruvottiyur (Industrial / Coastal Port)"},
                {"zone_no": 2, "zone_name": "Manali (Petrochemical & Freight)"},
                {"zone_no": 3, "zone_name": "Madhavaram (Logistics & Transport)"},
                {"zone_no": 4, "zone_name": "Tondiarpet (Dense Urban / Industrial)"}
            ],
            "official_gcc_wards_intersected": ["Wards 1-48"],
            "census_2011_basis": "Northern Industrial Corridor Worker Profiles",
            "spatial_method": "Spatial bounding intersection with GCC Zones 1-4"
        },
        "chennai_zone_3": {
            "sector_name": "Chennai — Southern Mixed Sector",
            "orientation": "South (-3.6 km South)",
            "gcc_administrative_zones": [
                {"zone_no": 13, "zone_name": "Adyar (Mixed Residential & IT Corridor)"},
                {"zone_no": 14, "zone_name": "Perungudi (OMR Tech & Residential)"},
                {"zone_no": 15, "zone_name": "Sholinganallur (Suburban Growth Corridor)"}
            ],
            "official_gcc_wards_intersected": ["Wards 170-200"],
            "census_2011_basis": "Southern Residential & High Vulnerability SVI baseline",
            "spatial_method": "Spatial bounding intersection with GCC Zones 13-15"
        },
        "chennai_zone_4": {
            "sector_name": "Chennai — Eastern Sector",
            "orientation": "East (+3.4 km East / Bay of Bengal Coastal Littoral)",
            "gcc_administrative_zones": [
                {"zone_no": 5, "zone_name": "Royapuram Coastal Strip"},
                {"zone_no": 9, "zone_name": "Marina / Santhome Littoral"},
                {"zone_no": 13, "zone_name": "Besant Nagar / Thiruvanmiyur Coastal Stretch"}
            ],
            "official_gcc_wards_intersected": ["Coastal littoral portions of Wards 60, 114, 115, 126, 173, 175"],
            "census_2011_basis": "Fisherfolk & Maritime Labor Primary Census records",
            "spatial_method": "Coastal littoral boundary buffer intersection"
        },
        "chennai_zone_5": {
            "sector_name": "Chennai — Western Sector",
            "orientation": "West (-3.5 km West / Developing Inland Arterials)",
            "gcc_administrative_zones": [
                {"zone_no": 7, "zone_name": "Ambattur (Industrial Estate & Residential)"},
                {"zone_no": 10, "zone_name": "Kodambakkam (Dense Residential Transit)"},
                {"zone_no": 11, "zone_name": "Valasaravakkam (Mixed Arterial Development)"},
                {"zone_no": 12, "zone_name": "Alandur (Transit Concourse & Residential)"}
            ],
            "official_gcc_wards_intersected": ["Wards 79-93, 127-142, 143-155, 156-167"],
            "census_2011_basis": "Western Arterial Corridor PCA tables",
            "spatial_method": "Spatial bounding intersection with GCC Zones 7, 10, 11, 12"
        }
    }
}


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_all_dataset_provenance() -> List[Dict[str, Any]]:
    """Returns metadata records for all integrated and supported datasets."""
    return list(DATASET_REGISTRY.values())


def get_dataset_provenance_by_id(dataset_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves provenance record for a specific dataset identifier."""
    return DATASET_REGISTRY.get(dataset_id)


def get_spatial_alignment_for_city(city_name: str) -> Dict[str, Any]:
    """
    Returns the documented spatial alignment and boundary methodology
    for the selected city.
    """
    if city_name.strip().lower() == "chennai":
        return CHENNAI_GCC_SPATIAL_ALIGNMENT

    # Global general alignment methodology for any geocoded city
    return {
        "city": city_name,
        "analytical_sectors_note": (
            f"For {city_name}, the HEATSHIELD AI twin constructs 5 radially defined geometric analysis sectors "
            "centered on the city coordinates. These sectors represent continuous spatial zones (Central Core, "
            "North, South, East, West) rather than official political administrative wards. Local census data "
            "is cross-referenced as demographic baselines rather than ward-by-ward legal demarcations."
        ),
        "methodology": "Radial 8-vertex convex hull projection around geocoded centroid",
        "data_classes": {
            "satellite": "Derived via Earth Engine polygon zonal reduction",
            "weather": "Bilinear coordinate point interpolation via Open-Meteo",
            "demographics": "Spatial sector demographic baseline heuristics",
            "risk": "IPCC multi-criteria synthetic calculation"
        }
    }

