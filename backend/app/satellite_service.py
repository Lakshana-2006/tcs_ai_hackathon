import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Try importing ee
try:
    import ee
    HAS_EE_PACKAGE = True
except ImportError:
    ee = None
    HAS_EE_PACKAGE = False

try:
    from google.oauth2 import service_account
    HAS_GOOGLE_AUTH = True
except ImportError:
    service_account = None
    HAS_GOOGLE_AUTH = False


# In-memory cache for Earth Engine zonal statistics and tile URLs
# Key format: (city_slug, dataset, start_date, end_date) -> { "timestamp": float, "data": dict }
_SATELLITE_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 7200  # 2 hours


class EarthEngineManager:
    """
    Manages Google Earth Engine authentication, dataset querying,
    cloud masking, index calculations, and zonal statistics extraction.
    """

    def __init__(self):
        self.is_initialized = False
        self.init_error: Optional[str] = None
        self.project_id: Optional[str] = None
        self.service_account_email: Optional[str] = None
        self.auth_method: Optional[str] = None
        self._try_initialize()

    def _try_initialize(self):
        """
        Attempts to authenticate and initialize Earth Engine using:
        1. Service Account JSON file (EE_KEY_FILE)
        2. Service Account credentials in environment variables (EE_SERVICE_ACCOUNT + EE_PRIVATE_KEY)
        3. Default local credentials (earthengine authenticate or application default)
        """
        if not HAS_EE_PACKAGE:
            self.is_initialized = False
            self.init_error = "earthengine-api Python package is not installed."
            return

        self.project_id = os.getenv("EE_PROJECT_ID") or os.getenv("EE_PROJECT")
        key_file = os.getenv("EE_KEY_FILE")
        sa_email = os.getenv("EE_SERVICE_ACCOUNT") or os.getenv("EE_CLIENT_EMAIL")
        private_key = os.getenv("EE_PRIVATE_KEY")

        # 1. Try Service Account Key File
        if key_file and os.path.isfile(key_file) and HAS_GOOGLE_AUTH:
            try:
                creds = service_account.Credentials.from_service_account_file(
                    key_file,
                    scopes=['https://www.googleapis.com/auth/earthengine']
                )
                ee.Initialize(credentials=creds, project=self.project_id)
                self.is_initialized = True
                self.auth_method = "service_account_file"
                self.service_account_email = creds.service_account_email
                logger.info(f"Earth Engine initialized via service account file: {key_file}")
                return
            except Exception as e:
                self.init_error = f"Service account key file authentication failed: {str(e)}"
                logger.warning(self.init_error)

        # 2. Try Service Account Credentials from Env Variables
        if sa_email and private_key and HAS_GOOGLE_AUTH:
            try:
                formatted_key = private_key.replace('\\n', '\n')
                info = {
                    "type": "service_account",
                    "client_email": sa_email,
                    "private_key": formatted_key,
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
                creds = service_account.Credentials.from_service_account_info(
                    info,
                    scopes=['https://www.googleapis.com/auth/earthengine']
                )
                ee.Initialize(credentials=creds, project=self.project_id)
                self.is_initialized = True
                self.auth_method = "service_account_env"
                self.service_account_email = sa_email
                logger.info(f"Earth Engine initialized via environment service account: {sa_email}")
                return
            except Exception as e:
                self.init_error = f"Service account env authentication failed: {str(e)}"
                logger.warning(self.init_error)

        # 3. Try Default Local Credentials (if user previously ran 'earthengine authenticate')
        try:
            if self.project_id:
                ee.Initialize(project=self.project_id)
            else:
                ee.Initialize()
            self.is_initialized = True
            self.auth_method = "default_credentials"
            logger.info("Earth Engine initialized via local default credentials.")
            return
        except Exception as e:
            self.is_initialized = False
            self.init_error = (
                "Earth Engine authentication not configured. "
                "Set EE_PROJECT_ID, EE_SERVICE_ACCOUNT, and EE_PRIVATE_KEY in backend/.env, "
                "or run 'earthengine authenticate'."
            )
            logger.info(f"Earth Engine not initialized: {self.init_error}")

    def get_status(self) -> Dict[str, Any]:
        """
        Returns structured authentication status and diagnostic metadata.
        """
        return {
            "authenticated": self.is_initialized,
            "status": "authenticated" if self.is_initialized else "unconfigured",
            "auth_method": self.auth_method,
            "project_id": self.project_id,
            "service_account": self.service_account_email,
            "error_message": self.init_error if not self.is_initialized else None,
            "supported_datasets": [
                {
                    "id": "LANDSAT/LC08/C02/T1_L2",
                    "name": "Landsat 8 Collection 2 Tier 1 Level-2 (LST via ST_B10)",
                    "resolution": "30m (resampled thermal)",
                    "metric": "Land Surface Temperature (°C)"
                },
                {
                    "id": "LANDSAT/LC09/C02/T1_L2",
                    "name": "Landsat 9 Collection 2 Tier 1 Level-2 (LST via ST_B10)",
                    "resolution": "30m (resampled thermal)",
                    "metric": "Land Surface Temperature (°C)"
                },
                {
                    "id": "COPERNICUS/S2_SR_HARMONIZED",
                    "name": "Sentinel-2 MSI Level-2A Surface Reflectance",
                    "resolution": "10m - 20m",
                    "metric": "NDVI, NDWI, NDBI, Vegetation Coverage %"
                },
                {
                    "id": "MODIS/061/MOD11A1",
                    "name": "MODIS Terra Land Surface Temperature and Emissivity Daily",
                    "resolution": "1000m (1km)",
                    "metric": "Regional Land Surface Temperature (°C)"
                }
            ],
            "setup_instructions": (
                "To enable live Google Earth Engine data processing:\n"
                "1. Create a Google Cloud Project with the Earth Engine API enabled.\n"
                "2. Create a Service Account and grant it 'Earth Engine Resource Viewer' or user role.\n"
                "3. In backend/.env, add:\n"
                "   EE_PROJECT_ID=your-gcp-project-id\n"
                "   EE_SERVICE_ACCOUNT=your-sa@project.iam.gserviceaccount.com\n"
                "   EE_PRIVATE_KEY=\"-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n\"\n"
                "4. Restart the backend server."
            )
        }


ee_manager = EarthEngineManager()


def get_earth_engine_status() -> Dict[str, Any]:
    return ee_manager.get_status()


# ==============================================================================
# SATELLITE DATA PROCESSING FUNCTIONS
# ==============================================================================

def get_landsat_lst_image(geometry: 'ee.Geometry', start_date: str, end_date: str) -> Optional['ee.Image']:
    """
    Extracts, merges, and cloud-masks Landsat 8 and Landsat 9 Collection 2 Level-2 Surface Temperature.
    Applies USGS Collection 2 Level-2 scale factor (0.00341802) and offset (149.0) to convert ST_B10 to Kelvin,
    then subtracts 273.15 to convert to Celsius.
    Masks clouds, cloud shadows, and dilated clouds using QA_PIXEL bitmask.
    """
    if not ee_manager.is_initialized:
        return None

    def mask_landsat_sr(img):
        qa = img.select('QA_PIXEL')
        # Bit 1 = Dilated Cloud, Bit 3 = Cloud, Bit 4 = Cloud Shadow
        dilated = qa.bitwiseAnd(1 << 1).eq(0)
        cloud = qa.bitwiseAnd(1 << 3).eq(0)
        shadow = qa.bitwiseAnd(1 << 4).eq(0)
        mask = dilated.And(cloud).And(shadow)
        
        # Scale factor for ST_B10: DN * 0.00341802 + 149.0 = Kelvin
        st = img.select('ST_B10')
        lst_k = st.multiply(0.00341802).add(149.0)
        lst_c = lst_k.subtract(273.15).rename('LST_C')
        
        return lst_c.updateMask(mask).copyProperties(img, ['system:time_start', 'SPACECRAFT_ID', 'CLOUD_COVER', 'DATE_ACQUIRED'])

    l8 = ee.ImageCollection('LANDSAT/LC08/C02/T1_L2') \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUD_COVER', 60))

    l9 = ee.ImageCollection('LANDSAT/LC09/C02/T1_L2') \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUD_COVER', 60))

    merged = l8.merge(l9)
    count = merged.size().getInfo()
    if count == 0:
        return None

    # Sort by cloud cover and take median of lowest-cloud images or composite
    sorted_col = merged.sort('CLOUD_COVER')
    processed_col = sorted_col.map(mask_landsat_sr)
    
    # Use median composite of clean observations
    mosaic = processed_col.median()
    
    # Attach metadata from the clearest single scene
    clearest = sorted_col.first()
    mosaic = mosaic.set('SPACECRAFT_ID', clearest.get('SPACECRAFT_ID'))
    mosaic = mosaic.set('system:time_start', clearest.get('system:time_start'))
    mosaic = mosaic.set('CLOUD_COVER', clearest.get('CLOUD_COVER'))
    mosaic = mosaic.set('DATE_ACQUIRED', clearest.get('DATE_ACQUIRED'))
    mosaic = mosaic.set('SCENE_COUNT', count)

    return mosaic


def get_sentinel2_indices_image(geometry: 'ee.Geometry', start_date: str, end_date: str) -> Optional['ee.Image']:
    """
    Extracts Sentinel-2 Level-2A Surface Reflectance, applies QA60 cloud/cirrus masking,
    and calculates:
    - NDVI = (B8 - B4) / (B8 + B4)
    - NDWI = (B3 - B8) / (B3 + B8)  (Water index)
    - NDBI = (B11 - B8) / (B11 + B8) (Built-up index)
    - Vegetation Cover % (pixels with NDVI >= 0.35)
    Note: Sentinel-2 does not provide thermal LST directly.
    """
    if not ee_manager.is_initialized:
        return None

    def mask_s2(img):
        # 1. QA60 cloud and cirrus bitmask
        qa = img.select('QA60')
        cloud_bit = 1 << 10
        cirrus_bit = 1 << 11
        qa_mask = qa.bitwiseAnd(cloud_bit).eq(0).And(qa.bitwiseAnd(cirrus_bit).eq(0))
        
        # 2. SCL (Scene Classification Layer) in S2_SR_HARMONIZED:
        # Values 3 = Cloud Shadows, 8 = Cloud Medium Prob, 9 = Cloud High Prob, 10 = Thin Cirrus
        scl = img.select('SCL')
        scl_clean = scl.neq(3).And(scl.neq(8)).And(scl.neq(9)).And(scl.neq(10))
        
        combined_cloud_mask = qa_mask.And(scl_clean)

        # Scale reflectance bands (B2=Blue, B3=Green, B4=Red, B8=NIR, B11=SWIR1) by 10000.0
        scaled = img.select(['B2', 'B3', 'B4', 'B8', 'B11']).divide(10000.0)
        
        b3 = scaled.select('B3')
        b4 = scaled.select('B4')
        b8 = scaled.select('B8')
        b11 = scaled.select('B11')
        
        ndvi = b8.subtract(b4).divide(b8.add(b4)).rename('NDVI')
        ndwi = b3.subtract(b8).divide(b3.add(b8)).rename('NDWI')
        ndbi = b11.subtract(b8).divide(b11.add(b8)).rename('NDBI')
        
        veg = ndvi.gte(0.35).rename('VEG_COVER')
        
        return ndvi.addBands(ndwi).addBands(ndbi).addBands(veg).updateMask(combined_cloud_mask) \
            .copyProperties(img, ['system:time_start', 'CLOUDY_PIXEL_PERCENTAGE', 'PRODUCT_ID'])

    s2 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 40))

    count = s2.size().getInfo()
    if count == 0:
        return None

    sorted_s2 = s2.sort('CLOUDY_PIXEL_PERCENTAGE')
    processed_s2 = sorted_s2.map(mask_s2)
    mosaic = processed_s2.median()
    
    clearest = sorted_s2.first()
    mosaic = mosaic.set('system:time_start', clearest.get('system:time_start'))
    mosaic = mosaic.set('CLOUDY_PIXEL_PERCENTAGE', clearest.get('CLOUDY_PIXEL_PERCENTAGE'))
    mosaic = mosaic.set('PRODUCT_ID', clearest.get('PRODUCT_ID'))
    mosaic = mosaic.set('SCENE_COUNT', count)

    return mosaic


