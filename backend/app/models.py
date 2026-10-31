from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class CurrencyInfo(BaseModel):
    code: str = "USD"
    symbol: str = "$"
    name: str = "US Dollar"
    rate_per_usd: float = 1.0
    default_budget: float = 3500000.0


class CitySelection(BaseModel):
    id: str
    name: str
    country: str
    country_code: str
    admin1: Optional[str] = ""
    latitude: float
    longitude: float
    timezone: Optional[str] = "UTC"
    display_name: str
    currency: CurrencyInfo


class WeatherResponse(BaseModel):
    status: str
    air_temperature_c: float
    relative_humidity_pct: float
    apparent_temperature_c: float
    wind_speed_kmh: float
    precipitation_mm: float
    condition: str
    timestamp: str
    data_source: str
    measurement_notice: str


class InterventionInput(BaseModel):
    id: str
    name: str
    intensity: float = Field(0.0, ge=0.0, le=100.0)
    unit: str = "%"


class ZoneSimRequest(BaseModel):
    zone_id: Optional[str] = None
    city_name: Optional[str] = "Global Metro"
    currency_code: Optional[str] = "USD"
    currency_symbol: Optional[str] = "$"
    currency_rate: Optional[float] = 1.0
    zone_data: Optional[Dict[str, Any]] = None  # Full zone snapshot if dynamic
    interventions: Dict[str, float] = Field(default_factory=dict)


class UncertaintyBounds(BaseModel):
    low: float
    expected: float
    high: float
    confidence_level: str = "90% CI"


class FactorBreakdown(BaseModel):
    hazard_score: float
    exposure_score: float
    vulnerability_score: float
    composite_risk: float
    lst_anomaly_c: float
    effective_exposure_pop: int


class SimulationResult(BaseModel):
    zone_id: str
    zone_name: str
    city_name: str
    currency_symbol: str = "$"
    baseline: FactorBreakdown
    simulated: FactorBreakdown
    risk_delta: float
    risk_reduction_pct: float
    lst_reduction_c: float
    people_protected: int
    estimated_cost_local: float
    estimated_cost_usd: float
    uncertainty: UncertaintyBounds
    intervention_breakdown: List[Dict[str, Any]]
    explanation_notes: List[str]


class CitySimulationResponse(BaseModel):
    city_name: str
    currency_symbol: str = "$"
    total_cost_local: float
    total_cost_usd: float
    total_people_protected: int
    avg_risk_reduction_pct: float
    avg_lst_reduction_c: float
    zone_results: List[SimulationResult]
    synthetic_notice: str


class OptimizeRequest(BaseModel):
    city_name: str = "Global Metro"
    country_code: str = "US"
    currency_code: str = "USD"
    currency_symbol: str = "$"
    currency_rate: float = 1.0
    total_budget_local: float = Field(default=3500000.0, ge=1000.0)
    equity_weighting: bool = Field(default=True)
    focus_objective: str = Field(default="balanced")
    zones: Optional[List[Dict[str, Any]]] = None  # Dynamic zone list for current city


class AllocatedIntervention(BaseModel):
    zone_id: str
    zone_name: str
    intervention_id: str
    intervention_name: str
    intensity: float
    unit: str
    cost_local: float
    cost_usd: float
    risk_reduction_points: float
    people_protected: int
    why_prioritized: str


class OptimizationResponse(BaseModel):
    city_name: str
    currency_code: str
    currency_symbol: str
    total_budget_local: float
    budget_utilized_local: float
    budget_remaining_local: float
    total_budget_usd: float
    budget_utilized_usd: float
    equity_weighting_applied: bool
    total_people_protected: int
    city_average_risk_before: float
    city_average_risk_after: float
    risk_reduction_pct: float
    allocations_by_zone: Dict[str, List[AllocatedIntervention]]
    zone_summaries: List[Dict[str, Any]]
    prioritization_rationale: List[str]
    synthetic_notice: str


class ChatMessage(BaseModel):
    role: str = "user"  # "user" | "assistant" | "system"
    content: str
    timestamp: Optional[str] = None


class DashboardContext(BaseModel):
    city: Optional[Dict[str, Any]] = None
    weather: Optional[Dict[str, Any]] = None
    zones: Optional[List[Dict[str, Any]]] = None
    selected_zone: Optional[Dict[str, Any]] = None
    selected_interventions: Optional[Dict[str, float]] = None
    simulation_result: Optional[Dict[str, Any]] = None


class ChatRequest(BaseModel):
    message: str
    conversation_history: List[ChatMessage] = Field(default_factory=list)
    context: Optional[DashboardContext] = None


class ChatResponse(BaseModel):
    reply: str
    is_configured: bool = True
    provider: Optional[str] = None
    setup_instructions: Optional[str] = None
    context_used: Optional[Dict[str, Any]] = None


class SatelliteStatusResponse(BaseModel):
    authenticated: bool
    status: str
    auth_method: Optional[str] = None
    project_id: Optional[str] = None
    service_account: Optional[str] = None
    error_message: Optional[str] = None
    supported_datasets: List[Dict[str, str]] = Field(default_factory=list)
    setup_instructions: Optional[str] = None


class SatelliteZonalRecord(BaseModel):
    zone_id: str
    zone_name: str
    data_type: str = "SATELLITE_DERIVED"
    is_real_satellite: bool = True
    data_quality_status: str
    landsat_lst: Dict[str, Any]
    sentinel2_indices: Dict[str, Any]
    modis_regional: Dict[str, Any]
    processing_timestamp: str


class SatelliteZonesResponse(BaseModel):
    authenticated: bool
    status: str
    city_name: str
    observation_window: Optional[str] = None
    zonal_statistics: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None


