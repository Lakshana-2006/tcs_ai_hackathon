"""
Synthetic Dataset for HEATSHIELD AI - Solaria Metro Digital Twin.
NOTE: All demographic, geographic, and climate figures are synthetic baseline assumptions
constructed for hackathon prototyping and illustrative decision-support demonstration.
"""

from typing import Dict, Any, List

CITY_CENTER = {"lat": 37.7749, "lng": -122.4194, "zoom": 13}

WEIGHTS = {
    "w_hazard": 0.35,
    "w_exposure": 0.30,
    "w_vulnerability": 0.35
}

ZONES_DATA: Dict[str, Dict[str, Any]] = {
    "zone-1": {
        "id": "zone-1",
        "name": "Downtown Central Business District",
        "short_name": "Solaria Core",
        "type": "Commercial / High-Rise",
        "centroid": [37.7890, -122.4010],
        "polygon": [
            [37.7950, -122.4100],
            [37.7990, -122.3950],
            [37.7870, -122.3900],
            [37.7810, -122.4030],
            [37.7890, -122.4120]
        ],
        "population": 124500,
        "daytime_commuters": 85000,
        "area_km2": 4.2,
        "baseline_hazard": {
            "air_temperature_c": 32.5,
            "apparent_temperature_c": 36.8,
            "relative_humidity_pct": 52.0,
            "lst_anomaly_c": 6.8,
            "peak_surface_temp_c": 43.8,
            "extreme_heat_days": 38,
            "uhi_intensity_index": 82.0,
            "hazard_score": 79.2,
            "weather_timestamp": "Latest Cached",
            "weather_data_source": "Solaria Digital Twin Meteorological Baseline"
        },
        "baseline_exposure": {
            "population_density_sqkm": 29642,
            "outdoor_worker_pct": 14.5,
            "outdoor_worker_count": 18052,
            "transit_commuter_density": "High",
            "building_density": "Very High (FAR 5.2 • 89% Built Impervious Footprint)",
            "exposure_score": 83.5
        },
        "baseline_vulnerability": {
            "elderly_pct": 11.2,
            "elderly_count": 13944,
            "children_pct": 6.8,
            "children_count": 8466,
            "poverty_rate_pct": 15.4,
            "canopy_cover_pct": 11.0,
            "canopy_deficit_pct": 89.0,
            "ac_penetration_pct": 88.0,
            "svi_score": 46.5,
            "vulnerability_score": 52.4
        },
        "heat_environmental": {
            "air_temperature_c": 32.5,
            "relative_humidity_pct": 52.0,
            "apparent_temperature_c": 36.8,
            "tree_canopy_cover_pct": 11.0,
            "building_density": "Very High (FAR 5.2 • 89% Built Impervious Footprint)",
            "water_availability": "Adequate (Dual-mains pressurized grid & 240 emergency hydrants)",
            "data_source_weather": "Solaria Meteorological Sensor Network (Synthetic Baseline)",
            "data_source_urban": "Municipal Digital Twin Heuristics (Synthetic)",
            "timestamp": "Latest Baseline",
            "temperature_is_measured": False
        },
        "population_vulnerability": {
            "total_population": 124500,
            "elderly_population": {"count": 13944, "pct": 11.2, "label": ">65 years"},
            "children_population": {"count": 8466, "pct": 6.8, "label": "<5 years"},
            "outdoor_worker_population": {"count": 18052, "pct": 14.5, "label": "Direct solar exposure workforce"},
            "poverty_rate_pct": 15.4,
            "ac_penetration_pct": 88.0,
            "is_synthetic": True
        },
        "infrastructure_urban": {
            "hospital_availability": "3 Tertiary Hospitals (850 Acute Beds • Full Trauma Hub)",
            "cooling_facility_availability": "3 Operational Facilities (Transit Hub HVAC Lounges • 1,400 capacity)",
            "land_use_classification": "Commercial / High-Rise Office & Corporate Headquarters",
            "power_demand": "175 MW (High Peak A/C Strain • 94% Substation Load)",
            "is_synthetic": True
        },
        "adaptive_capacity": {
            "score": 66.0,
            "rating": "Moderate-High (Strong trauma response, robust building envelopes)",
            "is_synthetic": True
        },
        "vulnerability_factors": [
            "Severe urban canyon heat trapping with thermal inertia",
            "Heavy daytime pedestrian & transit commuter exposure",
            "Impervious concrete coverage exceeds 85%"
        ],
        "recommended_priorities": ["cool_roofs", "green_corridors", "tree_planting"],
        "baseline_risk": 74.5
    },
    "zone-2": {
        "id": "zone-2",
        "name": "Vulcan Industrial & Freight Yard",
        "short_name": "Industrial Basin",
        "type": "Heavy Industrial / Logistics",
        "centroid": [37.7650, -122.3880],
        "polygon": [
            [37.7730, -122.3910],
            [37.7710, -122.3780],
            [37.7560, -122.3750],
            [37.7530, -122.3920],
            [37.7640, -122.3950]
        ],
        "population": 46200,
        "daytime_commuters": 42000,
        "area_km2": 6.8,
        "baseline_hazard": {
            "air_temperature_c": 34.8,
            "apparent_temperature_c": 41.2,
            "relative_humidity_pct": 48.0,
            "lst_anomaly_c": 8.4,
            "peak_surface_temp_c": 47.2,
            "extreme_heat_days": 46,
            "uhi_intensity_index": 92.5,
            "hazard_score": 91.5,
            "weather_timestamp": "Latest Cached",
            "weather_data_source": "Solaria Digital Twin Meteorological Baseline"
        },
        "baseline_exposure": {
            "population_density_sqkm": 6794,
            "outdoor_worker_pct": 42.0,
            "outdoor_worker_count": 19404,
            "transit_commuter_density": "Medium",
            "building_density": "High (FAR 2.2 • 78% Metal Roofs & Asphalt Storage)",
            "exposure_score": 71.8
        },
        "baseline_vulnerability": {
            "elderly_pct": 9.5,
            "elderly_count": 4389,
            "children_pct": 8.0,
            "children_count": 3696,
            "poverty_rate_pct": 28.5,
            "canopy_cover_pct": 6.5,
            "canopy_deficit_pct": 93.5,
            "ac_penetration_pct": 52.0,
            "svi_score": 72.0,
            "vulnerability_score": 78.4
        },
        "heat_environmental": {
            "air_temperature_c": 34.8,
            "relative_humidity_pct": 48.0,
            "apparent_temperature_c": 41.2,
            "tree_canopy_cover_pct": 6.5,
            "building_density": "High (FAR 2.2 • 78% Metal Roofs & Asphalt Storage)",
            "water_availability": "Constrained (Industrial Supply • Hydrant Deficit)",
            "data_source_weather": "Solaria Meteorological Sensor Network (Synthetic Baseline)",
            "data_source_urban": "Municipal Digital Twin Heuristics (Synthetic)",
            "timestamp": "Latest Baseline",
            "temperature_is_measured": False
        },
        "population_vulnerability": {
            "total_population": 46200,
            "elderly_population": {"count": 4389, "pct": 9.5, "label": ">65 years"},
            "children_population": {"count": 3696, "pct": 8.0, "label": "<5 years"},
            "outdoor_worker_population": {"count": 19404, "pct": 42.0, "label": "Direct solar exposure workforce"},
            "poverty_rate_pct": 28.5,
            "ac_penetration_pct": 52.0,
            "is_synthetic": True
        },
        "infrastructure_urban": {
            "hospital_availability": "1 Occupational Clinic (25 Beds • No Trauma Wing)",
            "cooling_facility_availability": "0 Dedicated Facilities (Critical Worker Sanctuary Gap)",
            "land_use_classification": "Heavy Industrial Logistics & Rail Freight Terminal",
            "power_demand": "245 MW (Heavy Industrial Machinery & Exhaust Baseload)",
            "is_synthetic": True
        },
        "adaptive_capacity": {
            "score": 34.0,
            "rating": "Deficient (High worker exposure, zero public cooling shelters)",
            "is_synthetic": True
        },
        "vulnerability_factors": [
            "Excessive dark metal roofing and vast asphalt yards",
            "High concentration of outdoor shift workers exposed to direct solar radiation",
            "Critically low tree canopy (6.5%) with heavy nocturnal heat retention"
        ],
        "recommended_priorities": ["cool_roofs", "permeable_pavements", "cooling_centers"],
        "baseline_risk": 81.2
    },
    "zone-3": {
        "id": "zone-3",
        "name": "Heritage Oldtown & Eastside Quarter",
        "short_name": "Historic Eastside",
        "type": "Dense Mixed Residential / Historic",
        "centroid": [37.7680, -122.4200],
        "polygon": [
            [37.7780, -122.4260],
            [37.7790, -122.4110],
            [37.7610, -122.4080],
            [37.7580, -122.4240],
            [37.7690, -122.4280]
        ],
        "population": 168000,
        "daytime_commuters": 25000,
        "area_km2": 5.1,
        "baseline_hazard": {
            "air_temperature_c": 33.6,
            "apparent_temperature_c": 39.4,
            "relative_humidity_pct": 54.0,
            "lst_anomaly_c": 7.1,
            "peak_surface_temp_c": 44.5,
            "extreme_heat_days": 41,
            "uhi_intensity_index": 84.0,
            "hazard_score": 82.8,
            "weather_timestamp": "Latest Cached",
            "weather_data_source": "Solaria Digital Twin Meteorological Baseline"
        },
        "baseline_exposure": {
            "population_density_sqkm": 32941,
            "outdoor_worker_pct": 21.5,
            "outdoor_worker_count": 36120,
            "transit_commuter_density": "Very High",
            "building_density": "Extremely Dense (FAR 3.8 • 93% Footprint • Unshaded Tenements)",
            "exposure_score": 88.6
        },
        "baseline_vulnerability": {
            "elderly_pct": 28.4,
            "elderly_count": 47712,
            "children_pct": 14.2,
            "children_count": 23856,
            "poverty_rate_pct": 34.0,
            "canopy_cover_pct": 12.0,
            "canopy_deficit_pct": 88.0,
            "ac_penetration_pct": 38.0,
            "svi_score": 89.2,
            "vulnerability_score": 89.5
        },
        "heat_environmental": {
            "air_temperature_c": 33.6,
            "relative_humidity_pct": 54.0,
            "apparent_temperature_c": 39.4,
            "tree_canopy_cover_pct": 12.0,
            "building_density": "Extremely Dense (FAR 3.8 • 93% Footprint • Unshaded Tenements)",
            "water_availability": "Vulnerable Deficit (Aging 60-year Cast Iron Mains • Low Pressure)",
            "data_source_weather": "Solaria Meteorological Sensor Network (Synthetic Baseline)",
            "data_source_urban": "Municipal Digital Twin Heuristics (Synthetic)",
            "timestamp": "Latest Baseline",
            "temperature_is_measured": False
        },
        "population_vulnerability": {
            "total_population": 168000,
            "elderly_population": {"count": 47712, "pct": 28.4, "label": ">65 years"},
            "children_population": {"count": 23856, "pct": 14.2, "label": "<5 years"},
            "outdoor_worker_population": {"count": 36120, "pct": 21.5, "label": "Direct solar exposure workforce"},
            "poverty_rate_pct": 34.0,
            "ac_penetration_pct": 38.0,
            "is_synthetic": True
        },
        "infrastructure_urban": {
            "hospital_availability": "1 Community Hospital (110 Beds • Severe Surge Deficit)",
            "cooling_facility_availability": "1 Public Community Hall (200 capacity • Heavily Overburdened)",
            "land_use_classification": "Dense Mixed Heritage Residential & Street Market",
            "power_demand": "94 MW (Aging Transformer Strain • 98% Overload Risk)",
            "is_synthetic": True
        },
        "adaptive_capacity": {
            "score": 22.0,
            "rating": "Critically Deficient (High senior density, 62% lack AC)",
            "is_synthetic": True
        },
        "vulnerability_factors": [
            "Severe social vulnerability: 28.4% senior population and high poverty",
            "Aging uninsulated brick tenements with lack of central cooling",
            "Highest heat mortality susceptibility per capita in the municipality"
        ],
        "recommended_priorities": ["cooling_centers", "tree_planting", "cool_roofs"],
        "baseline_risk": 86.9
    },
    "zone-4": {
        "id": "zone-4",
        "name": "Marina Riverside & Market District",
        "short_name": "Riverside District",
        "type": "Residential / Riverfront Waterfront",
        "centroid": [37.8030, -122.4350],
        "polygon": [
            [37.8100, -122.4450],
            [37.8120, -122.4200],
            [37.7980, -122.4220],
            [37.7960, -122.4420],
            [37.8050, -122.4480]
        ],
        "population": 91000,
        "daytime_commuters": 30000,
        "area_km2": 4.8,
        "baseline_hazard": {
            "air_temperature_c": 29.8,
            "apparent_temperature_c": 33.2,
            "relative_humidity_pct": 58.0,
            "lst_anomaly_c": 3.8,
            "peak_surface_temp_c": 38.6,
            "extreme_heat_days": 21,
            "uhi_intensity_index": 44.0,
            "hazard_score": 46.2,
            "weather_timestamp": "Latest Cached",
            "weather_data_source": "Solaria Digital Twin Meteorological Baseline"
        },
        "baseline_exposure": {
            "population_density_sqkm": 18958,
            "outdoor_worker_pct": 12.0,
            "outdoor_worker_count": 10920,
            "transit_commuter_density": "Moderate",
            "building_density": "Moderate-High (FAR 2.4 • 64% Built Footprint)",
            "exposure_score": 58.4
        },
        "baseline_vulnerability": {
            "elderly_pct": 17.5,
            "elderly_count": 15925,
            "children_pct": 11.0,
            "children_count": 10010,
            "poverty_rate_pct": 14.8,
            "canopy_cover_pct": 26.5,
            "canopy_deficit_pct": 73.5,
            "ac_penetration_pct": 82.0,
            "svi_score": 38.0,
            "vulnerability_score": 42.0
        },
        "heat_environmental": {
            "air_temperature_c": 29.8,
            "relative_humidity_pct": 58.0,
            "apparent_temperature_c": 33.2,
            "tree_canopy_cover_pct": 26.5,
            "building_density": "Moderate-High (FAR 2.4 • 64% Built Footprint)",
            "water_availability": "Abundant (Riverfront Promenade & Canal Hydrant Network)",
            "data_source_weather": "Solaria Meteorological Sensor Network (Synthetic Baseline)",
            "data_source_urban": "Municipal Digital Twin Heuristics (Synthetic)",
            "timestamp": "Latest Baseline",
            "temperature_is_measured": False
        },
        "population_vulnerability": {
            "total_population": 91000,
            "elderly_population": {"count": 15925, "pct": 17.5, "label": ">65 years"},
            "children_population": {"count": 10010, "pct": 11.0, "label": "<5 years"},
            "outdoor_worker_population": {"count": 10920, "pct": 12.0, "label": "Direct solar exposure workforce"},
            "poverty_rate_pct": 14.8,
            "ac_penetration_pct": 82.0,
            "is_synthetic": True
        },
        "infrastructure_urban": {
            "hospital_availability": "2 General Hospitals (340 Beds • Full Emergency ER)",
            "cooling_facility_availability": "2 Waterfront Public Pavilions (750 capacity)",
            "land_use_classification": "Mixed Commercial Waterfront & Urban Promenade",
            "power_demand": "68 MW (Moderate Residential Load • Stable Substation)",
            "is_synthetic": True
        },
        "adaptive_capacity": {
            "score": 74.0,
            "rating": "Substantial (River wind corridor, high AC, accessible ERs)",
            "is_synthetic": True
        },
        "vulnerability_factors": [
            "Beneficiary of natural river wind channel and microclimate buffer",
            "Localized pocket vulnerability along unshaded transit avenues",
            "Moderate income resilience with high AC penetration"
        ],
        "recommended_priorities": ["tree_planting", "green_corridors"],
        "baseline_risk": 48.4
    },
    "zone-5": {
        "id": "zone-5",
        "name": "Aurora Foothills & Tech Eco-Campus",
        "short_name": "Aurora Greenbelt",
        "type": "Master-Planned Suburban / Tech Hub",
        "centroid": [37.7450, -122.4500],
        "polygon": [
            [37.7550, -122.4650],
            [37.7580, -122.4380],
            [37.7390, -122.4350],
            [37.7340, -122.4600],
            [37.7470, -122.4680]
        ],
        "population": 72500,
        "daytime_commuters": 45000,
        "area_km2": 7.5,
        "baseline_hazard": {
            "air_temperature_c": 27.2,
            "apparent_temperature_c": 28.8,
            "relative_humidity_pct": 60.0,
            "lst_anomaly_c": 2.2,
            "peak_surface_temp_c": 35.8,
            "extreme_heat_days": 14,
            "uhi_intensity_index": 26.0,
            "hazard_score": 28.5,
            "weather_timestamp": "Latest Cached",
            "weather_data_source": "Solaria Digital Twin Meteorological Baseline"
        },
        "baseline_exposure": {
            "population_density_sqkm": 9666,
            "outdoor_worker_pct": 6.5,
            "outdoor_worker_count": 4712,
            "transit_commuter_density": "Low",
            "building_density": "Low-Moderate (FAR 1.1 • 35% Built Footprint • Campus Style)",
            "exposure_score": 34.2
        },
        "baseline_vulnerability": {
            "elderly_pct": 12.0,
            "elderly_count": 8700,
            "children_pct": 16.5,
            "children_count": 11962,
            "poverty_rate_pct": 8.2,
            "canopy_cover_pct": 44.0,
            "canopy_deficit_pct": 56.0,
            "ac_penetration_pct": 96.0,
            "svi_score": 19.5,
            "vulnerability_score": 24.8
        },
        "heat_environmental": {
            "air_temperature_c": 27.2,
            "relative_humidity_pct": 60.0,
            "apparent_temperature_c": 28.8,
            "tree_canopy_cover_pct": 44.0,
            "building_density": "Low-Moderate (FAR 1.1 • 35% Built Footprint • Campus Style)",
            "water_availability": "High (Modern Reclaimed Stormwater Retention & Reservoirs)",
            "data_source_weather": "Solaria Meteorological Sensor Network (Synthetic Baseline)",
            "data_source_urban": "Municipal Digital Twin Heuristics (Synthetic)",
            "timestamp": "Latest Baseline",
            "temperature_is_measured": False
        },
        "population_vulnerability": {
            "total_population": 72500,
            "elderly_population": {"count": 8700, "pct": 12.0, "label": ">65 years"},
            "children_population": {"count": 11962, "pct": 16.5, "label": "<5 years"},
            "outdoor_worker_population": {"count": 4712, "pct": 6.5, "label": "Direct solar exposure workforce"},
            "poverty_rate_pct": 8.2,
            "ac_penetration_pct": 96.0,
            "is_synthetic": True
        },
        "infrastructure_urban": {
            "hospital_availability": "1 University Medical Center (420 Platinum Beds)",
            "cooling_facility_availability": "4 Smart Community Centers (2,100 capacity • Solar Microgrid)",
            "land_use_classification": "Master-Planned Tech Eco-Campus & Low-Density Residential",
            "power_demand": "48 MW (LEED Platinum Efficiency • High Rooftop Solar)",
            "is_synthetic": True
        },
        "adaptive_capacity": {
            "score": 90.0,
            "rating": "Resilient (LEED Platinum envelopes, 44% canopy, solar microgrids)",
            "is_synthetic": True
        },
        "vulnerability_factors": [
            "High baseline vegetation coverage (44%) providing evaporative shielding",
            "High building energy efficiency standards (LEED Platinum/Gold)",
            "Low overall climate risk; functions as baseline reference zone"
        ],
        "recommended_priorities": ["green_corridors", "permeable_pavements"],
        "baseline_risk": 29.1
    }
}

