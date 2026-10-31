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

## ⚖️ Synthetic Demo & Academic Disclaimer

> **IMPORTANT**: Meteorological air temperatures and humidity are retrieved from real-time **Open-Meteo API**. Zone boundaries, demographic counts, vulnerability indices, and intervention impact response functions are **illustrative synthetic demo assumptions** for hackathon prototype decision-support. This software is **not scientifically validated** and must not be used for life-critical urban emergency management or municipal engineering.