def get_modis_lst_image(geometry: 'ee.Geometry', start_date: str, end_date: str) -> Optional['ee.Image']:
    """
    Extracts MODIS Terra Land Surface Temperature (MOD11A1 / MOD11A2) daily or 8-day composite.
    Applies documented scale factor: DN * 0.02 - 273.15 = Celsius.
    Spatial resolution: 1000m (1km).
    """
    if not ee_manager.is_initialized:
        return None

    def process_modis(img):
        lst = img.select('LST_Day_1km').multiply(0.02).subtract(273.15).rename('LST_MODIS_C')
        return lst.copyProperties(img, ['system:time_start'])

    modis = ee.ImageCollection('MODIS/061/MOD11A1') \
        .filterBounds(geometry) \
        .filterDate(start_date, end_date)

    count = modis.size().getInfo()
    if count == 0:
        # Fallback to 8-day composite
        modis = ee.ImageCollection('MODIS/061/MOD11A2') \
            .filterBounds(geometry) \
            .filterDate(start_date, end_date)
        count = modis.size().getInfo()
        if count == 0:
            return None

    mosaic = modis.map(process_modis).median()
    first_img = modis.sort('system:time_start', False).first()
    mosaic = mosaic.set('system:time_start', first_img.get('system:time_start'))
    mosaic = mosaic.set('SCENE_COUNT', count)
    return mosaic