INTERVENTIONS_CATALOG: Dict[str, Dict[str, Any]] = {
    "tree_planting": {
        "id": "tree_planting",
        "name": "Urban Canopy & Reforestation",
        "category": "Green Infrastructure",
        "unit": "% canopy expansion",
        "min_intensity": 0.0,
        "default_intensity": 25.0,
        "max_intensity": 50.0,
        "step": 0.5,
        "cost_per_unit_usd": 18000,
        "cooling_mechanism": "Direct shade interception & continuous evapotranspiration",
        "lst_reduction_per_unit_c": 0.055,
        "hazard_reduction_multiplier": 0.28,
        "exposure_reduction_multiplier": 0.08,
        "vulnerability_reduction_multiplier": 0.25,
        "uncertainty_sigma": 0.16,
        "reduces_surface_temp": True,
        "description": "Planting climate-hardy native shade trees in medians, parks, and residential streets. Long-term cooling benefits with biological lag."
    },
    "cool_roofs": {
        "id": "cool_roofs",
        "name": "Cool Roofs & High-Albedo Coatings",
        "category": "Reflective Infrastructure",
        "unit": "% roof area retrofitted",
        "min_intensity": 0.0,
        "default_intensity": 30.0,
        "max_intensity": 70.0,
        "step": 0.5,
        "cost_per_unit_usd": 12500,
        "cooling_mechanism": "High solar reflectance (albedo >= 0.75) and thermal emittance",
        "lst_reduction_per_unit_c": 0.045,
        "hazard_reduction_multiplier": 0.24,
        "exposure_reduction_multiplier": 0.04,
        "vulnerability_reduction_multiplier": 0.10,
        "uncertainty_sigma": 0.12,
        "reduces_surface_temp": True,
        "description": "Applying high-albedo elastomeric coating membranes on commercial flat roofs and residential buildings to reflect incoming solar radiation."
    },
    "cooling_centers": {
        "id": "cooling_centers",
        "name": "Emergency Resilient Cooling Hubs",
        "category": "Social & Health Defense",
        "unit": "operational hubs",
        "min_intensity": 0.0,
        "default_intensity": 4.0,
        "max_intensity": 10.0,
        "step": 1.0,
        "cost_per_unit_usd": 95000,
        "cooling_mechanism": "Safe indoor thermal haven, medical monitoring, cold hydration & clean air filtration",
        "lst_reduction_per_unit_c": 0.0,
        "hazard_reduction_multiplier": 0.0,
        "exposure_reduction_multiplier": 0.40,
        "vulnerability_reduction_multiplier": 0.35,
        "uncertainty_sigma": 0.10,
        "reduces_surface_temp": False,
        "description": "Equipping community centers, libraries, and schools with auxiliary microgrid power, high-volume HVAC, and medical triage for high-risk populations."
    },
    "permeable_pavements": {
        "id": "permeable_pavements",
        "name": "High-Albedo Permeable Pavements",
        "category": "Surface Modification",
        "unit": "% pavement area replaced",
        "min_intensity": 0.0,
        "default_intensity": 20.0,
        "max_intensity": 60.0,
        "step": 0.5,
        "cost_per_unit_usd": 14000,
        "cooling_mechanism": "Interlocking porous pavers with increased albedo and subsurface stormwater retention",
        "lst_reduction_per_unit_c": 0.032,
        "hazard_reduction_multiplier": 0.16,
        "exposure_reduction_multiplier": 0.05,
        "vulnerability_reduction_multiplier": 0.05,
        "uncertainty_sigma": 0.18,
        "reduces_surface_temp": True,
        "description": "Replacing heat-absorbing black asphalt on secondary roadways, parking lots, and alleys with reflective porous interlocking pavers."
    },
    "green_corridors": {
        "id": "green_corridors",
        "name": "Green Corridors & Micro-Misting Shelters",
        "category": "Pedestrian Protection",
        "unit": "km shaded transit corridor",
        "min_intensity": 0.0,
        "default_intensity": 5.0,
        "max_intensity": 15.0,
        "step": 0.5,
        "cost_per_unit_usd": 48000,
        "cooling_mechanism": "Linear vegetated bioswales, tensile fabric shading, and smart evaporative micro-misting",
        "lst_reduction_per_unit_c": 0.08,
        "hazard_reduction_multiplier": 0.14,
        "exposure_reduction_multiplier": 0.22,
        "vulnerability_reduction_multiplier": 0.15,
        "uncertainty_sigma": 0.15,
        "reduces_surface_temp": True,
        "description": "Continuous shaded walking corridors linking transit nodes to residential hubs, featuring solar-powered fine evaporative misting during peak heat."
    }
}
