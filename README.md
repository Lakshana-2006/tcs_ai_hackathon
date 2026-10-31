# HEATSHIELD AI — Global Urban Climate Resilience Digital Twin

> **Real-Time Global Urban Microclimate Twin**: Live Open-Meteo weather telemetry, global city geocoding, procedural 5-zone spatial analysis, IPCC AR6 heat risk modeling, what-if intervention simulation, currency-aware AI budget optimization, and explainable decision support.

---

## 🌟 What's New in Global Version 2.0

1. **Global City Search & Geocoding**:
   - Search and select **any city worldwide** (e.g., Chennai, Mumbai, Tokyo, London, Dubai, New York, Singapore, Paris, etc.).
   - Integrated Open-Meteo Geocoding API with fast local fallback directory for reliable offline support.
   - Quick pill buttons in the header for instant switching between major world metros.

2. **Real-Time Open-Meteo Global Weather Telemetry**:
   - Retrieves live weather for the selected city coordinates:
     - 🌡️ **Air Temperature (°C)** measured at 2m reference height.
     - 💧 **Relative Humidity (%)**
     - 🔥 **Apparent Temperature (°C)** (Heat index / feels-like)
     - ⏱️ **Timestamp & Data Source**: Open-Meteo Global Forecast Engine.
   - *Biophysical distinction*: Explicitly notes that air temperature is ambient weather, not satellite land-surface temperature (LST).

3. **Dynamic 5-Zone Microclimate Generation**:
   - For every selected city, 5 unique illustrative analysis zones are mathematically generated around the city's coordinates using spherical Earth radius projection:
     - **Zone 1: `[City] Central Core & CBD`** (High-density canyon, low canopy, transit rush)
     - **Zone 2: `[City] Industrial & Freight Basin`** (High thermal mass metal roofing, night-time heat trapping)
     - **Zone 3: `[City] Historic Old Quarter & Eastside`** (High Social Vulnerability Index, 29% seniors, low AC)
     - **Zone 4: `[City] Riverside Waterfront & Market`** (Water-cooling wind channel buffer)
     - **Zone 5: `[City] Suburban Greenbelt & Tech Park`** (High canopy cover, climate-resilient LEED campus)
   - Unique zone IDs (e.g., `chennai_zone_1`, `tokyo_zone_2`, `london_zone_3`) ensure zero cross-city collision. Old city zones are completely replaced upon city change.
   - Clearly labeled: *Zone boundaries are illustrative digital twin analysis perimeters, not official administrative municipal borders.*

4. **Currency-Aware Resilience Budgeting**:
   - Automatically adapts to the local currency of the selected country:
     - **India (IN)**: INR (₹) — formatted in Lakhs and Crores.
     - **Japan (JP)**: JPY (¥) — formatted in Millions / 億.
     - **United Kingdom (GB)**: GBP (£)
     - **United States (US)**: USD ($)
     - **United Arab Emirates (AE)**: AED
     - **European Union (EU)**: EUR (€)
     - Others: Local currency where mapped, or USD standard.
   - Multi-criteria greedy knapsack optimizer operates natively in local currency with equity weighting (SVI boost).

5. **IPCC AR6 Explainable Risk Decomposition**:
   $$\text{Composite Risk} = (0.35 \times \text{Hazard}) + (0.30 \times \text{Exposure}) + (0.35 \times \text{Vulnerability})$$
   - **Hazard (35%)**: Real-time Open-Meteo air temperature, apparent heat index, and zone UHI anomaly.
   - **Exposure (30%)**: Population density, daytime commuter flux, outdoor worker proportion.
   - **Vulnerability (35%)**: Senior % ($>65$), child %, poverty rate %, canopy deficit %, AC deficit %.

6. **Biophysical Intervention Constraint**:
   - **Cooling Centres**: Modeled strictly as **indoor human exposure & vulnerability havens** (protecting senior and outdoor worker lives). They have **0.0°C impact on outdoor Land Surface Temperature (LST)**.
   - **Tree Planting & Cool Roofs**: Physically reduce Land Surface Temperature via shade, albedo reflection, and evapotranspiration.

---

## 🚀 Quick Start Guide

### 1. Launch All (Fastest)
Double-click `start_all.bat` or run in terminal:
```cmd
start_all.bat
```
- **Frontend Dashboard**: `http://127.0.0.1:5173`
- **Backend API**: `http://127.0.0.1:8000`
- **Interactive Swagger Docs**: `http://127.0.0.1:8000/docs`

---

### 2. Manual Startup