# ==============================================================================
# LEAFLET TILE URL GENERATION
# ==============================================================================

def get_earth_engine_tile_urls(lat: float, lon: float, radius_km: float = 25.0) -> Dict[str, Any]:
    """
    Generates authentic Google Earth Engine map tile URLs (TileFetcher format)
    for Leaflet map integration:
    - LST (Landsat 8/9 thermal)
    - NDVI (Sentinel-2 vegetation)
    - NDWI (Sentinel-2 water)
    - NDBI (Sentinel-2 built-up)
    """
    default_layers = {
        "lst": {
            "name": "Land Surface Temperature (Landsat 8/9)",
            "band": "ST_B10",
            "resolution": "30m",
            "dataset": "LANDSAT/LC08/C02/T1_L2 + LC09",
            "palette": ["#0000ff", "#00ffff", "#ffff00", "#ff0000", "#7f0000"],
            "min_c": 20.0,
            "max_c": 50.0,
            "unit": "°C",
            "url": None,
            "ready": False
        },
        "ndvi": {
            "name": "Normalized Difference Vegetation Index (Sentinel-2)",
            "band": "NDVI",
            "resolution": "10m",
            "dataset": "COPERNICUS/S2_SR_HARMONIZED",
            "palette": ["#8B4513", "#FFF8DC", "#90EE90", "#228B22", "#006400"],
            "min": -0.1,
            "max": 0.75,
            "unit": "ratio",
            "url": None,
            "ready": False
        },
        "ndwi": {
            "name": "Normalized Difference Water Index (Sentinel-2)",
            "band": "NDWI",
            "resolution": "10m",
            "dataset": "COPERNICUS/S2_SR_HARMONIZED",
            "palette": ["#f7f7f7", "#d1e5f0", "#67a9cf", "#2166ac", "#053061"],
            "min": -0.4,
            "max": 0.4,
            "unit": "ratio",
            "url": None,
            "ready": False
        },
        "ndbi": {
            "name": "Normalized Difference Built-Up Index (Sentinel-2)",
            "band": "NDBI",
            "resolution": "20m",
            "dataset": "COPERNICUS/S2_SR_HARMONIZED",
            "palette": ["#2c7bb6", "#abd9e9", "#ffffbf", "#fdae61", "#d7191c"],
            "min": -0.3,
            "max": 0.5,
            "unit": "ratio",
            "url": None,
            "ready": False
        }
    }

    if not ee_manager.is_initialized:
        return {
            "authenticated": False,
            "status": "unconfigured",
            "tiles": default_layers,
            "message": "Earth Engine credentials not configured in backend/.env"
        }

    cache_key = f"tiles_{round(lat, 2)}_{round(lon, 2)}"
    cached = _SATELLITE_CACHE.get(cache_key)
    if cached and (time.time() - cached["timestamp"] < CACHE_TTL_SECONDS):
        return cached["data"]

    try:
        # Define 25km buffer around city coordinates
        point = ee.Geometry.Point([lon, lat])
        roi = point.buffer(radius_km * 1000)

        end_dt = datetime.utcnow()
        start_dt = end_dt - timedelta(days=90)
        start_str = start_dt.strftime('%Y-%m-%d')
        end_str = end_dt.strftime('%Y-%m-%d')

        tiles = {}

        # 1. Landsat LST MapId
        landsat_img = get_landsat_lst_image(roi, start_str, end_str)
        if landsat_img:
            lst_vis = {
                'min': 20.0,
                'max': 50.0,
                'palette': ['#0000ff', '#00ffff', '#ffff00', '#ff0000', '#7f0000']
            }
            map_id_lst = landsat_img.select('LST_C').getMapId(lst_vis)
            tiles['lst'] = {
                'url': map_id_lst['tile_fetcher'].url_format,
                'name': 'Land Surface Temperature (Landsat 8/9)',
                'min_c': 20.0,
                'max_c': 50.0,
                'resolution': '30m',
                'dataset': 'LANDSAT/LC08/C02/T1_L2 + LC09'
            }

        # 2. Sentinel-2 Indices MapIds
        s2_img = get_sentinel2_indices_image(roi, start_str, end_str)
        if s2_img:
            # NDVI
            ndvi_vis = {
                'min': -0.1,
                'max': 0.75,
                'palette': ['#8B4513', '#FFF8DC', '#90EE90', '#228B22', '#006400']
            }
            map_id_ndvi = s2_img.select('NDVI').getMapId(ndvi_vis)
            tiles['ndvi'] = {
                'url': map_id_ndvi['tile_fetcher'].url_format,
                'name': 'Normalized Difference Vegetation Index (Sentinel-2)',
                'min': -0.1,
                'max': 0.75,
                'resolution': '10m',
                'dataset': 'COPERNICUS/S2_SR_HARMONIZED'
            }

            # NDWI
            ndwi_vis = {
                'min': -0.4,
                'max': 0.4,
                'palette': ['#f7f7f7', '#d1e5f0', '#67a9cf', '#2166ac', '#053061']
            }
            map_id_ndwi = s2_img.select('NDWI').getMapId(ndwi_vis)
            tiles['ndwi'] = {
                'url': map_id_ndwi['tile_fetcher'].url_format,
                'name': 'Normalized Difference Water Index (Sentinel-2)',
                'min': -0.4,
                'max': 0.4,
                'resolution': '10m',
                'dataset': 'COPERNICUS/S2_SR_HARMONIZED'
            }

            # NDBI
            ndbi_vis = {
                'min': -0.3,
                'max': 0.4,
                'palette': ['#2ca02c', '#ffff99', '#ff7f00', '#e31a1c', '#67000d']
            }
            map_id_ndbi = s2_img.select('NDBI').getMapId(ndbi_vis)
            tiles['ndbi'] = {
                'url': map_id_ndbi['tile_fetcher'].url_format,
                'name': 'Normalized Difference Built-up Index (Sentinel-2)',
                'min': -0.3,
                'max': 0.4,
                'resolution': '20m',
                'dataset': 'COPERNICUS/S2_SR_HARMONIZED'
            }

        result = {
            "authenticated": True,
            "status": "success",
            "tiles": tiles,
            "observation_window": f"{start_str} to {end_str}",
            "center": [lat, lon]
        }
        _SATELLITE_CACHE[cache_key] = {"timestamp": time.time(), "data": result}
        return result

    except Exception as e:
        logger.error(f"Error generating Earth Engine tile URLs: {e}", exc_info=True)
        return {
            "authenticated": True,
            "status": "error",
            "tiles": {},
            "error_message": str(e)
        }