#### Backend (FastAPI):
```bash
cd backend
pip install -r requirements.txt
python run_backend.py
```

#### Frontend (React + Vite + Leaflet + Tailwind):
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Automated Global Verification Test Suite

Run the built-in 8-part automated test suite:
```bash
python backend/test_api.py
```
Verifies:
1. Global geocoding search for Chennai, Tokyo, London, Dubai, New York.
2. Real-time Open-Meteo weather fetch.
3. Generation of 5 unique zones for each city without cross-city ID collision.
4. Leaflet spatial polygon generation around real coordinates.
5. Local currency conversion (INR ₹, JPY ¥, GBP £, USD $, AED).
6. Cooling Centre biophysical rule ($0.0^\circ\text{C}$ LST drop).
7. Budget optimizer allocations and explainable prioritization rationales.

---

## 🛰️ Google Earth Engine (GEE) Satellite Pipeline & Data Provenance

HEATSHIELD AI integrates authentic satellite observations processed via the Google Earth Engine Python API (`earthengine-api`):

### 1. Integrated Satellite Instruments & Datasets

| Satellite & Instrument | GEE Collection Identifier | Spatial Resolution | Bands / Parameters | Scaling & Methodology |
| :--- | :--- | :--- | :--- | :--- |
| **Landsat 8 & 9 OLI/TIRS** | `LANDSAT/LC08/C02/T1_L2`<br>`LANDSAT/LC09/C02/T1_L2` | 30m *(resampled thermal)* | `ST_B10` (Surface Temperature)<br>`QA_PIXEL` (Cloud bitmask) | $\text{Kelvin} = \text{ST\_B10} \times 0.00341802 + 149.0$<br>$\text{LST (}^\circ\text{C)} = \text{Kelvin} - 273.15$<br>Masks dilated cloud, cirrus, cloud, cloud-shadow |
| **Sentinel-2 MSI Level-2A** | `COPERNICUS/S2_SR_HARMONIZED` | 10m – 20m | `B2`, `B3`, `B4`, `B8`, `B11`<br>`QA60` & `SCL` | Reflectance scale: $\div 10000.0$<br>$\text{NDVI} = \frac{B8 - B4}{B8 + B4}$<br>$\text{NDWI} = \frac{B3 - B8}{B3 + B8}$<br>$\text{NDBI} = \frac{B11 - B8}{B11 + B8}$<br>**Fractional Veg Cover (FVC %)** via Carlson & Ripley / Gutman & Ignatov |
| **MODIS Terra Daily / 8-Day** | `MODIS/061/MOD11A1`<br>`MODIS/061/MOD11A2` | 1000m *(1 km)* | `LST_Day_1km` | $\text{LST (}^\circ\text{C)} = \text{LST\_Day\_1km} \times 0.02 - 273.15$<br>Macro-scale regional temperature baseline |

### 2. Physical & Meteorological Distinctions

- **Atmospheric Air Temperature ($T_{\text{air}}$)**: Measured at 2m reference height above ground from Open-Meteo numerical weather telemetry.
- **Land Surface Temperature (LST)**: Radiative skin temperature of urban surfaces (asphalt, concrete, vegetation, roofs) measured from orbit via Landsat thermal infrared (`ST_B10`) and MODIS.
- **Temporal Forecast & Climate**: Future projections are driven by Open-Meteo NWP forecasts (7-14 day) and HighResMIP CMIP6 climate models through 2050. Satellite observations represent recorded physical observations and are not fabricated forward in time.

### 3. Google Earth Engine Authentication Setup

To activate live Earth Engine satellite raster streaming in `backend/.env`:

```dotenv
EE_PROJECT_ID=your-gcp-project-id
EE_SERVICE_ACCOUNT=your-service-account@your-project.iam.gserviceaccount.com
EE_KEY_FILE=./service-account-key.json
```
*(Alternatively, configure `EE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n..."` for containerized environments.)*

When unconfigured, the digital twin operates in transparent **Pre-Authentication Standby Mode**, providing demographic baselines and live Open-Meteo weather without substituting fabricated satellite measurements.

---

## ⚖️ Synthetic Demo & Academic Disclaimer

> **IMPORTANT**: Meteorological air temperatures and humidity are retrieved from real-time **Open-Meteo API**. Zone boundaries, demographic counts, vulnerability indices, and intervention impact response functions are **illustrative synthetic demo assumptions** for hackathon prototype decision-support. This software is **not scientifically validated** and must not be used for life-critical urban emergency management or municipal engineering.