# ==============================================================================
# ZONAL STATISTICS EXTRACTION FOR THE 5 ANALYSIS ZONES
# ==============================================================================

def compute_satellite_zonal_statistics(
    zones: List[Dict[str, Any]],
    city_name: str,
    days_back: int = 90
) -> Dict[str, Any]:
    """
    Computes genuine zonal statistics for the five analysis zones:
    - Mean, min, max Land Surface Temperature from Landsat 8/9 ST_B10 (30m)
    - Mean NDVI, NDWI, NDBI, and vegetation fraction from Sentinel-2 (10-20m)
    - Regional baseline from MODIS (1000m)
    - Valid pixel counts, acquisition dates, satellite names, and cloud cover.
    """
    if not ee_manager.is_initialized:
        return {
            "authenticated": False,
            "status": "unconfigured",
            "error_message": "Google Earth Engine service account is not configured in backend/.env",
            "setup_required": True,
            "zonal_statistics": {}
        }

    city_slug = city_name.lower().replace(" ", "_")
    cache_key = f"zonal_{city_slug}_{days_back}"
    cached = _SATELLITE_CACHE.get(cache_key)
    if cached and (time.time() - cached["timestamp"] < CACHE_TTL_SECONDS):
        return cached["data"]

    try:
        end_dt = datetime.utcnow()
        start_dt = end_dt - timedelta(days=days_back)
        start_str = start_dt.strftime('%Y-%m-%d')
        end_str = end_dt.strftime('%Y-%m-%d')

        # Convert zone polygons into Earth Engine Features
        ee_features = []
        zone_id_map = {}

        for z in zones:
            coords = z.get("polygon", [])
            # Leaflet polygon is [[lat, lon], ...]; GeoJSON / EE expects [[lon, lat], ...]
            ee_ring = [[p[1], p[0]] for p in coords]
            if ee_ring and ee_ring[0] != ee_ring[-1]:
                ee_ring.append(ee_ring[0])  # Close ring

            geom = ee.Geometry.Polygon(ee_ring)
            feat = ee.Feature(geom, {"zone_id": z["id"], "zone_name": z["name"]})
            ee_features.append(feat)
            zone_id_map[z["id"]] = z

        fc = ee.FeatureCollection(ee_features)
        total_bounds = fc.geometry().bounds()

        # 1. Query Landsat 8/9 Collection
        landsat_img = get_landsat_lst_image(total_bounds, start_str, end_str)

        # 2. Query Sentinel-2 Collection
        s2_img = get_sentinel2_indices_image(total_bounds, start_str, end_str)

        # 3. Query MODIS Collection
        modis_img = get_modis_lst_image(total_bounds, start_str, end_str)

        zonal_results = {}

        # Metadata extraction
        ls_satellite = "Landsat 8/9 OLI/TIRS"
        ls_date_str = "Unavailable"
        ls_clouds = 0.0
        if landsat_img:
            try:
                t_millis = landsat_img.get('system:time_start').getInfo()
                if t_millis:
                    ls_date_str = datetime.utcfromtimestamp(t_millis / 1000.0).strftime('%Y-%m-%d %H:%M UTC')
                sc_id = landsat_img.get('SPACECRAFT_ID').getInfo()
                if sc_id:
                    ls_satellite = f"{sc_id} Level-2"
                cc = landsat_img.get('CLOUD_COVER').getInfo()
                if cc is not None:
                    ls_clouds = round(float(cc), 1)
            except Exception as e:
                logger.warning(f"Could not extract Landsat metadata: {e}")

        s2_date_str = "Unavailable"
        s2_clouds = 0.0
        if s2_img:
            try:
                t_millis = s2_img.get('system:time_start').getInfo()
                if t_millis:
                    s2_date_str = datetime.utcfromtimestamp(t_millis / 1000.0).strftime('%Y-%m-%d %H:%M UTC')
                cc = s2_img.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()
                if cc is not None:
                    s2_clouds = round(float(cc), 1)
            except Exception as e:
                logger.warning(f"Could not extract Sentinel-2 metadata: {e}")

        # Compute zonal statistics for each individual zone
        for z in zones:
            zid = z["id"]
            coords = z.get("polygon", [])
            ee_ring = [[p[1], p[0]] for p in coords]
            if ee_ring and ee_ring[0] != ee_ring[-1]:
                ee_ring.append(ee_ring[0])
            ee_geom = ee.Geometry.Polygon(ee_ring)

            # Landsat LST Reduction
            lst_stats = {}
            if landsat_img:
                try:
                    stats = landsat_img.select('LST_C').reduceRegion(
                        reducer=ee.Reducer.mean().combine(ee.Reducer.minMax(), sharedInputs=True).combine(ee.Reducer.count(), sharedInputs=True),
                        geometry=ee_geom,
                        scale=30,
                        maxPixels=1e8
                    ).getInfo()
                    lst_stats = {
                        "mean_c": round(stats.get('LST_C_mean', 0.0), 2) if stats.get('LST_C_mean') is not None else None,
                        "min_c": round(stats.get('LST_C_min', 0.0), 2) if stats.get('LST_C_min') is not None else None,
                        "max_c": round(stats.get('LST_C_max', 0.0), 2) if stats.get('LST_C_max') is not None else None,
                        "pixel_count": stats.get('LST_C_count', 0)
                    }
                except Exception as e:
                    logger.warning(f"Zone {zid} Landsat reduce error: {e}")

            # Sentinel-2 Multispectral Indices Reduction
            s2_stats = {}
            if s2_img:
                try:
                    s2_reduced = s2_img.reduceRegion(
                        reducer=ee.Reducer.mean().combine(ee.Reducer.count(), sharedInputs=True),
                        geometry=ee_geom,
                        scale=20,
                        maxPixels=1e8
                    ).getInfo()
                    s2_stats = {
                        "ndvi_mean": round(s2_reduced.get('NDVI_mean', 0.0), 3) if s2_reduced.get('NDVI_mean') is not None else None,
                        "ndwi_mean": round(s2_reduced.get('NDWI_mean', 0.0), 3) if s2_reduced.get('NDWI_mean') is not None else None,
                        "ndbi_mean": round(s2_reduced.get('NDBI_mean', 0.0), 3) if s2_reduced.get('NDBI_mean') is not None else None,
                        "veg_cover_pct": round(s2_reduced.get('VEG_COVER_mean', 0.0) * 100.0, 1) if s2_reduced.get('VEG_COVER_mean') is not None else None,
                        "pixel_count": s2_reduced.get('NDVI_count', 0)
                    }
                except Exception as e:
                    logger.warning(f"Zone {zid} Sentinel-2 reduce error: {e}")

            # MODIS Regional LST
            modis_stats = {}
            if modis_img:
                try:
                    m_reduced = modis_img.select('LST_MODIS_C').reduceRegion(
                        reducer=ee.Reducer.mean(),
                        geometry=ee_geom,
                        scale=1000,
                        maxPixels=1e8
                    ).getInfo()
                    modis_stats = {
                        "modis_lst_c": round(m_reduced.get('LST_MODIS_C', 0.0), 2) if m_reduced.get('LST_MODIS_C') is not None else None
                    }
                except Exception as e:
                    logger.warning(f"Zone {zid} MODIS reduce error: {e}")

            zonal_results[zid] = {
                "zone_id": zid,
                "zone_name": z["name"],
                "data_type": "SATELLITE_DERIVED",
                "is_real_satellite": True,
                "data_quality_status": "VALID_OBSERVATION" if (lst_stats.get("mean_c") is not None) else "NO_DATA_CLOUD_COVERED",
                "landsat_lst": {
                    "satellite": ls_satellite,
                    "dataset": "LANDSAT/LC08/C02/T1_L2 + LC09",
                    "resolution": "30m",
                    "band": "ST_B10 (Scaled Kelvin - 273.15)",
                    "acquisition_date": ls_date_str,
                    "cloud_cover_pct": ls_clouds,
                    "mean_lst_c": lst_stats.get("mean_c"),
                    "min_lst_c": lst_stats.get("min_c"),
                    "max_lst_c": lst_stats.get("max_c"),
                    "valid_pixels": lst_stats.get("pixel_count", 0)
                },
                "sentinel2_indices": {
                    "satellite": "Sentinel-2 MSI",
                    "dataset": "COPERNICUS/S2_SR_HARMONIZED",
                    "resolution": "10m - 20m",
                    "acquisition_date": s2_date_str,
                    "cloud_cover_pct": s2_clouds,
                    "ndvi_mean": s2_stats.get("ndvi_mean"),
                    "ndwi_mean": s2_stats.get("ndwi_mean"),
                    "ndbi_mean": s2_stats.get("ndbi_mean"),
                    "vegetation_cover_pct": s2_stats.get("veg_cover_pct"),
                    "valid_pixels": s2_stats.get("pixel_count", 0),
                    "thermal_notice": "Sentinel-2 provides multispectral surface reflectance; thermal LST is derived from Landsat 8/9 and MODIS."
                },
                "modis_regional": {
                    "satellite": "MODIS Terra",
                    "dataset": "MODIS/061/MOD11A1",
                    "resolution": "1000m",
                    "temporal_resolution": "Daily / 8-Day Composite",
                    "mean_lst_c": modis_stats.get("modis_lst_c")
                },
                "processing_timestamp": datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
            }

        response_data = {
            "authenticated": True,
            "status": "success",
            "city_name": city_name,
            "observation_window": f"{start_str} to {end_str}",
            "zonal_statistics": zonal_results
        }
        _SATELLITE_CACHE[cache_key] = {"timestamp": time.time(), "data": response_data}
        return response_data

    except Exception as e:
        logger.error(f"Zonal satellite computation failed for {city_name}: {e}", exc_info=True)
        return {
            "authenticated": True,
            "status": "error",
            "error_message": f"Earth Engine calculation error: {str(e)}",
            "zonal_statistics": {}
        }
